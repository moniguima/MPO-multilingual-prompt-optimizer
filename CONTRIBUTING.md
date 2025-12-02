# Contributing to Multilingual Prompt Optimizer

Thank you for your interest in contributing to the Multilingual Prompt Optimizer (MPO)!

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project follows a code of conduct that encourages respectful and constructive collaboration. Please be professional and considerate in all interactions.

## How Can I Contribute?

### Reporting Bugs
- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include system information (Python version, OS, etc.)

### Suggesting Enhancements
- Open an issue with the "enhancement" label
- Clearly describe the proposed feature and its benefits
- Discuss implementation approaches if possible

### Adding Language Support
We welcome contributions for additional languages! To add a new language:

1. Create a new adapter in `src/mpo/adapters/` (e.g., `fr_adapter.py` for French)
2. Implement cultural adaptation logic based on linguistic theory
3. Add configuration to `config/languages.yaml`
4. Write comprehensive unit tests
5. Document the cultural rationale

### Improving Documentation
- Fix typos and clarify explanations
- Add examples and use cases
- Improve code comments and docstrings

## Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/multilingual-prompt-optimizer.git
cd multilingual-prompt-optimizer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src/mpo
```

## Pull Request Process

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the coding standards below
3. **Write/update tests** to cover your changes
4. **Run the test suite** and ensure all tests pass
5. **Update documentation** if you changed functionality
6. **Submit a pull request** with a clear description of changes

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines (black, isort)
- [ ] Documentation updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

## Coding Standards

### Python Style
- Follow **PEP 8** guidelines
- Use **type hints** for all function signatures
- Format code with **black** (line length: 100)
- Sort imports with **isort**

```bash
# Format your code before committing
black src/ tests/
isort src/ tests/

# Check types
mypy src/
```

### Testing
- Write unit tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common test data
- Test edge cases and error handling

### Documentation
- Write docstrings for all public classes and functions
- Use Google-style docstring format
- Include examples in docstrings where helpful
- Keep README and docs/ synchronized

## Project Structure

```
src/mpo/
├── core/          # Core abstractions (Prompt, Adapter, Evaluator)
├── adapters/      # Language-specific cultural adapters
├── providers/     # LLM API wrappers
├── metrics/       # Evaluation metrics
├── storage/       # Caching and experiment tracking
├── cli/           # Command-line interface
└── ui/            # Web interface (Gradio)
```

## Questions?

Feel free to open an issue for questions or discussion. For direct contact, see the README.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve MPO!
