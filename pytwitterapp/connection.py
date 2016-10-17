import requests
import json

from base64 import b64encode
from .exceptions import *


class TwitterConnection(object):
    def __init__(self,
                 bearer_token=None,
                 consumer_key=None,
                 consumer_secret=None,
                 url='https://api.twitter.com'):
        """
        Call Twitter endpoints that are accessible using application-only authentication

        You **MUST** specify either a bearer token or a consumer key / consumer secret pair. If you do not
        have a bearer token, .bearer_token() will generate one for you by authenticating with the key/secret pair.

        :param bearer_token: a bearer-token string to use for authentication. You must provide either this or a
                             `consumer_key` and `consumer_secret` pair.
        :param consumer_key: a string containing the consumer key
        :param consumer_secret: a string containing the consumer secret
        :param url: (optional) an alternative base URL for the Twitter API
        """
        if bearer_token is None and (consumer_key is None or consumer_secret is None):
            raise ValueError('Must provide either a bearer_token or BOTH of consumer_key and consumer_secret')

        self.bearer_token = bearer_token
        self.api_key = consumer_key
        self.api_secret = consumer_secret
        self.url = url
        self.session = requests.Session()

    @staticmethod
    def parse_error(response):
        if response.json():
            return json.dumps(response.json(), indent=3)
        else:
            return "HTTP error {code}: {content}".format(code=response.status_code, content=response.content)

    def bearer_token(self, force_auth=False, path='/oauth2/token'):
        """
        Get the bearer token, generating it via OAuth2 Application-Only authentication if necessary

        :param force_auth: complete the OAuth2 authentication step online even if we already have a bearer token
        :param path: specify a different API endpoint than the default
        :return: (str) the bearer token string; this will also be set in the `bearer_token` attribute
        """
        if self.bearer_token is not None and not force_auth:
            return self.bearer_token

        if self.api_key is None or self.api_secret is None:
            raise ValueError('Must provide both consumer key and consumer secret to acquire a bearer token')

        self.session = requests.Session()  # clean the session if we're starting with a fresh auth

        # Base64-encode the ASCII representation of "key:secret" string
        auth_string = b64encode("{key}:{secret}".format(key=self.api_key, secret=self.api_secret).encode('ascii'))

        response = self.session.post(
            self.url + path,
            headers={'Authorization': "Basic {}".format(auth_string)},
            data={'grant_type': 'client_credentials'})

        if not response.ok:
            raise TwitterAuthExecption("Authentication not ok. {}".format(self.parse_error(response)))

        rdata = response.json()
        if 'access_token' not in rdata:
            raise TwitterAuthExecption("Unknown response. {}".format(self.parse_error(rdata)))

        self.bearer_token = rdata['access_token']
        self.session.headers.update({'Authorization': "Bearer {}"})  # future requests will use the bearer token
        return self.bearer_token

    auth = bearer_token  # .auth is an alias for .bearer_token

    def search(self, query, path='/1.1/search/tweets.json', **kwargs):
        """
        Conduct an Application-Only authenticated Twitter search

        :param query: the query string to search Twitter for
        :param path: specify a different API endpoint than the default
        :param kwargs: arguments that the Twitter search endpoint understands
        :return: (dict) a dictionary decoded from the search results
        :raises TwitterSearchException: if there is an error
        """
        search_params = kwargs.copy()
        search_params['q'] = query
        response = self.session.get(
            self.url + path,
            params=search_params)

        if not response.ok:
            raise TwitterSearchException("Error conducting search. {}".format(self.parse_error(response)))

        return response.json()
