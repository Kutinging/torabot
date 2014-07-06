from celery.schedules import crontab
import os


# flask
SECRET_KEY = 'test'
CACHE_TYPE = 'simple'
TRAP_BAD_REQUEST_ERRORS = True

# celery
BROKER_URL = 'redis://'
CELERY_RESULT_BACKEND = 'redis://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {
    'sync': {
        'task': 'torabot.celery.sync_all',
        'schedule': crontab(minute='*/5'),  # check sync every 5 minutes
    },
    'notice': {
        'task': 'torabot.celery.notice_all',
        'schedule': crontab(minute='*/5'),  # notice every 5 minutes
    },
    'log_to_file': {
        'task': 'torabot.celery.log_to_file',
        'schedule': crontab(minute='*/1'),  # log every 1 minutes
    }
}

TORABOT_DEBUG = True
TORABOT_CONNECTION_STRING = (
    'postgresql+psycopg2://{0}:{0}@localhost/{0}'
    .format('torabot-dev')
)
TORABOT_SYNC_THREADS = 32
TORABOT_EMAIL_HEAD = 'torabot notice'
TORABOT_SPY_TIMEOUT = 30
TORABOT_SPY_SLAVES = 1
TORABOT_NOTICE_ROOM = 16
TORABOT_PAGE_ROOM = 16
TORABOT_BUBBLE_LOG = True
TORABOT_DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data')
TORABOT_EXAMPLE_USER_ID = 1
TORABOT_ISSUE_LIST_URI = 'https://github.com/Answeror/torabot/issues'
TORABOT_EMAIL_HOST = 'smtp.gmail.com'
TORABOT_EMAIL_PORT = 587
TORABOT_REST_WATCH_HIGHLIGHT_THRESHOLD = 4
TORABOT_DEFAULT_MAXWATCH = 42
TORABOT_TELL_ADMIN_NEW_USER = False
TORABOT_DEFAULT_SYNC_INTERVAL = 15 * 60  # integer, seconds
TORABOT_QUERY_EXPIRE = TORABOT_DEFAULT_SYNC_INTERVAL
TORABOT_RECENT_NOTICE_THRESHOLD = 8

# mod
TORABOT_DEFAULT_MOD = 'tora'
TORABOT_MOD_TORA_TRANSLATE = True
# pixiv cookies
# TORABOT_MOD_PIXIV_SPY_PHPSESSID = ''
TORABOT_MOD_PIXIV_SPY_MAX_ARTS = 12
TORABOT_MOD_YANDERE_COMPLETION_CACHE_TIMEOUT = 600
