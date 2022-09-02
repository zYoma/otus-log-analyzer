#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Any, Generator, Optional

import concurrent.futures
import configparser
import gzip
import optparse
import os
import re
import statistics
import sys
import time
from collections import Counter
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import date, datetime
from logging import getLogger
from logging.config import dictConfig
from string import Template

from conf.logging import get_logging_config


logger = getLogger("log-analyzer")

log_pattern = r'.* .*  .* \[.*\] \".* (?P<url>.*) .*\" .* .* \".*\" \".*\" \".*\" \".*\" \".*\" (?P<request_time>.*)'
service_name_pattern = r'nginx-access-ui'

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


class BaseLogAnalyzerError(Exception):
    pass


def get_config(config_file: dict) -> dict[str, Any]:
    """
    Путь к конфигурационному ini файлу передается в атрибуте --config.
    Дефолтная конфигурация обновляется переданной в файле.
    :param config_file: словарь с дефолтными конфигами
    :return: обновленная конфигурация
    """
    args_parser = optparse.OptionParser()
    config_ini_parser = configparser.ConfigParser()

    args_parser.add_option('-c', '--config', dest="config",
                           help="Абсолютный путь к файлу конфигурации", default="")
    options, _ = args_parser.parse_args()
    if options.config:
        config_ini_parser.read(options.config)
        try:
            [
                config_file.update({param.upper(): value})
                for param, value in config_ini_parser['log-analyzer'].items()
            ]
        except KeyError:
            logger.warning('Не удалось распарсить файл конфигурации.')
            raise BaseLogAnalyzerError

    return config_file


def get_log_files(log_dir: str) -> list[str]:
    """ Собираем список всех абсолютных путей к файлам в переданном каталоге.
        Парсятся имена файлов для получения даты. Итоговый список сортируется по дате.
    """
    logs = [
        os.path.join(dir_path, name)
        for (dir_path, _, filenames) in os.walk(log_dir)
        for name in filenames
        if re.search(service_name_pattern, name)  # Берем только логи сервиса ui
    ]
    file_dates = [get_file_date(file) for file in logs]
    return [x for _, x in sorted(zip(file_dates, logs), key=lambda pair: pair[0], reverse=True)]


def get_file_date(filename: str) -> date:
    filename = filename.split('/')[-1]
    if date := re.search(r'(?P<date>\d+)', filename):
        return datetime.strptime(date.group('date'), '%Y%m%d').date()

    logger.error(f'Не удается распарсить дату лог файла {filename}')
    raise BaseLogAnalyzerError


def get_report_name(filename: str) -> str:
    date = get_file_date(filename)
    return f"report-{datetime.strftime(date, '%Y.%m.%d')}.html"


def is_archive(filename: str) -> bool:
    ext = filename.split('.')[-1]
    return True if ext == 'gz' else False


def unpack_files(logs: list[str]) -> Generator[tuple[str, str, str], None, None]:
    for file in logs:
        report_name = get_report_name(file)
        filename = file.split('/')[-1]

        if is_archive(file):
            with gzip.open(file, 'rb') as f:
                log = f.read().decode()
        else:
            with open(file, 'r') as f:
                log = f.read()

        yield log, filename, report_name


def get_perc(total_count: float, count: float) -> float:
    try:
        return 100 / total_count * count
    except ZeroDivisionError:
        logger.error('Получен пустой файл.')
        raise BaseLogAnalyzerError


