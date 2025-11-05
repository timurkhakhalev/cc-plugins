---
name: steerings-generator
description: Extract tacit engineering knowledge through guided interviews and generate structured steerings. Use when user mentions "steerings", "tacit knowledge", "conventions", "engineering practices", "interview", or wants to document team/project knowledge. Also activates when user asks for "steerings for X", "document X conventions", or wants to extract knowledge about a specific topic. Supports reviewing and transforming existing steerings to standard format.
allowed-tools: Read, Write, AskUserQuestion, Glob, Task
---

# Steerings Generator

This skill conducts context-aware interviews to extract tacit engineering knowledge and generate agent-readable steerings. It analyzes the current codebase to ground questions in reality, while also asking about planned conventions and future intentions. Produces concise steerings in the format: **Intent (Why) → Rules (What) → Practices (How) → Meta**.

Supports both **predefined knowledge packs** (8 common areas like architecture, testing, security) and **custom topics** (user-specified areas like "GraphQL conventions", "Terraform patterns", "mobile development").

**Agent Consumption:** Generated steerings are placed in the configured steerings directory (default: `steerings/`) for AI coding agents to read. This is the canonical location. If using `.memory-bank/steerings/`, that is a separate persistence layer - agents should read from the configured `steeringsPath`.

## When to Use This Skill

Activate when the user wants to:

- Extract and document tacit engineering knowledge
- Create steerings for AI coding agents
- Document conventions, architecture decisions, or team practices
- Generate structured documentation from implicit knowledge
- Define standards for new or existing projects
- Document conventions for a specific technology or domain (custom topics)
- Review and transform existing steering files into standard format

## Prerequisites

- Interview pack guidance in `.claude/skills/tacit-knowledge/pack-reference.md` (defines topic areas and questions)
- Write access to create `steerings/` and `sessions/` directories
- Access to AskUserQuestion and Task tools

## Mode Selection

**Check if user wants to review/transform existing steerings:**

Detect keywords: "review steerings", "transform steerings", "convert steerings", "fix steerings format"

**If reviewing existing steerings:**

- Skip to **Review Mode** (Step R)
- Do NOT run interview flow

**Otherwise:**

- Continue with **Interview Flow** (Step 0)

## Interview Flow

### Step 0: Configure Output Paths

**Before starting the interview, determine where to save outputs:**

1. **Auto-detect existing folders:**
   - Check if `steerings/` exists in current working directory
   - Check if `sessions/` exists in current working directory

2. **Ask user to confirm or customize paths** using AskUserQuestion:

```yaml
questions:
  - question: "Where should generated steering files be saved?"
    header: "Steerings"
    multiSelect: false
    options:
      - label: "./steerings/"
        description: "Default location (will be created if doesn't exist)"
      - label: "docs/steerings/"
        description: "Inside docs/ folder"
      - label: ".steerings/"
        description: "Hidden folder in project root"
      - label: "Custom path"
        description: "Specify a custom directory path"

  - question: "Where should interview session files be saved?"
    header: "Sessions"
    multiSelect: false
    options:
      - label: "./sessions/"
        description: "Default location (will be created if doesn't exist)"
      - label: ".sessions/"
        description: "Hidden folder in project root"
      - label: "docs/sessions/"
        description: "Inside docs/ folder"
      - label: "Custom path"
        description: "Specify a custom directory path"
```

3. **Handle custom paths:**
   - If user selects "Custom path", they'll provide path via text input
   - Validate path is relative (not absolute)
   - Normalize "./" to current directory
   - Reject standalone "." (ambiguous)
   - Trim leading/trailing whitespace
   - Ensure path ends with "/" (add if missing, e.g., "my-docs/steerings" → "my-docs/steerings/")
   - Reject paths containing filenames (must be directory only)

4. **Store paths for use throughout the flow:**
   - `steeringsPath` (e.g., `"steerings/"`, `"docs/steerings/"`, `".steerings/"`)
   - `sessionsPath` (e.g., `"sessions/"`, `".sessions/"`, `"docs/sessions/"`)

5. **Create both directories immediately after confirmation if they don't exist**

6. **Preflight validation after directory creation:**
   - Check write permissions to both directories (attempt to create a test file `.write-test` and delete it)
   - Check for potential filename collisions if regenerating:
     - For predefined packs: Check if concise filenames (code-ownership.md, architecture-invariants.md, etc.) already exist
     - For custom topics: Check if `{packId}.md` already exists
   - Warn user if collisions detected, ask whether to overwrite or cancel
   - Check if `index.md` exists and warn if it will be regenerated

**Default values if skipped:**

- `steeringsPath = "steerings/"`
- `sessionsPath = "sessions/"`

### Step 1: Define Topics (Predefined Packs or Custom Topics)

**Detect if user specified a custom topic:**

- Check user's initial request for patterns: "steerings for X", "document X conventions", "extract knowledge about X"
- Extract topic name X from request
- Examples: "GraphQL API patterns", "Terraform modules", "mobile development", "React hooks"

**If custom topic detected:**

Check if topic is sufficiently clear. A clear topic has:

- Specific technology/domain mentioned
- Reasonable scope (not too broad like "everything" or "all frontend")

**If topic is unclear or too broad, use AskUserQuestion to clarify scope:**

