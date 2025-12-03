"""
Factory function for creating cultural adapters.

Supports hybrid adaptation with optional LLM provider.
"""

from typing import Dict, Optional
from ..core.adapter import CulturalAdapter
from ..providers.base import AbstractLLMProvider
from .en_adapter import EnglishAdapter
from .de_adapter import GermanAdapter
from .es_adapter import SpanishAdapter


def get_adapter(
    language_code: str,
    config: Dict,
    provider: Optional[AbstractLLMProvider] = None
) -> CulturalAdapter:
    """
    Factory function to instantiate the appropriate cultural adapter.

    Args:
        language_code: ISO language code ('en', 'de', 'es')
        config: Language configuration dictionary
        provider: Optional LLM provider for hybrid adaptation

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

    return adapter_class(config, provider)
