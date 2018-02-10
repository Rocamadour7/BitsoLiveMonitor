import requests


class APITicker:
    def __init__(self):
        self.url = 'https://api.bitso.com/v3/ticker/'

    def _send_request(self):
        response = requests.get(self.url)
        return response.json()

    def _handle_response(self, response):
        if not response['success']:
            return None
        else:
            payload = response['payload']
            return payload

    def _payload_handler(self, payload):
        for book in payload:
            if (not hasattr(self, book['book'])) or (self.__getattribute__(book['book']) != book['last']):
                self.__setattr__(book['book'], book['last'])

    def update(self):
        response_json = self._send_request()
        payload = self._handle_response(response_json)
        if payload is not None:
            self._payload_handler(payload)
        else:
            return None
