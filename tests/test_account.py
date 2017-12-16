import unittest
from unittest import mock
import time
import hmac
import hashlib

from account import Account


class TestAccount(unittest.TestCase):
    @staticmethod
    def _mock_response(
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things
        """
        mock_resp = mock.Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @classmethod
    def setUpClass(cls):
        cls.account = Account()
        cls.key = 'api-key'
        cls.secret = 'api-secret'
        cls.nonce = str(int(round(time.time() * 1000)))
        cls.request_path = '/v3/account_status/'
        cls.message = cls.nonce+'GET'+cls.request_path+''
        cls.signature = hmac.new('secret'.encode('UTF-8'), cls.message.encode('UTF-8'), hashlib.sha256).hexdigest()

    def setUp(self):
        pass

    def test_create_signature(self):
        account_signature = self.account.create_signature(nonce=self.nonce,
                                                          request_path=self.request_path,
                                                          json_payload='')
        self.assertEqual(self.signature, account_signature)

    def test_create_auth_header(self):
        auth_header = 'Bitso %s:%s:%s' % (self.key, self.nonce, self.signature)
        account_auth_header = self.account.create_auth_header()
        self.assertEqual(auth_header, account_auth_header)

    @mock.patch('requests.get')
    def test_get_request(self, mock_get):
        auth_header = 'Bitso %s:%s:%s' % (self.key, self.nonce, self.signature)
        content = {'success': True, 'payload': {'client_id': '000001', 'first_name': 'Foo', 'last_name': 'Bar'}}
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        result = self.account.get_request(request_path=self.request_path, auth_header=auth_header)
        self.assertEqual(result.json, content)

    @mock.patch('requests.get')
    def test_get_balance(self, mock_get):
        btc = 0.0001
        eth = 0.05
        xrp = 50.32

        content = [btc, eth, xrp]
        mock_resp = self._mock_response(content=content)
        mock_get.return_value = mock_resp
        balance = self.account._get_balance(json=content)
        self.assertEqual(btc, balance[0])
        self.assertEqual(eth, balance[1])
        self.assertEqual(xrp, balance[2])

    def test_get_btc(self):
        btc = 0.0001
        account_btc = self.account.btc
        self.assertEqual(btc, account_btc)

    def test_get_eth(self):
        eth = 0.0001
        account_eth = self.account.eth
        self.assertEqual(eth, account_eth)

    def test_get_xrp(self):
        xrp = 0.0001
        account_xrp = self.account.xrp
        self.assertEqual(xrp, account_xrp)
