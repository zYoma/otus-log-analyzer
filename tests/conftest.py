import pytest
import shutil
from pathlib import Path


@pytest.fixture(scope='session')
def create_log_files(mock_log_file_list):
    Path("./log_tmp").mkdir(parents=True, exist_ok=True)
    open('./log_tmp/nginx-access-ui.log-20180630.gz', 'a').close()
    open('./log_tmp/nginx-access-ui.log-20190630.gz', 'a').close()
    with open('./log_tmp/nginx-access-acc.log-20200430', 'w') as f:
        f.writelines(mock_log_file_list)
    yield
    shutil.rmtree('./log_tmp', ignore_errors=True)


@pytest.fixture()
def mock_logs_data():
    return [
        ('/api/v2/banner/15521472', '0.154'),
        ('/api/1/campaigns/?id=512672', '0.152'),
        ('/api/v2/banner/23796798', '0.353'),
        ('/agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=26647045&as_json=1', '0.125'),
        ('/api/1/campaigns/?id=3887786', '0.144'),
        ('/api/v2/group/6266784/statistic/sites/?date_type=week&date_to=2017-07-02&date_from=2017-06-26', '0.086'),
        ('/api/v2/banner/20174825/statistic/?date_from=2017-06-29&date_to=2017-06-29', '0.066'),
        ('/api/v2/banner/1279875', '0.358'),
        ('/agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=26661213&as_json=1', '0.075'),
        ('/api/1/campaigns/?id=498119', '0.147'),
        ('/capacity_progress/?task_id=e8f34cfb862f460fa39287f062c61f65&_=1498756373389', '0.001'),
        ('/api/v2/group/7130079/banners', '0.505'),
        ('/api/v2/banner/23640143', '2.434'),
        ('/api/v2/banner/16852664', '0.156'),
        ('/agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=23894002&as_json=1', '0.078'),
        ('/api/v2/group/6266785/statistic/sites/?date_type=week&date_to=2017-07-02&date_from=2017-06-26', '0.075'),
        ('/api/1/campaigns/?id=3512434', '0.208'),
        ('/api/v2/banner/22521090', '0.270'),
        ('/api/v2/banner/23904631', '0.161'),
        ('/api/v2/banner/23136048/statistic/?date_from=2017-06-29&date_to=2017-06-29', '0.049')
    ]


@pytest.fixture
def log_data_result():
    return [
        ('/api/v2/banner/25019354', '0.390'),
        ('/api/1/photogenic_banners/list/?server_name=WIN7RB4', '0.133'),
        ('/api/v2/banner/16852664', '0.199'),
        ('/api/v2/slot/4705/groups', '0.704'),
        ('/api/v2/internal/banner/24294027/info', '0.146'),
        ('/api/v2/group/1769230/banners', '0.628'),
        ('/api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28', '0.067'),
        ('/api/v2/banner/1717161', '0.138'),
        ('/export/appinstall_raw/2017-06-29/', '0.003'),
        ('/api/v2/slot/4822/groups', '0.157')
    ]


@pytest.fixture
def data_for_render_result():
    return [
        {
            'count': 1,
            'time_avg': 2.434,
            'time_max': 2.434,
            'time_sum': 2.434,
            'url': '/api/v2/banner/23640143',
            'time_med': 2.434,
            'time_perc': 43.48758263355369,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.505,
            'time_max': 0.505,
            'time_sum': 0.505,
            'url': '/api/v2/group/7130079/banners',
            'time_med': 0.505,
            'time_perc': 9.022690727175272,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.358,
            'time_max': 0.358,
            'time_sum': 0.358,
            'url': '/api/v2/banner/1279875',
            'time_med': 0.358,
            'time_perc': 6.396283723423262,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.353,
            'time_max': 0.353,
            'time_sum': 0.353,
            'url': '/api/v2/banner/23796798',
            'time_med': 0.353,
            'time_perc': 6.3069501518670705,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.27,
            'time_max': 0.27,
            'time_sum': 0.27,
            'url': '/api/v2/banner/22521090',
            'time_med': 0.27,
            'time_perc': 4.824012864034304,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.208,
            'time_max': 0.208,
            'time_sum': 0.208,
            'url': '/api/1/campaigns/?id=3512434',
            'time_med': 0.208,
            'time_perc': 3.7162765767375374,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.161,
            'time_max': 0.161,
            'time_sum': 0.161,
            'url': '/api/v2/banner/23904631',
            'time_med': 0.161,
            'time_perc': 2.876541004109344,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.156,
            'time_max': 0.156,
            'time_sum': 0.156,
            'url': '/api/v2/banner/16852664',
            'time_med': 0.156,
            'time_perc': 2.7872074325531533,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.154,
            'time_max': 0.154,
            'time_sum': 0.154,
            'url': '/api/v2/banner/15521472',
            'time_med': 0.154,
            'time_perc': 2.751474003930677,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.152,
            'time_max': 0.152,
            'time_sum': 0.152,
            'url': '/api/1/campaigns/?id=512672',
            'time_med': 0.152,
            'time_perc': 2.7157405753082005,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.147,
            'time_max': 0.147,
            'time_sum': 0.147,
            'url': '/api/1/campaigns/?id=498119',
            'time_med': 0.147,
            'time_perc': 2.6264070037520098,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.144,
            'time_max': 0.144,
            'time_sum': 0.144,
            'url': '/api/1/campaigns/?id=3887786',
            'time_med': 0.144,
            'time_perc': 2.5728068608182952,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.125,
            'time_max': 0.125,
            'time_sum': 0.125,
            'url': '/agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=26647045&as_json=1',
            'time_med': 0.125,
            'time_perc': 2.2333392889047703,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.086,
            'time_max': 0.086,
            'time_sum': 0.086,
            'url': '/api/v2/group/6266784/statistic/sites/?date_type=week&date_to=2017-07-02&date_from=2017-06-26',
            'time_med': 0.086,
            'time_perc': 1.5365374307664819,
            'count_perc': 5.0
        },
        {
            'count': 1,
            'time_avg': 0.078,
            'time_max': 0.078,
            'time_sum': 0.078,
            'url': '/agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=23894002&as_json=1',
            'time_med': 0.078,
            'time_perc': 1.3936037162765766,
            'count_perc': 5.0
        }
    ]


@pytest.fixture()
def create_report_dir():
    report_dir = "./report_tmp"
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    yield report_dir
    shutil.rmtree(report_dir, ignore_errors=True)


@pytest.fixture(scope='session')
def mock_log_file_list():
    return [
        '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n',
        '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133\n',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n',
        '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704\n',
        '1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146\n',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628\n',
        '1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067\n',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138\n',
        '1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003\n',
        '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157\n'
    ]
