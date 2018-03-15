import json
import logging
import urllib.parse as urlparse

from monotonic import monotonic
import requests

from directory_client_core.version import __version__
from sigauth.utils import RequestSigner


logger = logging.getLogger(__name__)


class BaseAPIClient:

    def __init__(self, base_url=None, api_key=None):
        assert base_url, "Missing base url"
        assert api_key, "Missing API key"
        assert base_url.endswith('/'), "Base url must end with trailing slash"
        self.base_url = base_url
        self.request_signer = RequestSigner(secret=api_key)

    def put(self, url, data, authenticator=None):
        return self.request(
            url=url,
            method="PUT",
            content_type="application/json",
            data=json.dumps(data),
            authenticator=authenticator,
        )

    def patch(self, url, data, files=None, authenticator=None):
        if files:
            response = self.request(
                url=url,
                method="PATCH",
                data=data,
                files=files,
                authenticator=authenticator
            )
        else:
            response = self.request(
                url=url,
                method="PATCH",
                content_type="application/json",
                data=json.dumps(data),
                authenticator=authenticator,
            )
        return response

    def get(self, url, params=None, authenticator=None):
        return self.request(
            url=url,
            method="GET",
            params=params,
            authenticator=authenticator,
        )

    def post(self, url, data={}, files=None, authenticator=None):
        if files:
            response = self.request(
                url=url,
                method="POST",
                data=data,
                files=files,
                authenticator=authenticator,
            )
        else:
            response = self.request(
                url=url,
                method="POST",
                content_type="application/json",
                data=json.dumps(data),
                authenticator=authenticator,
            )
        return response

    def delete(self, url, data=None, authenticator=None):
        return self.request(
            url=url,
            method="DELETE",
            authenticator=authenticator,
        )

    @staticmethod
    def build_url(base_url, partial_url):
        """
        Makes sure the URL is built properly.

        >>> urllib.parse.urljoin('https://test.com/1/', '2/3')
        https://test.com/1/2/3
        >>> urllib.parse.urljoin('https://test.com/1/', '/2/3')
        https://test.com/2/3
        >>> urllib.parse.urljoin('https://test.com/1', '2/3')
        https://test.com/2/3'
        """
        if not base_url.endswith('/'):
            base_url += '/'
        if partial_url.startswith('/'):
            partial_url = partial_url[1:]

        return urlparse.urljoin(base_url, partial_url)

    def request(
        self, method, url, content_type=None, data=None, params=None,
        files=None, authenticator=None
    ):

        logger.debug("API request {} {}".format(method, url))

        headers = {
            "User-agent": "EXPORT-DIRECTORY-API-CLIENT/{}".format(
                __version__
            )
        }
        if authenticator:
            headers.update(authenticator.get_auth_headers())

        if content_type:
            headers["Content-type"] = content_type

        url = self.build_url(self.base_url, url)

        start_time = monotonic()

        try:
            return self.send(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                files=files,
            )
        finally:
            elapsed_time = monotonic() - start_time
            logger.debug(
                "API {} request on {} finished in {}".format(
                    method, url, elapsed_time
                )
            )

    def sign_request(self, prepared_request):
        headers = self.request_signer.get_signature_headers(
            url=prepared_request.path_url,
            body=prepared_request.body,
            method=prepared_request.method,
            content_type=prepared_request.headers.get('Content-Type'),
        )
        prepared_request.headers.update(headers)
        return prepared_request

    def send(self, method, url, request=None, *args, **kwargs):

        prepared_request = requests.Request(
            method, url, *args, **kwargs
        ).prepare()

        signed_request = self.sign_request(prepared_request=prepared_request)
        return requests.Session().send(signed_request)
