from functools import wraps
import json
import logging
from urllib.parse import urlencode

import requests
from requests.exceptions import HTTPError, RequestException
from w3lib.url import canonicalize_url

from django.conf import settings

from directory_client_core.cache_control import ETagCacheControl


logger = logging.getLogger(__name__)


MESSAGE_CACHE_HIT = 'Fallback cache hit. Using cached content.'
MESSAGE_CACHE_MISS = 'Fallback cache miss. Cannot use any content.'
MESSAGE_NOT_FOUND = 'Resource not found.'


class ThrottlingFilter(logging.Filter):
    """
    Filters out records that have been seen within the past <period of time>
    thereby reducing noise.

    How this works:
        - with `cache.add` the entry is stored only if the key is not yet
          present in the cache
        - cache.add returns True if the entry is stored, otherwise False
        - these cache entries expire after <period of time>.

    Therefore `filter` returns True if the key hasn't been seen in the past
    <period of time>, and False if it has. The logger takes this to mean
    "don't log this"

    """

    def __init__(self, cache):
        self.cache = cache
        self.timeout_in_seconds = getattr(
            settings,
            'DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS',
            None
        ) or 60*60*24  # default 24 hours

    def create_cache_key(sef, record):
        return f'noise-{record.getMessage()}-{record.url}'

    def filter(self, record):
        key = self.create_cache_key(record)
        return self.cache.add(key, '', timeout=self.timeout_in_seconds)


class PopulateResponseMixin:

    @classmethod
    def from_response(cls, raw_response):
        response = cls()
        response.__setstate__(raw_response.__getstate__())
        return response


class LiveResponse(PopulateResponseMixin, requests.Response):
    pass


class FailureResponse(PopulateResponseMixin, requests.Response):
    pass


class CacheResponse(requests.Response):
    pass


def fallback(cache):
    """
    Caches content retrieved by the client, thus allowing the cached
    content to be used later if the live content cannot be retrieved.

    """

    log_filter = ThrottlingFilter(cache=cache)
    logger.filters = []
    logger.addFilter(log_filter)

    def get_cache_response(cache_key):
        content = cache.get(cache_key)
        if content:
            response = CacheResponse()
            response.__setstate__({
                'status_code': 200,
                '_content': content,
            })
            return response

    def get_cache_control(etag_cache_key):
        etag = cache.get(etag_cache_key)
        if etag:
            return ETagCacheControl(etag)

    def closure(func):
        @wraps(func)
        def wrapper(client, url, params={}, *args, **kwargs):
            cache_key = canonicalize_url(url + '?' + urlencode(params))
            etag_cache_key = 'etag-' + cache_key
            try:
                remote_response = func(
                    client,
                    url=url,
                    params=params,
                    cache_control=get_cache_control(etag_cache_key),
                    *args,
                    **kwargs,
                )
            except RequestException:
                # Failed to create the request e.g., the remote server is down,
                # perhaps a timeout occurred, or even connection closed by
                # remote, etc.
                response = get_cache_response(cache_key)
                if response:
                    logger.error(MESSAGE_CACHE_HIT, extra={'url': url})
                else:
                    raise
            else:
                log_context = {
                    'status_code': remote_response.status_code, 'url': url
                }
                if remote_response.status_code == 404:
                    logger.error(MESSAGE_NOT_FOUND, extra=log_context)
                    return LiveResponse.from_response(remote_response)
                elif remote_response.status_code == 304:
                    response = get_cache_response(cache_key)
                elif not remote_response.ok:
                    # Successfully requested the content, but the response is
                    # not OK (e.g., 500, 403, etc)
                    response = get_cache_response(cache_key)
                    if response:
                        logger.error(MESSAGE_CACHE_HIT, extra=log_context)
                    else:
                        logger.exception(MESSAGE_CACHE_MISS, extra=log_context)
                        response = FailureResponse.from_response(
                            remote_response
                        )
                else:
                    cache.set_many({
                        cache_key: remote_response.content,
                        etag_cache_key: remote_response.headers.get('ETag'),
                    }, settings.DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS)
                    response = LiveResponse.from_response(remote_response)
            return response
        return wrapper
    return closure
