from functools import wraps
from select import select
from flask import g, request, redirect, url_for
import sqlite3

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def sql_data_to_list_of_dicts(cursor_obj):
    """ Returns a Cursor Object as a list of dicts """
    try:
        list_data = []
        for item in cursor_obj:
            list_data.append({k: item[k] for k in item.keys()})
        return list_data
    except Exception as e:
        print(f'Failed to execute with error: \n{e}')
        return []
