import csv
from collections.abc import Sequence
from dataclasses import dataclass
from io import TextIOWrapper
from typing import Optional, TypedDict

from typing_extensions import NotRequired


class IOptions(TypedDict):
    fieldnames: NotRequired[Sequence[str]]
    delimiter: NotRequired[str]
    quotechar: NotRequired[str]
    skipinitialspace: NotRequired[bool]
    restkey: NotRequired[str]
    restval: NotRequired[str]


@dataclass
class CSVReader:
    """
    CSV file reader implementation.
    """

    options: Optional[IOptions] = None

    def load(self, file: TextIOWrapper) -> ...:
        """
        Load CSV content from a file.

        Args:
            file (TextIOWrapper): The file object to read from.
        Returns:
            ...: The content loaded from the CSV file.
        """

        options: IOptions = self.options if self.options is not None else {}

        content = [row for row in csv.DictReader(file, **options)]

        return content