```yaml
questions:
  - question: "What aspects of {topic} do you want to document?"
    header: "Aspects"
    multiSelect: true
    options:
      - label: "Code patterns and structure"
        description: "File organization, naming conventions, module structure"
      - label: "Architecture and design"
        description: "System design, component relationships, data flow"
      - label: "Development process"
        description: "Workflow, tooling, build/deploy process"
      - label: "Quality and testing"
        description: "Test patterns, quality standards, verification approach"
      - label: "Security and compliance"
        description: "Auth patterns, data handling, security practices"

  - question: "What level of detail should the conventions cover?"
    header: "Level"
    multiSelect: false
    options:
      - label: "File and module patterns"
        description: "How individual files and modules should be organized"
      - label: "System-level design"
        description: "How major components interact and depend on each other"
      - label: "Team workflows"
        description: "How team members collaborate and deliver changes"

  - question: "What's the scope of {topic}?"
    header: "Scope"
    multiSelect: false
    options:
      - label: "Specific library/framework"
        description: "Conventions for using a particular tool or library"
      - label: "General domain area"
        description: "Broader conventions across a technology domain"
      - label: "Cross-cutting concern"
        description: "Patterns that apply across the entire stack"
```

Generate topic definition:

- **packId**: kebab-case from topic name (e.g., "graphql-api-patterns")
- **packName**: Human-readable name (e.g., "GraphQL API Patterns")
- **packType**: "custom"
- **customTopicDescription**: Synthesize from clarification answers (1-2 sentences)

**If NO custom topic detected:**

Present all 8 available predefined knowledge packs in a single multi-select question:

```yaml
questions:
  - question: "Which knowledge areas do you want to document? (Select all that apply)"
    header: "Packs"
    multiSelect: true
    options:
      - label: "Codebase Topology & Ownership"
        description: "Document module boundaries, ownership, shared code patterns"
      - label: "Architecture & Design Invariants"
        description: "Document layering, dependencies, design patterns"
      - label: "Business Domain Contracts"
        description: "Document domain entities, business rules, compliance"
      - label: "Quality & Style Assurance"
        description: "Document code quality, Definition of Done, standards"
      - label: "Testing & Verification Strategy"
        description: "Document test types, coverage, structure"
      - label: "Risk & Historical Landmines"
        description: "Document dangerous areas, past failures, workarounds"
      - label: "Security, Data & Compliance"
        description: "Document auth, secrets, PII/PHI, security patterns"
      - label: "Delivery Lifecycle & Change Flow"
        description: "Document branching, PRs, deployment, configuration"
```

Map selected pack labels to pack IDs:

- "Codebase Topology & Ownership" → `codebase-topology-ownership`
- "Architecture & Design Invariants" → `architecture-design-invariants`
- "Business Domain Contracts" → `business-domain-contracts`
- "Quality & Style Assurance" → `quality-style-assurance`
- "Testing & Verification Strategy" → `testing-verification-strategy`
- "Risk & Historical Landmines" → `risk-historical-landmines`
- "Security, Data & Compliance" → `security-data-compliance`
- "Delivery Lifecycle & Change Flow" → `delivery-lifecycle-change-flow`

**Result:** List of topics to process (mix of predefined packs and/or custom topics), each with:

- `packId` (string)
- `packName` (string)
- `packType` ("predefined" | "custom")
- `customTopicDescription` (string, custom only)
- `explorationScope` (object with clarification answers, custom only)

Proceed to Step 2 with all selected topics.

### Step 2: Discover Existing Documentation & Conventions

**Run TWO Explore agents independently (both must complete before Step 3)** (before processing individual packs):

**Explore #1 - Documentation & Conventions:**

```yaml
subagent_type: "Explore"
description: "Find docs and conventions"
prompt: |
  Analyze this repository with medium thoroughness to find existing documentation and conventions:

  - Steering files (steerings/, .steerings/, docs/steerings/)
  - Development conventions (CONVENTIONS.md, DEVELOPMENT.md, CONTRIBUTING.md)
  - Architecture docs (ARCHITECTURE.md, docs/architecture/)
  - Code style guides (STYLE.md, .styleguide)
  - Agent instructions (CLAUDE.md, .claude/CLAUDE.md, .aider/, .cursor/)
  - README sections on conventions, patterns, standards
  - Package.json scripts showing development workflow
  - Config files with conventions (eslint, prettier, tsconfig)

  Report concrete findings with file paths. Focus on conventions, rules, and standards that affect how code should be written.
```

**Explore #2 - General Repository Context:**

```yaml
subagent_type: "Explore"
description: "Understand repo structure"
prompt: |
  Analyze this repository with medium thoroughness to understand:

  - Project purpose and domain
  - Tech stack and key dependencies
  - Directory structure and organization
  - Main modules and their responsibilities
  - Notable patterns or frameworks used

  Report high-level findings to provide context for interview questions.
```

**Usage of Findings:**

- Use docs findings to inform question generation (reference existing conventions)
- Ask clarifying questions during interview if docs are unclear or incomplete
- Incorporate documented conventions into generated steerings
- Reference repo context to make questions more specific and relevant
- **If no existing documentation found:** Proceed with topic guidance + generic repo structure from Step 2 Explore #2
- **Note:** These are global findings; Step 4 will discover topic-specific patterns without re-scanning general structure

**Caching for reuse:**

- Cache Step 2 findings for use in Step 4 and Step 7
- Pass as context to avoid re-scanning general repository structure
- Step 4 should focus only on topic-specific patterns, referencing Step 2 for general context

**Proceed to Step 3 after both Explore agents complete.**

### Step 3: Process Each Topic Sequentially

**IMPORTANT**: Process ONE topic at a time (whether predefined pack or custom topic) through all steps before moving to the next:

1. Analyze current topic with Explore (Step 4)
2. Generate questions for current topic (Step 5)
3. Conduct interview for current topic (Step 6)
4. Save current topic responses to session
5. Move to next topic and repeat Steps 4-6

