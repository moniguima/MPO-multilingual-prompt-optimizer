"""
Integration test for persuasive_pitch template with German casual adaptation using LMStudio.

This test demonstrates the complete workflow:
1. Load persuasive_pitch template with realistic placeholders
2. Adapt to German casual using GermanAdapter
3. Generate response using LocalLLMProvider (LMStudio)
4. Validate cultural appropriateness and output quality
"""

import pytest
from mpo.core.prompt import PromptTemplate, PromptDomain, FormalityLevel
from mpo.adapters import GermanAdapter
from mpo.providers.local_provider import LocalLLMProvider
from mpo.providers.base import GenerationConfig


@pytest.fixture
def german_config():
    """German language configuration with formality levels."""
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
def persuasive_pitch_template():
    """Create persuasive_pitch template with realistic placeholder values."""
    return PromptTemplate(
        id="persuasive_pitch",
        content=(
            "I want to propose that our team of {team_size} adopt {tool_name} "
            "for our development workflow. This tool addresses our {current_pain_point} "
            "problem and can deliver {key_metric}. Write a compelling pitch that will "
            "convince the team to try this new tool."
        ),
        domain=PromptDomain.PERSUASIVE,
        placeholders={
            "team_size": "12 developers",
            "tool_name": "GitHub Copilot",
            "current_pain_point": "repetitive boilerplate code",
            "key_metric": "30% faster development time"
        },
        description="Tool adoption proposal for development team"
    )


@pytest.fixture
def lmstudio_provider():
    """Create LocalLLMProvider instance for LMStudio."""
    return LocalLLMProvider(
        base_url="http://localhost:1234/v1"
    )


class TestPersuasivePitchGermanCasual:
    """Integration tests for persuasive_pitch with German casual adaptation."""

    def test_german_casual_adaptation(self, persuasive_pitch_template, german_config):
        """Test that German casual adaptation includes appropriate cultural markers."""
        adapter = GermanAdapter(german_config)
        variant = adapter.adapt(persuasive_pitch_template, FormalityLevel.CASUAL)

        # Verify basic properties
        assert variant.template_id == "persuasive_pitch"
        assert variant.language == "de"
        assert variant.formality == FormalityLevel.CASUAL

        # Verify German casual markers
        assert "Hallo" in variant.adapted_content, "Should include casual German greeting"
        assert "Kurze Frage:" in variant.adapted_content, "Should include casual introduction"
        assert "Viele Grüße" in variant.adapted_content, "Should include casual German closing"

        # Verify adaptation notes mention du form
        assert "du" in variant.adaptation_notes, "Should mention using 'du' pronoun"
        assert len(variant.adaptation_notes) > 0, "Should have adaptation notes"

        print(f"\n✓ Adapted Content:\n{variant.adapted_content}")
        print(f"\n✓ Adaptation Notes: {variant.adaptation_notes}")

    def test_rendered_template_with_placeholders(self, persuasive_pitch_template):
        """Test that placeholders are correctly rendered."""
        rendered = persuasive_pitch_template.render()

        # Verify placeholders are replaced
        assert "{team_size}" not in rendered
        assert "{tool_name}" not in rendered
        assert "12 developers" in rendered
        assert "GitHub Copilot" in rendered
        assert "repetitive boilerplate code" in rendered
        assert "30% faster development time" in rendered

        print(f"\n✓ Rendered Template:\n{rendered}")

    @pytest.mark.skipif(
        not LocalLLMProvider().is_available(),
        reason="LMStudio not running or no model loaded"
    )
    def test_lmstudio_generation(
        self,
        persuasive_pitch_template,
        german_config,
        lmstudio_provider
    ):
        """
        Test complete workflow: adapt to German casual and generate with LMStudio.

        IMPORTANT: This test requires LMStudio to be running with a model loaded.
        To run this test:
        1. Install LMStudio from https://lmstudio.ai/
        2. Download a model (e.g., Mistral 7B Instruct)
        3. Load the model and start the server (default: http://localhost:1234)
        """
        # 1. Adapt template to German casual
        adapter = GermanAdapter(german_config)
        variant = adapter.adapt(persuasive_pitch_template, FormalityLevel.CASUAL)

        # 2. Render with placeholders
        prompt_content = persuasive_pitch_template.render()
        full_prompt = variant.adapted_content.replace(
            persuasive_pitch_template.content,
            prompt_content
        )

        print(f"\n✓ Full Prompt Sent to LMStudio:\n{full_prompt}")

        # 3. Generate response using LMStudio
        config = GenerationConfig(
            max_tokens=500,
            temperature=0.7,
            top_p=0.9
        )

        response = lmstudio_provider.generate(full_prompt, config)

        # 4. Validate response structure
        assert "content" in response, "Response should contain 'content'"
        assert "tokens_input" in response, "Response should contain 'tokens_input'"
        assert "tokens_output" in response, "Response should contain 'tokens_output'"
        assert "model" in response, "Response should contain 'model'"
        assert "timestamp" in response, "Response should contain 'timestamp'"

        # 5. Validate response content
        content = response["content"]
        assert len(content) > 0, "Response content should not be empty"
        assert response["tokens_input"] > 0, "Should have input tokens"
        assert response["tokens_output"] > 0, "Should have output tokens"

        # 6. Print results
        print(f"\n✓ LLM Response:\n{content}")
        print(f"\n✓ Tokens (in/out): {response['tokens_input']}/{response['tokens_output']}")
        print(f"✓ Model: {response['model']}")
        print(f"✓ Provider: {response['metadata']['provider']}")

        # 7. Cultural validation (German casual characteristics)
        # Note: This is a basic check - more sophisticated NLP analysis could be added
        content_lower = content.lower()

        # Check for informal German markers (if response is in German)
        if any(word in content_lower for word in ['der', 'die', 'das', 'und', 'ist']):
            print("\n✓ Response appears to be in German")

    def test_model_availability(self, lmstudio_provider):
        """Test LMStudio availability and get loaded model info."""
        if lmstudio_provider.is_available():
            model_info = lmstudio_provider.get_loaded_model_info()
            print(f"\n✓ LMStudio Status: Available")
            print(f"✓ Loaded Model: {model_info.get('id', 'unknown')}")
            assert model_info["available"] is True
        else:
            pytest.skip("LMStudio is not running or no model is loaded")


