# CLI Agents Use Case Examples

## CI/CD Pipeline Examples

### GitHub Actions - Code Review

```yaml
name: AI Code Review
on:
  pull_request:
    branches: [main]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Claude Code CLI
        run: |
          curl -fsSL https://claude.ai/install.sh | sh
          echo "$CLAUDE_API_KEY" | claude auth login
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}

      - name: Review PR Changes
        run: |
          git diff origin/main...HEAD | claude -p "Review these changes for potential bugs, security issues, and best practices. Focus on: 1) Error handling 2) Performance 3) Security 4) Code quality"

      - name: Check for TODO Comments
        run: |
          find . -name "*.py" -o -name "*.js" -o -name "*.ts" | xargs grep -l "TODO\|FIXME" | claude -p "Review these files containing TODO/FIXME comments and suggest implementation approaches"
```

### GitLab CI - Documentation Generation

```yaml
stages:
  - analyze
  - build

code-analysis:
  stage: analyze
  image: node:18
  before_script:
    - npm install -g @anthropic-ai/claude-cli
  script:
    - |
      claude -p "Generate comprehensive API documentation for this codebase. Focus on: 1) Endpoints 2) Request/response formats 3) Authentication 4) Error codes" > API_DOCUMENTATION.md
      claude -p "Create a README with setup instructions, usage examples, and contribution guidelines" > README_ENHANCED.md
  artifacts:
    paths:
      - API_DOCUMENTATION.md
      - README_ENHANCED.md
```

### Jenkins Pipeline - Test Generation

```groovy
pipeline {
    agent any

    stages {
        stage('AI Test Generation') {
            steps {
                script {
                    sh '''
                        # Generate unit tests for untested functions
                        find src -name "*.py" -exec grep -L "def test_" {} \\; | codex exec --full-auto --skip-git-repo-check "Generate comprehensive unit tests for these files using pytest framework. Include edge cases and error handling."

                        # Generate integration tests
                        codex exec --full-auto "Create integration tests for the main API endpoints. Test authentication, data flow, and error scenarios."
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python -m pytest'
            }
        }
    }
}
```

## Shell Scripting Examples

### Code Quality Check Script

```bash
#!/bin/bash

# quality-check.sh - Automated code quality analysis

set -e

echo "🔍 Running AI-powered code quality checks..."

# Check for security vulnerabilities
echo "🔒 Checking for security issues..."
find . -name "*.py" -o -name "*.js" -o -name "*.ts" | \
  xargs grep -l "password\|secret\|token\|key" | \
  claude -p "Analyze these files for potential security vulnerabilities. Look for: 1) Hardcoded credentials 2) Insecure data handling 3) Missing input validation 4) Authentication bypasses"

# Check for performance issues
echo "⚡ Analyzing performance patterns..."
find . -name "*.py" | head -10 | \
  claude -p "Review these files for performance bottlenecks. Focus on: 1) Database queries 2) Loops and recursion 3) Memory usage 4) Async operations"

# Generate quality report
echo "📋 Generating quality report..."
claude -p "Create a comprehensive code quality report summarizing: 1) Security findings 2) Performance issues 3) Code style violations 4) Recommendations for improvement" > QUALITY_REPORT.md

echo "✅ Quality check completed. See QUALITY_REPORT.md"
```

### Automated Refactoring Script

```bash
#!/bin/bash

# refactor.sh - Automated code refactoring

PROJECT_DIR=${1:-.}
REFACTOR_TYPE=${2:-"general"}

echo "🔧 Starting automated refactoring in $PROJECT_DIR..."

cd "$PROJECT_DIR"

case "$REFACTOR_TYPE" in
  "security")
    codex exec --full-auto "Review all files for security issues and implement fixes: 1) Input sanitization 2) Output encoding 3) Authentication improvements 4) Secure headers"
    ;;
  "performance")
    codex exec --full-auto "Optimize code for performance: 1) Database query optimization 2) Caching strategies 3) Async/await patterns 4) Resource cleanup"
    ;;
  "documentation")
    codex exec --full-auto "Add comprehensive documentation: 1) Function docstrings 2) Type hints 3) Usage examples 4) README updates"
    ;;
  *)
    codex exec --full-auto "General code refactoring: 1) Improve naming conventions 2) Reduce complexity 3) Add error handling 4) Code organization"
    ;;
esac

echo "✅ Refactoring completed"
```

