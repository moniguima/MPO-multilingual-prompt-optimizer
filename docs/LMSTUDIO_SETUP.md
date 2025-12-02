# LMStudio Setup Guide

## Quick Start

### 1. Install LMStudio
Download from: https://lmstudio.ai/

### 2. Download a Model
Recommended models for multilingual support:

**Option 1: Gemma 3 12B** (Better quality, requires more RAM)
- Search for: `google/gemma-2-12b-instruct`
- Requires: ~24GB RAM
- Best for: High-quality multilingual responses

**Option 2: Mistral 7B Instruct v0.3** (Faster, lower RAM)
- Search for: `mistralai/Mistral-7B-Instruct-v0.3`
- Requires: ~16GB RAM
- Best for: Quick iterations, good DE/ES support

### 3. Start the Server
1. Load your chosen model in LMStudio
2. Click "Local Server" tab
3. Click "Start Server"
4. Verify it's running at: `http://localhost:1234`

### 4. Test Connection
```bash
# Test if LMStudio is accessible
curl http://localhost:1234/v1/models

# Or test with Python
python -c "from mpo.providers import LocalLLMProvider; print('Connected!' if LocalLLMProvider().is_available() else 'Not connected')"
```

## Usage with MPO

### Test Single Prompt
```bash
# Test with German, formal tone
mpo test business_email --provider local --live -l de -f formal

# Test with Spanish, casual tone
mpo test business_email --provider local --live -l es -f casual

# Test with English, neutral tone
mpo test business_email --provider local --live -l en -f neutral
```

### Run Full Benchmark
```bash
# Generate cache using local model (free!)
mpo benchmark --provider local

# This will test:
# - 5 prompts
# - 3 languages (en, de, es)
# - 3 formality levels (casual, neutral, formal)
# - Total: 45 evaluations
```

### Compare Providers
```bash
# Test same prompt with different providers
mpo test business_email --provider local --live -l de -f formal
mpo test business_email --provider anthropic --live -l de -f formal
mpo test business_email --provider mock --live -l de -f formal
```

## Expected Response Quality

### Local Models (LMStudio)
- ✅ Real multilingual responses
- ✅ Good German/Spanish support
- ✅ Zero cost
- ⚠️ May be less culturally nuanced than Claude
- ⚠️ Slower than API (depends on hardware)

### Claude (Anthropic)
- ✅ Highest quality cultural adaptation
- ✅ Best multilingual understanding
- ✅ Fast API response
- ❌ Costs money (~$1-2 for full benchmark)

### Mock Provider
- ✅ Zero cost
- ✅ Instant responses
- ❌ Unrealistic/templated responses
- ✅ Good for testing workflow

## Troubleshooting

### "Cannot connect to LMStudio"
1. Check LMStudio is running
2. Verify server is at http://localhost:1234
3. Ensure a model is loaded
4. Check firewall settings

### "Model returns empty responses"
1. Try increasing max_tokens in config/models.yaml
2. Check model is fully loaded (not still downloading)
3. Try a different model

### "Out of memory"
1. Use smaller model (Mistral 7B instead of Gemma 12B)
2. Close other applications
3. Reduce context length in LMStudio settings

## Configuration

### Change LMStudio Port
If LMStudio runs on different port:

```python
from mpo.providers import LocalLLMProvider

provider = LocalLLMProvider(base_url="http://localhost:5000/v1")
```

### Adjust Generation Settings
Edit `config/models.yaml`:
```yaml
generation_defaults:
  temperature: 0.7
  max_tokens: 1024  # Increase for longer responses
  top_p: 1.0
```

## Performance Tips

1. **Faster inference**: Use Mistral 7B instead of Gemma 12B
2. **Better quality**: Use Gemma 12B or Claude
3. **Batch processing**: Run benchmark overnight
4. **Cache results**: Results are cached after first run

## Sample Output

When testing with local provider, you'll see:
```
📝 Testing prompt: business_email
   Language: de | Formality: formal
   Provider: local
   Mode: 🔴 LIVE

📡 Connected to LMStudio - Model: gemma-2-12b-instruct

🔄 Adapted Prompt:
Sehr geehrte Damen und Herren

Ich möchte Sie höflich um Folgendes bitten:
...

🚀 Generating response...

🤖 LLM Response:
[German response from local model]

💾 Cached for future demo use

📊 Metrics:
   Tokens (in/out): 145/231
   Words: 198
   Sentences: 8
   Lexical diversity: 0.73
   Cultural appropriateness: 4.2
```

## Next Steps

After testing with local models:
1. Compare outputs with Claude (`--provider anthropic`)
2. Generate full benchmark cache
3. Create visualizations with `mpo report`
4. Fine-tune generation parameters

---

**Quick Reference**:
```bash
# Default (local LMStudio)
mpo test [prompt] --provider local --live

# With all options
mpo test business_email --provider local --live -l de -f formal -o output.json
```
