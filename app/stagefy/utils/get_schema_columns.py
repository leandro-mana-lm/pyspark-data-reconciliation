from typing import Any, Optional

import pyspark.sql.functions as f
import pyspark.sql.types as t
from pyspark.sql import Column, DataFrame


def get_schema_columns(
    dataframe: DataFrame,
    schema: t.StructType,
    default_values: Optional[dict[str, Any]] = None,
) -> list[Column]:
    """
    Builds a list of PySpark columns aligned to the provided schema, casting
    existing columns and creating missing ones with default values.

    Args:
        dataframe (DataFrame): The input DataFrame to be aligned with the
        schema.
        schema (t.StructType): The target schema defining the expected columns
        and their data types.
        default_values (Optional[dict[str, Any]], optional): A dictionary of
        default values for missing columns. Defaults to None.

    Returns:
        list[Column]: A list of columns with the specified schema applied.
    """

    dataframe_columns = set(dataframe.columns)
    default_values = default_values or {}

    return [
        f.col(column.name).cast(column.dataType).alias(column.name)
        if column.name in dataframe_columns
        else
        f.lit(default_values.get(column.name))
        .cast(column.dataType)
        .alias(column.name)
        for column in schema.fields
    ]
