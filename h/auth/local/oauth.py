import os

from oauthlib.oauth2 import ClientCredentialsGrant, InvalidClientError
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.exceptions import BadCSRFToken
from pyramid.interfaces import ISessionFactory
from pyramid.session import check_csrf_token, SignedCookieSessionFactory

from h.api import get_consumer


def add_credentials(request, **credentials):
    new_credentials = (request.extra_credentials or {})
    new_credentials.update(credentials)
    request.extra_credentials = new_credentials


class SessionAuthenticationGrant(ClientCredentialsGrant):
    def validate_token_request(self, request):
        try:
            check_csrf_token(request, token='assertion')
        except BadCSRFToken:
            raise InvalidClientError(request=request)

        request.client = get_consumer(request)

        if request.client is None:
            raise InvalidClientError(request=request)

        request.client_id = request.client_id or request.client.client_id

        userid = request.authenticated_userid
        if userid:
            add_credentials(request, userId=userid)


def session_from_config(settings, prefix='session.'):
    """Return a session factory from the provided settings."""
    secret_key = '{}secret'.format(prefix)
    secret = settings.get(secret_key)
    if secret is None:
        # Get 32 bytes (256 bits) from a secure source (urandom) as a secret.
        # Pyramid will add a salt to this. The salt and the secret together
        # will still be less than the, and therefore right zero-padded to,
        # 1024-bit block size of the default hash algorithm, sha512. However,
        # 256 bits of random should be more than enough for session secrets.
        secret = os.urandom(32)

    return SignedCookieSessionFactory(secret)


def includeme(config):
    config.include('pyramid_oauthlib')
    config.add_grant_type(SessionAuthenticationGrant)

    # Configure the authentication policy
    authn_debug = config.registry.settings.get('debug_authorization')
    authn_policy = SessionAuthenticationPolicy(prefix='', debug=authn_debug)
    config.set_authentication_policy(authn_policy)

    def register():
        if config.registry.queryUtility(ISessionFactory) is None:
            session_factory = session_from_config(config.registry.settings)
            config.registry.registerUtility(session_factory, ISessionFactory)

    config.action(None, register, order=1)
