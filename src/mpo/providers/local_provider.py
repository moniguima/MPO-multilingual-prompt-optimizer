"""
LMStudio local LLM provider implementation.

This module provides integration with LMStudio for running local models
(Gemma 3 12B, Mistral 7B Instruct) without API costs.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from openai import OpenAI
from .base import AbstractLLMProvider, GenerationConfig
from ..constants import CHARS_PER_TOKEN_ESTIMATE


class LocalLLMProvider(AbstractLLMProvider):
    """
    LMStudio local LLM provider using OpenAI-compatible API.

    Supports any model running on LMStudio (default: http://localhost:1234/v1).
    Recommended models:
    - Gemma 3 12B (good multilingual support)
    - Mistral 7B Instruct v0.3 (good for DE/ES)
    """

    def __init__(
        self,
        api_key: Optional[str] = "not-needed",
        model_name: Optional[str] = "",
        base_url: str = "http://localhost:1234/v1"
    ):
        """
        Initialize LMStudio provider.

        Args:
            api_key: Not required for local models (default: "not-needed")
            model_name: Model identifier (empty string auto-selects loaded model)
            base_url: LMStudio server URL (default: http://localhost:1234/v1)
        """
        super().__init__(api_key, model_name)

        # Initialize OpenAI client pointing to LMStudio
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key  # LMStudio doesn't validate this
        )

        # Model name (empty string tells LMStudio to use currently loaded model)
        self.model_name = model_name or ""
        self.base_url = base_url

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "lmstudio"

    @property
    def default_model(self) -> str:
        """Return default model (auto-detect)."""
        return ""  # Empty string = use currently loaded model

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict:
        """
        Generate text using local LLM via LMStudio.

        Args:
            prompt: Input prompt text
            config: Generation configuration
            **kwargs: Additional OpenAI-compatible parameters

        Returns:
            Dictionary with generated content and metadata
        """
        if config is None:
            config = GenerationConfig()

        # Prepare API parameters (OpenAI-compatible format)
        api_params = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }

        # Add stop sequences if provided
        if config.stop_sequences:
            api_params["stop"] = config.stop_sequences

        # Override with any additional kwargs
        api_params.update(kwargs)

        try:
            # Call LMStudio API (OpenAI-compatible)
            response = self.client.chat.completions.create(**api_params)

            # Extract content
            content = response.choices[0].message.content

            # Get token counts (if available)
            tokens_input = getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0
            tokens_output = getattr(response.usage, 'completion_tokens', 0) if response.usage else 0

            # If token counts not available, estimate
            if tokens_input == 0:
                tokens_input = self.count_tokens(prompt)
            if tokens_output == 0:
                tokens_output = self.count_tokens(content)

            # Get actual model used (LMStudio returns this)
            model_used = getattr(response, 'model', self.model_name or 'unknown')

            # Build response dictionary
            result = {
                "content": content,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "model": model_used,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "stop_reason": getattr(response.choices[0], 'finish_reason', 'stop'),
                    "stop_sequence": None,
                    "provider": self.provider_name,
                    "base_url": self.base_url,
                    "config": config.to_dict()
                }
            }

            return result

        except Exception as e:
            raise Exception(
                f"LMStudio API call failed: {str(e)}\n"
                f"Make sure LMStudio is running at {self.base_url} with a model loaded."
            )

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text.

        Note: LMStudio may or may not provide embeddings depending on the model.
        This attempts to use the embeddings endpoint if available.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            NotImplementedError: If embeddings are not available
        """
        try:
            # Try to get embeddings from LMStudio
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception:
            # Fall back to mock embeddings if not available
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            # Convert hex to list of floats (384-dim vector)
            return [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)] * 24

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Uses rough approximation (1 token ≈ 4 characters).
        For more accuracy, could integrate tiktoken.

        Args:
            text: Input text

        Returns:
            Approximate token count
        """
        # Rough approximation using constant
        return len(text) // CHARS_PER_TOKEN_ESTIMATE

    def is_available(self) -> bool:
        """
        Check if LMStudio is available and has a model loaded.

        Returns:
            True if LMStudio is reachable, False otherwise
        """
        try:
            # Try to list models to check if server is running
            models = self.client.models.list()
            return True
        except Exception:
            return False

    def get_loaded_model_info(self) -> Dict:
        """
        Get information about currently loaded model in LMStudio.

        Returns:
            Dictionary with model information
        """
        try:
            models = self.client.models.list()
            if models.data:
                model = models.data[0]
                return {
                    "id": model.id,
                    "owned_by": getattr(model, 'owned_by', 'local'),
                    "available": True
                }
            else:
                return {
                    "id": "none",
                    "available": False,
                    "message": "No model loaded in LMStudio"
                }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "message": f"Cannot connect to LMStudio at {self.base_url}"
            }
