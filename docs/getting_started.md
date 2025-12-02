# Getting Started with Multilingual Prompt Optimizer

Welcome to the Multilingual Prompt Optimizer (MPO)! This guide will help you get up and running quickly.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **pip** package manager
- **(Optional)** An Anthropic API key for live mode

## Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/multilingual-prompt-optimizer.git
cd multilingual-prompt-optimizer

# Install the package
pip install -e .
```

### Option 2: With Optional Dependencies

```bash
# Install with development tools
pip install -e ".[dev]"

# Install with UI components (Gradio, Jupyter)
pip install -e ".[ui]"

# Install everything
pip install -e ".[all]"
```

## Quick Start

### 1. Initialize the Project

```bash
mpo init
```

This command verifies your installation and creates necessary directories.

### 2. Try Demo Mode (No API Key Required)

Demo mode uses pre-cached responses, so you can explore the tool without any API costs:

```bash
# Test a business email prompt in formal German
mpo test business_email --language de --formality formal --demo

# Try Spanish with neutral formality
mpo test business_email --language es --formality neutral --demo

# English baseline
mpo test business_email --language en --formality neutral --demo
```

### 3. List Available Prompts

```bash
mpo list-prompts
```

Available prompts:
- `business_email` - Timeline extension request
- `technical_explanation` - RAG architecture explanation
- `creative_story` - Mystery novel opening
- `persuasive_pitch` - Tool adoption proposal
- `instructional_guide` - Git tutorial for beginners

### 4. Choosing Your LLM Provider

MPO supports multiple LLM providers. Choose based on your needs:

#### Option A: Demo Mode (Recommended for First Try)
Uses pre-cached responses - **free and instant**:
```bash
mpo test business_email --language de --formality formal --demo
```

✅ Best for: Quick evaluation, no setup needed

#### Option B: Anthropic Claude API (Best Quality)
High-quality cultural adaptation - **costs ~$0.02 per request**:

```bash
# 1. Create environment file
cp .env.example .env

# 2. Edit .env and add your API key
# ANTHROPIC_API_KEY=your_key_here

# 3. Run in live mode
mpo test business_email --language de --formality formal --live
```

✅ Best for: Production use, highest quality results

#### Option C: LMStudio (Free Local Models)
Run models locally - **completely free, no API needed**:

```bash
# 1. Install LMStudio
# Download from: https://lmstudio.ai/

# 2. In LMStudio application:
#    a. Download a model (recommended):
#       - "mistralai/Mistral-7B-Instruct-v0.3" (requires ~16GB RAM)
#       - "google/gemma-2-12b-instruct" (requires ~24GB RAM, better quality)
#
#    b. Start the local server:
#       - Click "Local Server" tab
#       - Click "Start Server"
#       - Verify it's running at http://localhost:1234

# 3. Test connection
curl http://localhost:1234/v1/models

# 4. Use with MPO
mpo test business_email --provider local --live --language de --formality formal

# 5. Run full benchmark (completely free!)
mpo benchmark --provider local
```

✅ Best for: Privacy, offline use, unlimited testing at zero cost

**Provider Comparison:**

| Feature | Demo | Anthropic | LMStudio |
|---------|------|-----------|----------|
| **Cost** | Free | ~$1-2 for benchmark | Free |
| **Quality** | Good | Excellent | Good |
| **Speed** | Instant | Fast | Medium (depends on hardware) |
| **Setup** | None | API key | Install app + download model |
| **Internet Required** | Yes (first time) | Yes | No (after model download) |
| **Privacy** | Cached responses | API calls | 100% local |

**Recommendation:**
1. Start with **Demo mode** to explore features
2. Try **LMStudio** for free unlimited testing
3. Use **Anthropic** for production/best quality

## Basic Usage

### Testing Single Prompts

The `mpo test` command adapts and evaluates a single prompt:

```bash
mpo test <prompt_id> --language <en|de|es> --formality <casual|neutral|formal> [--demo|--live] [--provider <anthropic|local>]
```

**Parameters:**
- `prompt_id`: One of the 5 available prompts (see list above)
- `--language`: Target language (en=English, de=German, es=Spanish)
- `--formality`: Communication style
  - `casual`: Informal, friendly (du/tú)
  - `neutral`: Professional standard
  - `formal`: Official, respectful (Sie/usted)
- `--demo`: Use cached responses (free, instant)
- `--live`: Generate fresh responses
- `--provider`: Choose LLM provider (default: anthropic)
  - `anthropic`: Anthropic Claude API (requires API key)
  - `local`: LMStudio local server (requires LMStudio running)

**Examples:**
```bash
# Demo mode (cached)
mpo test business_email --language de --formality formal --demo

