from flask import Blueprint, request
from app.models import User, Portfolio
import app.market_data as market_data
import app.utility as util
from app import db
from datetime import datetime
from sqlalchemy import update, insert, delete, func
from io import StringIO
import csv

from config import Config

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio/<username>/view', methods=['GET'])
def get_portfolio(username):
    """
    Retrieve a list of the equities and the quantity held on a particular date
    by a particular user, if they exist 
    """
    user_obj = User.query.filter(User.username == username).first()
    date = request.args.get('date')

    if user_obj is None:
        return util.build_json_response('User does not exist')

    if not util.is_valid_date_string(date):
        return util.build_json_response("Not a valid date of the form YYYY-MM-DD")

    following_date = util.add_days_to_date(date, 1)
    equities = db.session.query(Portfolio.ticker, func.sum(Portfolio.quantity))\
        .filter(Portfolio.user_id == user_obj.id) \
        .filter(Portfolio.transaction_date <= following_date) \
        .group_by(Portfolio.ticker).all()

    result = dict()
    for equity in equities:
        result[equity[0]] = equity[1]

    return util.build_json_response("Portfolio retrieved", equities=result)

@portfolio.route('/portfolio/<username>/buy', methods=['POST'])
def add_to_portfolio(username):
    """
    Adds a positive entry into the database to account for 'buying' a particular holding on a particular date
    only if the user exists and the price total (quantity * price) does not exceed the account balance
    """
    user_obj = User.query.filter(User.username == username).first()
    ticker = request.form.get('ticker')
    date = request.form.get('date')
    qty = request.form.get('qty')

    if user_obj is None:
        return util.build_json_response('User does not exist')

    if (len(ticker) == 0) or (not util.is_valid_date_string(date)):
        return util.build_json_response("No ticker or valid date of the form YYYY-MM-DD")

    if not qty.isnumeric() or int(qty) < 0:
        return util.build_json_response("Quantity is not valid")

    price = int(qty) * market_data.get_stock_price(ticker, date, 'low')

    if price > user_obj.balance:
        return util.build_json_response("Cost exceeds balance")

    new_balance = user_obj.balance - price
    date = datetime.fromisoformat(date)
    holding = Portfolio.query.\
        filter(Portfolio.user_id == user_obj.id)\
        .filter(Portfolio.transaction_date == date)\
        .filter(Portfolio.ticker == ticker)\
        .filter(Portfolio.transaction_type == 'BUY').first()

    try: 
        db.session.execute(
            update(User)
            .values(balance=new_balance)
            .where(User.id == user_obj.id)
        )

        if holding is None:
            holding = Portfolio(ticker, date, 'BUY', int(qty), user_obj.id)
            db.session.add(holding)
        else:
            db.session.execute(
                update(Portfolio)
                .values(quantity=holding.quantity + int(qty))
                .where(Portfolio.user_id == user_obj.id)
                .where(Portfolio.transaction_date == date)
                .where(Portfolio.ticker == ticker)
                .where(Portfolio.transaction_type == 'BUY')
            )
        db.session.commit()
    except:
        return util.build_json_response("Failure to update DB")

    return util.build_json_response("Stock added to portfolio", stock=request.form, balance=user_obj.balance)

@portfolio.route('/portfolio/<username>/sell', methods=['POST'])
def remove_from_portfolio(username):
    """
    Adds a negative entry into the database to account for 'selling' a particular holding on a particular date
    only if the user exists and the quantity being sold does not exceed the quantity held up to that date
    """
    user_obj = User.query.filter(User.username == username).first()
    ticker = request.form.get('ticker')
    date = request.form.get('date')
    qty = request.form.get('qty')

    if user_obj is None:
        return util.build_json_response('User does not exist')

    if (len(ticker) == 0) or (not util.is_valid_date_string(date)):
        return util.build_json_response("No ticker or valid date of the form YYYY-MM-DD")

    if not qty.isnumeric() or int(qty) < 0:
        return util.build_json_response("Quantity is not valid")

    following_date = util.add_days_to_date(date, 1)
    qty_held = db.session.query(func.sum(Portfolio.quantity))\
        .filter(Portfolio.user_id == user_obj.id) \
        .filter(Portfolio.transaction_date <= following_date) \
        .group_by(Portfolio.ticker).first()[0]

    if qty_held < int(qty): 
        return util.build_json_response("Cannot sell more than you hold")

    price = int(qty) * market_data.get_stock_price(ticker, date, 'low')
    new_balance = user_obj.balance + price
    date = datetime.fromisoformat(date)
    holding = Portfolio.query\
        .filter(Portfolio.user_id == user_obj.id)\
        .filter(Portfolio.transaction_date == date)\
        .filter(Portfolio.ticker == ticker)\
        .filter(Portfolio.transaction_type == 'SELL').first()

    try: 
        db.session.execute(
            update(User)
            .values(balance=new_balance)
            .where(User.id == user_obj.id)
        )

        if holding is None:
            holding = Portfolio(ticker, date, 'SELL', -int(qty), user_obj.id)
            db.session.add(holding)
        else:
            db.session.execute(
                update(Portfolio)
                .values(quantity=holding.quantity - int(qty))
                .where(Portfolio.user_id == user_obj.id)
                .where(Portfolio.transaction_date == date)
                .where(Portfolio.ticker == ticker)
                .where(Portfolio.transaction_type == 'SELL')
            )
        db.session.commit()
    except:
        return util.build_json_response("Failure to update DB")

    return util.build_json_response("Stock sold", stock=request.form, balance=user_obj.balance)

