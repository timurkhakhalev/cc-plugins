# Steerings Generator

A Claude Code skill that extracts tacit engineering knowledge through guided interviews and generates structured steerings for AI coding agents.

## What It Does

Steerings Generator conducts context-aware interviews to capture implicit conventions, patterns, and practices from your codebase. It produces agent-readable documentation in a structured format: **Intent → Rules → Practices → Meta**.

### Key Features

- **8 Predefined Knowledge Packs**: Architecture, testing, security, code ownership, quality, domain contracts, risk registry, delivery lifecycle
- **Custom Topics**: Document any technology/framework (GraphQL, Terraform, React patterns, etc.)
- **Context-Aware Questions**: Analyzes your codebase first, then asks relevant questions based on what exists
- **Review Mode**: Transform existing steerings to standard format

## Installation

1. Run Claude Code:

```bash
claude
```

2. Add the marketplace:

```
/plugin marketplace add https://github.com/timur-khakhalev/cc-plugins
```

3. Install this plugin:

```
/plugin install steerings-generator@timur-khakhalev-marketplace
```

4. Restart Claude Code

5. Start using the plugin

## Usage

### Basic Interview

```
User: "Run a steerings interview, use skill"
```

Claude will:

1. Ask which knowledge areas to document (select from 8 packs)
2. Analyze your codebase for each area
3. Generate context-specific questions
4. Save responses and generate steering files

### Custom Topic Interview

```
User: "Create steerings for GraphQL API conventions"
```

Claude will focus exclusively on your specified topic, generating 3-7 questions based on scope.

### Review Existing Steerings

```
User: "Review my steerings and fix formatting"
```

Claude will analyze existing files and transform them to standard format.

## Output

Generated files are saved to:

- **Steerings**: `./steerings/` (configurable)
- **Session records**: `./sessions/` (configurable)

Each steering includes:

- **Intent**: Why these conventions matter (1 sentence)
- **Rules**: Numbered prescriptive guidelines
- **Practices**: Implementation patterns with optional code examples
- **Meta**: Scope, task types, source interview, dependencies

## Knowledge Packs

1. **Codebase Topology & Ownership** → `code-ownership.md`
2. **Architecture & Design Invariants** → `architecture-invariants.md`
3. **Business Domain Contracts** → `domain-invariants.md`
4. **Quality & Style Assurance** → `quality-and-style.md`
5. **Testing & Verification Strategy** → `testing-strategy.md`
6. **Risk & Historical Landmines** → `risk-registry.md`
7. **Security, Data & Compliance** → `security-and-compliance.md`
8. **Delivery Lifecycle & Change Flow** → `delivery-lifecycle.md`

## Examples

### Example 1: Architecture Interview

```
User: "Document our architecture conventions"
Claude: [Analyzes codebase structure]
Claude: [Asks 5 questions about layering, dependencies, design patterns]
Claude: [Generates architecture-invariants.md]
```

### Example 2: Custom Topic

```
User: "Create steerings for our React hooks patterns"
Claude: [Explores React code]
Claude: [Asks 4 questions about hook conventions]
Claude: [Generates react-hooks-patterns.md]
```

## Configuration

Customize output paths during interview:

- Default steerings path: `./steerings/`
- Default sessions path: `./sessions/`
- Choose from preset options or specify custom paths

## Documentation

- **[SKILL.md](skills/steerings-generator/SKILL.md)**: Complete skill specification
- **[pack-reference.md](skills/steerings-generator/pack-reference.md)**: Knowledge pack details
- **[steering-template.md](skills/steerings-generator/steering-template.md)**: Output format template

## Requirements

- Claude Code CLI
- Write access to create steerings directories