DO NOT analyze all topics first and then generate all questions. Process sequentially.

The processing flow is the same for both predefined packs and custom topics, with differences in:

- **Step 4**: Predefined uses template Explore prompts, custom generates dynamic prompts
- **Step 5**: Custom topics use flexible question count (3-7 based on scope)

### Step 4: Analyze Topic-Specific Codebase Context

For the current topic being processed, **use Task tool with subagent_type=Explore** to discover existing patterns.

**Important:**

- Use thoroughness level "medium" for balanced exploration
- Explore finds what currently exists
- Questions will also cover planned/future conventions (not just what exists)
- Only analyze the current topic, not all topics at once
- **Note:** Focus only on topic-specific patterns; reference Step 2 for general structure
- **Reuse Step 2 cache:** Include Step 2 findings (docs/conventions + repo context) in Explore prompts to avoid re-scanning. Focus only on discovering new topic-specific patterns.

**Check packType to determine exploration approach:**

**For CUSTOM TOPICS (`packType: "custom"`):**

Generate dynamic Explore prompt from `customTopicDescription` and `explorationScope`:

```
Analyze this codebase with medium thoroughness for {topic}:

Topic: {customTopicDescription}

Focus areas based on user's scope:
{List aspects selected in clarification, e.g.:}
- Code patterns and structure
- Architecture and design
- Quality and testing

Look for:
- Files, directories, and modules related to {topic}
- Configuration files for {topic}
- Usage patterns and conventions
- Integration points with other systems
- Tests related to {topic}
- Documentation mentioning {topic}

Report concrete findings with file paths and code examples.
```

**For PREDEFINED PACKS (`packType: "predefined"`):**

Use template Explore prompts below based on packId.

**Explore Prompts by Predefined Pack:**

**Pack 1 - Codebase Topology & Ownership:**

```
Analyze this codebase with medium thoroughness to find:
- Shared code organization (shared/, common/, utils/, lib/ folders)
- Module boundary patterns (feature folders, domain folders, layers)
- Ownership markers (CODEOWNERS, README ownership sections)
- Directory structure conventions
- Import patterns and path aliases
- Workspace dependencies if monorepo

Report concrete findings with file paths and examples.
```

**Pack 2 - Architecture & Design Invariants:**

```
Analyze this codebase with medium thoroughness to find:
- Layering patterns (controllers, services, repositories, handlers)
- Dependency directions between layers
- Import conventions (relative vs path aliases)
- Event systems (EventEmitter, domain events, message buses)
- Design patterns (decorators, DTOs, factories)
- Performance patterns (caching, lazy loading)
- API conventions (REST, GraphQL, gRPC endpoints)

Report concrete findings with file paths and code examples.
```

**Pack 3 - Business Domain Contracts:**

```
Analyze this codebase with medium thoroughness to find:
- Domain entity definitions and models
- Permission/role enforcement patterns
- Feature flag or licensing tier implementations
- Audit log or compliance-related code
- Money-handling or financial logic
- Domain event naming patterns

Report concrete findings with file paths and examples.
```

**Pack 4 - Quality & Style Assurance:**

```
Analyze this codebase with medium thoroughness to find:
- Code formatting config (prettier, eslint)
- Naming conventions in actual code
- Logging and error handling patterns
- Observability instrumentation
- Quality check scripts (lint, type-check, test commands)
- PR templates or contribution guidelines

Report concrete findings with file paths and examples.
```

**Pack 5 - Testing & Verification Strategy:**

```
Analyze this codebase with medium thoroughness to find:
- Test file locations and naming patterns
- Test types used (unit, integration, e2e)
- Testing framework config (jest, vitest, cypress)
- Coverage configuration
- Test data and fixture patterns
- Mock/stub patterns

Report concrete findings with file paths and examples.
```

**Pack 6 - Risk & Historical Landmines:**

```
Analyze this codebase with medium thoroughness to find:
- Comments mentioning "TODO", "FIXME", "HACK", "DEPRECATED"
- Workarounds or legacy code markers
- Version-specific code or compatibility shims
- Areas with high complexity or technical debt
- Commented-out code blocks with explanations

Report concrete findings with file paths and examples.
```

**Pack 7 - Security, Data & Compliance:**

```
Analyze this codebase with medium thoroughness to find:
- Authentication/authorization implementations
- Secret management patterns (env vars, vaults)
- Input validation and sanitization
- PII/PHI handling code
- Security-related middleware or guards
- Data access control patterns
- Encryption or hashing usage

Report concrete findings with file paths and examples.
```

**Pack 8 - Delivery Lifecycle & Change Flow:**

```
Analyze this codebase with medium thoroughness to find:
- Git workflow files (.github/workflows, CI config)
- Branching strategy markers (branch protection, naming)
- PR templates and commit message conventions
- Deployment scripts and configuration
- Environment config patterns (.env files)
- Changelog or version management
- Release automation

Report concrete findings with file paths and examples.
```

**Task Tool Usage:**

```yaml
subagent_type: "Explore"
description: "Analyze codebase for {pack-name} patterns"
prompt: |
  [Use appropriate prompt from above based on selected pack]
```

### Step 5: Generate Context-Aware Questions (Current Topic Only)

**Determine question count:**

**For PREDEFINED PACKS:** Always generate 5 questions.

**For CUSTOM TOPICS:** Generate 3-7 questions based on topic scope:

- **3-4 questions** if:
  - Topic description < 50 chars OR
  - Single aspect selected OR
  - Explore findings ≤ 2 files/areas

