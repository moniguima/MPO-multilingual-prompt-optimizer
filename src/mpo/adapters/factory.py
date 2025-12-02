"""
Factory function for creating cultural adapters.
"""

from typing import Dict
from ..core.adapter import CulturalAdapter
from .en_adapter import EnglishAdapter
from .de_adapter import GermanAdapter
from .es_adapter import SpanishAdapter


def get_adapter(language_code: str, config: Dict) -> CulturalAdapter:
    """
    Factory function to instantiate the appropriate cultural adapter.

    Args:
        language_code: ISO language code ('en', 'de', 'es')
        config: Language configuration dictionary

    Returns:
        Appropriate CulturalAdapter subclass instance

    Raises:
        ValueError: If language code is not supported
    """
    adapters = {
        "en": EnglishAdapter,
        "de": GermanAdapter,
        "es": SpanishAdapter
    }

    adapter_class = adapters.get(language_code)
    if not adapter_class:
        raise ValueError(f"Unsupported language code: {language_code}")

    return adapter_class(config)
