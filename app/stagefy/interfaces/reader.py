from io import TextIOWrapper
from typing import Protocol, TypeVar

T = TypeVar('T', covariant=True)


class IFileReader(Protocol[T]):
    """
    Interface for file readers.
    """

    def load(self, file: TextIOWrapper) -> T:
        """
        Load data from a file.

        Args:
            file (TextIOWrapper): The file to read from.

        Returns:
            T: The data read from the file.
        """
        ...
