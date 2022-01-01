# import from standard library
# import from installed packages
import pytest
# import from project
from earthquakes.usgs_api import build_api_url


@pytest.fixture
def sample_url_query():
    method = 'query'
    parameters = {'format': 'csv',
                  'starttime': '2014-01-01',
                  'endtime': '2014-01-02'}
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-01-01' \
          '&endtime=2014-01-02'
    return method, parameters, url


class TestBuildApiUrl:
    def test_sample_url(self, sample_url_query):
        method, params, correct_url = sample_url_query
        url = build_api_url(method=method, parameters=params)

        print(f"*{correct_url}*")
        print(f"*{url}*")

        assert url == correct_url

    def test_empty_method(self, sample_url_query):
        _, params, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method='', parameters=params)

    def test_empty_params(self, sample_url_query):
        method, _, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method=method, parameters={})

    def test_invalid_method(self, sample_url_query):
        _, params, _ = sample_url_query
        with pytest.raises(ValueError):
            build_api_url(method='queri', parameters=params)

    def test_invalid_param_name(self, sample_url_query):
        method, params, _ = sample_url_query
        params['rad'] = 10
        with pytest.raises(ValueError):
            build_api_url(method=method, parameters=params)

    def test_invalid_param_format(self, sample_url_query):
        method, params, _ = sample_url_query
        params['format'] = 'gejson'
        with pytest.raises(ValueError):
            build_api_url(method=method, parameters=params)

    def test_no_param_format(self, sample_url_query):
        method, params, _ = sample_url_query
        del params['format']
        with pytest.raises(ValueError):
            build_api_url(method=method, parameters=params)

    def test_insufficient_params(self, sample_url_query):
        # TODO: think of parameters that require others to be submitted at the same time
        method, params, _ = sample_url_query
        params['latitude'] = 35.2
        with pytest.raises(ValueError):
            build_api_url(method=method, parameters=params)

    def test_insufficient_params_circle_search(self, sample_url_query):
        method, params, _ = sample_url_query
        circle_params = {'latitude': 35.2, 'longitude': 25.1, 'maxradiuskm': 5}
        for param in circle_params:
            params[param] = circle_params[param]
            with pytest.raises(ValueError):
                build_api_url(method=method, parameters=params)
            del params[param]

