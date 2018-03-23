# -*- coding: utf-8 -*-
from . import BASE_DIR
import os

# TODO: if you want to choose another directory, change LOG_DIR path.
LOG_DIR = BASE_DIR + '/log/'

if os.path.exists(LOG_DIR) is False:
    os.mkdir(LOG_DIR)

APP_KEY = 'app'
INBOUND_KEY = 'inbound'
OUTBOUND_KEY = 'outbound'
EPISODE_RESULT_KEY = 'episode_result'
TASK_RESULT_KEY = 'task_result'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] [%(module)s] %(process)d %(thread)d %(message)s'
        },
        'normal' : {
            'format': '%(asctime)s [%(levelname)s] [%(module)s] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
        'result': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'normal',
            'filename': LOG_DIR + 'application.log'
        },
        'inbound': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'normal',
            'filename': LOG_DIR + 'inbound.log'
        },
        'outbound': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'normal',
            'filename': LOG_DIR + 'outbound.log'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'task_result': {
            'level': 'INFO',
            'mode':'w',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'result',
            'filename': LOG_DIR + 'task_result.log'
        },
        'episode_result': {
            'level': 'INFO',
            'mode':'w',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'result',
            'filename': LOG_DIR + 'episode_result.log'
        }
    },
    'loggers': {
        APP_KEY: {
            # 'handlers': ['app'],
            'handlers': ['app', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        INBOUND_KEY: {
            'handlers': ['inbound'],
            'level': 'DEBUG',
            'backupCount': 4,
            'formatter': 'verbose',
        },
        OUTBOUND_KEY: {
            'handlers': ['outbound'],
            'level': 'DEBUG',
            'backupCount': 4,
            'formatter': 'verbose',
        },
        OUTBOUND_KEY: {
            'handlers': ['outbound'],
            'level': 'DEBUG',
            'backupCount': 4,
            'formatter': 'verbose',
        },
        TASK_RESULT_KEY: {
            'handlers': ['task_result'],
            'level': 'INFO',
            'backupCount': 4,
            'formatter': 'result',
        },
        EPISODE_RESULT_KEY: {
            'handlers': ['episode_result'],
            'level': 'INFO',
            'backupCount': 4,
            'formatter': 'result',
        },
    }
}

CHERRYPY_ACCESS_LOG = LOG_DIR + 'access.log'
CHERRYPY_ERROR_LOG = LOG_DIR + 'error.log'
