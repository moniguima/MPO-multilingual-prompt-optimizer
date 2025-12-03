"""
English cultural adapter.

English serves as the baseline language with minimal transformations.
"""

from typing import Optional

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, FormalityLevel
from ..providers.base import AbstractLLMProvider


class EnglishAdapter(CulturalAdapter):
    """
    English baseline adapter (minimal transformation).

    English serves as the baseline language with slight adjustments for formality
    but no major structural changes.
    """

    def __init__(self, config: dict, provider: Optional[AbstractLLMProvider] = None):
        """Initialize English adapter with optional LLM provider."""
        super().__init__(config, provider)

    def _apply_programmatic_adaptations(self, template: PromptTemplate, formality: FormalityLevel) -> str:
        """Apply minimal English cultural adaptations (Phase 1)."""
        content = template.content

        # English is baseline - minimal changes
        if formality == FormalityLevel.FORMAL:
            # Add formal markers if not present
            if not content.startswith(("Dear", "Hello", "Greetings")):
                content = "Please " + content.lower()[0] + content[1:]
        elif formality == FormalityLevel.CASUAL:
            # Make more conversational
            if content.startswith("Please "):
                content = content[7:]  # Remove "Please "

        return content

    def _build_llm_adaptation_prompt(
        self,
        programmatic_output: str,
        template: PromptTemplate,
        formality: FormalityLevel
    ) -> str:
        """
        Build English-specific LLM adaptation prompt (Phase 2).

        Refines tone, style, and domain-appropriateness for American English
        communication while maintaining the existing structure.

        Returns:
            System + user prompt for LLM refinement
        """
        system_prompt = f"""You are an American English communication expert. Refine the provided text to match American English professional communication norms.

KEY AMERICAN ENGLISH COMMUNICATION PRINCIPLES:
- Directness: Get to the point quickly. Americans value efficiency and clarity.
- Task-oriented: Focus on objectives and outcomes rather than process or relationship.
- Casual professionalism: Professional yet approachable. Avoid overly formal language.
- Action-focused: Use active voice and clear calls-to-action.
- Conciseness: Respect time - be brief but complete.
- Individualism: Emphasize personal responsibility and individual contributions.

TASK:
1. Maintain the core message and intent
2. Adjust tone to match {formality.value} formality level:
   - Formal: Professional but not stiff. Clear and respectful.
   - Neutral: Standard professional communication. Balanced and clear.
   - Casual: Conversational yet professional. Friendly and approachable.
3. Ensure language is appropriate for {template.domain.value} domain
4. Keep all {{placeholder}} variables unchanged in {{curly braces}}
5. Use active voice where possible
6. Remove unnecessary words or phrases
7. Ensure American English spelling and idioms (not British)

Context:
- Domain: {template.domain.value}
- Formality: {formality.value}
- Audience: American English speakers"""

        user_prompt = f"""Refine this text for American English professional communication:

INPUT:
{programmatic_output}

OUTPUT (refined for tone, clarity, and domain appropriateness):"""

        return system_prompt + "\n\n" + user_prompt
