#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Any, Generator, Optional

import configparser
import copy
import gzip
import optparse
import os
import re
import shutil
import statistics
import sys
import time
from collections import Counter
from datetime import date, datetime
from logging import getLogger
from logging.config import dictConfig
from string import Template

from conf.logging import get_logging_config


logger = getLogger("log-analyzer")

LOG_COMPILED = re.compile(
    r'.* .*  .* \[.*\] \".* (?P<url>.*) .*\" .* .* \".*\" \".*\" \".*\" \".*\" \".*\" (?P<request_time>.*)'
)
FILE_NAME_COMPILED = re.compile(r'^nginx-access-ui\.log-(?P<date>\d{8})(?P<ext>\.gz)?$')
SERVICE_NAME_PATTERN = r'nginx-access-ui'
TMP_REPORT_PATH = '/tmp/report.html'
CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def get_args_parser() -> Optional[configparser.ConfigParser]:
    args_parser = optparse.OptionParser()
    config_ini_parser = configparser.ConfigParser()

    args_parser.add_option('-c', '--config', dest="config",
                           help="Абсолютный путь к файлу конфигурации", default="")
    options, _ = args_parser.parse_args()
    if options.config:
        config_ini_parser.read(options.config)
        return config_ini_parser

    return None


def get_config(
        config_file: dict,
        config_ini_parser: Optional[configparser.ConfigParser]
) -> Optional[dict[str, Any]]:
    actual_config = copy.deepcopy(config_file)
    if config_ini_parser:
        try:
            [
                actual_config.update({param.upper(): value})
                for param, value in config_ini_parser['log-analyzer'].items()
            ]
        except KeyError:
            logger.error('Не удалось распарсить файл конфигурации.')
            return None

    return actual_config


def get_filename_from_path(path: str) -> str:
    if not path:
        return ''
    return path.split('/')[-1]


def get_log_files(log_dir: str) -> list[tuple]:
    result = []
    for (dir_path, _, filenames) in os.walk(log_dir):
        for name in filenames:
            # Берем только логи сервиса ui, только те у которых парсится дата в имени
            if re.search(SERVICE_NAME_PATTERN, name) and get_file_date(name):
                result.append((os.path.join(dir_path, name), get_file_date(name)))

    return sorted(result, key=lambda pair: pair[1], reverse=True)  # type: ignore


def get_file_date(file_path: str) -> Optional[date]:
    if date := FILE_NAME_COMPILED.match(get_filename_from_path(file_path)):
        try:
            return datetime.strptime(date.group('date'), '%Y%m%d').date()
        except (ValueError, AttributeError):
            pass

    logger.info(f'Не удается распарсить дату лог файла {file_path}')
    return None


def get_report_name(filename: str) -> str:
    date = get_file_date(filename)
    if not date:
        return 'report-unknown.html'
    return f"report-{datetime.strftime(date, '%Y.%m.%d')}.html"


def is_gzip_file(filename: str) -> bool:
    return filename.split('.')[-1] == 'gz'


def unpack_file(log: str) -> Generator[str, None, None]:
    is_archive = is_gzip_file(log)
    open_fn = gzip.open if is_archive else open
    with open_fn(log, 'rb') as f:  # type: ignore
        for line in f:
            yield line.decode()


def get_perc(total_count: float, count: float) -> float:
    if not total_count:
        return 0
    return 100 / total_count * count


def get_data_for_render(log_list: list, requests_count: int, report_size: int) -> Optional[list[dict[str, Any]]]:
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

    with open(TMP_REPORT_PATH, 'w') as f:
        f.write(result)

    shutil.move(TMP_REPORT_PATH, os.path.join(report_dir, report_name))


def pars_log(log_file: str) -> list[tuple[Any]]:
    return LOG_COMPILED.findall(log_file)


def get_log_data(log: str) -> tuple[list[tuple[Any]], int]:
    results = []
    requests_count = 0
    for log in unpack_file(log):
        data = pars_log(log)
        requests_count += 1
        results += data

    return results, requests_count


def main():
    conf = get_config(CONFIG, get_args_parser())
    if not conf:
        sys.exit(1)

    dictConfig(get_logging_config(conf.get('LOGGING_FILE_PATH')))
    try:
        last_log, _ = get_log_files(conf.get('LOG_DIR'))[0]
    except IndexError:
        logger.error('Файлов с логами не найдено.')
        sys.exit(1)

    report_name = get_report_name(last_log)
    report_dir = conf.get('REPORT_DIR')
    filename = get_filename_from_path(last_log)

    if os.path.exists(os.path.join(report_dir, report_name)):
        logger.info(f'Отчет {report_name} существует.')
        sys.exit(0)

    results, requests_count = get_log_data(last_log)
    if get_perc(requests_count, len(results)) < 50:
        logger.error(f'Неудалось распарсить больше половины файла {filename}')
        sys.exit(1)

    if data_for_render := get_data_for_render(results, requests_count, conf.get('REPORT_SIZE')):
        create_report(report_name, data_for_render, report_dir)


if __name__ == "__main__":
    start_time = time.time()

    try:
        main()
    except Exception as e:
        logger.exception(e)
        sys.exit(1)

    print("--- %s seconds ---" % (time.time() - start_time))
