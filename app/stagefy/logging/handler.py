from logging import StreamHandler

from .formatter import formatter

handler = StreamHandler()

handler.setFormatter(fmt=formatter)
