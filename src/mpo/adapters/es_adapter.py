"""
Spanish cultural adapter.

Implements Spanish (Latin American) cultural norms and communication patterns.
"""

from typing import Optional

from ..core.adapter import CulturalAdapter
from ..core.prompt import PromptTemplate, FormalityLevel
from ..providers.base import AbstractLLMProvider


class SpanishAdapter(CulturalAdapter):
    """
    Spanish cultural adapter (Latin American variant).

    Implements Spanish-specific cultural norms:
    - Tú (casual) vs. usted (formal) pronoun usage
    - Medium directness (balance between relationship and task)
    - High context sensitivity (warmth, personal connection)
    - Relational preambles in professional settings
    """

    def __init__(self, config: dict, provider: Optional[AbstractLLMProvider] = None):
        """Initialize Spanish adapter with optional LLM provider."""
        super().__init__(config, provider)

    def _apply_programmatic_adaptations(self, template: PromptTemplate, formality: FormalityLevel) -> str:
        """Apply Spanish (Latin American) programmatic adaptations (Phase 1)."""
        content = template.content

        # Get Spanish-specific formality markers
        greeting = self._get_greeting(formality)
        closing = self._get_closing(formality)

        # Spanish transformation strategy
        adapted_parts = []

        # 1. Add warm greeting
        if greeting:
            adapted_parts.append(greeting)

        # 2. Add relational preamble (Spanish values personal connection)
        if formality == FormalityLevel.FORMAL:
            adapted_parts.append("\n\nEspero que se encuentre bien.")
            adapted_parts.append("\nMe dirijo a usted para solicitar lo siguiente:")
        elif formality == FormalityLevel.NEUTRAL:
            adapted_parts.append("\n\nEspero que esté bien.")
            adapted_parts.append("\nLe escribo para pedirle lo siguiente:")
        else:  # casual
            adapted_parts.append("\n\n¿Qué tal? Te escribo porque:")

        # 3. Add the main content (will be refined by LLM if enabled)
        adapted_parts.append(f"\n{content}")

        # 4. Add gracious closing with relational element
        if formality in [FormalityLevel.FORMAL, FormalityLevel.NEUTRAL]:
            adapted_parts.append("\n\nAgradezco de antemano su atención y tiempo.")

        if closing:
            adapted_parts.append(f"\n{closing}")

        return "".join(adapted_parts)

    def _build_llm_adaptation_prompt(
        self,
        programmatic_output: str,
        template: PromptTemplate,
        formality: FormalityLevel
    ) -> str:
        """
        Build Spanish-specific LLM adaptation prompt (Phase 2).

        Instructs the LLM to refine the programmatic output with Latin American
        Spanish cultural nuances while preserving the structure.

        Returns:
            System + user prompt for LLM cultural refinement
        """
        pronoun = self._get_pronoun(formality)

        system_prompt = f"""You are a Latin American Spanish cultural communication expert. Transform the provided text to match Spanish-speaking cultural norms while preserving the existing structure.

KEY LATIN AMERICAN SPANISH CULTURAL PRINCIPLES:
- Relationship-first (confianza): Build personal connection before business transactions.
- High-context communication: Provide relational preambles and context before requests.
- Warmth (calidez): Even formal communication includes personal elements and well-being inquiries.
- Indirect requests: Soften requests to show respect - avoid abruptness.
- Gratitude (gratitud): Express thanks proactively and generously.
- Collectivism: Emphasize team, community, and relational benefits.

TASK:
1. Preserve the greeting, relational preambles, and closing lines EXACTLY as written (already culturally adapted)
2. Translate all English content to Spanish
3. Apply Latin American warmth and relationship-building tone
4. Maintain inductive argumentation pattern (context first, then point)
5. Keep all {{placeholder}} variables unchanged in {{curly braces}}
6. Use {pronoun} form consistently
7. Add softening phrases for requests (e.g., "si fuera posible", "agradecería mucho")
8. Ensure language feels natural for Latin American audience (not Castilian Spanish)

Context:
- Domain: {template.domain.value}
- Formality: {formality.value}
- Pronoun: {pronoun}
- Region: Latin America (prioritize warmth over Iberian directness)"""

        user_prompt = f"""Transform this partially adapted prompt to fully Latin American Spanish-appropriate communication:

INPUT (with Spanish scaffolding):
{programmatic_output}

OUTPUT (fully culturally adapted Spanish with warmth and relationship focus):"""

        return system_prompt + "\n\n" + user_prompt
