from logging import DEBUG, Logger

from .handler import handler

logger = Logger(name='stagefy')

logger.setLevel(level=DEBUG)
logger.addHandler(hdlr=handler)