- **5 questions** if: (default fallback)
  - Topic description 50-100 chars OR
  - 2-3 aspects selected OR
  - Explore findings 3-5 files/areas

- **6-7 questions** if:
  - Topic description > 100 chars OR
  - 4+ aspects selected OR
  - Explore findings 6+ files/areas

**If heuristics conflict, default to 5 questions.**

**Precise definitions:**

- **"areas"**: Unique directories or major modules returned by Explore agent findings
- **"aspects"**: Number of multi-select items chosen in clarification questions
- **"description length"**: Character count of customTopicDescription string

**Precedence when heuristics conflict:**

1. Description length (highest priority)
2. Aspect count
3. Explore findings (lowest priority)
4. Tie-breaker: Default to 5 questions

Based on **three sources**, generate questions dynamically for this topic only:

1. Topic-specific Explore findings (Step 4)
2. Documentation/conventions findings (Step 2)
3. Pack topic guidance (from pack-reference.md for predefined, or clarification scope for custom)

**Question Generation Guidelines:**

1. **Ground in current reality:** Use topic-specific Explore findings + existing docs to inform questions
2. **Reference actual code and docs:** "I see you use X pattern in Y file..." or "Your CONVENTIONS.md says X, but..."
3. **Clarify unclear docs:** If existing docs are incomplete or ambiguous, ask clarifying questions
4. **Ask about conventions, not roadmap:** Focus on "how should X be done?" not "will you build X?"
5. **Incorporate existing standards:** Reference documented conventions and ask if they should apply to related areas
6. **Offer 4 options (A/B/C/D):** Present realistic choices based on common patterns + existing conventions
7. **Mark one option as recommended:** Add "⭐ Recommended" as the LAST token in the description field (after a space) for the option you think is best practice. This star must appear at the exact end of the description text. See Step 7 Validation Requirements for detailed rule style examples.
8. **Only generate questions for current topic:** Do not generate questions for other topics yet
9. **If Explore finds nothing:** Generate questions based on establishing conventions (ask "how should X be done?" for the topic)

**Good vs Bad Questions:**

✅ **Good (asks about conventions):**

- "How should shared utilities be organized?"
- "Where should authentication logic live?"
- "What naming convention should API endpoints follow?"

❌ **Bad (asks about roadmap/features):**

- "Will you implement OAuth authentication in Q2?"
- "Are you planning to add a mobile app?"
- "What features are on the roadmap?"

**Example Generated Questions:**

For "Codebase Topology & Ownership" (after Explore finds `src/utils/` and `src/lib/`):

```
Q1: I found both `src/utils/` and `src/lib/` folders containing helper functions.
    Where should shared types, schemas, and business logic live going forward?
    A) Use `src/lib/` as canonical and migrate utils
    B) Use `src/utils/` and deprecate lib
    C) Keep both: lib for packages, utils for helpers
    D) Create new `src/shared/` and consolidate both ⭐ Recommended

Q2: I don't see a CODEOWNERS file. How should ownership be communicated?
    A) No need - solo project
    B) Add CODEOWNERS for key directories ⭐ Recommended
    C) Document in README files per module
    D) Use git history as implicit ownership
```

For "Testing Strategy" (even if nothing found):

```
Q1: I found a few Jest tests in `src/__tests__/`. Should this pattern continue?
    A) Yes, keep all tests in __tests__/
    B) Move to co-located *.test.ts files ⭐ Recommended
    C) Use both: __tests__/ for integration, *.test.ts for unit
    D) Create separate tests/ directory

Q2: What test types should be required for new features?
    A) Unit tests only
    B) Unit + integration tests ⭐ Recommended
    C) Unit + integration + e2e tests
    D) Based on risk (critical features get more coverage)
```

For "Quality & Style" (referencing existing docs from Step 2):

```
Q1: Your CONVENTIONS.md says "functions under 50 lines" but doesn't specify
    what to do when exceeded. What's the enforcement approach?
    A) Soft guideline - suggest refactoring in PR reviews
    B) Hard rule - CI fails if functions exceed limit
    C) Extract helpers immediately when approaching limit ⭐ Recommended
    D) Document exceptions with inline comments

Q2: I see prettier config but STYLE.md mentions "4 space indents" while
    prettier uses 2. Which should be canonical?
    A) Update STYLE.md to match prettier config ⭐ Recommended
    B) Update prettier to match STYLE.md
    C) Keep both - they apply to different file types
    D) Remove STYLE.md, rely on tooling
```

For **Custom Topic** "GraphQL API Conventions" (4 questions, narrow scope):

```
Q1: I found GraphQL schemas in src/graphql/schema/ and API resolvers in src/api/graphql/.
    Should schemas and resolvers be co-located?
    A) Keep separate - schemas in one place, resolvers grouped by domain
    B) Co-locate - each domain folder has schema + resolvers ⭐ Recommended
    C) Hybrid - keep schemas separate but organize resolvers by domain
    D) Consolidate everything in src/graphql/

Q2: Resolver functions range from 10-200 lines. What's the complexity threshold?
    A) Keep resolvers thin - delegate to service layer immediately ⭐ Recommended
    B) Allow complex resolvers if single responsibility
    C) Extract helpers when resolvers exceed 50 lines
    D) No limit - resolver complexity matches query complexity

Q3: No input validation visible in resolvers. Where should GraphQL input validation happen?
    A) In resolver functions directly
    B) Using GraphQL schema directives ⭐ Recommended
    C) In service layer before processing
    D) Combination of schema directives + service validation

Q4: How should GraphQL errors be structured and returned to clients?
    A) Use standard GraphQL error format
    B) Custom error codes in extensions field ⭐ Recommended
    C) HTTP status codes in headers
    D) Structured errors with error codes + localized messages
```

