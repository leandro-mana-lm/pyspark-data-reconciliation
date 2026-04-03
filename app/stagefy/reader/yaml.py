from dataclasses import dataclass
from io import TextIOWrapper

import yaml


@dataclass
class YAMLReader:
    """
    YAML file reader implementation.
    """

    def load(self, file: TextIOWrapper) -> ...:
        """
        Load YAML content from a file.

        Args:
            file (TextIOWrapper): The file object to read from.

        Returns:
            ...: The content loaded from the YAML file.
        """

        content = yaml.safe_load(file)

        return content
