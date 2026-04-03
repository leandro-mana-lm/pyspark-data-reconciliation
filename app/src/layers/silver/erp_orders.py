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

    @registry.save({**readers.silver.erp_orders.config['writer']})
    @registry.view({'name': 'erp_orders', 'step': 'calc'})
    @registry.refresh({
        'name': 'erp_orders',
        'step': 'stg',
        'read': readers.silver.erp_orders.config['reader'],
    })
    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """

        self.dataframe = self.spark.table(
            registry.name({'name': 'erp_orders', 'step': 'stg'}),
        ).select(
            f.upper(f.trim('order_id')).alias('order_id'),
            f.to_date(
                f.regexp_replace('order_date', r'\D+', ''),
                'yyyyMMdd',
            ).alias('order_date'),
            f.col('customer_id'),
            f.col('expected_amount').cast('decimal(10,2)'),
            f.upper('currency').alias('currency'),
            f.upper('payment_method').alias('payment_method'),
            f.upper('order_status').alias('order_status'),
            f.col('ingestion_date'),
            f.upper('source_file').alias('source_file'),
        ).coalesce(1)

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