**Topic Guidance:**

- **For predefined packs**: Use topic questions from pack-reference.md as guidance
- **For custom topics**: Use clarification scope (aspects/level/scope) to determine question areas
- Ensure questions cover both current state and conventions to establish
- Generate questions even if Explore finds nothing (ask about conventions to establish)

### Step 6: Conduct Interview (Current Topic Only)

Present generated questions for the current topic only using AskUserQuestion (max 4 per call):

```yaml
questions:
  - question: "{Generated question 1 based on Explore + topic guidance}"
    header: "Q1"
    multiSelect: false
    options:
      - label: "A) {Option based on findings/common patterns}"
        description: "{Brief rationale}"
      - label: "B) {Option}"
        description: "{Brief rationale} ⭐ Recommended"
      - label: "C) {Option}"
        description: "{Brief rationale}"
      - label: "D) {Option}"
        description: "{Brief rationale}"

  # ... questions 2-4
```

**Important:** Mark one option per question with "⭐ Recommended" at the end of the description field, based on best practices for the context.

**Question batching (max 4 per AskUserQuestion call):**

| Question Count | Batching Strategy               |
| -------------- | ------------------------------- |
| 3 questions    | Single call [Q1-Q3]             |
| 4 questions    | Single call [Q1-Q4]             |
| 5 questions    | Two calls: [Q1-Q4] then [Q5]    |
| 6 questions    | Two calls: [Q1-Q4] then [Q5-Q6] |
| 7 questions    | Two calls: [Q1-Q4] then [Q5-Q7] |

**Between batches:** Show progress recap before presenting second batch.
Example: "You've answered 4 questions. Next batch: {remaining} questions about {topic}..."

After completing the interview for the current topic, save responses to `{sessionsPath}{sessionId}.md` (using configured sessionsPath from Step 0), then return to Step 3 to process the next topic.

Capture responses in Markdown format:

```markdown
# Interview Session

**Session ID:** {uuid}
**Date:** {ISO date}
**Timestamp:** {ISO timestamp}

---

## Pack: Architecture & Design Invariants

**Pack ID:** architecture-design-invariants
**Pack Type:** predefined

### Question 1

**Question:** ...

**Selected Option:** B

**Option Text:** ...

**Notes:** ...

**Timestamp:** {ISO timestamp}

---

### Question 2

**Question:** ...

**Selected Option:** A

**Option Text:** ...

**Notes:** ...

**Timestamp:** {ISO timestamp}

---

## Pack: GraphQL API Conventions

**Pack ID:** graphql-api-conventions
**Pack Type:** custom

**Topic Description:** GraphQL schema organization, resolver patterns, error handling, and input validation conventions

**Exploration Scope:**

- **Aspects:** Code patterns and structure, Architecture and design
- **Level:** System-level design
- **Scope:** Specific library/framework

**Question Count:** 4

### Question 1

**Question:** ...

**Selected Option:** B

**Option Text:** ...

**Notes:** ...

**Timestamp:** {ISO timestamp}

---

### Question 2

**Question:** ...

**Selected Option:** C

**Option Text:** ...

**Notes:** ...

**Timestamp:** {ISO timestamp}
```

Save to `{sessionsPath}{sessionId}.md` (using configured sessionsPath from Step 0) after each topic interview is completed.

**After completing all pack interviews**, proceed to Step 7 to generate steerings.

### Step 7: Generate Steerings (After All Topics Completed)

**Delegate to general-purpose subagent** using Task tool:

