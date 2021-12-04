import json
import requests
from ratelimit import limits, sleep_and_retry
from .exceptions import ConfigurationError, HTTPError


__url_cache__ = {}


class KnowBe4(object):

    class_name = 'KnowBe4'

    def __init__(self, token=''):
        self._base_url = 'https://us.api.knowbe4.com/v1'
        self._token = token

    def _build_url(self, *args, **kwargs):
        '''
        Build a new API url from scratch.

        Taken from github.com/sigmavirus24/github3.py
        '''
        parts = [kwargs.get('base_url') or self._base_url]
        parts.extend(args)
        parts = [str(p) for p in parts]
        key = tuple(parts)
        if key not in __url_cache__:
            __url_cache__[key] = '/'.join(parts)
        return __url_cache__[key]

    def _check_token(self):
        if not self._token:
            raise ConfigurationError('No API Token set.')

    def _headers(self):
        return {'Authorization': 'Bearer {0}'.format(self._token)}

    def _json(self, response):
        if response is None:
            return None
        else:
            ret = response.json()
        return ret

    @sleep_and_retry
    @limits(calls=4, period=60)
    def _request(self, method, url, data=None, headers=None, json=True, pagination=False, page='1', per_page='250'):
        self._check_token()
        headers = self._headers()
        if pagination:
            resp = requests.request(method, url, data=data, headers=headers, params={'page': page, 'per_page': per_page})
            if 200 <= resp.status_code < 300 and len(resp.content) <= 2:
                return None
        else:
            resp = requests.request(method, url, data=data, headers=headers)
        if resp.status_code == 204:
            return None
        if 200 <= resp.status_code < 300:
            return resp
        else:
            resp.raise_for_status()

    def _get(self, url):
        return self._request('GET', url)

    def _get_paginated(self, url):
        responses = []
        page = 1
        while True:
            resp = self._request('GET', url, pagination=True, page=f"{page}")
            if resp is None:
                break
            responses.append(resp)
            page += 1
        return responses

    def _api_call(self, *args, **kwargs):
        url = self._build_url(*args)
        json = self._json(self._get(url))
        return json

    def _api_call_paginated(self, *args, **kwargs):
        url = self._build_url(*args)
        json = [item for sublist in map(self._json, self._get_paginated(url)) for item in sublist]
        return json

    def account(self):
        return self._api_call('account')

    def users(self):
        return self._api_call('users')

    def groups(self):
        return self._api_call('groups')

    def group(self, id):
        return self._api_call('groups', id)

    def group_members(self, id):
        return self._api_call('groups', id, 'members')

    def user(self, id):
        return self._api_call('users', id)

    def phishing_campaigns(self):
        return self._api_call('phishing', 'campaigns')

    def phishing_campaign(self, id):
        return self._api_call('phishing', 'campaigns', id)

    def phishing_security_tests(self):
        return self._api_call('phishing', 'security_tests')

    def phishing_campaign_security_tests(self, id):
        return self._api_call('phishing', 'campaigns', id, 'security_tests')

    def phishing_campaign_security_test(self, id):
        return self._api_call('phishing', 'security_tests', id)

    def phishing_campaign_security_test_recipients(self, id):
        return self._api_call('phishing', 'security_tests', id, 'recipients')

    def phishing_campaign_security_test_recipient(self, pst_id, id):
        return self._api_call('phishing', 'security_tests', pst_id, 'recipients', id)

    def store_purchases(self):
        return self._api_call('training', 'store_purchases')

    def store_purchase(self, id):
        return self._api_call('training', 'store_purchases', id)

    def policies(self):
        return self._api_call('policies')

    def policy(self, id):
        return self._api_call('policies', id)

    def training_campaigns(self):
        return self._api_call('training', 'campaigns')

    def training_campaign(self, id):
        return self._api_call('training', 'campaigns', id)

    def training_enrollments(self):
        return self._api_call_paginated('training', 'enrollments')

    def training_enrollment(self, id):
        return self._api_call('training', 'enrollment', id)
