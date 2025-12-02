# API Reference

Complete API documentation for using MPO programmatically in your Python projects.

## Table of Contents
- [Installation](#installation)
- [Core Classes](#core-classes)
- [Adapters](#adapters)
- [Providers](#providers)
- [Metrics](#metrics)
- [Storage](#storage)
- [Complete Example](#complete-example)

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Core Classes

### PromptTemplate

Represents a base prompt before cultural adaptation.

```python
from mpo.core.prompt import PromptTemplate, FormalityLevel, PromptDomain

template = PromptTemplate(
    id="business_email",
    content="I need to request an extension...",
    domain=PromptDomain.BUSINESS,
    default_formality=FormalityLevel.NEUTRAL,
    metadata={
        "author": "Monica Guimaraes",
        "version": "1.0"
    }
)
```

**Attributes:**
- `id` (str): Unique identifier
- `content` (str): The prompt text
- `domain` (PromptDomain): Category (BUSINESS, TECHNICAL, CREATIVE, etc.)
- `default_formality` (FormalityLevel): Default formality level
- `metadata` (dict): Additional information

---

### PromptVariant

Represents a culturally-adapted version of a prompt.

```python
from mpo.core.prompt import PromptVariant

variant = PromptVariant(
    template_id="business_email",
    language="de",
    formality=FormalityLevel.FORMAL,
    adapted_content="Sehr geehrte Damen und Herren...",
    adaptation_notes=["Added German greeting", "Used Sie form"]
)
```

**Attributes:**
- `template_id` (str): Reference to original template
- `language` (str): Target language code
- `formality` (FormalityLevel): Formality level
- `adapted_content` (str): The adapted prompt
- `adaptation_notes` (list[str]): Changes made during adaptation

---

### FormalityLevel

Enum representing formality levels.

```python
from mpo.core.prompt import FormalityLevel

FormalityLevel.CASUAL    # Informal, friendly
FormalityLevel.NEUTRAL   # Professional standard
FormalityLevel.FORMAL    # Official, respectful
```

---

### PromptDomain

Enum representing prompt categories.

```python
from mpo.core.prompt import PromptDomain

PromptDomain.BUSINESS       # Business communication
PromptDomain.TECHNICAL      # Technical explanations
PromptDomain.CREATIVE       # Creative writing
PromptDomain.PERSUASIVE     # Persuasive content
PromptDomain.INSTRUCTIONAL  # Tutorials and guides
```

---

## Adapters

### CulturalAdapter (Abstract Base)

Base class for language-specific adapters.

```python
from mpo.core.adapter import CulturalAdapter
from mpo.core.prompt import PromptTemplate, PromptVariant, FormalityLevel

class MyAdapter(CulturalAdapter):
    def adapt(self, template: PromptTemplate, formality: FormalityLevel) -> PromptVariant:
        # Implement adaptation logic
        pass
```

---

### Language-Specific Adapters

#### EnglishAdapter

```python
from mpo.adapters.en_adapter import EnglishAdapter
import yaml

# Load configuration
with open("config/languages.yaml") as f:
    config = yaml.safe_load(f)

adapter = EnglishAdapter(config['languages']['en'])
variant = adapter.adapt(template, FormalityLevel.FORMAL)
```

#### GermanAdapter

```python
from mpo.adapters.de_adapter import GermanAdapter
import yaml

# Load configuration
with open("config/languages.yaml") as f:
    config = yaml.safe_load(f)

adapter = GermanAdapter(config['languages']['de'])
variant = adapter.adapt(template, FormalityLevel.FORMAL)

# German-specific: Uses "Sie" for formal, "du" for casual
```

#### SpanishAdapter

```python
from mpo.adapters.es_adapter import SpanishAdapter
import yaml

# Load configuration
with open("config/languages.yaml") as f:
    config = yaml.safe_load(f)

adapter = SpanishAdapter(config['languages']['es'])
variant = adapter.adapt(template, FormalityLevel.FORMAL)

# Spanish-specific: Uses "usted" for formal, "tú" for casual
```

---

### Adapter Factory Function

Factory function for creating adapters by language code.

```python
from mpo.adapters.factory import get_adapter
import yaml
from pathlib import Path

# Load language configuration
config_dir = Path("config")
with open(config_dir / "languages.yaml") as f:
    lang_config = yaml.safe_load(f)

# Get adapter for a specific language
adapter = get_adapter("de", lang_config['languages']['de'])
variant = adapter.adapt(template, FormalityLevel.FORMAL)

# Or using the shorthand import
from mpo.adapters import get_adapter  # Also exported from package

# Create adapters for all supported languages
for lang_code in ["en", "de", "es"]:
    adapter = get_adapter(lang_code, lang_config['languages'][lang_code])
    # Use adapter...
```

**Function Signature:**
```python
def get_adapter(language_code: str, config: Dict) -> CulturalAdapter:
    """
    Factory function to instantiate the appropriate cultural adapter.

    Args:
        language_code: ISO language code ('en', 'de', 'es')
        config: Language configuration dictionary from languages.yaml

    Returns:
        Appropriate CulturalAdapter subclass instance

    Raises:
        ValueError: If language code is not supported
    """
```

---

## Providers

### AbstractLLMProvider

Base class for LLM API wrappers.

```python
from mpo.providers.base import AbstractLLMProvider
from mpo.core.prompt import LLMResponse

class MyProvider(AbstractLLMProvider):
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        # Implement API call
        pass
```

---

### AnthropicProvider

Wrapper for Anthropic Claude API.

```python
from mpo.providers.anthropic_provider import AnthropicProvider
import os

# Initialize with API key
provider = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Generate response
response = provider.generate(
    prompt="Write a professional email...",
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    temperature=0.7
)

print(response.content)
print(f"Tokens used: {response.tokens_used}")
```

**Parameters:**
- `api_key` (str): Anthropic API key
- `model` (str): Model name (default: claude-sonnet-4-20250514)
- `max_tokens` (int): Maximum response length
- `temperature` (float): Sampling temperature (0-1)

---

### LocalProvider

Wrapper for local LLM servers (e.g., LMStudio).

```python
from mpo.providers.local_provider import LocalProvider

provider = LocalProvider(
    base_url="http://localhost:1234/v1",
    model="local-model"
)

response = provider.generate(prompt="...")
```

---

## Metrics

### QuantitativeMetrics

Automated, objective measurements.

```python
from mpo.metrics.quantitative import QuantitativeMetrics

metrics = QuantitativeMetrics()

# Calculate all metrics
results = metrics.calculate(
    text="Sehr geehrte Damen und Herren...",
    language="de"
)

print(f"Token count: {results['token_count']}")
print(f"Lexical diversity: {results['lexical_diversity']}")
print(f"Sentence count: {results['sentence_count']}")
```

**Available Metrics:**
- `token_count`: Total tokens
- `word_count`: Total words
- `sentence_count`: Total sentences
- `lexical_diversity`: Type-token ratio
- `avg_sentence_length`: Average words per sentence
- `formality_markers`: Detected formality indicators

---

### QualitativeMetrics

Subjective, rubric-based assessments.

```python
from mpo.metrics.qualitative import QualitativeMetrics

metrics = QualitativeMetrics()

# Assess cultural appropriateness
score = metrics.assess_cultural_appropriateness(
    text="Sehr geehrte Damen und Herren...",
    language="de",
    formality="formal",
    domain="business"
)

print(f"Cultural score: {score}/5.0")

# Calculate readability
readability = metrics.calculate_readability(
    text="...",
    language="en"
)

print(f"Flesch score: {readability['flesch_score']}")
```

---

## Storage

### CacheManager

Manages cached responses for demo mode.

```python
from mpo.storage.cache_manager import CacheManager

cache = CacheManager(cache_dir="data/cache")

# Store a response
cache.store_response(
    prompt_id="business_email",
    language="de",
    formality="formal",
    response_text="...",
    metadata={"model": "claude-sonnet-4"}
)

# Retrieve a cached response
response = cache.get_response(
    prompt_id="business_email",
    language="de",
    formality="formal"
)

# Check cache status
status = cache.get_cache_status()
print(f"Cached responses: {status['total_cached']}")
```

---

### ExperimentTracker

Tracks experiments for reproducibility.

```python
from mpo.storage.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker(results_dir="data/experiments")

# Start an experiment
experiment_id = tracker.start_experiment(
    name="benchmark_v1",
    config={
        "model": "claude-sonnet-4",
        "languages": ["en", "de", "es"]
    }
)

# Log results
tracker.log_result(
    experiment_id=experiment_id,
    prompt_id="business_email",
    language="de",
    metrics={"cultural_score": 4.5}
)

# Complete experiment
tracker.complete_experiment(experiment_id)

# Retrieve results
results = tracker.get_experiment_results(experiment_id)
```

---

## Complete Example

Here's a full example using multiple components:

```python
import os
import yaml
from pathlib import Path
from mpo.core.prompt import PromptTemplate, FormalityLevel, PromptDomain
from mpo.adapters.factory import get_adapter
from mpo.providers.anthropic_provider import AnthropicProvider
from mpo.metrics.quantitative import QuantitativeMetrics
from mpo.metrics.qualitative import QualitativeMetrics
from mpo.storage.cache_manager import CacheManager

# 1. Load configuration
config_dir = Path("config")
with open(config_dir / "languages.yaml") as f:
    lang_config = yaml.safe_load(f)

# 2. Create a prompt template
template = PromptTemplate(
    id="my_prompt",
    content="Please explain RAG architecture to executives.",
    domain=PromptDomain.TECHNICAL,
    default_formality=FormalityLevel.FORMAL
)

# 3. Adapt for German formal context
adapter = get_adapter("de", lang_config['languages']['de'])
variant = adapter.adapt(template, FormalityLevel.FORMAL)

print(f"Adapted prompt:\n{variant.adapted_content}\n")
print(f"Adaptation notes: {variant.adaptation_notes}\n")

# 4. Generate response using LLM
provider = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = provider.generate(variant.adapted_content)

print(f"LLM Response:\n{response.content}\n")

# 5. Calculate metrics
quant_metrics = QuantitativeMetrics()
quant_results = quant_metrics.calculate(response.content, language="de")

qual_metrics = QualitativeMetrics()
cultural_score = qual_metrics.assess_cultural_appropriateness(
    response.content,
    language="de",
    formality="formal",
    domain="technical"
)

print(f"Metrics:")
print(f"  Tokens: {quant_results['token_count']}")
print(f"  Lexical diversity: {quant_results['lexical_diversity']:.3f}")
print(f"  Cultural score: {cultural_score}/5.0")

# 6. Cache the response
cache = CacheManager()
cache.store_response(
    prompt_id=template.id,
    language="de",
    formality="formal",
    response_text=response.content,
    metadata={"tokens": response.tokens_used}
)

print("\n✓ Response cached for future demo mode use")
```

---

## Type Hints

MPO uses comprehensive type hints for better IDE support:

```python
from typing import Optional, Dict, List
from mpo.core.prompt import PromptTemplate, PromptVariant, FormalityLevel

def process_prompt(
    template: PromptTemplate,
    language: str,
    formality: FormalityLevel,
    options: Optional[Dict[str, any]] = None
) -> PromptVariant:
    """Process a prompt with type-checked parameters."""
    # Implementation
    pass
```

---

## Error Handling

```python
from mpo.adapters.factory import get_adapter
import yaml

# Load configuration
with open("config/languages.yaml") as f:
    lang_config = yaml.safe_load(f)

try:
    # Attempt to use unsupported language
    adapter = get_adapter("fr", lang_config['languages'].get('fr', {}))
except ValueError as e:
    print(f"Language not supported: {e}")
    # Show available languages
    available = list(lang_config['languages'].keys())
    print(f"Available languages: {available}")
    # Output: Available languages: ['en', 'de', 'es']
```

---

## Configuration

Load custom configurations:

```python
import yaml
from pathlib import Path

# Load language configurations
with open("config/languages.yaml") as f:
    lang_config = yaml.safe_load(f)

# Access German configuration
german_config = lang_config["languages"]["de"]
print(german_config["formal_markers"])
```

---

## Further Reading

- **[Getting Started](getting_started.md)** - Basic usage patterns
- **[Examples](examples.md)** - See the API in action
- **[Architecture](architecture.md)** - System design and patterns
- **[Contributing](../CONTRIBUTING.md)** - Extend the API

---

*For questions or issues, please open a [GitHub issue](https://github.com/YOUR-USERNAME/multilingual-prompt-optimizer/issues).*
