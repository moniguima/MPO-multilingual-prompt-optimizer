"""
Cache management for demo mode (zero API costs at runtime).

This module handles storage and retrieval of pre-generated prompt variants
and LLM responses, enabling the demo to run without API keys.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from ..core.prompt import PromptVariant, LLMResponse, FormalityLevel


class CacheManager:
    """
    Manages cache for prompt variants and LLM responses.

    Enables demo mode by storing and retrieving pre-generated data,
    eliminating the need for API calls during demonstrations.
    """

    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize cache manager.

        Args:
            cache_dir: Root directory for cache storage
        """
        self.cache_dir = Path(cache_dir)
        self.prompts_dir = self.cache_dir / "prompts"
        self.responses_dir = self.cache_dir / "responses"

        # Create directories if they don't exist
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

        # Cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._load_metadata()

    def _load_metadata(self):
        """Load cache metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "cached_variants": {},
                "cached_responses": {}
            }

    def _save_metadata(self):
        """Save cache metadata."""
        self.metadata["updated_at"] = datetime.utcnow().isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _get_variant_cache_path(
        self,
        template_id: str,
        language: str,
        formality: str
    ) -> Path:
        """Get file path for cached variant."""
        filename = f"{template_id}_{language}_{formality}.json"
        return self.prompts_dir / filename

    def _get_response_cache_path(
        self,
        template_id: str,
        language: str,
        formality: str
    ) -> Path:
        """Get file path for cached response."""
        filename = f"{template_id}_{language}_{formality}_response.json"
        return self.responses_dir / filename

    def cache_variant(
        self,
        variant: PromptVariant
    ) -> None:
        """
        Cache a prompt variant.

        Args:
            variant: PromptVariant to cache
        """
        formality_str = variant.formality.value if isinstance(variant.formality, FormalityLevel) else variant.formality
        cache_path = self._get_variant_cache_path(
            variant.template_id,
            variant.language,
            formality_str
        )

        # Save variant to file
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(variant.to_dict(), f, indent=2, ensure_ascii=False)

        # Update metadata
        cache_key = f"{variant.template_id}_{variant.language}_{formality_str}"
        self.metadata["cached_variants"][cache_key] = {
            "file": str(cache_path.name),
            "cached_at": datetime.utcnow().isoformat()
        }
        self._save_metadata()

    def get_cached_variant(
        self,
        template_id: str,
        language: str,
        formality: str
    ) -> Optional[PromptVariant]:
        """
        Retrieve cached prompt variant.

        Args:
            template_id: Prompt template ID
            language: Language code
            formality: Formality level

        Returns:
            PromptVariant if cached, None otherwise
        """
        cache_path = self._get_variant_cache_path(template_id, language, formality)

        if not cache_path.exists():
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return PromptVariant.from_dict(data)

    def cache_response(
        self,
        response: LLMResponse,
        template_id: str,
        language: str,
        formality: str
    ) -> None:
        """
        Cache an LLM response.

        Args:
            response: LLMResponse to cache
            template_id: Associated prompt template ID
            language: Language code
            formality: Formality level
        """
        cache_path = self._get_response_cache_path(template_id, language, formality)

        # Save response to file
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(response.to_dict(), f, indent=2, ensure_ascii=False)

        # Update metadata
        cache_key = f"{template_id}_{language}_{formality}"
        self.metadata["cached_responses"][cache_key] = {
            "file": str(cache_path.name),
            "cached_at": datetime.utcnow().isoformat(),
            "model": response.model
        }
        self._save_metadata()

    def get_cached_response(
        self,
        template_id: str,
        language: str,
        formality: str
    ) -> Optional[LLMResponse]:
        """
        Retrieve cached LLM response.

        Args:
            template_id: Prompt template ID
            language: Language code
            formality: Formality level

        Returns:
            LLMResponse if cached, None otherwise
        """
        cache_path = self._get_response_cache_path(template_id, language, formality)

        if not cache_path.exists():
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return LLMResponse.from_dict(data)

    def is_cached(
        self,
        template_id: str,
        language: str,
        formality: str,
        include_response: bool = False
    ) -> bool:
        """
        Check if variant (and optionally response) is cached.

        Args:
            template_id: Prompt template ID
            language: Language code
            formality: Formality level
            include_response: Also check for cached response

        Returns:
            True if cached, False otherwise
        """
        variant_cached = self._get_variant_cache_path(template_id, language, formality).exists()

        if not include_response:
            return variant_cached

        response_cached = self._get_response_cache_path(template_id, language, formality).exists()
        return variant_cached and response_cached

    def list_cached_items(self) -> Dict:
        """
        List all cached items.

        Returns:
            Dictionary with cached variants and responses
        """
        return {
            "variants": list(self.metadata["cached_variants"].keys()),
            "responses": list(self.metadata["cached_responses"].keys()),
            "total_variants": len(self.metadata["cached_variants"]),
            "total_responses": len(self.metadata["cached_responses"]),
            "cache_version": self.metadata["version"]
        }

    def clear_cache(self, confirm: bool = False) -> None:
        """
        Clear all cached data.

        Args:
            confirm: Must be True to actually clear (safety check)
        """
        if not confirm:
            raise ValueError("Must pass confirm=True to clear cache")

        # Remove all cached files
        for file in self.prompts_dir.glob("*.json"):
            file.unlink()

        for file in self.responses_dir.glob("*.json"):
            file.unlink()

        # Reset metadata
        self.metadata = {
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "cached_variants": {},
            "cached_responses": {}
        }
        self._save_metadata()

    def validate_cache(self) -> Dict:
        """
        Validate cache integrity.

        Returns:
            Dictionary with validation results
        """
        issues = []
        stats = {
            "variants_in_metadata": len(self.metadata["cached_variants"]),
            "variants_on_disk": len(list(self.prompts_dir.glob("*.json"))),
            "responses_in_metadata": len(self.metadata["cached_responses"]),
            "responses_on_disk": len(list(self.responses_dir.glob("*.json"))),
            "issues": []
        }

        # Check for mismatches
        if stats["variants_in_metadata"] != stats["variants_on_disk"]:
            issues.append("Mismatch between metadata and disk for variants")

        if stats["responses_in_metadata"] != stats["responses_on_disk"]:
            issues.append("Mismatch between metadata and disk for responses")

        # Check if files in metadata actually exist
        for key, info in self.metadata["cached_variants"].items():
            file_path = self.prompts_dir / info["file"]
            if not file_path.exists():
                issues.append(f"Missing variant file: {info['file']}")

        for key, info in self.metadata["cached_responses"].items():
            file_path = self.responses_dir / info["file"]
            if not file_path.exists():
                issues.append(f"Missing response file: {info['file']}")

        stats["issues"] = issues
        stats["valid"] = len(issues) == 0

        return stats