# Anthropic API (live)
mpo test business_email --language de --formality formal --live

# LMStudio (live, local)
mpo test business_email --language de --formality formal --live --provider local
```

**Example Output:**
```
📝 Testing prompt: business_email
   Language: de | Formality: formal
   Mode: 🟢 DEMO

🔄 Adapted Prompt:
Sehr geehrte Damen und Herren,
[adapted content...]

📊 Metrics:
   Tokens (in/out): 156/234
   Lexical diversity: 0.742
   Cultural appropriateness: Excellent
```

### Running Benchmarks

Test all combinations (5 prompts × 3 languages × 3 formality levels = 45 tests):

```bash
# Demo mode (instant, free)
mpo benchmark --demo

# Live mode (generates fresh responses, costs ~$1-2)
mpo benchmark --live
```

### Generating Reports

Compare adaptations across languages and formality levels:

```bash
mpo report business_email
```

### Checking Cache Status

```bash
mpo cache-status
```

Shows how many cached responses are available for demo mode.

## Understanding Cultural Adaptation

MPO doesn't just translate prompts - it adapts them culturally:

### German (Formal Example)
- ✅ Uses "Sie" (formal you) instead of "du"
- ✅ Adds structured greeting: "Sehr geehrte Damen und Herren"
- ✅ Direct, concise phrasing (German communication preference)
- ✅ Professional closing: "Mit freundlichen Grüßen"

### Spanish (Formal Example)
- ✅ Uses "usted" (formal you) instead of "tú"
- ✅ Warm opening with relationship acknowledgment
- ✅ Contextual preambles (Spanish communication preference)
- ✅ Respectful closing: "Atentamente"

### English (Baseline)
- ✅ Task-focused, minimal formality markers
- ✅ Direct communication style
- ✅ Standard professional tone

## Next Steps

Now that you're set up, explore more:

- 📖 **[Examples](examples.md)** - See before/after adaptation comparisons
- 📊 **[Metrics Guide](metrics_guide.md)** - Understand evaluation metrics
- 🏗️ **[Architecture](architecture.md)** - Learn about the system design
- 🌍 **[Cultural Rationale](cultural_rationale.md)** - Linguistic theory behind adaptations
- 🔧 **[API Reference](api.md)** - Use MPO programmatically

## Troubleshooting

### Import Errors
```bash
# Reinstall in editable mode
pip install -e .
```

### API Key Issues
- Verify your `.env` file contains `ANTHROPIC_API_KEY=sk-...`
- Ensure the `.env` file is in the project root directory
- Try using `--demo` mode to bypass API requirements

### Cache Not Found
- Run `mpo benchmark --live` once to populate the cache
- Or continue using `--live` mode for fresh responses

### LMStudio Connection Issues

**"Cannot connect to LMStudio"**
```bash
# 1. Check if LMStudio is running
curl http://localhost:1234/v1/models

# 2. Verify the server is started in LMStudio
#    - Open LMStudio
#    - Click "Local Server" tab
#    - Ensure "Start Server" button shows server is running
#    - Default URL should be http://localhost:1234

# 3. Check if a model is loaded
#    - In LMStudio, ensure a model is selected and loaded
#    - Look for green "Loaded" status
```

**"Model returns empty or poor responses"**
- Try increasing `max_tokens` in `config/models.yaml`
- Ensure model is fully loaded (not still downloading)
- Use a different model (try Mistral 7B Instruct)
- Check model supports the target language

**"Out of memory errors"**
- Use a smaller model (Mistral 7B instead of Gemma 12B)
- Close other applications to free RAM
- Reduce context length in LMStudio settings

**"LMStudio running on different port"**
```bash
# If your LMStudio uses port 5000 instead of 1234
# Currently requires code modification (future: CLI option)
# For now, change port in LMStudio to use default 1234
```

**For detailed LMStudio setup and troubleshooting:**
See [LMSTUDIO_SETUP.md](LMSTUDIO_SETUP.md)

## Getting Help

- 📖 Check the [main README](../README.md)
- 🐛 [Report issues](https://github.com/YOUR-USERNAME/multilingual-prompt-optimizer/issues)
- 💬 [Contributing guide](../CONTRIBUTING.md)

---

Happy prompt optimizing! 🌍
