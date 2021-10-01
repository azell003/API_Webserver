class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI='sqlite:///storage/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DEFAULT_BALANCE = 100_000
    DEFAULT_STOCK_DATA_FILE = 'app/storage/top100.json'
    
test_config = TestConfig()