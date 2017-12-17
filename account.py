import time
import hmac
import hashlib
import requests
import configparser

config = configparser.ConfigParser()
config.read('credentials.ini')


class Account:
    def __init__(self):
        self.balance = {}
        self.api_key = config['API']['key']
        self.api_secret = config['API']['secret']
        self.nonce = lambda: str(int(round(time.time() * 1000)))

    def _create_signature(self, nonce, request_path, json_payload=''):
        message = nonce + 'GET' + request_path + json_payload
        signature = hmac.new(self.api_secret.encode('utf-8'),
                             message.encode('utf-8'),
                             hashlib.sha256).hexdigest()
        return signature

    def _create_auth_header(self, nonce, signature):
        auth_header = 'Bitso %s:%s:%s' % (self.api_key, nonce, signature)
        return auth_header

    def _get_request(self, request_path, auth_header):
        response = requests.get('https://api.bitso.com' + request_path,
                                headers={'Authorization': auth_header})
        return response

    def _parse_jason(self, response):
        response_json = response.json()
        return response_json

    def get_balance(self):
        balance_nonce = self.nonce()
        request_path = '/v3/balance/'
        signature = self._create_signature(nonce=balance_nonce, request_path=request_path)
        auth_header = self._create_auth_header(nonce=balance_nonce, signature=signature)
        response = self._get_request(request_path=request_path, auth_header=auth_header)
        json_content = self._parse_jason(response=response)
        for currency in json_content['payload']['balances']:
            self.balance[currency['currency']] = float(currency['available'])
        self.balance

    @property
    def btc(self):
        return self.balance['btc']

    @property
    def eth(self):
        return self.balance['eth']

    @property
    def xrp(self):
        return self.balance['xrp']

    @property
    def mxn(self):
        return self.balance['mxn']
