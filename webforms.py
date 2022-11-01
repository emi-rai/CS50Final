from ast import Pass, Sub
from tokenize import String
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import TextArea
#from flask_ckeditor import CKEditorField
import sqlite3


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    username = StringField('Enter username', validators=[DataRequired()])
    password = PasswordField('Type password', validators=[DataRequired()])
    confirmation = PasswordField('Confirm password', validators=[DataRequired()])
    register = SubmitField("Register")

class HikeLog(FlaskForm):
    hike_title = StringField('Name of Hike', validators=[DataRequired()])
    hike_date = StringField('Date of Hike', validators=[DataRequired()])
    content = StringField('Details', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Log Hike")