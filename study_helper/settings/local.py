from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_study_helper',
        'USER': 'study_helper_user',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}