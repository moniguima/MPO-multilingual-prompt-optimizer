"""
Unit tests for cultural adapters.
"""

import pytest
from mpo.core.prompt import PromptTemplate, PromptDomain, FormalityLevel
from mpo.adapters import GermanAdapter, SpanishAdapter, EnglishAdapter, get_adapter


@pytest.fixture
def sample_template():
    """Create a sample prompt template for testing."""
    return PromptTemplate(
        id="test_prompt",
        content="I need to request an extension for the project deadline.",
        domain=PromptDomain.BUSINESS,
        placeholders={},
        description="Test prompt"
    )


@pytest.fixture
def german_config():
    """German language configuration."""
    return {
        "name": "German",
        "code": "de",
        "cultural_params": {
            "formality_levels": {
                "formal": {
                    "pronoun": "Sie",
                    "greeting": "Sehr geehrte Damen und Herren",
                    "closing": "Hochachtungsvoll"
                },
                "neutral": {
                    "pronoun": "Sie",
                    "greeting": "Guten Tag",
                    "closing": "Mit freundlichen Grüßen"
                },
                "casual": {
                    "pronoun": "du",
                    "greeting": "Hallo",
                    "closing": "Viele Grüße"
                }
            }
        }
    }


@pytest.fixture
def spanish_config():
    """Spanish language configuration."""
    return {
        "name": "Spanish",
        "code": "es",
        "cultural_params": {
            "formality_levels": {
                "formal": {
                    "pronoun": "usted",
                    "greeting": "Estimado/a señor/señora",
                    "closing": "Cordialmente"
                },
                "neutral": {
                    "pronoun": "usted",
                    "greeting": "Buenos días",
                    "closing": "Atentamente"
                },
                "casual": {
                    "pronoun": "tú",
                    "greeting": "Hola",
                    "closing": "Saludos"
                }
            }
        }
    }


class TestGermanAdapter:
    """Test German cultural adaptations."""

    def test_formal_adaptation(self, sample_template, german_config):
        """Test formal German adaptation includes appropriate markers."""
        adapter = GermanAdapter(german_config)
        variant = adapter.adapt(sample_template, FormalityLevel.FORMAL)

        assert variant.language == "de"
        assert variant.formality == FormalityLevel.FORMAL
        assert "Sehr geehrte Damen und Herren" in variant.adapted_content
        assert "Hochachtungsvoll" in variant.adapted_content
        assert len(variant.adaptation_notes) > 0

    def test_casual_adaptation(self, sample_template, german_config):
        """Test casual German adaptation."""
        adapter = GermanAdapter(german_config)
        variant = adapter.adapt(sample_template, FormalityLevel.CASUAL)

        assert "Hallo" in variant.adapted_content
        assert "Kurze Frage" in variant.adapted_content
        assert variant.formality == FormalityLevel.CASUAL

    def test_neutral_adaptation(self, sample_template, german_config):
        """Test neutral German adaptation."""
        adapter = GermanAdapter(german_config)
        variant = adapter.adapt(sample_template, FormalityLevel.NEUTRAL)

        assert "Guten Tag" in variant.adapted_content
        assert variant.formality == FormalityLevel.NEUTRAL


class TestSpanishAdapter:
    """Test Spanish cultural adaptations."""

    def test_formal_adaptation(self, sample_template, spanish_config):
        """Test formal Spanish adaptation includes relational elements."""
        adapter = SpanishAdapter(spanish_config)
        variant = adapter.adapt(sample_template, FormalityLevel.FORMAL)

        assert variant.language == "es"
        assert variant.formality == FormalityLevel.FORMAL
        # Check for relational preamble
        assert "Espero que se encuentre bien" in variant.adapted_content
        assert "Cordialmente" in variant.adapted_content

    def test_casual_adaptation(self, sample_template, spanish_config):
        """Test casual Spanish adaptation."""
        adapter = SpanishAdapter(spanish_config)
        variant = adapter.adapt(sample_template, FormalityLevel.CASUAL)

        assert "Hola" in variant.adapted_content or "¿Qué tal?" in variant.adapted_content
        assert variant.formality == FormalityLevel.CASUAL

    def test_gratitude_expression(self, sample_template, spanish_config):
        """Test that formal Spanish includes gratitude (cultural norm)."""
        adapter = SpanishAdapter(spanish_config)
        variant = adapter.adapt(sample_template, FormalityLevel.FORMAL)

        assert "Agradezco" in variant.adapted_content


class TestEnglishAdapter:
    """Test English (baseline) adaptations."""

    def test_minimal_adaptation(self, sample_template):
        """English should have minimal adaptation."""
        config = {"name": "English", "code": "en", "cultural_params": {}}
        adapter = EnglishAdapter(config)
        variant = adapter.adapt(sample_template, FormalityLevel.NEUTRAL)

        assert variant.language == "en"
        # English should be close to original
        assert sample_template.content in variant.adapted_content or \
               variant.adapted_content in sample_template.content


class TestAdapterFactory:
    """Test adapter factory function."""

    def test_get_german_adapter(self, german_config):
        """Test getting German adapter via factory."""
        adapter = get_adapter("de", german_config)
        assert isinstance(adapter, GermanAdapter)

    def test_get_spanish_adapter(self, spanish_config):
        """Test getting Spanish adapter via factory."""
        adapter = get_adapter("es", spanish_config)
        assert isinstance(adapter, SpanishAdapter)

    def test_unsupported_language(self):
        """Test that unsupported language raises error."""
        with pytest.raises(ValueError, match="Unsupported language code"):
            get_adapter("fr", {})
