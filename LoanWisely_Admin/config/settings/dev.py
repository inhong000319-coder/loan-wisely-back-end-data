from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
USE_MOCK_DATA = False
DISABLE_AUTH = True

# Long-running admin jobs (normalize/EDA) need more time than the default 10s.
SPRING_TIMEOUT_SECS = 300

