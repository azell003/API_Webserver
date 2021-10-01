from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    balance = db.Column(db.Float, nullable=False)
    portfolio = db.relationship('Portfolio', cascade="all, delete")

    def __init__(self, username, balance):
        self.username = username
        self.balance = balance

    def __repr__(self):
        return f'<User {self.username}>'

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(64))
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(4))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, ticker, date, type, qty, uid):
        self.ticker = ticker
        self.transaction_date = date
        self.transaction_type = type
        self.quantity = qty
        self.user_id = uid

    def __repr__(self):
        return f'<Portfolio {self.transaction_date} {self.ticker} {self.transaction_type} {self.quantity}>'
