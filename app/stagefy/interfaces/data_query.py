from typing import Protocol

from pyspark.sql import DataFrame, SparkSession


class IDataQuery(Protocol):
    """
    Interface for data querying operations.

    Args:
        Protocol (class): Base protocol class for defining interfaces.
    """

    spark: SparkSession
    dataframe: DataFrame

    def __create_temp_views(self) -> None:
        """
        Create temporary views for data query.
        """
        ...

    def main(self) -> None:
        """
        Main method to execute the data query.
        """

        self.__create_temp_views()
