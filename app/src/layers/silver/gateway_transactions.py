from dataclasses import dataclass, field

import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession

from src import readers
from stagefy.decorators import DataFrameViewRegistry, set_class_logger

registry = DataFrameViewRegistry(task='pyspark_data_reconciliation')


@dataclass
@set_class_logger
class GatewayTransactions:
    """
    Data query for gateway transactions.
    """

    spark: SparkSession = field(init=False, repr=False)
    dataframe: DataFrame = field(init=False, repr=False)

    @registry.save({**readers.silver.gateway_transactions.config['writer']})
    @registry.view({'name': 'gateway_transactions', 'step': 'calc'})
    @registry.refresh({
        'name': 'gateway_transactions',
        'step': 'stg',
        'read': readers.silver.gateway_transactions.config['reader'],
    })
    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """

        self.dataframe = self.spark.table(
            registry.name({'name': 'gateway_transactions', 'step': 'stg'}),
        ).select(
            f.col('transaction_id'),
            f.trim(f.upper('order_id')).alias('order_id'),
            f.to_timestamp(
                f.regexp_replace('transaction_date', r'\D+', ''),
                'yyyyMMddHHmmss',
            ).alias('transaction_date'),
            f.col('paid_amount').cast('decimal(10,2)'),
            f.upper('currency').alias('currency'),
            f.upper('payment_method').alias('payment_method'),
            f.when(
                f.upper('transaction_status') == 'APPROVED',
                f.lit('PAID')
            ).otherwise(
                f.upper('transaction_status')
            ).alias('transaction_status'),
            f.col('ingestion_date'),
            f.upper('source_file').alias('source_file'),
        ).coalesce(1)

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
