from dataclasses import dataclass, field
from typing import Any, Optional

from pyspark.sql import SparkSession

from ..decorators import set_class_logger


@dataclass
@set_class_logger
class SparkConnection:
    """
    Class responsible for managing the Spark Connection.
    """

    spark: SparkSession = field(init=False, repr=False)
    config: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """
        Post-initialization method to build the Spark session and set
        configurations.
        """

        self.__build_spark_session()
        self.__set_spark_session_configuration()

    def __build_spark_session(self) -> None:
        """
        Build the Spark session.
        """

        self.spark = SparkSession.Builder().getOrCreate()

    def __set_spark_session_configuration(self) -> None:
        """
        Set Spark configurations.
        """

        if not self.config:
            return

        for key, value in self.config.items():
            self.spark.conf.set(key, value)