@portfolio.route('/portfolio/<username>/evaluate', methods=['GET'])
def evaluate_portfolio(username):
    """
    Returns the total portfolio balance at a particular date 
    along with the cash and equity split of that total if the employee exists
    """
    user_obj = User.query.filter(User.username == username).first()
    date = request.args.get('date')

    if user_obj is None:
        return util.build_json_response('User does not exist')

    if not util.is_valid_date_string(date):
        return util.build_json_response("Not a valid date of the form YYYY-MM-DD")

    following_date = util.add_days_to_date(date, 1)
    equities = db.session.query(Portfolio.ticker, func.sum(Portfolio.quantity))\
        .filter(Portfolio.user_id == user_obj.id) \
        .filter(Portfolio.transaction_date <= following_date) \
        .group_by(Portfolio.ticker).all()

    e_total = 0
    for equity in equities:
        price = equity[1] * market_data.get_stock_price(equity[0], date, 'low')
        e_total += price

    total = round(e_total + user_obj.balance, 2)
    cash = round(user_obj.balance, 2)
    e_total = round(e_total, 2)

    return util.build_json_response("Portfolio totals retrieved", equity_total=e_total, cash_balance=cash, account_total=total)

@portfolio.route('/portfolio/<username>/replace', methods=['POST'])
def replace_portfolio(username):
    """
    Clear all holdings and reset balance information for a user, if they exist
    and insert holdings as per the uploaded CSV file with rows containing (date,symbol,quantity,type)
    """
    user_obj = User.query.filter(User.username == username).first()
    
    if user_obj is None:
        return util.build_json_response('User does not exist')

    if 'file' not in request.files:
        return util.build_json_response("No file part in upload")
    
    file = request.files['file']
    if not file: 
        return util.build_json_response("File data not found")

    # Reset balance and delete existing holdings
    try:
        db.session.execute(
            update(User)
            .values(balance=Config.DEFAULT_BALANCE)
            .where(User.id == user_obj.id)
        )

        db.session.execute(
            delete(Portfolio)
            .where(Portfolio.user_id == user_obj.id)
        )

        db.session.commit()
    except:
        return util.build_json_response("Failure accessing DB")

    # read file contents and parse them out
    file_contents = StringIO(file.read().decode())
    csv_file = csv.DictReader(file_contents, delimiter=',')
    
    # insert all rows into DB as trades
    try:
        for row in csv_file:
            row['date'] = datetime.fromisoformat(row['date'])
            cur_equity = Portfolio(row['symbol'], row['date'], row['type'], row['quantity'], user_obj.id)
            db.session.add(cur_equity)     
        db.session.commit()
    except:
        return util.build_json_response("Failed to add trades to DB")

    return util.build_json_response("Portfolio replaced")

@portfolio.route('/portfolio/<username>/clear_holdings', methods=['DELETE'])
def clear_holdings(username):
    """
    Clear all holdings for a paritcular user, if they exist, and reset the balance back to the default balance amount
    """
    user_obj = User.query.filter(User.username == username).first()
    
    if user_obj is None:
        return util.build_json_response('User does not exist')

    try:
        db.session.execute(
            update(User)
            .values(balance=Config.DEFAULT_BALANCE)
            .where(User.id == user_obj.id)
        )

        db.session.execute(
            delete(Portfolio)
            .where(Portfolio.user_id == user_obj.id)
        )

        db.session.commit()
    except:
        return util.build_json_response("Failure accessing DB")

    return util.build_json_response("Portfolio cleared")

@portfolio.route('/portfolio/stock/<ticker>', methods=['GET'])
def get_price(ticker):
    """
    Retrieve price for a particular stock ticker on a particular date of the form YYYY-MM-DD (default price type to 'low')
    """
    date = request.args.get('date')
    if (date is None) or (not util.is_valid_date_string(date)): 
        return util.build_json_response("No date selected or not in the form YYYY-MM-DD")

    price = market_data.get_stock_price(ticker, date, 'low')
    if price is None:
        return util.build_json_response("No Data Found")
    return util.build_json_response("Stock found", ticker=ticker, date=date, price=price)
