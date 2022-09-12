import os
import pytest

from log_analyzer import (
    CONFIG,
    create_report,
    get_config,
    get_data_for_render,
    get_filename_from_path,
    get_log_data,
    get_log_files,
    get_perc,
    get_report_name,
    is_gzip_file,
    pars_log,
    unpack_file
)


@pytest.mark.parametrize('filename, result', [  # noqa
    ('nginx-access-ui.log-20170630.gz', 'report-2017.06.30.html'),
    ('./root/nginx-access-ui.log-20170630.gz', 'report-2017.06.30.html'),
    ('nginx-access-ui.log-20170630', 'report-2017.06.30.html'),
    ('nginx-access-ui.log-20170.gz', 'report-unknown.html'),
    ('nginx-access-ui.log.gz', 'report-unknown.html'),
])
def test_get_report_name(filename, result):
    test_result = get_report_name(filename)
    assert test_result == result


@pytest.mark.parametrize('filename, result', [  # noqa
    ('nginx-access-ui.log-20170630.gzz', False),
    ('./root/nginx-access-ui.log-20170630.gz', True),
    ('nginx-access-ui.log-20170630', False),
])
def test_is_archive(filename, result):
    test_result = is_gzip_file(filename)
    assert test_result == result


@pytest.mark.parametrize('total_count, count, result', [  # noqa
    (1000, 20, 2.0),
    (5, 2, 40.0),
    (0, 20, 0),
])
def test_get_perc(total_count, count, result):
    test_result = get_perc(total_count, count)
    assert test_result == result


def test_get_log_files(create_log_files):
    result = get_log_files('./log_tmp')
    assert str(result) == "[File(filename='./log_tmp/nginx-access-ui.log-20190630.gz', " \
                          "date=datetime.date(2019, 6, 30)), " \
                          "File(filename='./log_tmp/nginx-access-ui.log-20180630.gz', " \
                          "date=datetime.date(2018, 6, 30))]"


def test_get_log_data(create_log_files, log_data_result):
    result, count = get_log_data('./log_tmp/nginx-access-acc.log-20200430', pars_log)
    assert count == 10
    assert result == log_data_result


def test_create_report(log_data_result, create_report_dir):
    report_name = 'report-2017.06.30.html'
    create_report(report_name=report_name, data=log_data_result, report_dir=create_report_dir)
    assert os.path.exists(os.path.join(create_report_dir, report_name))

    with open(os.path.join(create_report_dir, report_name), 'r') as f:
        result = f.read()
        assert len(result) == 4293


@pytest.mark.parametrize('config_args, result', [  # noqa
    ({'any': 1}, {'REPORT_SIZE': 1000, 'REPORT_DIR': './reports', 'LOG_DIR': './log', 'any': 1}),
    ({}, {'LOG_DIR': './log', 'REPORT_DIR': './reports', 'REPORT_SIZE': 1000}),
    (None, {'LOG_DIR': './log', 'REPORT_DIR': './reports', 'REPORT_SIZE': 1000}),
    (
        {'REPORT_DIR': './other', 'REPORT_SIZE': 1500},
        {'LOG_DIR': './log', 'REPORT_DIR': './other', 'REPORT_SIZE': 1500}
    ),
])
def test_get_config(config_args, result):
    test_result = get_config(CONFIG, config_args)
    assert test_result == result


@pytest.mark.parametrize('path, result', [  # noqa
    ('nginx-access-ui.log-20170630.gz', 'nginx-access-ui.log-20170630.gz'),
    ('./root/nginx-access-ui.log-20170630.gz', 'nginx-access-ui.log-20170630.gz'),
    ('/1/2/3/nginx-access-ui.log-20170630', 'nginx-access-ui.log-20170630'),
    (None, ''),
    ('', ''),
])
def test_get_filename_from_path(path, result):
    test_result = get_filename_from_path(path)
    assert test_result == result


def test_unpack_file(create_log_files, mock_log_file_list):
    results = []
    for i in unpack_file('./log_tmp/nginx-access-acc.log-20200430'):
        results.append(i)

    assert results == mock_log_file_list


def test_get_data_for_render(mock_logs_data, data_for_render_result):
    result = get_data_for_render(mock_logs_data, 20, 15)
    assert result == data_for_render_result
