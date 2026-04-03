from dataclasses import dataclass, field

import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession

from src import readers
from stagefy.decorators import DataFrameViewRegistry, set_class_logger

registry = DataFrameViewRegistry(task='pyspark_data_reconciliation')


@dataclass
@set_class_logger
class ErpOrders:
    """
    Data query for ERP orders.
    """

    spark: SparkSession = field(init=False, repr=False)
    dataframe: DataFrame = field(init=False, repr=False)

    @registry.save({**readers.bronze.erp_orders.config['writer']})
    @registry.view({'name': 'erp_orders', 'step': 'stg'})
    @registry.refresh({
        'name': 'erp_orders_raw',
        'step': 'stg',
        'read': {**readers.bronze.erp_orders.config['reader']},
    })
    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """

        self.dataframe = self.spark.table(
            registry.name({'name': 'erp_orders_raw', 'step': 'stg'})
        ).alias(
            'raw'
        ).select(
            'raw.*',
            f.current_timestamp().alias('ingestion_date'),
            f.element_at(
                col=f.split(f.input_file_name(), '/'),
                extraction=-1,
            ).alias('source_file'),
        ).coalesce(1)

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
