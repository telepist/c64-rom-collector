"""
Local filesystem implementation of the FileRepository interface.
"""
from pathlib import Path
from typing import Iterator, Union, BinaryIO
import shutil

from ..repository import FileRepository

class LocalFileRepository(FileRepository):
    """Implementation of FileRepository for local filesystem."""

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read file from local filesystem."""
        path = Path(path)
        return path.read_bytes()

    def write_file(self, path: Union[str, Path], data: bytes) -> None:
        """Write file to local filesystem."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> Iterator[Path]:
        """List files in local filesystem directory."""
        directory = Path(directory)
        return directory.glob(pattern)

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if path exists in local filesystem."""
        return Path(path).exists()

    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy file in local filesystem."""
        src, dst = Path(src), Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Move file in local filesystem."""
        src, dst = Path(src), Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def get_file_size(self, path: Union[str, Path]) -> int:
        """Get file size in local filesystem."""
        return Path(path).stat().st_size

    def remove_file(self, path: Union[str, Path]) -> None:
        """Remove file from local filesystem."""
        path = Path(path)
        path.unlink()

    def remove_directory(self, path: Union[str, Path], recursive: bool = False) -> None:
        """Remove directory from local filesystem."""
        path = Path(path)
        if recursive:
            shutil.rmtree(path)
        else:
            path.rmdir()

    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if path is a file in local filesystem."""
        return Path(path).is_file()

    def is_dir(self, path: Union[str, Path]) -> bool:
        """Check if path is a directory in local filesystem."""
        return Path(path).is_dir()
