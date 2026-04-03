from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Literal, Optional, TypedDict, TypeVar

from typing_extensions import NotRequired

from ..interfaces import IFileReader

T = TypeVar('T')


class IOptions(TypedDict):
    mode: NotRequired[Literal['r']]
    encoding: NotRequired[str]
    newline: NotRequired[str]


@dataclass
class FileReader(Generic[T]):
    """
    A class to read files using a specified file reader.
    """

    reader: IFileReader[T]
    source: str | Path
    options: Optional[IOptions] = None

    def load(self) -> T:
        """
        Reads the file from the specified source using the provided reader.

        Raises:
            FileNotFoundError: If the specified file is not found.

        Returns:
            T: The content read from the file.
        """

        try:
            path = Path(self.source)
            options: IOptions = self.options \
                if self.options is not None \
                else {}

            with path.open(**options) as file:
                content = self.reader.load(file)

            return content
        except FileNotFoundError:
            raise FileNotFoundError(f'File not found: {self.source}')
