from app.models import User, Portfolio

def test_user_model():
    user = User('myUser', 100_000)

    assert user.username == 'myUser'
    assert user.balance == 100_000
    assert user.__repr__() == '<User myUser>'

def test_portfolio_model():
    stock = Portfolio('AAPL', '2017-01-03', 'BUY', 10, 1)
    
    assert stock.ticker == 'AAPL'
    assert stock.transaction_date == '2017-01-03'
    assert stock.transaction_type == 'BUY'
    assert stock.quantity == 10
    assert stock.user_id == 1
    assert stock.__repr__() == '<Portfolio 2017-01-03 AAPL BUY 10>'