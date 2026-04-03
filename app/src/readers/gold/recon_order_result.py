from typing import TypedDict

from stagefy.interfaces import IReadOptions, ISavingOptions
from stagefy.reader import FileReader, YAMLReader


class IReader(TypedDict):
    erp_orders: IReadOptions
    gateway_transactions: IReadOptions


class IConfig(TypedDict):
    reader: IReader
    writer: ISavingOptions


reader = FileReader[IConfig](
    reader=YAMLReader(),
    source='/workspace/app/src/config/gold/recon_order_result.yaml',
)

config = reader.load()
