import json
import logging
from unittest.mock import patch

from freezegun import freeze_time
import pytest
import requests_mock
import requests

from django.core.cache import caches

from directory_client_core.base import AbstractAPIClient
from directory_client_core import helpers


@pytest.fixture
def fallback_cache():
    return caches['fallback']


@pytest.fixture(autouse=True)
def clear_fallback_cache(fallback_cache):
    fallback_cache.clear()


@pytest.fixture
def cached_client(fallback_cache):

    class APIClient(AbstractAPIClient):
        version = 1

        @helpers.fallback(cache=fallback_cache)
        def get(self, *args, **kwargs):
            return super().get(*args, **kwargs)

        def retrieve(self, slug):
            return self.get(
                url='/some/path/{slug}/'.format(slug=slug),
                params={'x': 'y', 'a': 'b'},
            )

    return APIClient(
        base_url='http://example.com',
        api_key='debug',
        sender_id='test-sender',
        timeout=5,
    )


def test_good_response_cached(cached_client, fallback_cache):
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    path = '/some/path/thing/'

    with requests_mock.mock() as mock:
        mock.get('http://example.com' + path, content=expected_data)
        cached_client.retrieve('thing')

    cache_key = path + '?a=b&x=y'
    assert fallback_cache.get(cache_key) == expected_data


def test_good_response_etag(cached_client, fallback_cache):
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    path = '/some/path/thing/'

    url = 'http://example.com' + path
    headers = {'ETag': '"123"'}

    # given the page has been cached
    with requests_mock.mock() as mock:
        mock.get(url, content=expected_data, headers=headers)
        cached_client.retrieve('thing')

    cache_key = path + '?a=b&x=y'
    assert fallback_cache.get(cache_key) == expected_data
    # and the etag has been saved
    assert fallback_cache.get('etag-' + cache_key) == '"123"'

    # when the same page is requested and the remote server returns 304
    with requests_mock.mock() as mock:
        mock.get(url, content=b'', headers=headers, status_code=304)
        response = cached_client.retrieve('thing')
        request = mock.request_history[0]

    # then the request exposed the etag cache headers
    assert request.headers['If-None-Match'] == '"123"'

    # and the cached content is returned
    assert isinstance(response, helpers.CacheResponse)


@freeze_time('2012-01-14')
def test_good_response_cache_timeout(cached_client, fallback_cache, settings):
    settings.DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 100
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    path = '/some/path/thing/'

    with requests_mock.mock() as mock:
        mock.get('http://example.com' + path, content=expected_data)
        cached_client.retrieve('thing')

    cache_key = path + '?a=b&x=y'

    key = fallback_cache.make_key(cache_key)
    fallback_cache.validate_key(key)

    assert fallback_cache._expire_info.get(key) == 1326499300.0


def test_bad_resonse_cache_hit(cached_client, caplog):
    path = '/some/path/thing/'
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    url = 'http://example.com' + path

    with requests_mock.mock() as mock:
        mock.get(url, content=expected_data)
        response_one = cached_client.retrieve('thing')

    with requests_mock.mock() as mock:
        mock.get(url, status_code=400)
        response_two = cached_client.retrieve('thing')

    assert response_one.status_code == 200
    assert response_one.content == expected_data
    assert isinstance(response_one, helpers.LiveResponse)

    assert response_two.status_code == 200
    assert response_two.content == expected_data
    assert isinstance(response_two, helpers.CacheResponse)

    log = caplog.records()[-1]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_CACHE_HIT
    assert log.status_code == 400
    assert log.url == path


def test_bad_response_cache_miss(cached_client, caplog):
    path = '/some/path/thing/'
    url = 'http://example.com' + path

    with requests_mock.mock() as mock:
        mock.get(url, status_code=400)
        response = cached_client.retrieve('thing')

    assert response.status_code == 400
    assert isinstance(response, helpers.FailureResponse)

    log = caplog.records()[-1]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_CACHE_MISS
    assert log.status_code == 400
    assert log.url == path


def test_bad_response_404(cached_client, caplog):
    path = '/some/path/thing/'
    url = 'http://example.com' + path

    with requests_mock.mock() as mock:
        mock.get(url, status_code=404)
        response = cached_client.retrieve('thing')

    assert response.status_code == 404
    assert isinstance(response, helpers.LiveResponse)

    log = caplog.records()[-1]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_NOT_FOUND
    assert log.status_code == 404
    assert log.url == path


def test_connection_error_cache_hit(cached_client, caplog):
    path = '/some/path/thing/'
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    url = 'http://example.com' + path

    with requests_mock.mock() as mock:
        mock.get(url, content=expected_data)
        response_one = cached_client.retrieve('thing')

    with patch('directory_client_core.base.AbstractAPIClient.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        response_two = cached_client.retrieve('thing')

    assert response_one.status_code == 200
    assert response_one.content == expected_data
    assert isinstance(response_one, helpers.LiveResponse)

    assert response_two.status_code == 200
    assert response_two.content == expected_data
    assert isinstance(response_two, helpers.CacheResponse)

    log = caplog.records()[-1]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_CACHE_HIT
    assert log.url == path


def test_connection_error_cache_miss(cached_client, caplog):
    with patch('directory_client_core.base.AbstractAPIClient.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(requests.exceptions.ConnectionError):
            cached_client.retrieve('thing')

    assert len(caplog.records()) == 0


def test_cache_querystrings(cached_client, fallback_cache):
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    path = '/some/path/thing/'

    with requests_mock.mock() as mock:
        mock.get('http://example.com' + path, content=expected_data)
        cached_client.retrieve('thing',)

    cache_key = path + '?a=b&x=y'
    assert fallback_cache.get(cache_key) == expected_data


def test_logging_noise_filtering(cached_client, caplog):

    path = '/some/path/thing/'
    expected_data = bytes(json.dumps({'key': 'value'}), 'utf8')
    url = 'http://example.com' + path

    with requests_mock.mock() as mock:
        mock.get(url, content=expected_data)
        cached_client.retrieve('thing')

    with patch('directory_client_core.base.AbstractAPIClient.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        cached_client.retrieve('thing')

    errors = [item for item in caplog.records() if item.levelname == 'ERROR']
    assert len(errors) == 1

    with patch('directory_client_core.base.AbstractAPIClient.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        cached_client.retrieve('thing')

    # second log entry was filtered out
    errors = [item for item in caplog.records() if item.levelname == 'ERROR']
    assert len(errors) == 1


def test_throttling_log_filter_timeout(settings, fallback_cache):
    settings.DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS = 40
    log_filter = helpers.ThrottlingFilter(cache=fallback_cache)

    assert log_filter.timeout_in_seconds == 40


def test_throttling_log_filter_timeout_default_day(settings, fallback_cache):
    settings.DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS = None
    log_filter = helpers.ThrottlingFilter(cache=fallback_cache)

    assert log_filter.timeout_in_seconds == 60*60*24  # 24 hours


def test_throttling_filter(fallback_cache):
    log_filter = helpers.ThrottlingFilter(cache=fallback_cache)
    logger = logging.getLogger()
    record = logger.makeRecord(
        name='',
        level='ERROR',
        fn='',
        lno='',
        msg='something bad happened',
        args=[],
        exc_info='',
        extra={'url': 'https://www.google.com'}
    )

    assert log_filter.filter(record) is True
    assert log_filter.filter(record) is False
