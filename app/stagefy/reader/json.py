import json
from dataclasses import dataclass
from io import TextIOWrapper


@dataclass
class JSONReader:
    """
    JSON file reader implementation.
    """

    def load(self, file: TextIOWrapper) -> ...:
        """
        Load JSON content from a file.

        Args:
            file (TextIOWrapper): The file object to read from.

        Returns:
            ...: The content loaded from the JSON file.
        """

        content = json.load(file)

        return content