def get_log_data(log_list: list, requests_count: int, report_size: int) -> Optional[list[dict[str, Any]]]:
    """
    Функция получает на вход список распаршенных логов, отдельно собирает список урлов для подсчета
    количества (используется collections.Counter) и формирует словарь для расчета требуемых значений
    вида {'url': [1.2, 1,3, 1.4]}, где значения - списки request_time относящихся к данному урлу.
    На выходе формируется результирующий список отсортированный по time_sum и обрезанный по report_size.

    :param log_list: список распаршенных логов
    :param requests_count: общее колличество записей в логе
    :param report_size: количество строк для рапорта из конфига
    :return: список результатов для генерации таблицы
    """
    urls_data: dict[str, Any] = {}
    url_list: list[str] = []
    total_request_time = 0.0
    for url, request_time in log_list:
        url_list.append(url)
        request_time = float(request_time)
        total_request_time += request_time
        if request_time_list := urls_data.get(url):
            request_time_list.append(request_time)
            urls_data[url] = request_time_list
        else:
            urls_data[url] = [request_time]

    urls_count = Counter(url_list)

    result = []
    for url in urls_count.keys():
        request_time_list = urls_data[url]
        count = urls_count[url]
        time_sum = sum(request_time_list)
        url_data: dict = {
            "count": count,
            "time_avg": statistics.fmean(request_time_list),
            "time_max": max(request_time_list),
            "time_sum": time_sum,
            "url": url,
            "time_med": statistics.median(request_time_list),
            "time_perc": get_perc(total_request_time, time_sum),
            "count_perc": get_perc(requests_count, count)
        }
        result.append(url_data)

    return sorted(result, key=lambda d: d['time_sum'], reverse=True)[:int(report_size)]  # type: ignore


def create_report(report_name: str, data: list, report_dir: str):
    with open('report.html', 'r') as f:
        src = Template(f.read())
        result = src.safe_substitute(table_json=data)

    with open(os.path.join(report_dir, report_name), 'w') as f:
        f.write(result)


def pars_log(log_file: str) -> list[tuple[Any]]:
    return re.findall(log_pattern, log_file)


def get_slice_size_and_remainder(requests_count: int, worker_count: int) -> tuple[int, int]:
    """
    Для параллельного парсинга данных делим лог на чанки. Функция определяет размер среза и остаток.
    :param requests_count: всего строк в логе
    :param worker_count: число процессов
    :return: размер чанка и остаток
    """
    slice_size = requests_count // worker_count
    remainder = requests_count % worker_count
    assert slice_size * worker_count + remainder == requests_count
    return slice_size, remainder


def data_preparation_for_processing(
        executor: ProcessPoolExecutor,
        log_file_list: list,
        slice_size: int,
        remainder: int,
        worker_count: int
) -> dict[Future[list[tuple[Any]]], str]:
    """ Функция нарезает исходный лог файл на чанки для паралельного исполнения."""
    slice_start = 0
    slice_end = slice_size
    future_to_pars = {}
    for i in range(worker_count):
        if i + 1 == worker_count:
            # Если это последний чанк, добавляем остаток строк
            slice_end += remainder + 1
        log_slice = log_file_list[slice_start:slice_end]
        chunk = '\n'.join(log_slice)
        future_to_pars[executor.submit(pars_log, chunk)] = chunk

        slice_start = slice_end
        slice_end += slice_size

    return future_to_pars


def main():
    conf = get_config(config)

    logging_file_path = conf.get('LOGGING_FILE_PATH')
    log_dir = conf.get('LOG_DIR')
    report_size = conf.get('REPORT_SIZE')
    report_dir = conf.get('REPORT_DIR')
    worker_count = int(conf.get('WORKER_COUNT', 1))

    dictConfig(get_logging_config(logging_file_path))

    logs = get_log_files(log_dir)
    for log, filename, report_name in unpack_files(logs):
        if os.path.exists(os.path.join(report_dir, report_name)):
            logger.info(f'Отчет {report_name} существует. ')
            continue

        log_file_list = log.split('\n')
        requests_count = len(log_file_list)
        slice_size, remainder = get_slice_size_and_remainder(requests_count, worker_count)

        with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count) as executor:
            future_to_pars = data_preparation_for_processing(
                executor,
                log_file_list,
                slice_size,
                remainder,
                worker_count
            )

            results = []
            for future in concurrent.futures.as_completed(future_to_pars):
                try:
                    pars_data = future.result()
                except Exception:
                    logger.error(f'Ошибка парсинга файла {filename}')
                else:
                    results += pars_data

        if get_perc(requests_count, len(results)) < 50:
            logger.error(f'Неудалось распарсить больше половины файла {filename}')
            continue

        data_for_render = get_log_data(results, requests_count, report_size)
        if data_for_render:
            create_report(report_name, data_for_render, report_dir)


if __name__ == "__main__":
    start_time = time.time()

    try:
        main()
    except Exception as e:
        if not isinstance(e, BaseLogAnalyzerError):
            logger.exception(e)
        sys.exit(1)

    print("--- %s seconds ---" % (time.time() - start_time))
