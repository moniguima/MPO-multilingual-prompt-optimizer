"""
English cultural adapter.

English serves as the baseline language with minimal transformations.
"""

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, PromptVariant, FormalityLevel


class EnglishAdapter(CulturalAdapter):
    """
    English baseline adapter (minimal transformation).

    English serves as the baseline language with slight adjustments for formality
    but no major structural changes.
    """

    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        """Apply minimal English cultural adaptations."""
        content = template.content
        notes = []

        # English is baseline - minimal changes
        if formality == FormalityLevel.FORMAL:
            # Add formal markers if not present
            if not content.startswith(("Dear", "Hello", "Greetings")):
                content = "Please " + content.lower()[0] + content[1:]
                notes.append("Added 'Please' for formal tone")
        elif formality == FormalityLevel.CASUAL:
            # Make more conversational
            if content.startswith("Please "):
                content = content[7:]  # Remove "Please "
                notes.append("Removed 'Please' for casual tone")

        return PromptVariant(
            template_id=template.id,
            language=self.language_code,
            formality=formality,
            adapted_content=content,
            adaptation_notes="; ".join(notes) if notes else "Baseline English, minimal adaptation"
        )
