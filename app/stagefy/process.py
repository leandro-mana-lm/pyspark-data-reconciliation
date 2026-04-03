from dataclasses import dataclass

from .connections import SparkConnection
from .decorators import set_class_logger
from .interfaces import IDataQuery


@dataclass
@set_class_logger
class Process:
    """
    Class responsible for processing data.

    Args:
        SparkConnection (class): Base class for Spark connection.

    Raises:
        RuntimeError: If the main method has not been executed before
        checking views.
    """

    connection: SparkConnection
    parameters: list[IDataQuery]

    def __check_parameters(self) -> None:
        """
        Check if parameters are valid.
        """

        if not self.parameters:
            raise ValueError('No data queries provided in parameters.')

    def create_temp_view(self) -> None:
        """
        Create temporary views in Spark.
        """

        for data_query in self.parameters:
            data_query.spark = self.connection.spark
            data_query.main()

    def run(self) -> None:
        """
        Main method to execute the data processing.
        """

        self.__check_parameters()
        self.create_temp_view()
