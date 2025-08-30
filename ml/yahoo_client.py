import os
import time
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

YAHOO_TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_token'
FANTASY_BASE = 'https://fantasysports.yahooapis.com/fantasy/v2'

class YahooOAuthClient:
    """Simple Yahoo OAuth2 client for Fantasy API with auto-refresh and retry."""

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        self.client_id = client_id or os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('YAHOO_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('YAHOO_ACCESS_TOKEN')
        self.refresh_token = refresh_token or os.getenv('YAHOO_REFRESH_TOKEN')
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})

    def build_auth_url(self, redirect_uri, scope='fspt-w'):  # scope fspt-w is example
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'language': 'en-us'
        }
        return f'https://api.login.yahoo.com/oauth2/request_auth?{urlencode(params)}'

    def fetch_token_with_code(self, code, redirect_uri):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(YAHOO_TOKEN_URL, data=data, headers=headers)
        r.raise_for_status()
        tok = r.json()
        self.access_token = tok.get('access_token')
        self.refresh_token = tok.get('refresh_token')
        self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
        return tok

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError('No refresh token available')
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(YAHOO_TOKEN_URL, data=data, headers=headers)
        r.raise_for_status()
        tok = r.json()
        self.access_token = tok.get('access_token')
        if 'refresh_token' in tok:
            self.refresh_token = tok.get('refresh_token')
        self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
        return tok

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def get(self, path, params=None):
        url = FANTASY_BASE + path
        r = self.session.get(url, params=params, timeout=20)
        if r.status_code == 401 and self.refresh_token:
            # try refreshing once
            self.refresh()
            r = self.session.get(url, params=params, timeout=20)
        if r.status_code == 429:
            # rate limited - raise to trigger retry/backoff
            r.raise_for_status()
        r.raise_for_status()
        # Yahoo returns XML by default; request JSON by appending /<resource>.json or use format=json where supported
        return r.json()

    def post(self, path, data=None):
        url = FANTASY_BASE + path
        r = self.session.post(url, data=data)
        if r.status_code == 401 and self.refresh_token:
            self.refresh()
            r = self.session.post(url, data=data)
        r.raise_for_status()
        return r.json()
