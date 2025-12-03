# Architecture & Design Decisions

## Overview

The Multilingual Prompt Optimizer (MPO) is designed as a modular, extensible system for cultural adaptation of LLM prompts. This document outlines key architectural decisions and their rationales.

## Design Principles

### 1. **Modularity & Extensibility**
Every component is designed to be easily replaceable or extended:
- New languages: Add adapter class + config
- New LLM providers: Implement AbstractLLMProvider
- New metrics: Add to metrics module
- New storage backends: Swap CacheManager implementation

### 2. **Separation of Concerns**
Clear boundaries between:
- **Core Logic** (`core/`): Prompt handling, adaptation, evaluation
- **Infrastructure** (`providers/`, `storage/`): External services, persistence
- **Metrics** (`metrics/`): Evaluation logic
- **Interface** (`cli/`, `ui/`): User interaction

### 3. **Testability**
- Abstract interfaces enable mocking (MockAnthropicProvider)
- Pure functions for metrics (no side effects)
- Dependency injection throughout
- Mock data for testing without API costs

### 4. **Reproducibility**
- Version-controlled configuration (YAML)
- Experiment tracking with metadata
- Cached results for demo mode
- Deterministic evaluation pipeline

---

## Architectural Decisions (ADR-Style)

### ADR-001: Cultural Adaptation Strategy

**Context:**
Need to transform prompts beyond simple translation to account for cultural communication norms.

**Decision:**
Use **hybrid adaptation strategy** combining deterministic programmatic rules with LLM-based cultural refinement.

**Rationale:**
This two-phase approach leverages the strengths of both programmatic and LLM-based adaptation:

**Phase 1: Programmatic Adaptation (Structural)**
- **Pros:**
  - Deterministic and explainable
  - Zero runtime costs
  - Fast (no API calls)
  - Easy to version control and document
  - Reliable for structural elements (greetings, closings, pronouns)
- **Cons:**
  - Limited to predefined rules
  - Cannot handle nuanced cultural expression

**Phase 2: LLM Refinement (Cultural Nuance)**
- **Pros:**
  - Handles subtle cultural nuances (tone, argumentation patterns, idioms)
  - Context-aware adaptations
  - More natural-sounding output
  - Adapts to domain-specific requirements
- **Cons:**
  - Additional API cost (~$0.002-0.01 per adaptation)
  - Slight latency (~1-2 seconds)
  - Non-deterministic (mitigated by low temperature=0.3)

**Combined Benefits:**
- Best of both worlds: structural consistency + cultural nuance
- Graceful degradation: Falls back to programmatic if LLM unavailable
- Cost-effective: Only LLM-refines after efficient programmatic scaffolding
- Transparent: Clear separation between rule-based and AI-enhanced adaptation

**Alternatives Considered:**
1. Programmatic-only (original approach) - lacks cultural nuance for complex adaptations
2. LLM-only adaptation - expensive, loses deterministic structure, harder to debug
3. Translation API + post-processing - lacks cultural depth
4. Fine-tuned models - high complexity, inflexible

**Implementation:**
- Abstract `CulturalAdapter` base class with two-phase orchestration
- Language-specific subclasses (EnglishAdapter, GermanAdapter, SpanishAdapter)
- Each adapter implements:
  - `_apply_programmatic_adaptations()`: Structural scaffolding
  - `_build_llm_adaptation_prompt()`: Cultural refinement instructions
- Configuration-driven parameters (languages.yaml)
- Optional LLM provider passed to adapters
- Automatic mode selection based on config + provider availability

---

### ADR-002: LLM Provider Abstraction

**Context:**
Need to support multiple LLM providers (Anthropic, OpenAI, etc.) for comparison.

**Decision:**
Use **abstract provider interface** with concrete implementations.

**Rationale:**
- Allows easy swapping between providers
- Enables mock providers for testing
- Future-proof for multi-provider comparison
- Follows Dependency Inversion Principle (SOLID)

**Implementation:**
```python
class AbstractLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, config: GenerationConfig) -> Dict:
        pass

class AnthropicProvider(AbstractLLMProvider):
    # Concrete implementation
```

