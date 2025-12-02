# Claude AI Instructions

This file contains specific instructions and guidelines for Claude AI when working on this project.

---

## Core Principles

**IMPORTANT**: Whenever you write code, it must follow the SOLID design principles. Never write code that violates these principles. If you do, you will be asked to refactor it.

### SOLID Principles Reminder

- **S - Single Responsibility Principle:** Each class should have one and only one reason to change.
- **O - Open/Closed Principle:** Classes should be open for extension but closed for modification.
- **L - Liskov Substitution Principle:** Derived classes must be substitutable for their base classes.
- **I - Interface Segregation Principle:** Clients should not be forced to depend on interfaces they do not use.
- **D - Dependency Inversion Principle:** Depend on abstractions, not concretions.

---

## Interactive Workflow

**CRITICAL**: Claude must work interactively with the user, similar to a CLI session. Never execute changes without explicit confirmation.

### Confirmation Required For:
- **File edits** - Propose changes, wait for approval before using Edit/Write tools
- **Git operations** - Ask before commits, pushes, or any git commands
- **Bash commands** - Describe what command will do, get confirmation before execution
- **File reads** - Confirm which files to read when multiple options exist
- **Task planning** - Present the plan, get approval before proceeding

### Workflow Pattern:
1. **Understand** - Clarify the task with user
2. **Propose** - Describe what you'll do (e.g., "I'll edit CLAUDE.md to add...")
3. **Show** - Present the specific changes (diffs, commands, etc.)
4. **Confirm** - Wait for explicit approval: "yes", "proceed", "do it", or modifications
5. **Execute** - Only after confirmation, execute the changes
6. **Report** - Summarize what was done

### Example Interaction:
```
User: "Update the README"
Claude: "I'll update README.md to add the new section about X.
        Shall I proceed with this change?"
User: "Yes"
Claude: [Executes the edit]
Claude: "✓ Done. README.md updated with new section."
```

### Exceptions:
- Reading documentation files for understanding (no changes)
- Using tools to gather information (Glob, Grep for searching)
- Responding to questions without making changes

**Note**: This workflow ensures the user maintains full control, similar to working directly with CLI tools.

---

## Additional Guidelines

### Code Quality
- Write clean, readable, well-documented code
- Include comprehensive docstrings for all classes and functions
- Use type hints where appropriate
- Follow PEP 8 style guidelines

### Documentation
- Keep documentation up to date with code changes
- Provide clear examples in README files
- Include usage instructions for all scripts

### Testing
- Write testable code with clear separation of concerns
- Provide test examples where appropriate
- Document test procedures

---

**Note:** This file should be read at the start of each coding session to ensure consistent code quality.