# Example of how to run this test manually (outside pytest):
def run_manual_test():
    """
    Manual test function for development/debugging.

    Run with: python -c "from tests.integration.test_persuasive_pitch_german_casual import run_manual_test; run_manual_test()"
    """
    print("=== Manual Test: Persuasive Pitch - German Casual with LMStudio ===\n")

    # Setup
    german_config = {
        "name": "German",
        "code": "de",
        "cultural_params": {
            "formality_levels": {
                "casual": {
                    "pronoun": "du",
                    "greeting": "Hallo",
                    "closing": "Viele Grüße"
                }
            }
        }
    }

    template = PromptTemplate(
        id="persuasive_pitch",
        content=(
            "I want to propose that our team of {team_size} adopt {tool_name} "
            "for our development workflow. This tool addresses our {current_pain_point} "
            "problem and can deliver {key_metric}. Write a compelling pitch that will "
            "convince the team to try this new tool."
        ),
        domain=PromptDomain.PERSUASIVE,
        placeholders={
            "team_size": "12 developers",
            "tool_name": "GitHub Copilot",
            "current_pain_point": "repetitive boilerplate code",
            "key_metric": "30% faster development time"
        },
        description="Tool adoption proposal"
    )

    # Adapt
    adapter = GermanAdapter(german_config)
    variant = adapter.adapt(template, FormalityLevel.CASUAL)

    print(f"Adapted Content:\n{variant.adapted_content}\n")
    print(f"Notes: {variant.adaptation_notes}\n")

    # Generate (if LMStudio available)
    provider = LocalLLMProvider()
    if provider.is_available():
        prompt = variant.adapted_content.replace(
            template.content,
            template.render()
        )
        response = provider.generate(prompt)
        print(f"LLM Response:\n{response['content']}\n")
        print(f"Tokens: {response['tokens_input']}/{response['tokens_output']}")
    else:
        print("⚠️  LMStudio not available. Skipping generation.")


if __name__ == "__main__":
    run_manual_test()
