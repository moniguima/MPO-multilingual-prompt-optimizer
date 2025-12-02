"""
Multilingual Prompt Optimizer (MPO)

A tool for cultural adaptation of LLM prompts across languages,
demonstrating measurable performance improvements.
"""

__version__ = "1.0.0"

from .core.prompt import (
    PromptTemplate,
    PromptVariant,
    LLMResponse,
    PromptDomain,
    FormalityLevel
)

from .core.adapter import CulturalAdapter
from .adapters import (
    EnglishAdapter,
    GermanAdapter,
    SpanishAdapter,
    get_adapter
)

from .core.evaluator import PromptEvaluator

from .providers.base import AbstractLLMProvider, GenerationConfig
from .providers.anthropic_provider import AnthropicProvider, MockAnthropicProvider
from .providers.openai_provider import OpenAIProvider, MockOpenAIProvider
from .providers.local_provider import LocalLLMProvider

from .storage.cache_manager import CacheManager
from .storage.experiment_tracker import ExperimentTracker, ExperimentConfig, ExperimentRun

# Import constants module for easy access
from . import constants

__all__ = [
    # Version
    "__version__",

    # Core
    "PromptTemplate",
    "PromptVariant",
    "LLMResponse",
    "PromptDomain",
    "FormalityLevel",

    # Adapters
    "CulturalAdapter",
    "EnglishAdapter",
    "GermanAdapter",
    "SpanishAdapter",
    "get_adapter",

    # Evaluator
    "PromptEvaluator",

    # Providers
    "AbstractLLMProvider",
    "GenerationConfig",
    "AnthropicProvider",
    "MockAnthropicProvider",
    "OpenAIProvider",
    "MockOpenAIProvider",
    "LocalLLMProvider",

    # Storage
    "CacheManager",
    "ExperimentTracker",
    "ExperimentConfig",
    "ExperimentRun",

    # Constants
    "constants",
]
