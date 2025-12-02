"""
OpenAI GPT API provider implementation.

This module wraps the OpenAI API for text generation and embeddings,
following the AbstractLLMProvider interface.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from openai import OpenAI
from .base import AbstractLLMProvider, GenerationConfig
from ..constants import CHARS_PER_TOKEN_ESTIMATE


class OpenAIProvider(AbstractLLMProvider):
    """
    OpenAI GPT API provider.

    Supports GPT-4, GPT-4-turbo, GPT-3.5-turbo models with full embeddings support.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model_name: Model identifier (defaults to gpt-4-turbo)
        """
        super().__init__(api_key, model_name)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Set model
        self.model_name = model_name or self.default_model

        # Try to import tiktoken for accurate token counting
        try:
            import tiktoken
            self.tiktoken = tiktoken
            self.encoder = None  # Lazy load when needed
        except ImportError:
            self.tiktoken = None
            self.encoder = None

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "openai"

    @property
    def default_model(self) -> str:
        """Return default GPT model."""
        return "gpt-4-turbo-preview"

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict:
        """
        Generate text using OpenAI GPT API.

        Args:
            prompt: Input prompt text
            config: Generation configuration
            **kwargs: Additional OpenAI-specific parameters

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
            api_params["stop"] = config.stop_sequences

        # Override with any additional kwargs
        api_params.update(kwargs)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(**api_params)

            # Extract content
            content = response.choices[0].message.content

            # Get token counts
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens

            # Build response dictionary
            result = {
                "content": content,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "model": response.model,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "finish_reason": response.choices[0].finish_reason,
                    "provider": self.provider_name,
                    "config": config.to_dict(),
                    "system_fingerprint": getattr(response, 'system_fingerprint', None)
                }
            }

            return result

        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text using OpenAI's embedding API.

        Args:
            text: Input text

        Returns:
            Embedding vector (1536-dimensional for text-embedding-3-small)
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            raise Exception(f"OpenAI embeddings API call failed: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Falls back to approximation if tiktoken is not available.

        Args:
            text: Input text

        Returns:
            Token count
        """
        if self.tiktoken:
            try:
                # Lazy load encoder
                if self.encoder is None:
                    # Use cl100k_base encoding (used by gpt-4, gpt-3.5-turbo)
                    self.encoder = self.tiktoken.get_encoding("cl100k_base")

                tokens = self.encoder.encode(text)
                return len(tokens)
            except Exception:
                # Fall back to approximation if encoding fails
                pass

        # Fallback: rough approximation
        return len(text) // CHARS_PER_TOKEN_ESTIMATE

    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        return self.api_key is not None

    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        models_info = {
            "gpt-4-turbo-preview": {
                "name": "GPT-4 Turbo",
                "context_window": 128000,
                "max_output": 4096,
                "cost_input_per_m": 10.00,
                "cost_output_per_m": 30.00,
                "supports_vision": True
            },
            "gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "context_window": 128000,
                "max_output": 4096,
                "cost_input_per_m": 10.00,
                "cost_output_per_m": 30.00,
                "supports_vision": True
            },
            "gpt-4": {
                "name": "GPT-4",
                "context_window": 8192,
                "max_output": 8192,
                "cost_input_per_m": 30.00,
                "cost_output_per_m": 60.00,
                "supports_vision": False
            },
            "gpt-4-32k": {
                "name": "GPT-4 32K",
                "context_window": 32768,
                "max_output": 32768,
                "cost_input_per_m": 60.00,
                "cost_output_per_m": 120.00,
                "supports_vision": False
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "context_window": 16385,
                "max_output": 4096,
                "cost_input_per_m": 0.50,
                "cost_output_per_m": 1.50,
                "supports_vision": False
            },
            "gpt-3.5-turbo-16k": {
                "name": "GPT-3.5 Turbo 16K",
                "context_window": 16385,
                "max_output": 16385,
                "cost_input_per_m": 3.00,
                "cost_output_per_m": 4.00,
                "supports_vision": False
            }
        }

        return models_info.get(
            self.model_name,
            {"name": self.model_name, "info": "Unknown model"}
        )


class MockOpenAIProvider(AbstractLLMProvider):
    """
    Mock OpenAI provider for testing without API calls.

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
        return "openai-mock"

    @property
    def default_model(self) -> str:
        return "gpt-4-turbo-mock"

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
            content = "Dies ist eine simulierte GPT-Antwort auf Deutsch. "
            content += "In der Praxis würde GPT hier eine kulturell angepasste deutsche Antwort generieren."
        elif "Buenos días" in prompt or "usted" in prompt or "Cordialmente" in prompt:
            content = "Esta es una respuesta simulada de GPT en español. "
            content += "En la práctica, GPT generaría aquí una respuesta culturalmente adaptada al español."
        else:
            content = "This is a mock GPT response for testing purposes. "
            content += "In production, GPT would generate a culturally-appropriate response here."

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
                "finish_reason": "stop",
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
        # Convert hex to list of floats (1536-dim like OpenAI's text-embedding-3-small)
        # Create pattern by repeating the hash
        base_vector = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]
        return (base_vector * 96)[:1536]  # 16 * 96 = 1536

    def count_tokens(self, text: str) -> int:
        """Mock token counting."""
        return len(text) // CHARS_PER_TOKEN_ESTIMATE

    def is_available(self) -> bool:
        """Mock is always available."""
        return True

    def get_model_info(self) -> Dict:
        """Get mock model info."""
        return {
            "name": self.model_name,
            "context_window": 128000,
            "max_output": 4096,
            "cost_input_per_m": 0.00,
            "cost_output_per_m": 0.00,
            "mock": True
        }
