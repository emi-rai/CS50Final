from operator import truediv
from os import environ, path
from dotenv import load_dotenv


# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))


class Config:
    """ Set Flask configuration variables """
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    TEMPLATES_AUTO_RELOAD = True
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'