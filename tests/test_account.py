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
        cls.key = cls.account.api_key
        cls.secret = cls.account.api_secret
        cls.nonce = str(int(round(time.time() * 1000)))
        cls.request_path = '/v3/account_status/'
        cls.message = cls.nonce + 'GET' + cls.request_path + ''
        cls.signature = hmac.new(cls.secret.encode('UTF-8'), cls.message.encode('UTF-8'), hashlib.sha256).hexdigest()

    def setUp(self):
        pass

    def test_create_signature(self):
        account_signature = self.account._create_signature(nonce=self.nonce,
                                                           request_path=self.request_path,
                                                           json_payload='')
        self.assertEqual(self.signature, account_signature)

    def test_create_auth_header(self):
        auth_header = 'Bitso %s:%s:%s' % (self.key, self.nonce, self.signature)
        account_auth_header = self.account._create_auth_header(nonce=self.nonce, signature=self.signature)
        self.assertEqual(auth_header, account_auth_header)

    @mock.patch('requests.get')
    def test_get_request(self, mock_get):
        auth_header = 'Bitso %s:%s:%s' % (self.key, self.nonce, self.signature)
        content = {'success': True, 'payload': {'client_id': '000001', 'first_name': 'Foo', 'last_name': 'Bar'}}
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        result = self.account._get_request(request_path=self.request_path, auth_header=auth_header)
        self.assertEqual(result.json(), content)

    @mock.patch('requests.get')
    def test_get_balance(self, mock_get):
        btc = 0.0001
        eth = 0.05
        xrp = 50.32
        mxn = 127.54

        import json
        content = json.dumps({'payload':
            {'balances':
                [{
                    'currency': 'btc',
                    'available': btc
                }, {
                    'currency': 'eth',
                    'available': eth,
                }, {
                    'currency': 'xrp',
                    'available': xrp,
                }, {
                    'currency': 'mxn',
                    'available': mxn
                }]
            }})
        content = json.loads(content)
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        balance = self.account._get_balance()
        self.assertEqual(btc, balance['btc'])
        self.assertEqual(eth, balance['eth'])
        self.assertEqual(xrp, balance['xrp'])
        self.assertEqual(mxn, balance['mxn'])

    @mock.patch('requests.get')
    def test_get_details(self, mock_get):
        import json
        content_dict = {
            "success": True,
            "payload": {
                "client_id": "1234",
                "first_name": "Claude",
                "last_name": "Shannon",
                "status": "active",
                "daily_limit": "5300.00",
                "monthly_limit": "32000.00",
                "daily_remaining": "3300.00",
                "monthly_remaining": "31000.00",
                "cellphone_number": "verified",
                "cellphone_number_stored": "+525555555555",
                "email_stored": "shannon@maxentro.py",
                "official_id": "submitted",
                "proof_of_residency": "submitted",
                "signed_contract": "unsubmitted",
                "origin_of_funds": "unsubmitted"
            }
        }
        content = json.loads(json.dumps(content_dict))
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        details = self.account._get_details()
        self.assertDictEqual(content_dict['payload'], details)

    @mock.patch('requests.get')
    def test_connect(self, mock_get):
        tic = time.time()

        btc = 0.0001
        eth = 0.05
        xrp = 50.32
        mxn = 127.54

        import json
        content_json = {'success': True, 'payload':
            {'balances':
                [{
                    'currency': 'btc',
                    'available': btc
                }, {
                    'currency': 'eth',
                    'available': eth,
                }, {
                    'currency': 'xrp',
                    'available': xrp,
                }, {
                    'currency': 'mxn',
                    'available': mxn
                }]
            }}
        content = json.loads(json.dumps(content_json))
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        self.account.connect()
        toc = time.time()
        self.assertGreater(toc-tic, 1.0)

    def test_get_btc(self):
        btc = 0.0001
        self.account.balance['btc'] = btc
        account_btc = self.account.btc
        self.assertEqual(btc, account_btc)

    def test_get_eth(self):
        eth = 0.05
        self.account.balance['eth'] = eth
        account_eth = self.account.eth
        self.assertEqual(eth, account_eth)

    def test_get_xrp(self):
        xrp = 50.32
        self.account.balance['xrp'] = xrp
        account_xrp = self.account.xrp
        self.assertEqual(xrp, account_xrp)

    def test_get_mxn(self):
        mxn = 127.54
        self.account.balance['mxn'] = mxn
        account_mxn = self.account.mxn
        self.assertEqual(mxn, account_mxn)

    def test_get_full_name(self):
        full_name = 'Claude Shannon'
        self.account.details['first_name'] = 'claude  '
        self.account.details['last_name'] = ' shannon'
        account_full_name = self.account.full_name
        self.assertEqual(full_name, account_full_name)

    def test_is_active(self):
        self.account.details['status'] = 'active'
        self.assertTrue(self.account.is_active)

    def test_is_not_active(self):
        self.account.details['status'] = 'inactive'
        self.assertFalse(self.account.is_active)
