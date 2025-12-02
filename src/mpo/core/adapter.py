"""
Cultural adaptation strategies for different languages.

This module implements the core cultural adaptation logic base class.
Language-specific implementations are in the adapters/ package.
"""

from abc import ABC, abstractmethod
from typing import Dict
from .prompt import PromptTemplate, PromptVariant, FormalityLevel


class CulturalAdapter(ABC):
    """
    Abstract base class for language-specific cultural adaptations.

    Each language subclass implements cultural transformation rules based on:
    - Formality markers (pronouns, honorifics)
    - Directness preferences (context-setting, preambles)
    - Structural conventions (greetings, closings, transitions)
    """

    def __init__(self, config: Dict):
        """
        Initialize adapter with language-specific configuration.

        Args:
            config: Cultural parameters from languages.yaml
        """
        self.config = config
        self.language_code = config.get("code", "unknown")
        self.language_name = config.get("name", "Unknown")

    @abstractmethod
    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        """
        Apply cultural transformations to a prompt template.

        Args:
            template: Base prompt template to adapt
            formality: Desired formality level

        Returns:
            PromptVariant with culturally-appropriate modifications
        """
        pass

    def _get_greeting(self, formality: FormalityLevel) -> str:
        """Get culturally-appropriate greeting for formality level."""
        formality_params = self.config.get("cultural_params", {}).get("formality_levels", {})
        return formality_params.get(formality.value, {}).get("greeting", "")

    def _get_closing(self, formality: FormalityLevel) -> str:
        """Get culturally-appropriate closing for formality level."""
        formality_params = self.config.get("cultural_params", {}).get("formality_levels", {})
        return formality_params.get(formality.value, {}).get("closing", "")

    def _get_pronoun(self, formality: FormalityLevel) -> str:
        """Get appropriate pronoun (e.g., Sie/du in German) for formality level."""
        formality_params = self.config.get("cultural_params", {}).get("formality_levels", {})
        return formality_params.get(formality.value, {}).get("pronoun", "")
