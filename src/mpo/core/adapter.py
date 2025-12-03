"""
Cultural adaptation strategies for different languages.

This module implements the core cultural adaptation logic base class.
Language-specific implementations are in the adapters/ package.

Supports hybrid adaptation: programmatic (rule-based) + LLM-based refinement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import logging

from .prompt import PromptTemplate, PromptVariant, FormalityLevel, PromptDomain
from .adaptation_config import AdaptationStrategy, LLMAdaptationConfig
from ..providers.base import AbstractLLMProvider, GenerationConfig

logger = logging.getLogger(__name__)


class CulturalAdapter(ABC):
    """
    Abstract base class for language-specific cultural adaptations.

    Each language subclass implements cultural transformation rules based on:
    - Formality markers (pronouns, honorifics)
    - Directness preferences (context-setting, preambles)
    - Structural conventions (greetings, closings, transitions)
    """

    def __init__(self, config: Dict, provider: Optional[AbstractLLMProvider] = None):
        """
        Initialize adapter with language-specific configuration.

        Args:
            config: Cultural parameters from languages.yaml
            provider: Optional LLM provider for hybrid adaptation
        """
        self.config = config
        self.language_code = config.get("code", "unknown")
        self.language_name = config.get("name", "Unknown")
        self._provider = provider

        # Parse LLM adaptation configuration
        llm_config_data = config.get('llm_adaptation', {})
        self.llm_adaptation_config = (
            LLMAdaptationConfig.from_dict(llm_config_data)
            if llm_config_data.get('enabled', False)
            else None
        )

    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        """
        Apply cultural transformations to a prompt template.

        Two-phase hybrid adaptation:
        1. Phase 1 (Programmatic): Apply rule-based structural adaptations
        2. Phase 2 (LLM - Optional): Apply nuanced cultural refinement

        Args:
            template: Base prompt template to adapt
            formality: Desired formality level

        Returns:
            PromptVariant with culturally-appropriate modifications
        """
        # Phase 1: Always apply programmatic adaptations
        programmatic_output = self._apply_programmatic_adaptations(template, formality)

        # Phase 2: Apply LLM refinement if configured and available
        if self._should_use_llm_adaptation():
            try:
                final_output = self._apply_llm_adaptation(
                    programmatic_output, template, formality
                )
                adaptation_notes = self._build_adaptation_notes(
                    "hybrid", template, formality
                )
                logger.info(f"Successfully applied hybrid adaptation for {self.language_code}")
            except Exception as e:
                # Fallback to programmatic if LLM fails
                logger.warning(
                    f"LLM adaptation failed for {self.language_code}: {e}. "
                    f"Falling back to programmatic only."
                )
                final_output = programmatic_output
                adaptation_notes = self._build_adaptation_notes(
                    "programmatic_fallback", template, formality
                )
        else:
            final_output = programmatic_output
            adaptation_notes = self._build_adaptation_notes(
                "programmatic", template, formality
            )

        return PromptVariant(
            template_id=template.id,
            language=self.language_code,
            formality=formality,
            adapted_content=final_output,
            adaptation_notes=adaptation_notes,
            timestamp=datetime.now().isoformat(),
            metadata={"strategy": self._get_strategy_name()}
        )

    def _build_adaptation_notes(
        self, mode: str, template: PromptTemplate, formality: FormalityLevel
    ) -> str:
        """Build adaptation notes describing what was done."""
        if mode == "hybrid":
            return (
                f"Hybrid adaptation ({self.language_code}): "
                f"Programmatic structure + LLM cultural refinement. "
                f"Domain: {template.domain.value}, Formality: {formality.value}"
            )
        elif mode == "programmatic_fallback":
            return (
                f"Programmatic-only adaptation ({self.language_code}): "
                f"LLM refinement failed, using rule-based only. "
                f"Domain: {template.domain.value}, Formality: {formality.value}"
            )
        else:  # programmatic
            return (
                f"Programmatic-only adaptation ({self.language_code}): "
                f"Rule-based cultural transformations. "
                f"Domain: {template.domain.value}, Formality: {formality.value}"
            )

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

    def _should_use_llm_adaptation(self) -> bool:
        """
        Check if LLM-based adaptation should be used.

        Returns:
            True if LLM adaptation is configured, enabled, and provider is available
        """
        return (
            self.llm_adaptation_config is not None and
            self.llm_adaptation_config.enabled and
            self._provider is not None
        )

    def _get_strategy_name(self) -> str:
        """Get the current adaptation strategy name."""
        if self.llm_adaptation_config:
            return self.llm_adaptation_config.strategy.value
        return AdaptationStrategy.PROGRAMMATIC_ONLY.value

    @abstractmethod
    def _apply_programmatic_adaptations(
        self, template: PromptTemplate, formality: FormalityLevel
    ) -> str:
        """
        Apply deterministic structural adaptations (Phase 1).

        This method implements rule-based cultural adaptations:
        - Greetings and closings
        - Formality markers (pronouns)
        - Structural preambles

        Args:
            template: Base prompt template
            formality: Desired formality level

        Returns:
            Partially adapted prompt with cultural scaffolding

        Note:
            To be implemented by subclasses with existing adapt() logic.
        """
        pass

    def _apply_llm_adaptation(
        self,
        programmatic_output: str,
        template: PromptTemplate,
        formality: FormalityLevel
    ) -> str:
        """
        Apply LLM-based cultural refinement (Phase 2).

        Uses the LLM provider to apply nuanced cultural transformations:
        - Tone adjustment
        - Argumentation pattern adaptation
        - Idiomatic expression
        - Translation with cultural awareness

        Args:
            programmatic_output: Output from Phase 1 (programmatic adaptations)
            template: Original prompt template (for context)
            formality: Desired formality level

        Returns:
            Fully culturally adapted prompt

        Raises:
            Exception: If LLM call fails (caller should catch and fallback)
        """
        llm_prompt = self._build_llm_adaptation_prompt(
            programmatic_output, template, formality
        )

        config = GenerationConfig(
            temperature=self.llm_adaptation_config.temperature,
            max_tokens=self.llm_adaptation_config.max_tokens
        )

        logger.debug(f"Calling LLM for {self.language_code} adaptation with temperature={config.temperature}")
        result = self._provider.generate(llm_prompt, config)
        return result['content'].strip()

    @abstractmethod
    def _build_llm_adaptation_prompt(
        self,
        programmatic_output: str,
        template: PromptTemplate,
        formality: FormalityLevel
    ) -> str:
        """
        Build prompt for LLM cultural refinement.

        Constructs a meta-prompt that instructs the LLM how to refine the
        programmatic adaptation with language-specific cultural nuances.

        Args:
            programmatic_output: Output from Phase 1
            template: Original template (for domain/context)
            formality: Desired formality level

        Returns:
            LLM instruction prompt (system + user prompt)

        Note:
            To be implemented by subclasses with language-specific instructions.
        """
        pass
