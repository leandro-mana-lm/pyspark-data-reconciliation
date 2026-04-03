from dataclasses import dataclass, field

import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession

from src import readers
from stagefy.decorators import DataFrameViewRegistry, set_class_logger
from stagefy.interfaces import IView

registry = DataFrameViewRegistry(task='pyspark_data_reconciliation')

config = readers.gold.recon_order_result.config

refresh_views: list[IView] = [
    {
        'name': view,
        'step': 'calc',
        'read': {**config['reader'][view]},
    }
    for view in ('erp_orders', 'gateway_transactions')
]


@dataclass
@set_class_logger
class ReconOrderResult:
    """
    Data query to generate reconciliation order results.
    """

    spark: SparkSession = field(init=False, repr=False)
    dataframe: DataFrame = field(init=False, repr=False)

    @registry.save({**readers.gold.recon_order_result.config['writer']})
    @registry.view({'name': 'recon_order_result', 'step': 'calc'})
    @registry.refresh(*refresh_views)
    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """

        self.dataframe = self.spark.table(
            registry.name({'name': 'erp_orders', 'step': 'calc'})
        ).alias(
            'eo'
        ).join(
            other=self.spark.table(
                registry.name({
                    'name': 'gateway_transactions',
                    'step': 'calc',
                })
            ).alias('gt'),
            on=f.col('eo.order_id') == f.col('gt.order_id'),
            how='full',
        ).select(
            f.coalesce('eo.order_id', 'gt.order_id').alias('order_id'),
            f.col('eo.order_date').alias('erp_order_date'),
            f.col('gt.transaction_date').alias('gateway_transaction_date'),
            f.col('eo.customer_id').alias('customer_id'),
            f.col('eo.expected_amount').alias('erp_amount'),
            f.col('gt.paid_amount').alias('gateway_amount'),
            f.when(
                (f.col('eo.expected_amount').isNotNull()) &
                (f.col('gt.paid_amount').isNotNull()),
                f.col('eo.expected_amount') - f.col('gt.paid_amount')
            ).cast('decimal(10,2)').alias('amount_difference'),
            f.col('eo.currency').alias('erp_currency'),
            f.col('gt.currency').alias('gateway_currency'),
            f.col('eo.order_status').alias('erp_status'),
            f.col('gt.transaction_status').alias('gateway_status'),
            f.col('eo.order_id').isNotNull().alias('exists_in_erp'),
            f.col('gt.order_id').isNotNull().alias('exists_in_gateway'),
            f.col('eo.payment_method').alias('erp_payment_method'),
            f.col('gt.payment_method').alias('gateway_payment_method'),
            f.when(
                f.col('eo.order_id').isNull(),
                f.lit('MISSING_IN_ERP')
            ).when(
                f.col('gt.order_id').isNull(),
                f.lit('MISSING_IN_GATEWAY')
            ).when(
                f.abs(
                    f.col('eo.expected_amount') - f.col('gt.paid_amount')
                ) > 0.01,
                f.lit('AMOUNT_MISMATCH')
            ).when(
                f.col('eo.order_status') != f.col('gt.transaction_status'),
                f.lit('STATUS_MISMATCH')
            ).otherwise(
                f.lit('MATCHED')
            ).alias('reconciliation_status'),
            f.coalesce(
                'eo.ingestion_date',
                'gt.ingestion_date'
            ).alias('ingestion_date'),
        ).coalesce(1)

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
