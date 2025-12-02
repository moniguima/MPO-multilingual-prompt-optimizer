"""
Abstract base interface for LLM providers.

This module defines the contract that all LLM providers must implement,
allowing easy swapping between different models (Claude, GPT-4, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for LLM text generation."""
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1.0
    stop_sequences: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for API calls."""
        config = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
        if self.stop_sequences:
            config["stop_sequences"] = self.stop_sequences
        return config


class AbstractLLMProvider(ABC):
    """
    Abstract interface for LLM API providers.

    All provider implementations must support:
    1. Text generation from prompts
    2. Text embeddings for semantic similarity
    3. Token counting for cost tracking
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize LLM provider.

        Args:
            api_key: API authentication key (if None, read from environment)
            model_name: Specific model identifier
        """
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict:
        """
        Generate text response from prompt.

        Args:
            prompt: Input prompt text
            config: Generation configuration (temperature, max_tokens, etc.)
            **kwargs: Provider-specific additional parameters

        Returns:
            Dictionary containing:
            {
                "content": str,           # Generated text
                "tokens_input": int,      # Input token count
                "tokens_output": int,     # Output token count
                "model": str,             # Model identifier
                "timestamp": str,         # ISO timestamp
                "metadata": Dict          # Provider-specific metadata
            }

        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (provider-specific tokenization).

        Args:
            text: Input text

        Returns:
            Number of tokens

        Raises:
            Exception: If tokenization fails
        """
        pass

    def is_available(self) -> bool:
        """
        Check if provider is properly configured and available.

        Returns:
            True if API key is set and provider is ready, False otherwise
        """
        return self.api_key is not None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g., 'anthropic', 'openai')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model identifier for this provider."""
        pass
