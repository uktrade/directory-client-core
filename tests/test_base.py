from io import StringIO
import http
from unittest import TestCase

import pytest
import requests

from tests import stub_request
from directory_client_core.base import AbstractAPIClient
from directory_client_core import authentication, cache_control


class TestAPIClient(AbstractAPIClient):
    version = 1


class AbstractAPIClientTest(TestCase):

    def setUp(self):
        self.client = TestAPIClient(
            base_url='https://example.com/',
            api_key='test',
            sender_id='test-sender-id',
            timeout=2,
        )

    def test_request_signer(self):
        assert self.client.request_signer.secret == 'test'
        assert self.client.request_signer.sender_id == 'test-sender-id'

    @stub_request('https://example.com/test', 'post')
    def test_request(self, stub):
        self.client.request("POST", 'test', data='data')

    @stub_request('https://example.com/test', 'post')
    def test_post_encodes_json(self, stub):
        data = {'key': 'value'}
        self.client.post('test', data=data)
        request = stub.request_history[0]
        assert request.headers['Content-type'] == 'application/json'
        assert request.text == '{"key": "value"}'

    @stub_request('https://example.com/test', 'post')
    def test_post_no_payload(self, stub):
        self.client.post('test')
        request = stub.request_history[0]
        assert request.headers['Content-type'] == 'application/json'
        assert request.text == '{}'

    @stub_request('https://example.com/test', 'put')
    def test_put_encodes_json(self, stub):
        data = {'key': 'value'}
        self.client.put('test', data=data)
        request = stub.request_history[0]
        assert request.headers['Content-type'] == 'application/json'
        assert request.text == '{"key": "value"}'

    @stub_request('https://example.com/test', 'patch')
    def test_patch_encodes_json_without_file(self, stub):
        data = {'key': 'value'}
        self.client.patch('test', data=data)
        request = stub.request_history[0]
        assert request.headers['Content-type'] == 'application/json'
        assert request.text == '{"key": "value"}'

    @stub_request('https://example.com/thing/', 'patch')
    def test_patch_encodes_form_with_file(self, stub):
        data = {'key': 'value'}
        files = {'logo': StringIO('hello')}
        self.client.patch(url='thing/', data=data, files=files)
        request = stub.request_history[0]
        header = request.headers['Content-type']
        assert header.startswith('multipart/form-data; boundary=')

    def test_sign_request(self):
        url = 'https://example.com'
        prepared_request = requests.Request(
            "POST", url, data='data'
        ).prepare()

        self.client.sign_request(prepared_request=prepared_request)

    @stub_request('https://example.com', 'post')
    def test_send_response_ok(self, stub):
        response = self.client.send(method="POST", url="https://example.com")

        assert response.request.timeout == 2
        assert response.status_code == http.client.OK

    @stub_request('https://example.com', 'post', http.client.BAD_REQUEST)
    def test_send_response_not_ok(self, stub):
        response = self.client.send(method="POST", url="https://example.com")
        assert response.status_code == http.client.BAD_REQUEST

    @stub_request('https://example.com/test', 'get')
    def test_authenticator(self, stub):
        self.client.request(
            "GET",
            'test',
            authenticator=authentication.BearerAuthenticator('123'),
        )

        request = stub.request_history[0]

        assert request.headers['Authorization'] == 'Bearer 123'

    @stub_request('https://example.com/test', 'get')
    def test_cache_control(self, stub):
        self.client.request(
            "GET", 'test', cache_control=cache_control.ETagCacheControl('123'),
        )

        request = stub.request_history[0]

        assert request.headers['If-None-Match'] == '123'


@pytest.mark.parametrize(
    'base_url,partial_url,expected_result',
    [
        (
            'http://test.com/1/',
            '/2/3/',
            'http://test.com/1/2/3/'
        ),
        (
            'http://test.com/1',
            '2/3/',
            'http://test.com/1/2/3/'
        ),
        (
            'http://test.com/1',
            '/2/3/',
            'http://test.com/1/2/3/'
        ),
        (
            'http://test.com/1/',
            '2/3/',
            'http://test.com/1/2/3/'
        )
    ]
)
def test_build_url(base_url, partial_url, expected_result):
    assert TestAPIClient.build_url(base_url, partial_url) == expected_result
