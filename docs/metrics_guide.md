# Metrics Guide

This guide explains how MPO evaluates prompt adaptations across languages and formality levels.

## Table of Contents
- [Overview](#overview)
- [Quantitative Metrics](#quantitative-metrics)
- [Qualitative Metrics](#qualitative-metrics)
- [Comparative Metrics](#comparative-metrics)
- [Interpretation](#interpretation)

## Overview

MPO uses a multi-faceted evaluation approach combining:

1. **Quantitative metrics** - Objective, automated measurements
2. **Qualitative metrics** - Subjective, rubric-based assessments
3. **Comparative metrics** - Cross-language and cross-formality comparisons

All metrics are calculated automatically when you run `mpo test` or `mpo benchmark`.

## Quantitative Metrics

### Token Efficiency

**Definition:** Measures how efficiently the adapted prompt uses tokens relative to information conveyed.

**Metrics:**
- **Token count** (input/output): Raw token usage
- **Tokens per sentence**: Average tokens per sentence
- **Tokens per word**: Token-to-word ratio

**Formula:**
```
Token Efficiency = Total Tokens / Number of Sentences
```

**Why it matters:**
- API costs are based on token usage
- Some languages (e.g., German) may use fewer tokens for equivalent meaning
- Indicates prompt conciseness

**Example Output:**
```
Tokens (in/out): 156/234
Tokens per sentence: 26.0
Tokens per word: 1.79
```

---

### Lexical Diversity

**Definition:** Measures vocabulary richness using Type-Token Ratio (TTR).

**Formula:**
```
Lexical Diversity = Unique Words / Total Words
```

**Range:** 0.0 to 1.0 (higher = more diverse vocabulary)

**Why it matters:**
- Higher diversity often indicates more sophisticated language
- Can reveal differences in language expressiveness
- Helps identify repetitive or simplistic responses

**Example Output:**
```
Lexical diversity: 0.742
```

**Interpretation:**
- 0.6-0.7: Good diversity
- 0.7-0.8: Excellent diversity
- 0.8+: Very high diversity (might indicate overly complex language)

---

### Structural Features

**Definition:** Detects presence of cultural communication markers.

**Detected Features:**
- **Greetings**: Opening salutations
  - German: "Sehr geehrte...", "Liebe..."
  - Spanish: "Estimados...", "Queridos..."
  - English: "Dear...", "Hi...", "Hello..."

- **Closings**: Closing phrases
  - German: "Mit freundlichen Grüßen", "Viele Grüße"
  - Spanish: "Atentamente", "Cordialmente", "Saludos"
  - English: "Best regards", "Sincerely", "Cheers"

- **Lists/Structure**: Numbered or bulleted lists
- **Emphasis**: Use of bold, italics, or formatting

**Why it matters:**
- Confirms cultural adaptation is applied
- Ensures appropriate formality level
- Validates adherence to language norms

**Example Output:**
```
Structural features:
  ✓ Has greeting: "Sehr geehrte Damen und Herren"
  ✓ Has closing: "Mit freundlichen Grüßen"
  ✓ Uses lists: Yes (3 items)
```

---

### Formality Marker Detection

**Definition:** Identifies language-specific formality indicators.

**German Markers:**
- **Formal**: "Sie", "Ihnen", "Hochachtungsvoll"
- **Casual**: "du", "dir", "Tschüss"

**Spanish Markers:**
- **Formal**: "usted", "ustedes", "señor/señora"
- **Casual**: "tú", "vos", "amigo/amiga"

**Why it matters:**
- Ensures correct pronoun usage for formality level
- Validates cultural appropriateness
- Critical for German and Spanish adaptations

**Example Output:**
```
Formality markers:
  Language: German
  Detected: Sie (formal)
  Expected: formal
  ✓ Match: Yes
```

---

### Sentiment Analysis

**Definition:** Measures emotional tone using basic sentiment analysis.

**Scores:**
- **Polarity**: Negative (-1) to Positive (+1)
- **Subjectivity**: Objective (0) to Subjective (1)

**Why it matters:**
- Validates tone appropriateness for context
- Identifies unintended emotional shifts
- Useful for persuasive and creative prompts

**Example Output:**
```
Sentiment:
  Polarity: 0.15 (slightly positive)
  Subjectivity: 0.42 (moderately objective)
```

---

## Qualitative Metrics

### Cultural Appropriateness Score

**Definition:** Subjective rubric-based assessment of cultural fit.

**Scale:** 1-5 (Poor to Excellent)

**Evaluation Criteria:**

| Score | Rating | Description |
|-------|--------|-------------|
| 5 | Excellent | Perfect cultural adaptation, native-like quality |
| 4 | Good | Appropriate cultural markers, minor improvements possible |
| 3 | Acceptable | Basic adaptation present, room for improvement |
| 2 | Poor | Minimal adaptation, feels translated |
| 1 | Inadequate | No cultural adaptation, inappropriate for context |

**Factors Considered:**
- ✅ Correct formality markers (Sie/du, usted/tú)
- ✅ Appropriate greeting/closing conventions
- ✅ Communication style (direct vs. relational)
- ✅ Structural preferences (German structured, Spanish warm)
- ✅ Idiomatic naturalness

**Example Output:**
```
Cultural Appropriateness: 5/5 (Excellent)
Notes: Perfect use of Sie form, structured format appropriate
       for German business context, natural phrasing
```

---

### Readability Score

**Definition:** Measures text complexity and reading ease.

**English:**
- **Flesch Reading Ease**: 0-100 (higher = easier)
- **Flesch-Kincaid Grade**: U.S. grade level

**German/Spanish:**
- Custom readability metrics adapted for language structure

**Why it matters:**
- Ensures appropriate complexity for audience
- Validates clarity of communication
- Helps maintain accessibility

**Example Output:**
```
Readability:
  Flesch Reading Ease: 62.5 (Standard)
  Grade Level: 8.2
  Assessment: Appropriate for general business audience
```

**Interpretation (Flesch Reading Ease):**
- 90-100: Very easy (5th grade)
- 60-70: Standard (8th-9th grade)
- 30-50: Difficult (college)
- 0-30: Very difficult (professional)

---

## Comparative Metrics

### Baseline Comparison

**Definition:** Compares adapted versions to English baseline.

**Metrics:**
- Token efficiency change
- Structural feature differences
- Sentiment shifts

**Example Output:**
```
Comparison to English baseline:
  Token efficiency: +15% (more efficient)
  Structural additions: +2 features (greeting, closing)
  Sentiment change: +0.05 (slightly warmer)
```

---

### Cross-Language Analysis

**Definition:** Compares same prompt across different languages.

**Use Cases:**
- Identify which language adaptations are most effective
- Understand language-specific patterns
- Validate consistency across languages

**Example Output:**
```
Cross-Language Comparison (business_email, formal):

  Language | Tokens | Lexical Div | Cultural Score
  ---------|--------|-------------|---------------
  English  | 142    | 0.68        | 4.0
  German   | 156    | 0.74        | 4.5
  Spanish  | 168    | 0.71        | 4.7
```

---

### Cross-Formality Analysis

**Definition:** Compares same language across formality levels.

**Example Output:**
```
Cross-Formality Comparison (German, business_email):

  Formality | Pronoun | Greeting Type | Cultural Score
  ----------|---------|---------------|---------------
  Casual    | du      | "Hallo,"      | 4.2
  Neutral   | Sie     | "Guten Tag,"  | 4.3
  Formal    | Sie     | "Sehr geehrte"| 4.5
```

---

## Interpretation

### Reading Metric Reports

When you run `mpo test`, you'll see output like this:

```
📊 Metrics:
   Tokens (in/out): 156/234
   Words: 87
   Sentences: 6
   Lexical diversity: 0.742

   Formality markers: ✓ Sie (formal)
   Structural features: ✓ Greeting, ✓ Closing, ✓ Lists

   Cultural appropriateness: 4.5/5.0 (Excellent)
   Readability: 65.2 (Standard)

   Sentiment: +0.15 polarity, 0.42 subjectivity
```

### What to Look For

**Good Adaptation:**
- ✅ Formality markers match target level
- ✅ Cultural score 4.0+
- ✅ Appropriate structural features present
- ✅ Lexical diversity 0.6+
- ✅ Readability appropriate for context

**Needs Improvement:**
- ❌ Missing cultural markers
- ❌ Cultural score below 3.5
- ❌ No greeting/closing for formal contexts
- ❌ Low lexical diversity (<0.5)
- ❌ Inappropriate readability level

---

## Accessing Metrics Programmatically

You can use MPO's metrics modules in your own code:

```python
from mpo.metrics.quantitative import QuantitativeMetrics
from mpo.metrics.qualitative import QualitativeMetrics

# Calculate quantitative metrics
quant = QuantitativeMetrics()
metrics = quant.calculate(response_text, language="de")

# Calculate qualitative metrics
qual = QualitativeMetrics()
cultural_score = qual.assess_cultural_appropriateness(
    response_text,
    language="de",
    formality="formal"
)
```

See the [API Reference](api.md) for detailed usage.

---

## Further Reading

- **[Examples](examples.md)** - See metrics in action with real adaptations
- **[Cultural Rationale](cultural_rationale.md)** - Understanding the "why" behind metrics
- **[Architecture](architecture.md)** - How metrics are implemented

---

*Metrics help us measure what matters: cultural appropriateness and communication effectiveness.*
