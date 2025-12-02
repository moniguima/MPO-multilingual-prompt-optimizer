"""
Global constants for the Multilingual Prompt Optimizer.

This module centralizes all configuration constants used across the application,
including language codes, formality levels, system-wide defaults, and directory paths.
"""

import os
from pathlib import Path
from typing import Dict, List, Final

# ==============================================================================
# LANGUAGE CONSTANTS
# ==============================================================================

# Supported language codes
SUPPORTED_LANGUAGES: Final[List[str]] = ['en', 'de', 'es', 'fr']

# Language code to full name mapping
LANGUAGE_NAMES: Final[Dict[str, str]] = {
    'en': 'English',
    'de': 'German',
    'es': 'Spanish',
    'fr': 'French'
}

# Language code to native name mapping (for UI display)
LANGUAGE_NATIVE_NAMES: Final[Dict[str, str]] = {
    'en': 'English',
    'de': 'Deutsch',
    'es': 'Español',
    'fr': 'Français'
}

# ==============================================================================
# FORMALITY CONSTANTS
# ==============================================================================

# Supported formality levels (in order from casual to formal)
FORMALITY_LEVELS: Final[List[str]] = ['casual', 'neutral', 'formal']

# Formality level guidance for LLM generation
FORMALITY_GUIDANCE: Final[Dict[str, str]] = {
    'formal': 'Use professional, business-appropriate language. Avoid excessive politeness.',
    'neutral': 'Use standard professional language.',
    'casual': 'Use conversational, friendly language.'
}

# Formality level display names
FORMALITY_DISPLAY_NAMES: Final[Dict[str, str]] = {
    'casual': 'Casual',
    'neutral': 'Neutral',
    'formal': 'Formal'
}

# ==============================================================================
# MODEL CONFIGURATION CONSTANTS
# ==============================================================================

# Default token estimation (characters per token)
CHARS_PER_TOKEN_ESTIMATE: Final[int] = 4

# Default generation configuration
DEFAULT_MAX_TOKENS: Final[int] = 1000
DEFAULT_TEMPERATURE: Final[float] = 0.7

# ==============================================================================
# DIRECTORY PATHS
# ==============================================================================

# Base directories (can be overridden via environment variables)
CONFIG_DIR: Final[Path] = Path(os.getenv("MPO_CONFIG_DIR", "config"))
DATA_DIR: Final[Path] = Path(os.getenv("MPO_DATA_DIR", "data"))
CACHE_DIR: Final[Path] = Path(os.getenv("MPO_CACHE_DIR", "data/cache"))
REPORTS_DIR: Final[Path] = Path(os.getenv("MPO_REPORTS_DIR", "reports"))

# Derived directories
EXPERIMENTS_DIR: Final[Path] = DATA_DIR / "experiments"

# ==============================================================================
# CACHE CONFIGURATION
# ==============================================================================

# Cache directory name (deprecated - use CACHE_DIR instead)
CACHE_DIR_NAME: Final[str] = 'cache'

# Cache metadata filename
CACHE_METADATA_FILE: Final[str] = 'cache_metadata.json'

# ==============================================================================
# EXPERIMENT TRACKING
# ==============================================================================

# Experiments directory name
EXPERIMENTS_DIR_NAME: Final[str] = 'experiments'

# Experiment results filename pattern
EXPERIMENT_RESULTS_FILE: Final[str] = 'results.json'

# Experiment config filename
EXPERIMENT_CONFIG_FILE: Final[str] = 'config.json'

# ==============================================================================
# EVALUATION METRICS
# ==============================================================================

# Sentiment keywords for basic sentiment analysis
POSITIVE_SENTIMENT_KEYWORDS: Final[List[str]] = [
    'great', 'excellent', 'wonderful', 'fantastic', 'good',
    'happy', 'pleased', 'satisfied', 'delighted', 'glad'
]

NEGATIVE_SENTIMENT_KEYWORDS: Final[List[str]] = [
    'bad', 'poor', 'terrible', 'awful', 'horrible',
    'unhappy', 'disappointed', 'frustrated', 'angry', 'upset'
]

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_language_name(language_code: str) -> str:
    """
    Get the full English name for a language code.

    Args:
        language_code: ISO language code (e.g., 'en', 'de', 'es')

    Returns:
        Full English name of the language

    Raises:
        ValueError: If language code is not supported
    """
    if language_code not in LANGUAGE_NAMES:
        raise ValueError(
            f"Unsupported language code: {language_code}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    return LANGUAGE_NAMES[language_code]


def get_formality_guidance(formality_level: str) -> str:
    """
    Get the generation guidance for a formality level.

    Args:
        formality_level: Formality level ('casual', 'neutral', 'formal')

    Returns:
        Guidance string for LLM generation

    Raises:
        ValueError: If formality level is not supported
    """
    if formality_level not in FORMALITY_GUIDANCE:
        raise ValueError(
            f"Unsupported formality level: {formality_level}. "
            f"Supported levels: {', '.join(FORMALITY_LEVELS)}"
        )
    return FORMALITY_GUIDANCE[formality_level]


def validate_language_code(language_code: str) -> bool:
    """
    Check if a language code is supported.

    Args:
        language_code: ISO language code to validate

    Returns:
        True if supported, False otherwise
    """
    return language_code in SUPPORTED_LANGUAGES


def validate_formality_level(formality_level: str) -> bool:
    """
    Check if a formality level is supported.

    Args:
        formality_level: Formality level to validate

    Returns:
        True if supported, False otherwise
    """
    return formality_level in FORMALITY_LEVELS
