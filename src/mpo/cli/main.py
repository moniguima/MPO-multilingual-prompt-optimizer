"""
Command-line interface for Multilingual Prompt Optimizer.

Provides commands for prompt adaptation, evaluation, and reporting.
"""

import click
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from ..core.prompt import PromptTemplate, PromptDomain, FormalityLevel
from ..adapters import get_adapter
from ..core.evaluator import PromptEvaluator
from ..providers.anthropic_provider import AnthropicProvider, MockAnthropicProvider
from ..providers.openai_provider import OpenAIProvider, MockOpenAIProvider
from ..providers.local_provider import LocalLLMProvider
from ..providers.base import GenerationConfig
from ..storage.cache_manager import CacheManager
from ..storage.experiment_tracker import ExperimentTracker, ExperimentConfig
from ..metrics import quantitative, qualitative
from ..constants import (
    FORMALITY_LEVELS,
    SUPPORTED_LANGUAGES,
    CONFIG_DIR,
    DATA_DIR,
    CACHE_DIR,
    REPORTS_DIR,
    EXPERIMENTS_DIR
)

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Multilingual Prompt Optimizer (MPO)

    Cultural adaptation of LLM prompts across languages for measurable
    performance improvements.
    """
    pass


# Usage examples:
#   mpo init                          # Initialize project and check configuration
@cli.command()
def init():
    """Initialize MPO project structure and configuration."""
    click.echo("🌍 Initializing Multilingual Prompt Optimizer...")

    # Check if config files exist
    required_files = [
        CONFIG_DIR / "languages.yaml",
        CONFIG_DIR / "prompts.yaml",
        CONFIG_DIR / "models.yaml"
    ]

    missing_files = [f for f in required_files if not f.exists()]

    if missing_files:
        click.echo(click.style("❌ Missing configuration files:", fg="red"))
        for f in missing_files:
            click.echo(f"   - {f}")
        click.echo("\nPlease ensure config files are in place.")
        return

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        click.echo(click.style("⚠️  No .env file found", fg="yellow"))
        click.echo("Please create a .env file with your API keys")
        click.echo("You can copy from .env.example if available")

    # Create cache manager to initialize cache structure
    cache = CacheManager(str(CACHE_DIR))

    click.echo(click.style("\n✅ Initialization complete!", fg="green"))
    click.echo("\nNext steps:")
    click.echo("  1. Add your API key to .env file")
    click.echo("  2. Try: mpo test business_email")
    click.echo("  3. Or run: mpo benchmark")


# Usage examples:
#   mpo test business_email                              # Test in demo mode (default)
#   mpo test business_email --live                       # Test with live API
#   mpo test business_email -l de -f formal              # Test German formal variant
#   mpo test persuasive_pitch -l es --provider anthropic --live  # Live test with Claude
#   mpo test technical_explanation -o results.json       # Save output to file
@cli.command()
@click.argument('prompt_id')
@click.option('--language', '-l', default='en', help='Target language (en, de, es)')
@click.option('--formality', '-f', default='neutral',
              type=click.Choice(['casual', 'neutral', 'formal']),
              help='Formality level')
@click.option('--provider', '-p', default='local',
              type=click.Choice(['anthropic', 'openai', 'local', 'mock']),
              help='LLM provider (anthropic=Claude, openai=GPT, local=LMStudio, mock=testing)')
@click.option('--live', is_flag=True, help='Use live API (requires API key)')
@click.option('--output', '-o', help='Output file path (optional)')
def test(prompt_id: str, language: str, formality: str, provider: str, live: bool, output: Optional[str]):
    """Test a prompt with cultural adaptation."""

    # Load configurations
    with open(CONFIG_DIR / "languages.yaml") as f:
        lang_config = yaml.safe_load(f)

    with open(CONFIG_DIR / "prompts.yaml") as f:
        prompts_config = yaml.safe_load(f)

    with open(CONFIG_DIR / "models.yaml") as f:
        models_config = yaml.safe_load(f)

    # Validate prompt ID
    if prompt_id not in prompts_config['prompts']:
        click.echo(click.style(f"❌ Unknown prompt: {prompt_id}", fg="red"))
        click.echo(f"\nAvailable prompts: {', '.join(prompts_config['prompts'].keys())}")
        return

    # Load prompt template
    prompt_meta = prompts_config['prompts'][prompt_id]
    template_file = Path("prompts") / prompt_meta['file']

    if not template_file.exists():
        click.echo(click.style(f"❌ Template file not found: {template_file}", fg="red"))
        return

    with open(template_file) as f:
        prompt_content = f.read()

    template = PromptTemplate(
        id=prompt_id,
        content=prompt_content,
        domain=PromptDomain(prompt_meta['domain']),
        placeholders=prompt_meta.get('placeholders', {}),
        description=prompt_meta.get('description', '')
    )

    # Render template with default placeholders
    rendered_content = template.render()

    click.echo(f"\n📝 Testing prompt: {click.style(prompt_id, fg='cyan', bold=True)}")
    click.echo(f"   Language: {language} | Formality: {formality}")
    click.echo(f"   Provider: {provider}")
    click.echo(f"   Mode: {'🔴 LIVE' if live else '🟢 DEMO'}\n")

    # Initialize components
    formality_enum = FormalityLevel(formality)

    # Get adapter and adapt prompt
    adapter = get_adapter(language, lang_config['languages'][language])
    variant = adapter.adapt(template, formality_enum)

    click.echo(click.style("🔄 Adapted Prompt:", fg="yellow"))
    click.echo(f"{variant.adapted_content}\n")
    click.echo(click.style(f"📋 Adaptation notes: {variant.adaptation_notes}", fg="blue"))

    # Get or generate response
    cache = CacheManager(str(CACHE_DIR))

    if not live:
        # Use cached response
        response = cache.get_cached_response(prompt_id, language, formality)

        if response:
            click.echo(click.style("\n✅ Retrieved from cache", fg="green"))
        else:
            click.echo(click.style("\n⚠️  No cached response found", fg="yellow"))
            click.echo("Run with --live to generate new response, or run 'mpo benchmark' to generate cache.")
            return
    else:
        # Live API call - select provider
        llm_provider = None

        if provider == 'anthropic':
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                click.echo(click.style("❌ ANTHROPIC_API_KEY not found in environment", fg="red"))
                click.echo("Add your API key to .env file or use --provider local")
                return
            llm_provider = AnthropicProvider(api_key=api_key)
            click.echo(click.style(f"🤖 Using Claude API - Model: {llm_provider.model_name}", fg="cyan"))

        elif provider == 'openai':
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                click.echo(click.style("❌ OPENAI_API_KEY not found in environment", fg="red"))
                click.echo("Add your API key to .env file or use --provider local")
                return
            llm_provider = OpenAIProvider(api_key=api_key)
            click.echo(click.style(f"🤖 Using OpenAI API - Model: {llm_provider.model_name}", fg="cyan"))

        elif provider == 'local':
            llm_provider = LocalLLMProvider()
            # Check if LMStudio is available
            if not llm_provider.is_available():
                click.echo(click.style("❌ Cannot connect to LMStudio", fg="red"))
                click.echo("Make sure LMStudio is running at http://localhost:1234 with a model loaded")
                click.echo("Or use --provider anthropic or --demo mode")
                return
            model_info = llm_provider.get_loaded_model_info()
            click.echo(click.style(f"📡 Connected to LMStudio - Model: {model_info.get('id', 'unknown')}", fg="cyan"))

        elif provider == 'mock':
            llm_provider = MockAnthropicProvider()
            click.echo(click.style("🎭 Using mock provider (test mode)", fg="yellow"))

        domain_config = models_config.get('generation_configs', {}).get(
            prompt_meta['domain'],
            models_config['generation_defaults']
        )

        # Filter out 'note' fields that aren't part of GenerationConfig
        config_params = {k: v for k, v in domain_config.items() if k != 'note'}
        config = GenerationConfig(**config_params)
        evaluator = PromptEvaluator(llm_provider, lang_config['languages'])

        click.echo(click.style("\n🚀 Generating response...", fg="cyan"))
        response = evaluator.evaluate_variant(variant, config)

        # Cache the response
        cache.cache_variant(variant)
        cache.cache_response(response, prompt_id, language, formality)
        click.echo(click.style("💾 Cached for future demo use", fg="green"))

    # Display response
    click.echo(click.style("\n🤖 LLM Response:", fg="green", bold=True))
    click.echo(f"{response.content}\n")

    # Calculate metrics
    click.echo(click.style("📊 Metrics:", fg="magenta"))
    click.echo(f"   Tokens (in/out): {response.tokens_input}/{response.tokens_output}")

    quant_metrics = quantitative.calculate_all_quantitative_metrics(
        response.content, response.tokens_output, language
    )
    click.echo(f"   Words: {quant_metrics['length_metrics']['word_count']}")
    click.echo(f"   Sentences: {quant_metrics['token_efficiency']['total_sentences']}")
    click.echo(f"   Lexical diversity: {quant_metrics['lexical_diversity']['type_token_ratio']}")

    qual_metrics = qualitative.calculate_all_qualitative_metrics(
        response.content, language, formality, prompt_meta['domain']
    )
    click.echo(f"   Cultural appropriateness: {qual_metrics['cultural_appropriateness']['overall_rating']}")

    # Save to file if requested
    if output:
        output_path = Path(output)
        output_data = {
            "prompt_id": prompt_id,
            "template": template.content,
            "variant": variant.to_dict(),
            "response": response.to_dict(),
            "metrics": {
                "quantitative": quant_metrics,
                "qualitative": qual_metrics
            }
        }

        import json
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        click.echo(click.style(f"\n💾 Saved to: {output_path}", fg="green"))


# Usage examples:
#   mpo benchmark                     # Run benchmark in demo mode (default, free)
#   mpo benchmark --live              # Run benchmark with live API (costs ~$3-4)
#   mpo benchmark --provider openai --live  # Use OpenAI instead of default
@cli.command()
@click.option('--provider', '-p', default='local',
              type=click.Choice(['anthropic', 'openai', 'local', 'mock']),
              help='LLM provider (anthropic=Claude, openai=GPT, local=LMStudio, mock=testing)')
@click.option('--live', is_flag=True, help='Use live API (costs money!)')
def benchmark(provider: str, live: bool):
    """Run full benchmark across all prompts, languages, and formality levels."""

    if live:
        click.echo(click.style("⚠️  WARNING: Live mode will make ~90 API calls", fg="yellow"))
        click.echo("Estimated cost: $3-4 USD")
        if not click.confirm("Continue?"):
            return

    # Load configs
    with open(CONFIG_DIR / "languages.yaml") as f:
        lang_config = yaml.safe_load(f)

    with open(CONFIG_DIR / "prompts.yaml") as f:
        prompts_config = yaml.safe_load(f)

    with open(CONFIG_DIR / "models.yaml") as f:
        models_config = yaml.safe_load(f)

    # Initialize provider
    llm_provider = None

    if not live:
        # Override provider selection for demo mode
        llm_provider = MockAnthropicProvider()
        click.echo(click.style("🎭 Using mock provider (demo mode)", fg="cyan"))
    elif provider == 'anthropic':
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            click.echo(click.style("❌ ANTHROPIC_API_KEY not set", fg="red"))
            return
        llm_provider = AnthropicProvider(api_key=api_key)
        click.echo(click.style(f"🤖 Using Claude API - Model: {llm_provider.model_name}", fg="cyan"))
    elif provider == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            click.echo(click.style("❌ OPENAI_API_KEY not set", fg="red"))
            return
        llm_provider = OpenAIProvider(api_key=api_key)
        click.echo(click.style(f"🤖 Using OpenAI API - Model: {llm_provider.model_name}", fg="cyan"))
    elif provider == 'local':
        llm_provider = LocalLLMProvider()
        if not llm_provider.is_available():
            click.echo(click.style("❌ Cannot connect to LMStudio", fg="red"))
            click.echo("Make sure LMStudio is running at http://localhost:1234 with a model loaded")
            return
        model_info = llm_provider.get_loaded_model_info()
        click.echo(click.style(f"📡 Connected to LMStudio - Model: {model_info.get('id', 'unknown')}", fg="cyan"))
    elif provider == 'mock':
        llm_provider = MockAnthropicProvider()
        click.echo(click.style("🎭 Using mock provider (test mode)", fg="yellow"))

    evaluator = PromptEvaluator(llm_provider, lang_config['languages'])
    cache = CacheManager(str(CACHE_DIR))
    tracker = ExperimentTracker(str(EXPERIMENTS_DIR))

    # Create experiment
    exp_config = ExperimentConfig(
        prompt_ids=list(prompts_config['prompts'].keys()),
        languages=SUPPORTED_LANGUAGES[:3],  # Use first 3 languages (en, de, es)
        formality_levels=FORMALITY_LEVELS,
        model=llm_provider.default_model,
        demo_mode=not live
    )

    experiment = tracker.create_experiment(
        name=f"Benchmark {'(live)' if live else '(demo)'}",
        config=exp_config
    )

    click.echo(f"\n🧪 Starting experiment: {experiment.id}")
    click.echo(f"   Prompts: {len(exp_config.prompt_ids)}")
    click.echo(f"   Languages: {len(exp_config.languages)}")
    click.echo(f"   Formality levels: {len(exp_config.formality_levels)}")
    click.echo(f"   Total evaluations: {len(exp_config.prompt_ids) * len(exp_config.languages) * len(exp_config.formality_levels)}\n")

    # Run benchmark
    results_count = 0

    with click.progressbar(
        prompts_config['prompts'].items(),
        label='Processing prompts'
    ) as prompts:
        for prompt_id, prompt_meta in prompts:
            # Load template
            template_file = Path("prompts") / prompt_meta['file']
            with open(template_file) as f:
                prompt_content = f.read()

            template = PromptTemplate(
                id=prompt_id,
                content=prompt_content,
                domain=PromptDomain(prompt_meta['domain']),
                placeholders=prompt_meta.get('placeholders', {})
            )

            # Test each language and formality
            for language in exp_config.languages:
                for formality_str in exp_config.formality_levels:
                    formality = FormalityLevel(formality_str)

                    # Adapt and evaluate
                    variant = evaluator.adapt_prompt(template, language, formality)

                    domain_config = models_config.get('generation_configs', {}).get(
                        prompt_meta['domain'],
                        models_config['generation_defaults']
                    )
                    # Filter out 'note' fields that aren't part of GenerationConfig
                    config_params = {k: v for k, v in domain_config.items() if k != 'note'}
                    config = GenerationConfig(**config_params)

                    response = evaluator.evaluate_variant(variant, config)

                    # Cache results
                    cache.cache_variant(variant)
                    cache.cache_response(response, prompt_id, language, formality_str)

                    # Track result
                    tracker.store_result(experiment.id, {
                        "prompt_id": prompt_id,
                        "language": language,
                        "formality": formality_str,
                        "variant": variant.to_dict(),
                        "response": response.to_dict()
                    })

                    results_count += 1

    # Update experiment
    tracker.update_experiment(
        experiment,
        status="completed",
        results_summary={
            "total_evaluations": results_count,
            "prompts": len(exp_config.prompt_ids),
            "languages": exp_config.languages,
            "formality_levels": exp_config.formality_levels
        }
    )

    click.echo(click.style(f"\n✅ Benchmark complete!", fg="green", bold=True))
    click.echo(f"   Results cached for demo mode")
    click.echo(f"   Experiment ID: {experiment.id}")
    click.echo(f"\nNext: mpo report {list(prompts_config['prompts'].keys())[0]}")


# Usage examples:
#   mpo report business_email         # Generate text report for prompt
#   mpo report creative_story         # Compare all language variants
@cli.command()
@click.argument('prompt_id')
def report(prompt_id: str):
    """Generate comparison report for a prompt across languages."""

    click.echo(f"📊 Generating report for: {click.style(prompt_id, fg='cyan', bold=True)}\n")

    # Load configs
    with open(CONFIG_DIR / "prompts.yaml") as f:
        prompts_config = yaml.safe_load(f)

    if prompt_id not in prompts_config['prompts']:
        click.echo(click.style(f"❌ Unknown prompt: {prompt_id}", fg="red"))
        return

    cache = CacheManager(str(CACHE_DIR))
    prompt_meta = prompts_config['prompts'][prompt_id]

    # Collect all cached responses
    languages = SUPPORTED_LANGUAGES[:3]  # Use first 3 languages (en, de, es)

    click.echo("Language | Formality | Cached | Words | Cultural Score")
    click.echo("-" * 60)

    for lang in languages:
        for formal in FORMALITY_LEVELS:
            response = cache.get_cached_response(prompt_id, lang, formal)

            if response:
                quant = quantitative.calculate_all_quantitative_metrics(
                    response.content, response.tokens_output, lang
                )
                qual = qualitative.calculate_all_qualitative_metrics(
                    response.content, lang, formal, prompt_meta['domain']
                )

                word_count = quant['length_metrics']['word_count']
                cultural_score = qual['cultural_appropriateness']['overall_score']

                click.echo(
                    f"{lang:8} | {formal:9} | ✅     | "
                    f"{word_count:5} | {cultural_score:.1f}/5.0"
                )
            else:
                click.echo(f"{lang:8} | {formal:9} | ❌     | -     | -")

    click.echo(f"\n💡 Tip: Run 'mpo benchmark' to generate all cached responses")


# Usage examples:
#   mpo html-report business_email                    # Generate HTML report
#   mpo html-report product_copy -o reports/my.html   # Custom output path
@cli.command('html-report')
@click.argument('prompt_id')
@click.option('--output', '-o', help='Output file path (default: reports/{prompt_id}_report.html)')
def html_report(prompt_id: str, output: Optional[str]):
    """Generate interactive HTML report with Plotly visualizations."""
    from ..reports import HTMLReportGenerator

    click.echo(f"📊 Generating HTML report for: {click.style(prompt_id, fg='cyan', bold=True)}\n")

    # Load configs
    with open(CONFIG_DIR / "prompts.yaml") as f:
        prompts_config = yaml.safe_load(f)

    if prompt_id not in prompts_config['prompts']:
        click.echo(click.style(f"❌ Unknown prompt: {prompt_id}", fg="red"))
        return

    cache = CacheManager(str(CACHE_DIR))
    generator = HTMLReportGenerator(cache)

    try:
        output_path = generator.generate_prompt_report(
            prompt_id,
            output_path=Path(output) if output else None
        )

        click.echo(click.style(f"✅ Report generated successfully!", fg="green"))
        click.echo(f"📄 Output: {output_path}")
        click.echo(f"\n💡 Open in browser: open {output_path}")

    except Exception as e:
        click.echo(click.style(f"❌ Error generating report: {str(e)}", fg="red"))
        raise


# Usage examples:
#   mpo list-prompts                  # Show all available prompt templates
@cli.command()
def list_prompts():
    """List all available prompt templates."""

    with open(CONFIG_DIR / "prompts.yaml") as f:
        prompts_config = yaml.safe_load(f)

    click.echo(click.style("\n📝 Available Prompts:\n", fg="cyan", bold=True))

    for prompt_id, meta in prompts_config['prompts'].items():
        click.echo(f"  {click.style(prompt_id, fg='green', bold=True)}")
        click.echo(f"    Domain: {meta['domain']}")
        click.echo(f"    Description: {meta['description']}")
        click.echo()


# Usage examples:
#   mpo cache-status                  # Show cache statistics and validation
@cli.command()
def cache_status():
    """Show cache statistics."""

    cache = CacheManager(str(CACHE_DIR))
    stats = cache.list_cached_items()
    validation = cache.validate_cache()

    click.echo(click.style("\n💾 Cache Status:\n", fg="cyan", bold=True))
    click.echo(f"  Total variants cached: {stats['total_variants']}")
    click.echo(f"  Total responses cached: {stats['total_responses']}")
    click.echo(f"  Cache version: {stats['cache_version']}")
    click.echo(f"  Cache directory: {CACHE_DIR}")

    if validation['valid']:
        click.echo(click.style("\n  ✅ Cache is valid", fg="green"))
    else:
        click.echo(click.style("\n  ⚠️  Cache has issues:", fg="yellow"))
        for issue in validation['issues']:
            click.echo(f"     - {issue}")


if __name__ == "__main__":
    cli()