```yaml
subagent_type: "general-purpose"
description: "Generate steering documents"
prompt: |
  Generate steering documents from this interview session.

  {If session file > 50KB, chunk into sections by pack. Provide each pack's Q&A separately. Otherwise provide complete session content.}

  Session Data (Markdown format):
  {Provide complete session Markdown content from {sessionsPath}{sessionId}.md file, or chunked by pack if large}

  Output Paths:
  - Steerings directory: {steeringsPath}
  - Sessions directory: {sessionsPath}

  Existing Documentation & Conventions:
  {Provide findings from Step 2 Explore #1 - Documentation & Conventions}

  Repository Context:
  {Provide findings from Step 2 Explore #2 - General Repository Context}

  Template Guidelines:
  {Provide steering-template.md content}

  Requirements:

  1. Create one steering file per topic in `{steeringsPath}{filename}.md` (using configured steeringsPath)

     **For predefined packs**, use these concise filenames for ease of reference (full pack context is in file content):
     - codebase-topology-ownership → code-ownership.md
     - architecture-design-invariants → architecture-invariants.md
     - business-domain-contracts → domain-invariants.md
     - quality-style-assurance → quality-and-style.md
     - testing-verification-strategy → testing-strategy.md
     - risk-historical-landmines → risk-registry.md
     - security-data-compliance → security-and-compliance.md
     - delivery-lifecycle-change-flow → delivery-lifecycle.md

     **For custom topics**, generate filename from packId:
     - Use packId directly as filename (already kebab-case)
     - Example: "graphql-api-conventions" → graphql-api-conventions.md
     - Validate no collisions with predefined pack filenames

  2. Format requirements:
     - Intent: Single concise sentence explaining why these conventions matter
     - Rules: Numbered prescriptive statements guiding HOW to do assigned tasks, not proactive commands to do extra work (no Source/Rationale/Applies metadata)
     - Practices: Simple format with heading + explanation + optional code example (only when truly needed to clarify)
     - Meta: Scope, task types, session info, dependencies
       - For custom topics: Include "Topic Type: custom", "Topic Description: {customTopicDescription}", and "Exploration Scope: {aspects/level/scope}"

  3. Rule style - generate prescriptive/conditional rules, not proactive commands:

     ✅ **Good rules (prescribe methodology, timeless):**
     - "When implementing features, keep functions under 50 lines by extracting helpers"
     - "New features require unit tests covering happy path and error cases"
     - "Throw typed errors with descriptive messages; catch at boundary layers"
     - "Extract shared logic used 3+ times into `src/shared/utils/`"
     - "Use environment variables for secrets and API keys"
     - "Store configuration in YAML files under `config/`"

     ❌ **Bad rules (proactive commands or temporal language):**
     - "Proactively refactor complex functions exceeding 50 lines"
     - "Add comprehensive test coverage to existing modules"
     - "Improve error handling in legacy code"
     - "Look for opportunities to extract reusable utilities"
     - "Continue using environment variables for secrets" (use "Use" not "Continue using")
     - "Keep using YAML for configuration" (use "Store" not "Keep using")

     Rules guide HOW to do the assigned task, not WHAT extra tasks to do.
     Rules should be timeless conventions, not references to current state.

  4. Transform interview responses:
     - Synthesize "why" from user's selected options and notes into one sentence for Intent
     - Convert selected options into numbered prescriptive rules (following style guidelines in point 3)
     - Write rules as timeless prescriptions ("Use X", "Keep Y under Z"), NOT as continuations ("Continue using X", "Keep using Y")
     - Remove temporal context from questions (ignore "I found X" framing, just state the convention)
     - Provide concrete code examples in Practices section only when needed

  5. Incorporate existing documentation:
     - Reference conventions from existing docs (CONVENTIONS.md, CLAUDE.md, etc.) in relevant steerings
     - Align generated rules with documented standards unless interview responses indicate changes
     - Consolidate scattered conventions into appropriate steering sections
     - Note when interview answers clarify or extend existing documentation
     - If existing steerings found, enhance rather than duplicate

  6. DO NOT include:
     - Source/Rationale/Applies fields in rules
     - Enforcement section
     - Structured subsections (What/How/Example/Anti-pattern) in Practices unless showing multiple approaches

  7. Code examples should be:
     - Optional: Only include when the practice cannot be clearly understood without code
     - Concise: 5-15 lines typical, max 25 lines when needed
     - Meaningful: Include necessary context (imports, types, file paths)
     - Realistic: Use actual patterns from interview responses and codebase
     - Focused: One clear concept per example
     - NOT full file dumps or trivial snippets
     - Many practices are better explained with prose alone

  8. Validate outputs:
     - Intent is 1 sentence
     - Rules are numbered prescriptive statements without metadata (following point 3 style)
     - Practices have simple format with optional code examples (only when needed)
     - Filename is kebab-case matching pack
     - File < 200 lines (MUST split if exceeds: use pattern base-name.md + base-name-{subtopic}.md, e.g., architecture-invariants.md → architecture-invariants.md + architecture-invariants-performance.md)
     - Document splits in generation summary
     - All required sections present
     - Recommended options marked with "⭐ Recommended" at exact end of description field

  9. Generate index.md:
     - Create `{steeringsPath}index.md` as table of contents
     - List all generated steering files with links
     - Provide 1-2 sentence description of what each file covers
     - Format as markdown list with relative links

  10. Return summary of generated files with rule/practice counts
     - Report any files that were split due to length constraints
```

### Step 8: Present Results

Show summary from subagent:

```
Generated steerings:
- {steeringsPath}code-ownership.md (5 rules, 3 practices)
- {steeringsPath}architecture-invariants.md (7 rules, 4 practices)
- {steeringsPath}testing-strategy.md (6 rules, 3 practices)
- {steeringsPath}index.md (table of contents)

Session saved: {sessionsPath}{sessionId}.md
```

**Agent Consumption Note:**
Agents should read steerings from: {steeringsPath}
This is the canonical location for agent consumption.

Suggest next steps:

- Review generated steerings for accuracy
- Edit steerings to add project-specific details
- Commit steerings to git
- Reference in CLAUDE.md or agent instructions
- Run additional interviews for other knowledge areas

## Example Workflows

### Example 1: Custom Topic - GraphQL Conventions

**User request:** "I want to create steerings for GraphQL API conventions"

**Flow:**

1. **Step 1**: Detect custom topic "GraphQL API conventions"
   - Topic is clear, skip clarification
   - Generate: `packId: "graphql-api-conventions"`, `packType: "custom"`
2. **Step 2**: Run docs/conventions discovery (parallel Explore)
3. **Step 3-6**: Process custom topic
   - **Step 4**: Dynamic Explore prompt: "Analyze for GraphQL schemas, resolvers, query patterns..."
   - **Step 5**: Generate 4-5 questions based on findings (narrow scope)
   - **Step 6**: Conduct interview
4. **Step 7**: Generate `steerings/graphql-api-conventions.md` with Meta including custom topic metadata
5. **Step 8**: Present results

### Example 2: Custom Topic - Terraform Patterns (with clarification)

**User request:** "Document our infrastructure conventions"

**Flow:**

1. **Step 1**: Detect custom topic "infrastructure conventions" (too broad)
   - Ask clarification: "What aspects? (Code patterns, Architecture, Process, etc.)"
   - User selects: "Code patterns and structure", "Security and compliance"
   - Ask level: User selects "File and module patterns"
   - Ask scope: User selects "Specific library/framework"
   - Refine to: "Terraform module organization and security patterns"
   - Generate: `packId: "terraform-patterns"`, `customTopicDescription: "..."`