### Dependency Update Script

```bash
#!/bin/bash

# update-dependencies.sh - Smart dependency management

echo "📦 Analyzing and updating dependencies..."

# Check for security updates
gemini -p "Analyze package.json/requirements.txt for security vulnerabilities and outdated dependencies. Suggest specific version updates with migration notes." > DEPENDENCY_ANALYSIS.md

# Update packages (if safe)
if [ "$1" = "--auto" ]; then
  echo "🚀 Auto-updating dependencies..."
  droid exec "Update all dependencies to latest safe versions. Create migration plan for breaking changes." --auto medium
fi

# Generate changelog
claude -p "Create a changelog entry documenting dependency updates, security improvements, and potential breaking changes." > CHANGELOG.md

echo "✅ Dependency analysis completed"
```

## Automation Workflow Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🤖 Running AI pre-commit checks..."

# Check commit message
commit_msg=$(git log -1 --pretty=%B)
echo "$commit_msg" | claude -p "Validate this commit message. Check for: 1) Clear description 2) Proper format 3) Issue references 4) Breaking change indicators"

if [ $? -ne 0 ]; then
  echo "❌ Commit message validation failed"
  exit 1
fi

# Quick code review of staged changes
git diff --cached | claude -p "Quick review of staged changes. Check for: 1) Obvious bugs 2) Syntax errors 3) Missing tests 4) Security issues"

if [ $? -ne 0 ]; then
  echo "❌ Code review found issues"
  exit 1
fi

echo "✅ Pre-commit checks passed"
```

### Release Preparation Script

```bash
#!/bin/bash

# prepare-release.sh - Automated release preparation

VERSION=${1:-"patch"}
RELEASE_BRANCH=${2:-"release"}

echo "🚀 Preparing release for version bump: $VERSION"

# Create release branch
git checkout -b "$RELEASE_BRANCH"

# Update version numbers
codex exec --full-auto "Update all version numbers in the project for a $VERSION release: 1) package.json 2) __init__.py files 3) Docker files 4) Documentation"

# Generate release notes
git log --oneline $(git describe --tags --abbrev=0)..HEAD | \
  qwen -p "Create comprehensive release notes from these commits. Categorize by: 1) Features 2) Bug fixes 3) Breaking changes 4) Security improvements" > RELEASE_NOTES.md

# Update documentation
droid exec "Update all documentation for new release: 1) API docs 2) README 3) Installation guides 4) Migration guides" --auto low

echo "✅ Release preparation completed"
echo "📋 Review RELEASE_NOTES.md and commit changes"
```

### Database Migration Helper

```bash
#!/bin/bash

# migrate-db.sh - AI-assisted database migrations

MIGRATION_NAME=${1:-"auto_migration"}

echo "🗄️ Generating migration: $MIGRATION_NAME"

# Analyze schema changes
find models/ -name "*.py" | \
  claude -p "Analyze these model files for schema changes since last migration. Identify: 1) New tables 2) Column changes 3) Index changes 4) Relationship updates"

# Generate migration file
codex exec --full-auto "Create a database migration file named ${MIGRATION_NAME}.py. Include: 1) Forward migration 2) Rollback migration 3) Data transformations 4) Safety checks"

# Generate test data
gemini -p "Generate test data and validation queries for the new migration. Include: 1) Sample records 2) Constraint tests 3) Performance test queries"

echo "✅ Migration generated. Review and run: python manage.py migrate"
```

## Monitoring and Maintenance Examples

### Log Analysis Script

```bash
#!/bin/bash

