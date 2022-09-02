import os
import pytest

from log_analyzer import (
    BaseLogAnalyzerError,
    create_report,
    data_preparation_for_processing,
    get_log_data,
    get_log_files,
    get_perc,
    get_report_name,
    get_slice_size_and_remainder,
    is_archive
)

from .conftest import data_preparation_for_processing_result_1, data_preparation_for_processing_result_2


@pytest.mark.parametrize('filename, result, error', [  # noqa
    ('nginx-access-ui.log-20170630.gz', 'report-2017.06.30.html', False),
    ('./root/nginx-access-ui.log-20170630.gz', 'report-2017.06.30.html', False),
    ('nginx-access-ui.log-20170630', 'report-2017.06.30.html', False),
    ('nginx-access-ui.log-20170.gz', '', ValueError),
    ('nginx-access-ui.log.gz', '', BaseLogAnalyzerError),
])
def test_get_report_name(filename, result, error):
    if error:
        with pytest.raises(error):
            get_report_name(filename)
    else:
        test_result = get_report_name(filename)
        assert test_result == result


@pytest.mark.parametrize('filename, result', [  # noqa
    ('nginx-access-ui.log-20170630.gzz', False),
    ('./root/nginx-access-ui.log-20170630.gz', True),
    ('nginx-access-ui.log-20170630', False),
])
def test_is_archive(filename, result):
    test_result = is_archive(filename)
    assert test_result == result


@pytest.mark.parametrize('total_count, count, result, error', [  # noqa
    (1000, 20, 2.0, False),
    (5, 2, 40.0, False),
    (0, 20, 2.0, BaseLogAnalyzerError),
])
def test_get_perc(total_count, count, result, error):
    if error:
        with pytest.raises(error):
            get_perc(total_count, count)
    else:
        test_result = get_perc(total_count, count)
        assert test_result == result


def test_get_log_files(create_log_files):
    result = get_log_files('./log_tmp')
    assert result == ['./log_tmp/nginx-access-ui.log-20190630.gz', './log_tmp/nginx-access-ui.log-20180630.gz']


def test_get_log_data(mock_logs_data, log_data_result):
    result = get_log_data(mock_logs_data, 20, 15)
    assert result == log_data_result


def test_create_report(log_data_result, create_report_dir):
    report_name = 'report-2017.06.30.html'
    create_report(report_name=report_name, data=log_data_result, report_dir=create_report_dir)
    assert os.path.exists(os.path.join(create_report_dir, report_name))

    with open(os.path.join(create_report_dir, report_name), 'r') as f:
        result = f.read()
        assert len(result) == 6679


@pytest.mark.parametrize('requests_count, worker_count, result', [  # noqa
    (1000, 8, (125, 0)),
    (1000, 1, (1000, 0)),
    (1542561, 8, (192820, 1)),
    (10, 2, (5, 0)),
    (10, 4, (2, 2)),
])
def test_get_slice_size_and_remainder(requests_count, worker_count, result):
    test_result = get_slice_size_and_remainder(requests_count, worker_count)
    assert test_result == result


class MockExecutor:
    def submit(self, one, two):
        pass

@pytest.mark.parametrize('slice_size, remainder, worker_count, result', [  # noqa
    (5, 0, 2, data_preparation_for_processing_result_1()),
    (2, 2, 4, data_preparation_for_processing_result_2()),
])
def test_data_preparation_for_processing(mock_log_file_list, slice_size, remainder, worker_count, result):
    test_result = data_preparation_for_processing(
        MockExecutor(),
        mock_log_file_list,
        slice_size,
        remainder,
        worker_count,
    )
    assert test_result == result