2. **Step 2**: Run docs/conventions discovery
3. **Step 3-6**: Process custom topic with focused exploration
4. **Step 7**: Generate `steerings/terraform-patterns.md`
5. **Step 8**: Present results

### Example 3: Mixed - Predefined + Custom

**User request:** "Run tacit knowledge interview" (no custom topic specified)

**Flow:**

1. **Step 1**: No custom topic detected, show predefined packs
   - User selects: Pack 2 (Architecture), Pack 5 (Testing)
2. **Step 2**: Run docs/conventions discovery
3. **Step 3-6**: Process Pack 2 → Process Pack 5
4. **Step 7**: Generate architecture-invariants.md and testing-strategy.md
5. **Step 8**: Present results

**Later:**

**User request:** "Now add steerings for React hooks patterns"

**Flow:**

1. **Step 1**: Detect custom topic, skip pack selection
2. Process custom topic through Steps 2-8
3. Generate react-hooks-patterns.md

### Example 4: Review Mode - Transform Existing Steerings

**User request:** "Review my existing steerings and fix the format"

**Flow:**

1. **Mode Selection**: Detect "review" keyword, enter Review Mode
2. **Step R1**: Auto-detect `./steerings/` directory
3. **Step R2**: Explore agent analyzes 5 files:
   - 2 compliant (match format)
   - 3 need transformation (verbose rules, missing sections, long code examples)
4. **Step R3**: Show summary to user
5. **Step R4**: User selects "Transform all to standard format"
6. **Step R5**: Subagent transforms 3 files:
   - Adds missing Intent sections
   - Simplifies rule format
   - Trims code examples
   - Adds Meta sections
7. **Step R6**: Present transformation results

**Result:** All steerings now follow Intent → Rules → Practices → Meta format

## Review Mode (Step R)

**Use when user wants to review/transform existing steerings.**

**Note:** Transformation is a sanctioned generator action (not manual editing). Rewriting steerings to match the standard format aligns with repository policy about maintaining consistent structure.

### Step R1: Locate Existing Steerings

**Auto-detect steering directories:**

Use Glob to find common locations:

- `steerings/` or `./steerings/`
- `.steerings/`
- `docs/steerings/`
- Any path from CLAUDE.md or project docs

**If multiple locations found or none found:**

Ask user to specify path using AskUserQuestion:

```yaml
questions:
  - question: "Where are your existing steering files located?"
    header: "Location"
    multiSelect: false
    options:
      - label: "./steerings/"
        description: "Default location"
      - label: "docs/steerings/"
        description: "Inside docs folder"
      - label: ".steerings/"
        description: "Hidden folder"
```

### Step R2: Analyze Existing Steerings

**Use Task tool with Explore agent to analyze all steering files:**

```yaml
subagent_type: "Explore"
description: "Analyze existing steerings"
prompt: |
  Analyze all steering files in {steeringsPath} with medium thoroughness:

  For each .md file, check:
  - Structure: Does it follow Intent → Rules → Practices → Meta format?
  - Intent section: Is there a single concise "why" sentence?
  - Rules section: Are rules numbered and prescriptive? Any metadata/verbose formatting?
  - Practices section: Simple format (heading + explanation + code) or complex subsections?
  - Meta section: Contains Scope, Task Types, Source Interview, Generated, Dependencies?
  - Filename: kebab-case, descriptive?
  - File size: Under ~200 lines?
  - Code examples: Concise (5-15 lines) or too long/short?

  Report findings:
  - Files that match standard format (compliant)
  - Files needing transformation (non-compliant with specific issues)
  - Missing required sections
  - Structural problems

  Provide file paths and specific issues for each non-compliant file.
```

### Step R3: Present Review Summary

Show user:

```
Found {N} steering files in {steeringsPath}:

✅ Compliant (match standard format):
- architecture-invariants.md
- testing-strategy.md

⚠️ Need transformation:
- code-organization.md: Missing Intent section, rules have verbose metadata
- api-conventions.md: No Meta section, code examples too long (50+ lines)
- error-handling.md: Rules are proactive commands instead of prescriptive conventions
```

### Step R4: Ask User What to Do

```yaml
questions:
  - question: "How should non-compliant steerings be handled?"
    header: "Action"
    multiSelect: false
    options:
      - label: "Transform all to standard format"
        description: "Automatically rewrite non-compliant files to match template"
      - label: "Transform specific files"
        description: "Choose which files to transform"
      - label: "Backup and transform"
        description: "Create .bak copies before transforming non-compliant files"
      - label: "Generate transformation plan only"
        description: "Show what would change without making edits"
      - label: "Skip transformation"
        description: "Keep files as-is"
```

### Step R5: Transform Steerings

**If user chooses transformation, delegate to general-purpose subagent:**

