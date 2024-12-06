import os
from os import environ
apisettings = {
  "serviceurl": "http://local.test:8000/api/v1/",
#   "serviceurl": "https://www.geodesignhub.com/api/v1/",
}


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SUPER-SECRET'
    LOGFILE = "log.log"
    REDIS_URL = environ.get("REDIS_URL", "redis://localhost:6379")
    LANGUAGES = {"en": "English"}

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_BACKTRACE = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    LOG_BACKTRACE = False
    LOG_LEVEL = 'INFO'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}