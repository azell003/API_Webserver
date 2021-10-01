from datetime import datetime
from config import config
import pandas as pd

df = pd.read_json(config.DEFAULT_STOCK_DATA_FILE)
df['date'] = pd.to_datetime(df['date'])

def get_stock_price(ticker, date, price_type):
    """
    Return the price for a ticker on a particular date 
    where price_type could be 'low', 'high', 'open', 'close'
    """
    date = pd.to_datetime(date)

    row = df.loc[
        (df['Name'] == ticker.upper()) &
        (df['date'] == date)
    ]

    if len(row.index) == 0:
        return None

    return float(row[price_type])
