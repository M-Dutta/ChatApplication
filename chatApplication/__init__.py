import logging
from django.conf import settings

# Setup Loggers
FORMAT = '%(asctime)s %(levelname)s: %(module)s.%(funcName)s.%(lineno)d - %(message)s'
logging.basicConfig(format=FORMAT, level='DEBUG' if settings.DEBUG else 'INFO')