**Trade-offs:**
- Slight added complexity vs. direct API calls
- Worth it for flexibility and testability

---

### ADR-003: Storage Strategy

**Context:**
Need to cache responses for demo mode (zero API costs) while maintaining reproducibility.

**Decision:**
Use **JSON files for cache** with optional SQLite for complex queries.

**Rationale:**
- **JSON files:**
  - Git-friendly (version control of experiments)
  - Human-readable (transparency)
  - No database setup required
  - Easy to share (just commit to repo)
- **SQLite (optional):**
  - For aggregation queries during analysis
  - Not required for core functionality

**Alternatives Considered:**
1. Database-only (PostgreSQL): Overkill for portfolio project
2. Pickle files: Not human-readable, versioning issues
3. Cloud storage (S3): Adds deployment complexity

**Implementation:**
- `CacheManager` for JSON-based cache
- `ExperimentTracker` for experiment logs
- Both use filesystem, can be extended

---

### ADR-004: Metrics Approach

**Context:**
Need both quantitative (measurable) and qualitative (judgment-based) evaluation.

**Decision:**
Implement **dual metrics system**:
1. Quantitative: Automated calculations (tokens, length, diversity)
2. Qualitative: Rule-based rubric (cultural appropriateness)

**Rationale:**
- Quantitative shows numerical rigor
- Qualitative demonstrates domain expertise
- Combined approach more compelling than either alone

**Limitations:**
- Qualitative metrics are heuristic-based (not ML-based)
- Future: Could add human evaluation or fine-tuned classifiers

**Implementation:**
- `metrics/quantitative.py`: Pure functions, no dependencies on LLM
- `metrics/qualitative.py`: Rubric-based scoring with cultural rules

---

### ADR-005: Demo Mode Architecture

**Context:**
Non-technical viewers shouldn't need API keys to try the tool.

**Decision:**
Implement **cache-first demo mode** with pre-generated responses.

**Rationale:**
- Lowers barrier to entry (anyone can run demo)
- Showcases results without API costs
- Enables offline demos

**Implementation:**
```python
if demo_mode:
    response = cache.get_cached_response(...)
else:
    response = provider.generate(...)
    cache.cache_response(...)
```

**Developer Workflow:**
1. One-time: Run `mpo benchmark --live` (costs ~$1-2)
2. Commit cached responses to Git
3. Users run `mpo benchmark --demo` (free)

---

### ADR-006: CLI vs. Web UI Priority

**Context:**
Limited time for portfolio project - prioritize CLI or web UI?

**Decision:**
**CLI-first with optional Gradio UI** for broader accessibility.

**Rationale:**
- CLI demonstrates engineering rigor (proper tooling)
- Gradio adds visual appeal
- Both serve different audiences:
  - CLI: Technical evaluators, extensibility
  - Gradio: visual learners

