import os

from .settings import *
from dotenv import load_dotenv


load_dotenv()

DEBUG = True

SECRET_KEY = os.environ["SECRET_KEY"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        # "HOST": os.environ["DB_HOST"],
        # "PORT": os.environ["PORT"],
    }
}
