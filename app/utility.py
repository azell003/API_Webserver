from datetime import date, datetime
from flask import jsonify
import time
from datetime import datetime, timedelta

def build_json_response(message: str,  **kwargs):
    """
    Build a JSON object with 'message' and 'data' keys to be returned as the API response
    """
    json_obj = dict()
    json_obj['message'] = message
    if len(kwargs) > 0:
        json_obj['data'] = kwargs
    return jsonify(json_obj)
    
def is_valid_date_string(date: str):
    """
    Ensures that the date is of the form YYYY-MM-DD
    """
    try:
        time.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False

def add_days_to_date(date: str, num_days: int):
    """
    Returns a date which is the addition of the original date and num_days number of days
    """
    date_1 = datetime.fromisoformat(date)
    return date_1 + timedelta(days=num_days)