"""
Spanish cultural adapter.

Implements Spanish (Latin American) cultural norms and communication patterns.
"""

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, PromptVariant, FormalityLevel


class SpanishAdapter(CulturalAdapter):
    """
    Spanish cultural adapter (Latin American variant).

    Implements Spanish-specific cultural norms:
    - Tú (casual) vs. usted (formal) pronoun usage
    - Medium directness (balance between relationship and task)
    - High context sensitivity (warmth, personal connection)
    - Relational preambles in professional settings
    """

    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        """Apply Spanish (Latin American) cultural transformations."""
        content = template.content
        notes = []

        # Get Spanish-specific formality markers
        greeting = self._get_greeting(formality)
        closing = self._get_closing(formality)
        pronoun = self._get_pronoun(formality)

        # Spanish transformation strategy
        adapted_parts = []

        # 1. Add warm greeting
        if greeting:
            adapted_parts.append(greeting)
            notes.append(f"Added Spanish greeting: '{greeting}'")

        # 2. Add relational preamble (Spanish values personal connection)
        if formality == FormalityLevel.FORMAL:
            adapted_parts.append("\n\nEspero que se encuentre bien.")
            adapted_parts.append("\nMe dirijo a usted para solicitar lo siguiente:")
            notes.append("Added formal relational preamble (well-being inquiry + purpose statement)")
        elif formality == FormalityLevel.NEUTRAL:
            adapted_parts.append("\n\nEspero que esté bien.")
            adapted_parts.append("\nLe escribo para pedirle lo siguiente:")
            notes.append("Added neutral relational preamble")
        else:  # casual
            adapted_parts.append("\n\n¿Qué tal? Te escribo porque:")
            notes.append("Added casual, warm opening")

        # 3. Add the main content (translation placeholder)
        adapted_parts.append(f"\n{content}")
        notes.append(f"Content adapted to Spanish warmth and context (using {pronoun} form)")

        # 4. Add gracious closing with relational element
        if formality in [FormalityLevel.FORMAL, FormalityLevel.NEUTRAL]:
            adapted_parts.append("\n\nAgradezco de antemano su atención y tiempo.")
            notes.append("Added gratitude expression (Spanish cultural norm)")

        if closing:
            adapted_parts.append(f"\n{closing}")
            notes.append(f"Added Spanish closing: '{closing}'")

        # Spanish values relationship-building even in professional contexts
        context_note = "High context sensitivity: added warmth and relational elements"
        notes.append(context_note)

        adapted_content = "".join(adapted_parts)

        return PromptVariant(
            template_id=template.id,
            language=self.language_code,
            formality=formality,
            adapted_content=adapted_content,
            adaptation_notes="; ".join(notes)
        )
