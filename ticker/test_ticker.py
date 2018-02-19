import unittest
from unittest import mock
from unittest.mock import MagicMock

from ticker.api_ticker import APITicker


class TestTicker(unittest.TestCase):
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
        cls.ticker = APITicker()

    @mock.patch('requests.get')
    def test_send_request(self, mock_get):
        content = {'success': True, 'payload': [
            {'book': 'btc_mxn', 'volume': '22.31349615', 'high': '5750.00'}]}
        mock_resp = self._mock_response(content=content, json_data=content)
        mock_get.return_value = mock_resp

        result = self.ticker._send_request()
        self.assertEqual(result, content)

    def test_success_handle_response(self):
        success_response = {'success': True, 'payload': {
            'book': 'btc_mxn', 'volume': '22.31349615', 'high': '5750.00'}}
        payload = self.ticker._handle_response(success_response)
        self.assertEqual(success_response['payload'], payload)

    def test_fail_handle_response(self):
        fail_response = {'success': False, 'error': {
            'message': 'ERROR_MESSAGE', 'code': 'ERROR_CODE'}}
        payload = self.ticker._handle_response(fail_response)
        self.assertIsNone(payload)

    def test_payload_handler(self):
        payload = [{'book': 'btc_mxn', 'last': '161030.08'},
                   {'book': 'etc_mxn', 'last': '16499.00'},
                   {'book': 'xrp_msn', 'last': '16.84'}]
        books = [book['book'] for book in payload]
        self.ticker._payload_handler(payload)
        for book in books:
            self.assertTrue(hasattr(self.ticker, book))

    def test_update_with_payload(self):
        expected_response = {'success': True, 'payload': [{'book': 'btc_mxn', 'last': '161030.08'},
                                                          {'book': 'etc_mxn', 'last': '16499.00'},
                                                          {'book': 'xrp_msn', 'last': '16.84'}]}
        expected_payload = [{'book': 'btc_mxn', 'last': '161030.08'},
                            {'book': 'etc_mxn', 'last': '16499.00'},
                            {'book': 'xrp_msn', 'last': '16.84'}]

        self.ticker._send_request = MagicMock(return_value=expected_response)
        self.ticker._handle_response = MagicMock(return_value=expected_payload)
        self.ticker._payload_handler = MagicMock()

        self.ticker.update()
        self.ticker._send_request.assert_called_once()
        self.ticker._handle_response.assert_called_once_with(self.ticker._send_request.return_value)
        self.ticker._payload_handler.assert_called_once_with(
            self.ticker._handle_response.return_value)

    def test_update_without_payload(self):
        expected_response = {'success': True, 'payload': [{'book': 'btc_mxn', 'last': '161030.08'},
                                                          {'book': 'etc_mxn', 'last': '16499.00'},
                                                          {'book': 'xrp_msn', 'last': '16.84'}]}

        self.ticker._send_request = MagicMock(return_value=expected_response)
        self.ticker._handle_response = MagicMock(return_value=None)
        self.ticker._payload_handler = MagicMock()

        self.ticker.update()
        self.ticker._send_request.assert_called_once()
        self.ticker._handle_response.assert_called_once_with(self.ticker._send_request.return_value)
        self.ticker._payload_handler.assert_not_called()
