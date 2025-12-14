# CLI Agent Commands Reference

## Claude Code CLI (Anthropic)

### Basic Headless Usage
```bash
claude -p "Your prompt here"
```

### Key Flags
- `-p`: Execute one-shot prompt and exit
- `--model <model>`: Specify model (optional)

### Examples
```bash
# Basic one-shot query
claude -p "Explain this function"

# Pipe input to Claude
cat error.log | claude -p "Summarize these errors"
```

### Authentication
Requires configured API key or OAuth token. Run `claude --help` for setup options.

---

## OpenAI Codex CLI

### Basic Headless Usage
```bash
codex exec "Your prompt here"
codex e "Your prompt here"  # Short alias
```

### Key Flags
- `--full-auto`: Unattended operation with workspace-write sandbox
- `--dangerously-bypass-approvals-and-sandbox` or `--yolo`: Complete hands-off mode (use carefully)
- `--cd <path>`: Set working directory
- `--model <model>` or `-m`: Specify model (e.g., `-m gpt-5.1`)
- `--sandbox`: A sandbox types: `read-only`, `workspace-write`
- `--config`: Pass config variables:
    - `model_reasoning_effort`: Model reasoning effort: `low`, `medium`, `high`;
    - 

### Examples
```bash
# Automated refactoring
codex exec --full-auto "Update all README links to HTTPS"

# Different working directory
codex exec --cd /path/to/project "Fix failing tests"
```

### Input Methods
```bash
# Pipe prompt from file
codex exec - < prompt.txt

codex exec --model gpt-5.1 --sandbox workspace-write --config model_reasoning_effort=low < /tmp/test.md

# Standard input
echo "Review this code" | codex exec -
```

---

## Google Gemini CLI

### Basic Headless Usage
```bash
gemini --prompt "Your prompt here"
gemini -p "Your prompt here"  # Short form
```

### Key Flags
- `--prompt` or `-p`: Execute prompt and exit
- `--output-format <format>`: Output format (json, stream-json)
- `--model <model>`: Specify model variant

### Examples
```bash
# Basic query
gemini -p "Summarize API design in this repo"

# Pipe input with prompt
echo "List TODO comments" | gemini -p "-"

# JSON output
gemini -p "Analyze code structure" --output-format json

# Process file with instruction
cat DESIGN.md | gemini -p "Improve this design document"
```

### Authentication
Requires Google account authentication or API key setup.

---

## OpenCode CLI

### Basic Headless Usage
```bash
opencode -p "Your prompt here"
opencode --prompt "Your prompt here"
```

### Key Flags
- `-p` or `--prompt`: Execute single prompt and exit
- `-f <format>` or `--format`: Output format (json)
- `-q` or `--quiet`: Suppress loading spinner
- `--cwd <path>`: Set working directory

### Examples
```bash
# Basic query
opencode -p "Explain Go context usage"

# JSON output
opencode -p "How many files in project?" -f json

# Quiet mode for scripting
opencode -p "Review code" -q

# Different working directory
opencode -p "Analyze this project" --cwd /path/to/project
```

### Environment Setup
Requires API keys for providers (OpenAI, Anthropic, etc.) in environment variables.

---

## Alibaba Qwen Code CLI

### Basic Headless Usage
```bash
qwen -p "Your prompt here"
```

### Key Flags
- `-p` or `--prompt`: Execute one-shot prompt
- `--output-format <format>`: Output format (json)
- `--model <model>`: Specify Qwen model variant
- `--yolo`: Bypass confirmations (similar to other agents)

### Examples
```bash
# Code review
qwen -p "Review this code for potential bugs"

# Generate tests
qwen -p "Generate unit tests for utils.py"

# Pipe diff for review
git diff | qwen -p "Review this diff for errors"

# JSON output
qwen -p "List project files" --output-format json
```

### Authentication
- First-time setup: Run `qwen` interactively to login with Qwen.ai OAuth
- Cached credentials: Used automatically for subsequent `-p` calls
- Local models: Set OPENAI_API_KEY and related env vars for local LLM servers

---

## Factory Droid CLI

### Basic Headless Usage
```bash
droid exec "Your prompt here"
```

### Key Flags
- `--auto <level>`: Set autonomy level (low, medium, high)
- `--skip-permissions-unsafe`: Bypass all permission checks (use carefully)
- `--cwd <path>`: Set working directory
- `-f <file>`: Read prompt from file
- `-o <format>`: Output format (json)

### Autonomy Levels
- **Default (no flag)**: Read-only mode, safe for analysis
- `--auto low`: Allow low-risk file edits (documentation, simple refactors)
- `--auto medium`: Allow development operations (install packages, run tests)
- `--auto high`: Permit production-level changes (full access)

### Examples
```bash
# Read-only analysis
droid exec "List all TODO comments across the project"

# Low-risk edits
droid exec "Fix typos in README.md" --auto low

# Development operations
droid exec "Fix failing unit tests" --auto medium

# High-risk changes
droid exec "Implement OAuth2 migration" --auto high

# Read prompt from file
droid exec -f prompt.md

# JSON output
droid exec "Analyze codebase" -o json

# Different working directory
droid exec "Review this code" --cwd /path/to/project
```

### Safety Notes
- Default mode is read-only for safety
- Use `--skip-permissions-unsafe` only in sandboxed environments
- Consider autonomy levels carefully based on use case

---

## Common Patterns

### piping Input
Most agents support piping input:
```bash
# Pipe file content
cat file.txt | agent -p "Process this"

# Pipe command output
git log --oneline | agent -p "Summarize commits"
```

### Reading from Files
```bash
# Direct file reading (if supported)
agent -f prompt.txt

# Using cat and pipe
cat prompt.txt | agent -p "-"
```

### JSON Output
For scripting and automation:
```bash
# JSON output format
agent -p "Query" --output-format json
agent -p "Query" -f json
agent -p "Query" -o json
```

### Automation Flags
For completely unattended operation:
```bash
# Various automation flags per agent
codex --full-auto "Task"
droid --auto medium "Task"
gemini --yolo "Task"  # if available
```