import os

DEBUG = os.environ.get('DEBUG')
ENV = os.environ.get('ENV')

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY')


CACHE_TYPE = "filesystem"
CACHE_DIR = "lti_cache_dir"
CACHE_DEFAULT_TIMEOUT = 600
DEBUG_TB_INTERCEPT_REDIRECTS = False

SQLALCHEMY_DATABASE_URI = os.environ.get('DB_STRING')

GOOGLE_ANALYTICS = os.environ.get('GOOGLE_ANALYTICS')
