from typing import Literal, TypedDict

import pyspark.sql.types as t
from typing_extensions import NotRequired

IFormat = Literal[
    'delta',
    'parquet',
    'csv',
    'jdbc',
    'json',
    'orc',
    'parquet',
    'text'
]


class IReadOptions(TypedDict):
    path: str
    format: IFormat
    schema: NotRequired[str | t.StructType]
    header: NotRequired[bool]
    inferSchema: NotRequired[bool]
    sep: NotRequired[str]
    multiLine: NotRequired[bool]
    pathGlobFilter: NotRequired[str]
    url: NotRequired[str]
    dbtable: NotRequired[str]
    user: NotRequired[str]
    password: NotRequired[str]
    driver: NotRequired[str]
    query: NotRequired[str]


class ISavingOptions(TypedDict):
    path: str
    format: Literal['delta', 'parquet', 'csv', 'json', 'orc']
    mode: Literal['append', 'overwrite', 'ignore', 'errorifexists']


class IView(TypedDict):
    name: str
    prefix: NotRequired[bool]
    step: NotRequired[Literal['stg', 'ctx', 'calc', 'out', 'chk', 'dbg']]
    cache: NotRequired[bool]
    read: NotRequired[IReadOptions]
    save: NotRequired[ISavingOptions]
