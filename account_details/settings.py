import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class ParamConfig:
    def __init__(self):
        self.bitso_api_key = os.environ.get('API_KEY')
        self.bitso_api_secret = os.environ.get('API_SECRET')


config = ParamConfig()
