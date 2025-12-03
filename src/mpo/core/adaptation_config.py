"""
Configuration classes for hybrid adaptation system.

Defines strategies and configuration for combining programmatic and LLM-based
cultural adaptations.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class AdaptationStrategy(Enum):
    """Strategy for applying cultural adaptations."""

    PROGRAMMATIC_ONLY = "programmatic_only"  # Rule-based only (fast, deterministic, free)
    HYBRID_SEQUENTIAL = "hybrid_sequential"   # Programmatic → LLM refinement (best quality)
    LLM_ONLY = "llm_only"                     # Full LLM transformation (experimental)


@dataclass
class LLMAdaptationConfig:
    """Configuration for LLM-based cultural adaptation."""

    enabled: bool
    strategy: AdaptationStrategy
    transformation_instructions: Dict[str, Any]
    llm_system_prompt: str
    temperature: float = 0.3  # Low for consistency
    max_tokens: int = 2048

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMAdaptationConfig':
        """
        Parse LLM adaptation configuration from YAML dictionary.

        Args:
            data: Dictionary from languages.yaml llm_adaptation section

        Returns:
            LLMAdaptationConfig instance

        Example:
            >>> config_dict = {
            ...     'enabled': True,
            ...     'strategy': 'hybrid_sequential',
            ...     'transformation_instructions': {...},
            ...     'llm_system_prompt': '...',
            ...     'temperature': 0.3
            ... }
            >>> config = LLMAdaptationConfig.from_dict(config_dict)
        """
        return cls(
            enabled=data.get('enabled', False),
            strategy=AdaptationStrategy(data.get('strategy', 'hybrid_sequential')),
            transformation_instructions=data.get('transformation_instructions', {}),
            llm_system_prompt=data.get('llm_system_prompt', ''),
            temperature=data.get('temperature', 0.3),
            max_tokens=data.get('max_tokens', 2048)
        )
