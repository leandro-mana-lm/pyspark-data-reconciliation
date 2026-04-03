from typing import TypedDict

from stagefy.interfaces import IReadOptions, ISavingOptions
from stagefy.reader import FileReader, YAMLReader


class IConfig(TypedDict):
    reader: IReadOptions
    writer: ISavingOptions


reader = FileReader[IConfig](
    reader=YAMLReader(),
    source='/workspace/app/src/config/silver/erp_orders.yaml',
)

config = reader.load()
