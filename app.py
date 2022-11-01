from re import S
import re
import sqlite3
from tabnanny import check
from flask import Flask, render_template, session, flash, request, redirect 
from flask_session import Session
from flask_login import LoginManager, login_required, UserMixin, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

import os

from helpers import sql_data_to_list_of_dicts
from webforms import LoginForm, RegisterForm, HikeLog
import creds


# Instantiate Flask App
app = Flask(__name__)

# Add secret key
app.config['SECRET_KEY'] = creds.SECRET_KEY

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session(app)
sess.init_app(app)

# Configure application for login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create User class
class Users(UserMixin):
    def __init__(self, id, created, username, user_password):
        self.id = int(id)
        self.created = created
        self.username = username
        self.user_password = user_password
        self.authenticated = False
    
    def is_active(self):
        return self.is_active()
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id

# Create HikeLog class
class Log(UserMixin):
    def __init__(self, id, user_id, created, hike_title, hike_date, content):
        self.id = int(id)
        self.user_id = int(user_id)
        self.created = created
        self.hike_title = hike_title
        self.hike_date = hike_date
        self.content = content

    def is_active(self):
        return self.is_active()
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id
        

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute('SELECT * from users where id = ?', (user_id,))
    row = curs.fetchone()
    if row is None:
        return None
    else: 
        return Users(int(row[0]), row[1], row[2], row[3])

# Open connection to database.db and enable name-based access to columns
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        return render_template('home.html', username=request.args.get('username'))


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/register', methods=['POST', 'GET'])
def register():

    form = RegisterForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Check that username is not already in the database
            db = get_db_connection()
            check_username = db.execute('SELECT * FROM users WHERE username = ?', (form.username.data,)).fetchall()

            if check_username:
                flash('Sorry, this username is already taken')
                return render_template('register.html', form=form)

            # Check that password and confirmation match
            elif form.password.data != form.confirmation.data:
                flash('Passwords do not match - Please try again')
                return render_template('register.html', form=form)

            # Make password hash
            else: 
                hash = generate_password_hash(form.password.data)
                # Enter username and password hash into users database
                db.execute('INSERT INTO users (username, user_password) VALUES (?, ?)', (form.username.data, hash))
                db.commit()
                user_obj = db.execute('SELECT id FROM users WHERE username = ?', (form.username.data,))
                # Convert object into list
                user_list = sql_data_to_list_of_dicts(user_obj)
                print(user_list)
                print(user_list[0]["id"])
                # Load the user
                user = load_user(user_list[0]["id"])
                # Login the user
                login_user(user)
                # Start session
                session['username'] = user.id
                # Return the home page
                return render_template('/home.html', username=form.username.data)
        
        flash('Please complete all fields')
        return render_template('register.html', form=form)
    
    else: 
        return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():

    form = LoginForm()

    if request.method() == 'POST':
        if form.validate_on_submit():
            # Check username on form is in the database
            conn = get_db_connection()
            curs = conn.cursor()
            curs_obj = curs.execute('SELECT * FROM users WHERE username = ?', (form.username.data,))
            user_list = sql_data_to_list_of_dicts(curs_obj)

            # If user is in database
            if user_list:
        
                user = load_user(user_list[0]['id'])
                
                # If username and password match database, log the user in and initiate a session
                if form.username.data == user.username and check_password_hash(user.user_password, form.password.data):
                    login_user(user)
                    session['username'] = user.id
                    return redirect('/home?username=' + request.form.get('username'))
                
                # If the username or password are incorrect, flash a message and reload the login form
                elif not user.username:
                    flash('Username Not Found - Try Again')
                    return render_template('login.html', form=form)

                elif not check_password_hash(user.user_password, form.password.data):
                    flash('Wrong Password - Try Again')
                    return render_template('login.html', form=form)
                
            flash('Username Not Found - Try Again!')
            
            return render_template('login.html', form=form)  
    
    return render_template('login.html', form=form)

@app.route('/loghike', methods =['GET', 'POST'])
@login_required
def loghike():

    form = HikeLog()    

    if request.method == 'POST':

        if form.validate_on_submit():
            # Connect to the database
            db = get_db_connection()
            # Insert info into database
            db.execute('INSERT INTO hikelog (hike_title, hike_date, content, user_id) VALUES (?, ?, ?, ?)', (form.hike_title.data, form.hike_date.data, form.content.data, session.get('username')))
            db.commit()
            # Show user message
            flash('Hike Logged!')

        # Redirect to the webpage
        return render_template("loghike.html", form=form)
    
    return render_template("loghike.html", form=form)

@app.route('/viewlog')
@login_required
def viewlog():
    # Get all logged hikes from database
    db = get_db_connection()
    log_obj = db.execute('SELECT hike_title, hike_date, content, created FROM hikelog WHERE user_id = ?', (session.get('username'),))
    log_list = sql_data_to_list_of_dicts(log_obj)
    print(log_list)

    return render_template('viewlog.html', log_list=log_list)
