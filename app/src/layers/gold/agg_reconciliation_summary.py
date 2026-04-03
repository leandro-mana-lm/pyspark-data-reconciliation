from dataclasses import dataclass, field

import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession

from src import readers
from stagefy.decorators import DataFrameViewRegistry, set_class_logger

registry = DataFrameViewRegistry(task='pyspark_data_reconciliation')


@dataclass
@set_class_logger
class AggReconciliationSummary:
    """
    Data query to aggregate reconciliation summary.
    """

    spark: SparkSession = field(init=False, repr=False)
    dataframe: DataFrame = field(init=False, repr=False)

    @registry.save({
        **readers.gold.agg_reconciliation_summary.config['writer']
    })
    @registry.view({'name': 'agg_reconciliation_summary', 'step': 'calc'})
    @registry.refresh({
        'name': 'recon_order_result',
        'step': 'calc',
        'read': {**readers.gold.agg_reconciliation_summary.config['reader']},
    })
    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """

        status_condition = [
            ('matched_count', f.col('reconciliation_status') == 'MATCHED'),
            ('divergent_count', f.col('reconciliation_status') != 'MATCHED'),
            (
                'missing_in_erp_count',
                f.col('reconciliation_status') == 'MISSING_IN_ERP'
            ),
            (
                'missing_in_gateway_count',
                f.col('reconciliation_status') == 'MISSING_IN_GATEWAY',
            ),
            (
                'amount_mismatch_count',
                f.col('reconciliation_status') == 'AMOUNT_MISMATCH'
            ),
            (
                'status_mismatch_count',
                f.col('reconciliation_status') == 'STATUS_MISMATCH'
            ),
        ]

        self.dataframe = self.spark.table(
            registry.name({'name': 'recon_order_result', 'step': 'calc'})
        ).select(
            f.count(f.lit(1)).alias('total_orders'),
            *[
                f.sum(f.when(condition, 1).otherwise(0)).alias(alias)
                for alias, condition in status_condition
            ],
        ).select(
            f.col('total_orders'),
            *[f.col(column) for column, _ in status_condition],
            (
                (f.col('matched_count') / f.col('total_orders')) * 100
            ).alias('match_rate'),
        ).coalesce(1)

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
