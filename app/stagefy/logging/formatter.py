from logging import Formatter

formatter = Formatter(
    fmt=' | '.join([
        '%(asctime)s.%(msecs)d',
        '%(levelname)s',
        '%(name)s',
        '%(message)s',
    ]),
    datefmt='%Y-%m-%d %H:%M:%S',
)
