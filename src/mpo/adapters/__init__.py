"""
Cultural adapters for different languages.

This package contains language-specific cultural adaptation implementations.
"""

from .en_adapter import EnglishAdapter
from .de_adapter import GermanAdapter
from .es_adapter import SpanishAdapter
from .factory import get_adapter

__all__ = [
    'EnglishAdapter',
    'GermanAdapter',
    'SpanishAdapter',
    'get_adapter'
]
