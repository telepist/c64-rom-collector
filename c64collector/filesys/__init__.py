"""
File system abstraction layer for C64 ROM collector.
Provides a clean, storage-agnostic API for file operations.
"""

from .repository import FileRepository
from .providers.local import LocalFileRepository

__all__ = ['FileRepository', 'LocalFileRepository']
