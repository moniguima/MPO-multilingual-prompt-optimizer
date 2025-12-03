"""
German cultural adapter.

Implements German-specific cultural norms and communication patterns.

Supports hybrid adaptation: programmatic structure + LLM cultural refinement.
"""

from typing import Optional

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, FormalityLevel
from ..providers.base import AbstractLLMProvider


class GermanAdapter(CulturalAdapter):
    """
    German cultural adapter.

    Implements German-specific cultural norms:
    - Sie (formal) vs. du (casual) pronoun usage
    - High directness preference (Germans value precision and clarity)
    - Structured communication (clear opening, body, closing)
    - Professional formality in business contexts

    Supports hybrid mode: programmatic scaffolding + LLM refinement.
    """

    def __init__(self, config: dict, provider: Optional[AbstractLLMProvider] = None):
        """Initialize German adapter with optional LLM provider."""
        super().__init__(config, provider)

    def _apply_programmatic_adaptations(self, template: PromptTemplate, formality: FormalityLevel) -> str:
        """
        Apply German programmatic structural adaptations (Phase 1).

        Adds German cultural scaffolding:
        - Greeting based on formality
        - Context-setting preamble
        - Closing phrase

        Returns:
            Partially adapted prompt with German structure
        """
        content = template.content

        # Get German-specific formality markers
        greeting = self._get_greeting(formality)
        closing = self._get_closing(formality)

        # German transformation strategy
        adapted_parts = []

        # 1. Add appropriate greeting
        if greeting:
            adapted_parts.append(greeting)

        # 2. Add context-setting (Germans value clear structure)
        if formality == FormalityLevel.FORMAL:
            adapted_parts.append("\nIch möchte Sie um Folgendes bitten:")
        elif formality == FormalityLevel.NEUTRAL:
            adapted_parts.append("\nIch bitte um Folgendes:")
        else:  # casual
            adapted_parts.append("\nKurze Frage:")

        # 3. Add the main content (will be refined by LLM if enabled)
        adapted_parts.append(f"\n{content}")

        # 4. Add appropriate closing
        if closing:
            adapted_parts.append(f"\n\n{closing}")

        return "".join(adapted_parts)

    def _build_llm_adaptation_prompt(
        self,
        programmatic_output: str,
        template: PromptTemplate,
        formality: FormalityLevel
    ) -> str:
        """
        Build German-specific LLM adaptation prompt (Phase 2).

        Instructs the LLM to refine the programmatic output with German
        cultural nuances while preserving the structure.

        Returns:
            System + user prompt for LLM cultural refinement
        """
        pronoun = self._get_pronoun(formality)

        system_prompt = f"""You are a German cultural communication expert. Transform the provided text to match German cultural norms while preserving the existing structure.

KEY GERMAN CULTURAL PRINCIPLES:
- Directness (Sachlichkeit): Germans value clarity and precision. Be explicit and unambiguous.
- Low-context communication: Provide necessary context but focus on facts over relationship-building.
- Structured format: Clear opening → body → closing.
- Formality: Use {pronoun} form consistently throughout.
- Efficiency: No unnecessary politeness padding or small talk.
- Deductive reasoning: State the point first, then provide supporting details.

TASK:
1. Preserve the greeting and closing lines EXACTLY as written (already culturally adapted)
2. Translate all English content to German
3. Apply German directness and precision (Sachlichkeit) to the tone
4. Maintain deductive argumentation pattern (point first, then evidence)
5. Keep all {{placeholder}} variables unchanged in {{curly braces}}
6. Use {pronoun} form consistently
7. Avoid excessive politeness - Germans prefer clarity over courtesy

Context:
- Domain: {template.domain.value}
- Formality: {formality.value}
- Pronoun: {pronoun}"""

        user_prompt = f"""Transform this partially adapted prompt to fully German-appropriate communication:

INPUT (with German scaffolding):
{programmatic_output}

OUTPUT (fully culturally adapted German with Sachlichkeit):"""

        return system_prompt + "\n\n" + user_prompt
