# import from standard library
from datetime import datetime
# import from installed packages
import pytest
# import from project
from earthquakes.usgs_api import build_api_url, FORMAT_ARG, START_DATE_ARG, END_DATE_ARG, LATITUDE_ARG, \
    LONGITUDE_ARG, MAX_RADIUS_KM_ARG


@pytest.fixture
def sample_url_query():
    method = 'query'
    arguments = {FORMAT_ARG: 'csv',
                  START_DATE_ARG: datetime(year=2014, month=1, day=1),
                  END_DATE_ARG: datetime(year=2014, month=1, day=2)}
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-01-01' \
          '&endtime=2014-01-02'
    return method, arguments, url


class TestBuildApiUrl:
    def test_sample_url(self, sample_url_query):
        method, args, correct_url = sample_url_query
        url = build_api_url(method=method, arguments=args)

        print(f"*{correct_url}*")
        print(f"*{url}*")
        # TODO: improve assertion by decoding returned url and comparing parameters
        assert url == correct_url

    def test_empty_method(self, sample_url_query):
        _, args, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method='', arguments=args)

    def test_empty_args(self, sample_url_query):
        method, _, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method=method, arguments={})

    def test_invalid_method(self, sample_url_query):
        _, args, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method='queri', arguments=args)

    def test_invalid_arg_name(self, sample_url_query):
        method, args, _ = sample_url_query
        args['rad'] = 10
        with pytest.raises(ValueError):
            build_api_url(method=method, arguments=args)

    def test_invalid_arg_format(self, sample_url_query):
        method, args, _ = sample_url_query
        args['format'] = 'gejson'
        with pytest.raises(ValueError):
            build_api_url(method=method, arguments=args)

    def test_no_arg_format(self, sample_url_query):
        method, args, _ = sample_url_query
        del args['format']
        with pytest.raises(ValueError):
            build_api_url(method=method, arguments=args)

    def test_insufficient_args(self, sample_url_query):
        # TODO: think of parameters that require others to be submitted at the same time
        method, args, _ = sample_url_query
        args['latitude'] = 35.2
        with pytest.raises(AssertionError):
            build_api_url(method=method, arguments=args)

    def test_insufficient_args_circle_search(self, sample_url_query):
        method, args, _ = sample_url_query
        circle_args = {LATITUDE_ARG: 35.2, LONGITUDE_ARG: 25.1, MAX_RADIUS_KM_ARG: 5}
        for param in circle_args:
            args[param] = circle_args[param]
            with pytest.raises(AssertionError):
                build_api_url(method=method, arguments=args)
            del args[param]