# analyze-logs.sh - AI-powered log analysis

LOG_FILE=${1:-"app.log"}
TIMEFRAME=${2:-"24h"}

echo "📊 Analyzing logs from $LOG_FILE (last $TIMEFRAME)..."

# Extract errors and warnings
grep -E "(ERROR|WARN|CRITICAL)" "$LOG_FILE" | \
  qwen -p "Analyze these log entries for: 1) Error patterns 2) Root causes 3) Frequency analysis 4) Recommended fixes" > ERROR_ANALYSIS.md

# Performance analysis
grep -E "(slow|timeout|memory|performance)" "$LOG_FILE" | \
  claude -p "Identify performance issues from these logs. Focus on: 1) Slow queries 2) Memory leaks 3) Timeout patterns 4) Resource bottlenecks" > PERFORMANCE_ISSUES.md

# Generate summary
gemini -p "Create an executive summary of log analysis including: 1) Critical issues 2) Performance impact 3) Security concerns 4) Action items" > LOG_SUMMARY.md

echo "✅ Log analysis completed. Check *.md files"
```

### Health Check Automation

```bash
#!/bin/bash

# health-check.sh - Automated system health analysis

echo "🏥 Running AI-powered health checks..."

# Code health
find . -name "*.py" | head -20 | \
  droid exec "Analyze code health indicators: 1) Code complexity 2) Test coverage gaps 3) Dead code 4) Anti-patterns" --auto low > CODE_HEALTH.md

# Dependency health
claude -p "Analyze project dependencies for: 1) Security vulnerabilities 2) License compliance 3) Version conflicts 4) Maintenance status" > DEPENDENCY_HEALTH.md

# Architecture health
gemini -p "Review project architecture for: 1) Design patterns 2) Coupling issues 3) Scalability concerns 4) Technical debt" > ARCHITECTURE_HEALTH.md

# Generate actionable report
claude -p "Create a prioritized action plan based on health checks. Include: 1) Critical fixes 2) Improvements 3) Technical debt roadmap 4) Resource allocation" > HEALTH_ACTION_PLAN.md

echo "✅ Health check completed. Review generated reports"
```

## Integration Examples

### Slack Integration

```bash
#!/bin/bash

# slack-ai-notify.sh - Send AI analysis to Slack

WEBHOOK_URL=${SLACK_WEBHOOK_URL}
PROJECT_DIR=${1:-"."}

cd "$PROJECT_DIR"

# Analyze recent changes
git diff HEAD~1 | \
  claude -p "Analyze recent changes and create a concise summary for team notification. Include: 1) Key changes 2) Impact 3) Any action needed" > CHANGE_SUMMARY.txt

# Send to Slack
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$(cat CHANGE_SUMMARY.txt)\"}" \
  "$WEBHOOK_URL"

echo "📢 AI summary sent to Slack"
```

### Email Reports

```bash
#!/bin/bash

# email-ai-report.sh - Generate and email AI reports

EMAIL=${1:-"team@example.com"}
REPORT_TYPE=${2:-"weekly"}

echo "📧 Generating $REPORT_TYPE report..."

case "$REPORT_TYPE" in
  "weekly")
    git log --since="1 week ago" --oneline | \
      qwen -p "Create a weekly development report. Include: 1) Features completed 2) Bugs fixed 3) Code quality metrics 4) Team achievements" > weekly_report.md
    ;;
  "security")
    find . -name "*.py" -o -name "*.js" | \
      claude -p "Generate a security audit report. Include: 1) Vulnerabilities found 2) Risk assessment 3) Remediation steps 4) Best practices" > security_report.md
    ;;
esac

# Send email (using mail command or your preferred method)
mail -s "AI-generated $REPORT_TYPE report" "$EMAIL" < "${REPORT_TYPE}_report.md"

echo "✅ Report emailed to $EMAIL"
```