**Implementation:**
- Phase 1: Robust CLI with full functionality
- Phase 2: Gradio wrapper around core logic (reuse, don't duplicate)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI / Gradio UI                      │
│                    (User Interface Layer)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     PromptEvaluator                          │
│              (Orchestration & Workflow)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PromptTemplate│  │PromptVariant │  │  LLMResponse │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────┬───────────────┬────────────────┬────────────────┘
            │               │                │
            ▼               ▼                ▼
    ┌─────────────┐  ┌────────────┐  ┌──────────────┐
    │  Adapters   │  │ Providers  │  │   Metrics    │
    │             │  │            │  │              │
    │ - German    │  │ - Anthropic│  │ - Quant.     │
    │ - Spanish   │  │ - Mock     │  │ - Qual.      │
    │ - English   │  │ - (OpenAI) │  │ - Comp.      │
    └─────────────┘  └────────────┘  └──────────────┘
            │               │                │
            ▼               ▼                ▼
    ┌─────────────────────────────────────────────┐
    │            Storage & Persistence             │
    │  ┌────────────┐        ┌──────────────────┐│
    │  │CacheManager│        │ExperimentTracker ││
    │  │  (Demo)    │        │  (Reproducibility)││
    │  └────────────┘        └──────────────────┘│
    └─────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Config Files │
                    │   (YAML)     │
                    └──────────────┘
```

---

## Data Flow

### Evaluation Pipeline

1. **Input**: Prompt template + language + formality
2. **Adaptation**: CulturalAdapter transforms based on config
3. **Generation**: LLMProvider generates response (or retrieves from cache)
4. **Evaluation**: Metrics modules calculate scores
5. **Storage**: Results cached and tracked
6. **Output**: Display to user or generate report

### Cache Flow (Demo Mode)

```
┌─────────┐      ┌─────────────┐      ┌──────────┐
│ User    │─────▶│ CLI Command │─────▶│ Cache?   │
│ Request │      │             │      │          │
└─────────┘      └─────────────┘      └────┬─────┘
                                            │
                                ┌───────────┴───────────┐
                                │                       │
                                ▼ YES                   ▼ NO
                        ┌──────────────┐        ┌─────────────┐
                        │ Return Cache │        │ Error or    │
                        │ (Instant)    │        │ Prompt Live │
                        └──────────────┘        └─────────────┘
```

---

## Code Quality Standards

### Type Safety
- Type hints on all functions
- mypy static type checking
- Dataclasses for structured data

### Testing Strategy
- Unit tests: Core logic (adapters, metrics)
- Integration tests: Full evaluation pipeline
- Mocking: External APIs (no real API calls in tests)
- Coverage target: 80%+

### Documentation
- Docstrings: Google style
- Inline comments: Only for complex logic
- README: Dual audience (technical + non-technical)
- ADRs: This document

### Code Style
- Black formatter (100 char line length)
- isort for imports
- flake8 linting
- Pre-commit hooks (future)

---

## Performance Considerations

### Caching Strategy
- Cache variants: Avoid re-running adapters
- Cache responses: Avoid redundant API calls
- Cache metadata: Quick lookups without file reads

### Scalability
- Current: Single-threaded, local filesystem
- Future: Async API calls, database backend, distributed caching

### Cost Optimization
- Demo mode: Zero runtime costs
- Batch evaluation: Reuse provider connection
- Token efficiency: Metrics track cost per evaluation

---

## Security Considerations

### API Key Management
- Environment variables (.env file)
- Never committed to Git (.gitignore)
- Clear error messages for missing keys

### Input Validation
- Template ID validation
- Language code validation
- Formality level enum (prevents invalid values)

### Data Privacy
- No PII in prompts (configurable)
- Results stored locally (not cloud)
- Export control for experiment data

---

## Extension Points

### Adding a New Language

1. Create adapter class:
```python
class FrenchAdapter(CulturalAdapter):
    def adapt(self, template, formality):
        # Implement French-specific rules
```

2. Add to factory:
```python
adapters = {
    "fr": FrenchAdapter,
    # ...
}
```

3. Add config to `languages.yaml`

### Adding a New LLM Provider

1. Implement interface:
```python
class OpenAIProvider(AbstractLLMProvider):
    def generate(self, prompt, config):
        # OpenAI API call
```

2. Update CLI to support provider selection

### Adding a New Metric

1. Add function to `metrics/quantitative.py` or `qualitative.py`
2. Include in aggregation functions
3. Update report generation

---

## Lessons Learned

### What Worked Well
- Abstract interfaces enable flexibility
- Configuration-driven approach reduces hardcoding
- Demo mode makes project accessible
- Type hints catch bugs early

### What Could Be Improved
- Async API calls would speed up batch evaluation
- Database backend for complex analytics
- More sophisticated cultural rules (ML-based?)
- Human-in-the-loop evaluation

### Trade-offs Made
- Simplicity vs. feature completeness (MVP focus)
- Rule-based vs. ML-based adaptation (explainability)
- Local storage vs. cloud (simplicity)
- CLI vs. web UI priority (developer audience first)

---

## References

- **Design Patterns**: Gang of Four (Strategy, Factory, Repository)
- **Python Best Practices**: PEP 8, Python Packaging Guide
- **Testing**: pytest documentation, Test-Driven Development
- **Architecture**: Clean Architecture (Robert C. Martin), Domain-Driven Design

