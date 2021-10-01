from flask import Blueprint, jsonify
from config import config
from app import db
from app.models import User
import app.utility as util

user = Blueprint('user', __name__)

@user.route('/user/<username>', methods=['GET'])
def get_user(username):
    """
    Retrieve a user and balance information from the database if it exists
    """
    user_obj = User.query.filter(User.username == username).first()
    if user_obj is None:
        return util.build_json_response('User does not exist')

    return util.build_json_response('User retrieved', username=user_obj.username, balance=user_obj.balance)

@user.route('/user/all', methods=['GET'])
def get_all_users():
    """
    Retrieve a list of users from the database if at least one user exists
    """
    user_obj = User.query.all()
    if user_obj is None:
        return util.build_json_response('No users found')

    user_list = [u.username for u in user_obj]
    return util.build_json_response('User list retrieved', users=user_list)

@user.route('/user/<username>', methods=['POST'])
def create_user(username):
    """
    Create a user if it does not already exist in the database and return the username and balance information
    """
    user_obj = User(username=username, balance=config.DEFAULT_BALANCE)
    try:
        db.session.add(user_obj)
        db.session.commit()
    except:
        return util.build_json_response('User creation has failed because user already exists or database connection error')

    return util.build_json_response('User created', user=username, balance=config.DEFAULT_BALANCE)

@user.route('/user/<username>', methods=['PUT'])
def update_user(username):
    return util.build_json_response('Update not allowed', user=username)

@user.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    """
    Delete a user if it exists in the database and return the user that was deleted
    """
    user_obj = User.query.filter(User.username == username).first()
    
    if user_obj is None:
        return util.build_json_response('User does not exist')

    try:
        db.session.delete(user_obj)
        db.session.commit()
    except:
        return util.build_json_response('Could not delete user')
    
    return util.build_json_response('User deleted', user=username)