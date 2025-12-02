"""
Prompt evaluation orchestration.

This module coordinates the evaluation process: adapting prompts, sending to LLMs,
and collecting responses for analysis.
"""

from typing import Dict, List, Optional
from datetime import datetime

from .prompt import PromptTemplate, PromptVariant, LLMResponse, FormalityLevel
from ..adapters import get_adapter
from ..providers.base import AbstractLLMProvider, GenerationConfig
from ..constants import LANGUAGE_NAMES, get_formality_guidance


class PromptEvaluator:
    """
    Orchestrates prompt evaluation across languages and formality levels.

    Responsibilities:
    1. Adapt prompts using cultural adapters
    2. Send adapted prompts to LLM providers
    3. Collect and store responses
    4. Track experiment metadata
    """

    def __init__(
        self,
        provider: AbstractLLMProvider,
        language_configs: Dict[str, Dict]
    ):
        """
        Initialize evaluator.

        Args:
            provider: LLM provider instance
            language_configs: Dictionary of language configurations from languages.yaml
        """
        self.provider = provider
        self.language_configs = language_configs
        self._adapters = {}

    def _get_adapter(self, language_code: str):
        """Get or create cached adapter for language."""
        if language_code not in self._adapters:
            if language_code not in self.language_configs:
                raise ValueError(f"No configuration found for language: {language_code}")
            config = self.language_configs[language_code]
            self._adapters[language_code] = get_adapter(language_code, config)
        return self._adapters[language_code]

    def adapt_prompt(
        self,
        template: PromptTemplate,
        language: str,
        formality: FormalityLevel
    ) -> PromptVariant:
        """
        Adapt a prompt template for a specific language and formality level.

        Args:
            template: Base prompt template
            language: Target language code
            formality: Desired formality level

        Returns:
            PromptVariant with cultural adaptations
        """
        adapter = self._get_adapter(language)
        return adapter.adapt(template, formality)

    def evaluate_variant(
        self,
        variant: PromptVariant,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """
        Evaluate a prompt variant by sending to LLM.

        Args:
            variant: Culturally adapted prompt variant
            config: Generation configuration

        Returns:
            LLMResponse with model output and metadata
        """
        if config is None:
            config = GenerationConfig()

        # Wrap the adapted content with instruction to generate the content
        # This prevents the LLM from responding as an assistant
        # Map language codes to full names
        target_language = LANGUAGE_NAMES.get(variant.language, variant.language)

        # Build formality instruction
        formality_note = get_formality_guidance(variant.formality.value)

        # Build example for few-shot learning
        example_input = """Hola

¿Qué tal? Te escribo porque:
I need your help with something urgent.

Gracias
Saludos"""

        example_output = """Hola

¿Qué tal? Te escribo porque:
Necesito tu ayuda con algo urgente.

Gracias
Saludos"""

        instructed_prompt = f"""Task: Translate ONLY English sentences to {target_language}. Copy all {target_language} text exactly as-is, including line breaks.

Example:
Input:
{example_input}

Output:
{example_output}

Now translate this text ({formality_note}):
Input:
{variant.adapted_content}

Output:"""

        # Generate response from LLM
        result = self.provider.generate(instructed_prompt, config)

        # Create structured response object
        variant_id = f"{variant.template_id}_{variant.language}_{variant.formality.value}"

        response = LLMResponse(
            variant_id=variant_id,
            content=result["content"],
            model=result["model"],
            tokens_input=result["tokens_input"],
            tokens_output=result["tokens_output"],
            timestamp=result["timestamp"],
            metadata={
                **result.get("metadata", {}),
                "language": variant.language,
                "formality": variant.formality.value,
                "adaptation_notes": variant.adaptation_notes
            }
        )

        return response

    def evaluate_template_comprehensive(
        self,
        template: PromptTemplate,
        languages: List[str],
        formality_levels: List[FormalityLevel],
        config: Optional[GenerationConfig] = None
    ) -> Dict[str, Dict[str, LLMResponse]]:
        """
        Comprehensively evaluate a template across multiple languages and formality levels.

        Args:
            template: Base prompt template
            languages: List of language codes to test
            formality_levels: List of formality levels to test
            config: Generation configuration

        Returns:
            Nested dictionary: {language: {formality: LLMResponse}}
        """
        results = {}

        for language in languages:
            results[language] = {}
            for formality in formality_levels:
                # Adapt prompt
                variant = self.adapt_prompt(template, language, formality)

                # Evaluate variant
                response = self.evaluate_variant(variant, config)

                results[language][formality.value] = response

        return results

    def batch_evaluate(
        self,
        templates: List[PromptTemplate],
        language: str,
        formality: FormalityLevel,
        config: Optional[GenerationConfig] = None
    ) -> List[LLMResponse]:
        """
        Evaluate multiple templates for a specific language and formality level.

        Args:
            templates: List of prompt templates
            language: Target language code
            formality: Formality level
            config: Generation configuration

        Returns:
            List of LLMResponse objects
        """
        responses = []

        for template in templates:
            variant = self.adapt_prompt(template, language, formality)
            response = self.evaluate_variant(variant, config)
            responses.append(response)

        return responses
