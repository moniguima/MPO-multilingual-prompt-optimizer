"""
Core prompt template and variant data structures.

This module defines the foundational classes for managing prompts and their
culturally-adapted variants across different languages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class PromptDomain(Enum):
    """Categories of prompt use cases."""
    BUSINESS = "business"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    PERSUASIVE = "persuasive"
    INSTRUCTIONAL = "instructional"


class FormalityLevel(Enum):
    """Formality levels for cultural adaptation."""
    CASUAL = "casual"
    NEUTRAL = "neutral"
    FORMAL = "formal"


@dataclass
class PromptTemplate:
    """
    Base prompt template in English with metadata.

    Attributes:
        id: Unique identifier for the prompt
        content: The actual prompt text in English
        domain: Category of the prompt (business, technical, etc.)
        placeholders: Dictionary of placeholder keys and their default values
        description: Human-readable description of the prompt's purpose
        metadata: Additional custom metadata
    """
    id: str
    content: str
    domain: PromptDomain
    placeholders: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """
        Render the prompt with placeholder substitutions.

        Args:
            **kwargs: Key-value pairs for placeholder substitution

        Returns:
            Rendered prompt string with placeholders replaced
        """
        rendered = self.content
        # Use provided values, fall back to defaults
        values = {**self.placeholders, **kwargs}
        for key, value in values.items():
            rendered = rendered.replace(f"{{{key}}}", str(value))
        return rendered


@dataclass
class PromptVariant:
    """
    Culturally adapted version of a prompt template.

    Attributes:
        template_id: ID of the source PromptTemplate
        language: Target language code (e.g., 'de', 'es')
        formality: Formality level applied
        adapted_content: The culturally adapted prompt text
        adaptation_notes: Explanation of what cultural changes were made
        timestamp: When this adaptation was created
        metadata: Additional variant-specific metadata
    """
    template_id: str
    language: str
    formality: FormalityLevel
    adapted_content: str
    adaptation_notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "template_id": self.template_id,
            "language": self.language,
            "formality": self.formality.value,
            "adapted_content": self.adapted_content,
            "adaptation_notes": self.adaptation_notes,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PromptVariant":
        """Create PromptVariant from dictionary."""
        return cls(
            template_id=data["template_id"],
            language=data["language"],
            formality=FormalityLevel(data["formality"]),
            adapted_content=data["adapted_content"],
            adaptation_notes=data.get("adaptation_notes", ""),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class LLMResponse:
    """
    Response from an LLM for a given prompt variant.

    Attributes:
        variant_id: Identifier linking to the PromptVariant
        content: The LLM's response text
        model: Model identifier (e.g., 'claude-sonnet-4')
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        timestamp: When this response was generated
        metadata: Additional response metadata (temperature, etc.)
    """
    variant_id: str
    content: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "variant_id": self.variant_id,
            "content": self.content,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LLMResponse":
        """Create LLMResponse from dictionary."""
        return cls(
            variant_id=data["variant_id"],
            content=data["content"],
            model=data["model"],
            tokens_input=data.get("tokens_input", 0),
            tokens_output=data.get("tokens_output", 0),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {})
        )
