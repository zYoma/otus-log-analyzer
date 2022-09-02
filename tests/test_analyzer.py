from log_analyzer import get_report_name, BaseLogAnalyzerError, is_archive, get_perc
import pytest


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
            get_perc(total_count,count)
    else:
        test_result = get_perc(total_count,count)
        assert test_result == result
