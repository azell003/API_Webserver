import json

def test_getting_existing_stock_prices(test_client, init_database): 
    response = test_client.get('/portfolio/stock/aapl?date=2017-01-03')
    
    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'Stock found' in data['message']
    assert '2017-01-03' in data['data']['date']
    assert 'aapl' in data['data']['ticker']
    assert 114.76 == data['data']['price']

def test_adding_stock_to_portfolio(test_client, init_database): 
    response = test_client.post('/portfolio/user2/buy', data=dict(
        ticker='aapl', 
        date='2017-01-03', 
        qty=10
    ))

    data = json.loads(response.data)

    assert response.status_code == 200
    assert b'Stock added to portfolio' in response.data
    assert data['data']['balance'] == 98852.4
    assert data['data']['stock']['ticker'] == 'aapl'
    assert data['data']['stock']['qty'] == '10'
    assert data['data']['stock']['date'] == '2017-01-03'


def test_buying_and_selling_stock_to_portfolio(test_client, init_database):
    buy_resp = test_client.post('/portfolio/user1/buy', data=dict(
        ticker='aapl', 
        date='2017-01-03', 
        qty=10
    ))

    sell_resp = test_client.post('/portfolio/user1/sell', data=dict(
        ticker='aapl', 
        date='2017-01-04', 
        qty=10
    ))

    sell = json.loads(sell_resp.data)

    assert buy_resp.status_code == 200
    assert sell_resp.status_code == 200
    assert b'Stock sold' in sell_resp.data
    assert sell['data']['balance'] == 100009.9
    assert sell['data']['stock']['ticker'] == 'aapl'
    assert sell['data']['stock']['qty'] == '10'
    assert sell['data']['stock']['date'] == '2017-01-04'

def test_selling_more_stock_than_held(test_client, init_database):
    sell_resp = test_client.post('/portfolio/user1/sell', data=dict(
        ticker='fb', 
        date='2017-01-04', 
        qty=10
    ))

    assert sell_resp.status_code == 200
    assert b'Cannot sell more than you hold' in sell_resp.data

def test_view_entire_portfolio(test_client, init_database):
    test_client.post('/portfolio/user3/buy', data=dict(
        ticker='aapl', 
        date='2017-01-03', 
        qty=10
    ))

    test_client.post('/portfolio/user3/buy', data=dict(
        ticker='fb', 
        date='2017-01-04', 
        qty=5
    ))

    test_client.post('/portfolio/user3/buy', data=dict(
        ticker='amzn', 
        date='2017-01-04', 
        qty=2
    ))
    response = test_client.get('/portfolio/user3/view?date=2017-01-04')
    
    holdings = json.loads(response.data)

    assert response.status_code == 200
    assert b'Portfolio retrieved' in response.data
    assert holdings['data']['equities']['aapl'] == 10
    assert holdings['data']['equities']['fb'] == 5
    assert holdings['data']['equities']['amzn'] == 2

def test_evaluate_portfolio(test_client, init_database):
    response = test_client.get('/portfolio/user3/evaluate?date=2017-01-04')
    
    holdings = json.loads(response.data)

    assert response.status_code == 200
    assert b'Portfolio totals retrieved' in response.data
    assert holdings['data']['account_total'] == 100009.90
    assert holdings['data']['cash_balance'] == 96757.55
    assert holdings['data']['equity_total'] == 3252.35

def test_replacing_portfolio_with_trade_file(test_client, init_database):
    file_path = 'tests/functional/resources/stock_portfolio.csv'
    with open(file_path, 'rb') as f:
        replace_resp = test_client.post('/portfolio/user1/replace', content_type='multipart/form-data', data=dict(
            file=(f, f.name)
        ))
    response = test_client.get('/portfolio/user1/view?date=2017-03-15')

    holdings = json.loads(response.data)

    assert replace_resp.status_code == 200
    assert response.status_code == 200
    assert b'Portfolio replaced' in replace_resp.data
    assert b'Portfolio retrieved' in response.data
    assert holdings['data']['equities']['NFLX'] == 25
    assert holdings['data']['equities']['AMD'] == 15
    assert holdings['data']['equities']['GOOG'] == 10

def test_clearing_portfolio(test_client, init_database):
    delete_resp = test_client.delete('/portfolio/user1/clear_holdings')
    response = test_client.get('/portfolio/user1/view?date=2017-12-31')

    data = json.loads(response.data)

    assert response.status_code == 200
    assert b'Portfolio cleared' in delete_resp.data
    assert b'Portfolio retrieved' in response.data
    assert not data['data']['equities']
