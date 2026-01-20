# Quickstart: Tasks to GitHub Issues

> **Spec:** 001-tasks-to-issues  
> **Created:** 2026-01-20

---

## Prerequisites

- Python 3.11+
- GitHub CLI (`gh`) installed and authenticated
- A repository with speckit tasks.md files

---

## Quick Setup

### 1. Install GitHub CLI (if not installed)

**Windows:**
```powershell
winget install GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

### 2. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate via browser or token.

### 3. Create Development Environment

```bash
cd speckit-to-issue

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

---

## Development Workflow

### Running the CLI

```bash
# During development
python -m speckit_to_issue.cli create specs/tasks.md --dry-run

# Or after pip install -e .
speckit-to-issue create specs/tasks.md --dry-run
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/speckit_to_issue --cov-report=term-missing

# Specific test file
pytest tests/unit/test_parser.py
```

### Linting and Type Checking

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/
```

---

## Usage Examples

### Create Issues (Dry Run)

```bash
speckit-to-issue create specs/001-feature/tasks.md --dry-run
```

### Create Issues for Real

```bash
speckit-to-issue create specs/001-feature/tasks.md
```

### Skip Completed Tasks

```bash
speckit-to-issue create specs/001-feature/tasks.md --skip-complete
```

### Assign to Copilot Coding Agent

```bash
speckit-to-issue create specs/001-feature/tasks.md --assign-copilot
```

### Target Specific Repository

```bash
speckit-to-issue create specs/001-feature/tasks.md --repo owner/other-repo
```

### Check Sync Status

```bash
speckit-to-issue status specs/001-feature/tasks.md
```

---

## Sample tasks.md

Create a test file at `specs/sample/tasks.md`:

```markdown
# Tasks: Sample Feature

> **Spec:** sample-feature  
> **Created:** 2026-01-20

---

## Phase 1: Setup

### T001: Create project structure
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **Acceptance Criteria:**
  - [ ] Create src/ directory
  - [ ] Create tests/ directory
  - [ ] Add __init__.py files

### T002: Add configuration
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T001
- **File:** `src/config.py`
- **Acceptance Criteria:**
  - [ ] Create config module
  - [ ] Add environment variable support
```

---

## Troubleshooting

### "gh: command not found"
Install GitHub CLI from https://cli.github.com

### "not logged in to any GitHub hosts"
Run `gh auth login` and complete authentication

### "repository not found"
Check repository name or ensure you have access

### "rate limit exceeded"
Wait a few minutes or check `gh api rate_limit`

---

## Next Steps

1. Run `speckit-to-issue create` on your Weather App tasks
2. Check GitHub Issues to see created issues
3. Assign issues to Copilot Coding Agent
4. Watch the AI SDLC in action!
