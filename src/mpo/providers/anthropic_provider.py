"""
Anthropic Claude API provider implementation.

This module wraps the Anthropic API for text generation and embeddings,
following the AbstractLLMProvider interface.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from anthropic import Anthropic
from .base import AbstractLLMProvider, GenerationConfig
from ..constants import CHARS_PER_TOKEN_ESTIMATE


class AnthropicProvider(AbstractLLMProvider):
    """
    Anthropic Claude API provider.

    Supports Claude models (Sonnet, Haiku) for text generation.
    Note: Anthropic doesn't provide embeddings API, so we use a fallback.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model_name: Model identifier (defaults to claude-sonnet-4)
        """
        super().__init__(api_key, model_name)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Set model
        self.model_name = model_name or self.default_model

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "anthropic"

    @property
    def default_model(self) -> str:
        """Return default Claude model."""
        return "claude-sonnet-4-20250514"

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict:
        """
        Generate text using Claude API.

        Args:
            prompt: Input prompt text
            config: Generation configuration
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            Dictionary with generated content and metadata
        """
        if config is None:
            config = GenerationConfig()

        # Prepare API parameters
        api_params = {
            "model": self.model_name,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Add stop sequences if provided
        if config.stop_sequences:
            api_params["stop_sequences"] = config.stop_sequences

        # Override with any additional kwargs
        api_params.update(kwargs)

        try:
            # Call Anthropic API
            response = self.client.messages.create(**api_params)

            # Extract content (Claude returns list of content blocks)
            content = response.content[0].text

            # Get token counts
            tokens_input = response.usage.input_tokens
            tokens_output = response.usage.output_tokens

            # Build response dictionary
            result = {
                "content": content,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "model": response.model,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence,
                    "provider": self.provider_name,
                    "config": config.to_dict()
                }
            }

            return result

        except Exception as e:
            raise Exception(f"Anthropic API call failed: {str(e)}")

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text.

        Note: Anthropic doesn't provide embeddings API. This is a placeholder
        that could use Voyage AI (Anthropic's recommended embeddings provider)
        or return a simple hash-based representation for demo purposes.

        Args:
            text: Input text

        Returns:
            Embedding vector (placeholder implementation)

        Raises:
            NotImplementedError: Anthropic doesn't provide native embeddings
        """
        # For MVP, we'll raise NotImplementedError
        # In production, integrate with Voyage AI or OpenAI embeddings
        raise NotImplementedError(
            "Anthropic doesn't provide embeddings API. "
            "Consider using Voyage AI or OpenAI embeddings for semantic similarity."
        )

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using Anthropic's tokenization.

        Note: Anthropic's Python SDK doesn't expose tokenization directly.
        This is an approximate implementation.

        Args:
            text: Input text

        Returns:
            Approximate token count (rough estimate: ~4 chars per token)
        """
        # Rough approximation using constant
        # More accurate: use tiktoken or Anthropic's tokenization if available
        return len(text) // CHARS_PER_TOKEN_ESTIMATE

    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        return self.api_key is not None

    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        models_info = {
            "claude-sonnet-4-20250514": {
                "name": "Claude Sonnet 4",
                "context_window": 200000,
                "max_output": 8192,
                "cost_input_per_m": 3.00,
                "cost_output_per_m": 15.00
            },
            "claude-haiku-4-20250514": {
                "name": "Claude Haiku 4",
                "context_window": 200000,
                "max_output": 8192,
                "cost_input_per_m": 0.80,
                "cost_output_per_m": 4.00
            }
        }

        return models_info.get(
            self.model_name,
            {"name": self.model_name, "info": "Unknown model"}
        )


class MockAnthropicProvider(AbstractLLMProvider):
    """
    Mock Anthropic provider for testing without API calls.

    Returns predefined responses based on prompt patterns.
    """

    def __init__(
        self,
        api_key: Optional[str] = "mock-key",
        model_name: Optional[str] = None
    ):
        """Initialize mock provider."""
        super().__init__(api_key, model_name)
        self.model_name = model_name or self.default_model
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "anthropic-mock"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-mock"

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict:
        """Generate mock response."""
        self.call_count += 1

        if config is None:
            config = GenerationConfig()

        # Generate mock content based on prompt language
        if "Guten Tag" in prompt or "Sie" in prompt or "Grüße" in prompt:
            content = "Dies ist eine simulierte Antwort auf Deutsch. "
            content += "In der Praxis würde Claude hier eine kulturell angepasste deutsche Antwort generieren."
        elif "Buenos días" in prompt or "usted" in prompt or "Cordialmente" in prompt:
            content = "Esta es una respuesta simulada en español. "
            content += "En la práctica, Claude generaría aquí una respuesta culturalmente adaptada al español."
        else:
            content = "This is a mock response for testing purposes. "
            content += "In production, Claude would generate a culturally-appropriate response here."

        # Mock token counts (approximate)
        tokens_input = len(prompt) // 4
        tokens_output = len(content) // 4

        return {
            "content": content,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "model": self.model_name,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "provider": self.provider_name,
                "config": config.to_dict(),
                "mock": True,
                "call_count": self.call_count
            }
        }

    def get_embeddings(self, text: str) -> List[float]:
        """Return mock embeddings."""
        # Return a simple hash-based vector for testing
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # Convert hex to list of floats (384-dim like Voyage AI)
        return [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)] * 24

    def count_tokens(self, text: str) -> int:
        """Mock token counting."""
        return len(text) // CHARS_PER_TOKEN_ESTIMATE
