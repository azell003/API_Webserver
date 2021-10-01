class Config(object):
    # SQL Alchemy Configuration
    SQLALCHEMY_DATABASE_URI='sqlite:///storage/api_webserver.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # General Configuration
    DEFAULT_BALANCE = 100_000
    DEFAULT_STOCK_DATA_FILE = 'app/storage/top100.json'

config = Config()