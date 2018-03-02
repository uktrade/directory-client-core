from directory_client_core import authentication


def test_authentication_negotiator_sso():
    authenticator = authentication.AuthenticatorNegotiator(
        sso_session_id='123', bearer_token=None
    )

    assert isinstance(authenticator, authentication.SessionSSOAuthenticator)
    assert authenticator.value == '123'


def test_authentication_negotiator_bearer():
    authenticator = authentication.AuthenticatorNegotiator(
        sso_session_id=None, bearer_token='123'
    )

    assert isinstance(authenticator, authentication.BearerAuthenticator)
    assert authenticator.value == '123'


def test_bearer_authenticator():
    authenticator = authentication.BearerAuthenticator('123')

    assert authenticator.get_auth_headers() == {
        'Authorization': 'Bearer 123'
    }


def test_sso_authenticator():
    authenticator = authentication.SessionSSOAuthenticator('123')

    assert authenticator.get_auth_headers() == {
        'Authorization': 'SSO_SESSION_ID 123'
    }
