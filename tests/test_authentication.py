import pytest

from directory_client_core import authentication


def test_authentication_negotiator_neither():
    with pytest.raises(AssertionError):
        authentication.AuthenticatorNegotiator()


def test_authentication_negotiator_sso():
    authenticator = authentication.AuthenticatorNegotiator(sso_session_id='12')

    assert isinstance(authenticator, authentication.SessionSSOAuthenticator)
    assert authenticator.value == '12'


def test_authentication_negotiator_bearer():
    authenticator = authentication.AuthenticatorNegotiator(bearer_token='12')

    assert isinstance(authenticator, authentication.BearerAuthenticator)
    assert authenticator.value == '12'


def test_bearer_authenticator():
    authenticator = authentication.BearerAuthenticator('12')

    assert authenticator.headers == {
        'Authorization': 'Bearer 12'
    }


def test_sso_authenticator():
    authenticator = authentication.SessionSSOAuthenticator('12')

    assert authenticator.headers == {
        'Authorization': 'SSO_SESSION_ID 12'
    }
