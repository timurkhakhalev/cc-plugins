# Headless CLI Agents Skill

Comprehensive guide for running AI coding agents in non-interactive (headless) mode for automation, CI/CD pipelines, and scripting.

## Installation

### 1. Add the Marketplace

First, add this marketplace to Claude Code:

```bash
claude
```

Then run:

```
/plugin marketplace add https://github.com/timur-khakhalev/cc-plugins
```

### 2. Install the Skill

```
/plugin install headless-cli-agents@timur-khakhalev-marketplace
```

### 3. Restart Claude Code

Exit and restart Claude Code to load the new skill.

### 4. Enable the Skill

The skill will be automatically available. To use it, simply ask questions related to:

- "Make a research for the project about how feature X is implemented in project; put report at path /some/path/report.md"
- "How do I run Claude Code in non-interactive mode?"
- "Show me how to use AI agents in CI/CD pipelines"
- "How can I automate code reviews with CLI agents?"
- "What are the best practices for headless AI agent usage?"

## What This Skill Provides

This skill teaches you how to use six popular AI coding agents in headless mode:

### Supported Agents
- **Claude Code CLI** - General-purpose coding with excellent code understanding
- **OpenAI Codex CLI** - Complex refactoring and code transformation
- **Google Gemini CLI** - Analysis and documentation tasks
- **OpenCode CLI** - Multi-provider support
- **Alibaba Qwen Code CLI** - Local model support
- **Factory Droid CLI** - Controlled automation with safety levels

### Key Features
- **Quick Reference**: Compare all agents at a glance
- **Safety Guidelines**: Different autonomy levels and when to use each
- **Integration Examples**: GitHub Actions, GitLab CI, shell scripts
- **Best Practices**: Security, performance, and reliability considerations
- **Troubleshooting**: Common issues and solutions

## Example Usage

### Quick Start
```
Make a research for the project about how feature X is implemented in project; put report at path /some/path/report.md
```

### CI/CD Integration
```
Show me how to set up automated test generation in my CI pipeline
```

### Scripting
```
How can I create a shell script that uses AI agents to analyze logs?
```

### Safety and Automation
```
What's the safest way to use AI agents for automated refactoring?
```

## Skill Contents

The skill includes:

- **Main Guide** (`SKILL.md`): Comprehensive documentation with quick reference tables
- **Command Reference** (`references/agent-specific-commands.md`): Detailed syntax for all agents
- **Use Case Examples** (`references/use-case-examples.md`): Real-world CI/CD and scripting examples
- **Validation Script** (`scripts/validate-agent-setup.py`): Helper to verify agent installations

## Common Use Cases

### CI/CD Pipelines
- Automated code reviews
- Test generation
- Documentation updates
- Security scanning

### Shell Scripts
- Bulk code analysis
- Automated refactoring
- Log analysis
- Dependency management

### Git Hooks
- Pre-commit validation
- Post-commit analysis
- Automated testing

### Monitoring
- Code quality reports
- Security audits
- Performance analysis

## Safety Considerations

This skill emphasizes safe automation practices:
- Use read-only mode for security analysis
- Implement human review for high-risk changes
- Never use dangerous automation flags in production
- Always validate AI-generated code before deployment

## Getting Help

If you need help with specific agents or use cases, ask questions like:
- "What's the difference between Claude Code and Codex CLI?"
- "How do I handle authentication for multiple agents?"
- "Show me examples of safe automation patterns"
- "How do I debug failed AI agent operations?"
- "Make a research for the project about how feature X is implemented in project; put report at path /some/path/report.md"

The skill will provide detailed guidance based on your specific needs and context.