```yaml
subagent_type: "general-purpose"
description: "Transform steerings to standard format"
prompt: |
  Transform non-compliant steering files to match standard format.

  Backup Policy:
  {If user selected "Backup and transform": Before overwriting each file, create a backup copy with .bak extension (e.g., code-ownership.md → code-ownership.md.bak)}
  {Otherwise: Overwrite directly without backup}

  Files to transform:
  {List of files from Step R3 with specific issues}

  Standard Format (from steering-template.md):
  {Provide complete template content}

  Transformation Guidelines:

  **Note:** These transformations align with repository policy. Steerings are generated artifacts maintained through sanctioned generator actions, not manual edits.

  1. **Intent Section:**
     - If missing: Synthesize from existing content (1 sentence "why")
     - If too long: Condense to single sentence
     - Extract core purpose from introduction/rules

  2. **Rules Section:**
     - Remove Source/Rationale/Applies metadata
     - Convert verbose rule format to simple numbered list
     - Change proactive commands to prescriptive/conditional rules:
       ❌ "Proactively refactor X" → ✅ "When implementing Y, keep X under Z"
       ❌ "Continue using X" → ✅ "Use X for Y"
     - Keep rules numbered and imperative
     - Remove temporal language ("currently", "keep using")

  3. **Practices Section:**
     - Simplify complex subsections (What/How/Example/Anti-pattern) to heading + explanation + code
     - Trim code examples to 5-15 lines (max 25)
     - Remove full file dumps
     - Add file paths as comments in code blocks
     - Keep only meaningful examples (remove trivial snippets)

  4. **Meta Section:**
     - Add if missing with: Scope, Task Types, Source Interview (N/A if transformed), Generated (current timestamp), Dependencies
     - Use existing metadata if present
     - If no Source Interview: Mark as "Source Interview: Transformed from existing documentation"

  5. **Structural:**
     - Ensure single H1 heading
     - Make headings unique
     - Validate kebab-case filename (rename if needed)
     - Split if > 200 lines

  6. **Preserve Content:**
     - Keep domain knowledge and specific conventions intact
     - Don't change technical accuracy
     - Maintain code example correctness
     - Preserve project-specific details

  For each file:
  - Read existing content
  - Transform according to guidelines
  - Write to same path (overwrite)
  - Report changes made

  Return summary:
  - Files transformed
  - Key changes per file
  - Any issues encountered
```

### Step R5.5: Regenerate Index

After transformations (especially if files were renamed or split), regenerate index.md:

**Delegate to general-purpose subagent:**

```yaml
subagent_type: "general-purpose"
description: "Regenerate steerings index"
prompt: |
  Regenerate {steeringsPath}index.md to reflect current steering files.

  Scan {steeringsPath} for all .md files (except index.md itself).

  Create table of contents with:
  - Alphabetical list of steering files
  - Relative links
  - 1-2 sentence description of each file's scope

  Format as markdown list with links.
```

### Step R6: Present Transformation Results

Show summary from subagent:

```
Transformed {N} steering files:

✅ code-organization.md
   - Added Intent section: "We organize by feature to enable independent evolution"
   - Simplified rules: Removed metadata, converted 8 rules to prescriptive format
   - Trimmed 3 code examples from 40+ lines to 10-15 lines

✅ api-conventions.md
   - Added Meta section with Scope: project, Task Types: write-code, setup
   - Condensed Practices: Removed What/How subsections, kept simple format
   - Split into api-conventions.md (120 lines) and api-error-handling.md (80 lines)

✅ error-handling.md
   - Converted 5 proactive command rules to conditional rules
   - Removed temporal language ("continue using" → "use")

All files now match standard format.
```

**Suggest next steps:**

- Review transformed files
- Commit changes to git
- Run interview flow for new topics if needed

## Pack Structure

**8 Available Packs:** (see [pack-reference.md](pack-reference.md))

1. Codebase Topology & Ownership
2. Architecture & Design Invariants
3. Business Domain Contracts
4. Quality & Style Assurance
5. Testing & Verification Strategy
6. Risk & Historical Landmines
7. Security, Data & Compliance
8. Delivery Lifecycle & Change Flow

**How topics are processed:**

- **Predefined packs** define common topic areas with template Explore prompts
- **Custom topics** allow documenting any technology/domain with dynamic exploration
- Explore agent discovers what exists in codebase for each topic
- Questions are generated dynamically combining findings + topic guidance
- Questions cover both current state AND future plans

## Tips

1. **Use custom topics for specific technologies**: Document conventions for frameworks, libraries, or tools not covered by predefined packs (e.g., "Next.js patterns", "Prisma schemas", "Kubernetes configs")
2. **Be specific in answers**: Add notes explaining context and reasoning
3. **Mix predefined and custom**: Use predefined packs for broad areas, custom topics for specific technologies
4. **Review and refine**: Generated steerings are starting points, edit for clarity
5. **Cover future plans**: Answer based on planned conventions, not just what exists today
6. **Layer by scope**: Generate separate steerings for project/team/developer levels

## Troubleshooting

**Skill not activating?**

- Use keywords: "steerings", "tacit knowledge", "interview", "conventions"
- For custom topics: "steerings for X", "document X conventions"
- For review mode: "review steerings", "transform steerings", "fix steerings format"

**Custom topic too broad?**

- Answer clarification questions to narrow scope
- Break into multiple focused custom topics instead of one broad topic

**Questions not relevant?**

- For custom topics: Provide more specific topic description and clarification
- Explore might need more specific context
- Remember questions cover both present and planned future

**Custom topic overlaps with predefined pack?**

- Use predefined pack if it covers 80%+ of what you need
- Use custom topic for specific technology within broader area (e.g., "GraphQL" vs "Architecture")

**Generated steerings too generic?**

- Add detailed notes in interview answers
- Include specific examples from your codebase or plans

**Code examples too long/short?**

- Generated examples should be 5-15 lines
- Report if subagent produces full file dumps or trivial snippets

## Reference Files

- [pack-reference.md](pack-reference.md) — 8 knowledge areas with topic questions, when to use each pack, and outcome mapping
- [steering-template.md](steering-template.md) — Output format and validation rules
