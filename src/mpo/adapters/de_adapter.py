"""
German cultural adapter.

Implements German-specific cultural norms and communication patterns.
"""

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, PromptVariant, FormalityLevel


class GermanAdapter(CulturalAdapter):
    """
    German cultural adapter.

    Implements German-specific cultural norms:
    - Sie (formal) vs. du (casual) pronoun usage
    - High directness preference (Germans value precision and clarity)
    - Structured communication (clear opening, body, closing)
    - Professional formality in business contexts
    """

    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        """Apply German cultural transformations."""
        content = template.content
        notes = []

        # Get German-specific formality markers
        greeting = self._get_greeting(formality)
        closing = self._get_closing(formality)
        pronoun = self._get_pronoun(formality)

        # German transformation strategy
        adapted_parts = []

        # 1. Add appropriate greeting
        if greeting:
            adapted_parts.append(greeting)
            notes.append(f"Added German greeting: '{greeting}'")

        # 2. Add context-setting (Germans value clear structure)
        if formality == FormalityLevel.FORMAL:
            adapted_parts.append("\nIch möchte Sie um Folgendes bitten:")
            notes.append("Added formal request preamble")
        elif formality == FormalityLevel.NEUTRAL:
            adapted_parts.append("\nIch bitte um Folgendes:")
            notes.append("Added neutral request preamble")
        else:  # casual
            adapted_parts.append("\nKurze Frage:")
            notes.append("Added casual introduction")

        # 3. Add the main content (will be translated by evaluator)
        adapted_parts.append(f"\n{content}")
        notes.append(f"Content to be translated to German (using {pronoun} form)")

        # 4. Add appropriate closing
        if closing:
            adapted_parts.append(f"\n\n{closing}")
            notes.append(f"Added German closing: '{closing}'")

        # Germans value directness - no excessive politeness padding
        directness_note = "Maintained high directness (German cultural preference)"
        notes.append(directness_note)

        adapted_content = "".join(adapted_parts)

        return PromptVariant(
            template_id=template.id,
            language=self.language_code,
            formality=formality,
            adapted_content=adapted_content,
            adaptation_notes="; ".join(notes)
        )
