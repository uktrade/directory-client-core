from directory_client_core import cache_control


def test_sso_authenticator():
    instance = cache_control.ETagCacheControl('123')

    assert instance.headers == {
        'If-None-Match': '123'
    }
