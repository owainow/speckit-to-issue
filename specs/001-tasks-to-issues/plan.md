# Implementation Plan: Tasks to GitHub Issues

> **Spec:** 001-tasks-to-issues  
> **Created:** 2026-01-20

---

## 1. Implementation Strategy

### 1.1 Approach
**Bottom-up build** - Start with models and parser, then build up through services to CLI. This ensures each layer is tested before building the next.

### 1.2 Implementation Order
```
Phase 1: Project Setup
    └── pyproject.toml, directory structure, dependencies
    
Phase 2: Core Models
    └── Data classes for Task, Issue, Results
    
Phase 3: Parser
    └── Parse tasks.md files into Task objects
    
Phase 4: GitHub Integration
    └── gh CLI wrapper for issue operations
    
Phase 5: Mapper
    └── Convert Tasks to Issue bodies
    
Phase 6: CLI Commands
    └── create, status commands with all options
    
Phase 7: Polish & Packaging
    └── Error handling, help text, distribution
```

---

## 2. Architecture

### 2.1 Module Structure
```
src/speckit_to_issue/
├── __init__.py           # Package init, version
├── cli.py                # Typer CLI entry point
├── models.py             # Data classes
├── parser.py             # tasks.md parsing
├── github.py             # gh CLI wrapper
├── mapper.py             # Task → Issue body
├── labels.py             # Label management
└── exceptions.py         # Custom exceptions
```

### 2.2 Dependency Flow
```
cli.py
   ├── parser.py ──→ models.py
   ├── github.py ──→ models.py, exceptions.py
   ├── mapper.py ──→ models.py
   └── labels.py ──→ github.py
```

---

## 3. File Changes

### 3.1 New Files
| File | Purpose |
|------|---------|
| `pyproject.toml` | Package configuration, dependencies |
| `src/speckit_to_issue/__init__.py` | Package init with version |
| `src/speckit_to_issue/cli.py` | Typer CLI commands |
| `src/speckit_to_issue/models.py` | Data classes |
| `src/speckit_to_issue/parser.py` | tasks.md parsing |
| `src/speckit_to_issue/github.py` | GitHub CLI wrapper |
| `src/speckit_to_issue/mapper.py` | Issue body generation |
| `src/speckit_to_issue/labels.py` | Label management |
| `src/speckit_to_issue/exceptions.py` | Custom exceptions |
| `tests/conftest.py` | Pytest fixtures |
| `tests/unit/test_parser.py` | Parser tests |
| `tests/unit/test_mapper.py` | Mapper tests |
| `tests/unit/test_models.py` | Model tests |
| `tests/integration/test_cli.py` | CLI integration tests |
| `README.md` | Documentation |

---

## 4. Component Specifications

### 4.1 Parser (`parser.py`)

**Responsibilities:**
- Read tasks.md file
- Extract spec name from path
- Parse task blocks with regex
- Detect phases
- Determine completion status

**Key Functions:**
```python
def parse_tasks_file(file_path: Path) -> ParseResult:
    """Parse a tasks.md file and return structured data."""
    
def parse_task_block(content: str, phase: str, spec_name: str) -> Task:
    """Parse a single task block."""
    
def is_task_complete(title: str, criteria: list[str]) -> bool:
    """Determine if a task is marked complete."""
```

### 4.2 GitHub Integration (`github.py`)

**Responsibilities:**
- Check gh CLI availability
- Verify authentication
- Get current repository
- List existing issues
- Create issues
- Create labels

**Key Functions:**
```python
def check_gh_available() -> bool:
    """Check if gh CLI is installed."""
    
def check_authenticated() -> bool:
    """Check if user is authenticated."""
    
def get_current_repo() -> str:
    """Get current repository (owner/repo)."""
    
def list_issues(repo: str) -> list[ExistingIssue]:
    """List all issues in repository."""
    
def create_issue(issue: Issue, repo: str) -> str:
    """Create issue and return URL."""
    
def ensure_labels(labels: list[str], repo: str) -> None:
    """Create labels if they don't exist."""
```

### 4.3 Mapper (`mapper.py`)

**Responsibilities:**
- Convert Task to Issue
- Generate issue body from template
- Build label list
- Format for Copilot mode

**Key Functions:**
```python
def task_to_issue(task: Task, copilot_mode: bool = False) -> Issue:
    """Convert a Task to an Issue."""
    
def build_issue_body(task: Task, copilot_mode: bool = False) -> str:
    """Generate issue body markdown."""
    
def get_labels_for_task(task: Task) -> list[str]:
    """Generate labels for a task."""
```

### 4.4 CLI (`cli.py`)

**Commands:**
```python
@app.command()
def create(
    tasks_file: Path,
    dry_run: bool = False,
    skip_complete: bool = False,
    assign_copilot: bool = False,
    force: bool = False,
    repo: Optional[str] = None,
    milestone: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Create GitHub issues from tasks.md"""

@app.command()
def status(
    tasks_file: Path,
    repo: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Show sync status between tasks and issues"""

@app.command()
def version() -> None:
    """Show version"""
```

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Module | Test File | Coverage Target |
|--------|-----------|-----------------|
| parser.py | test_parser.py | 95% |
| mapper.py | test_mapper.py | 95% |
| models.py | test_models.py | 90% |
| labels.py | test_labels.py | 90% |

### 5.2 Integration Tests

| Scenario | Approach |
|----------|----------|
| CLI commands | Use CliRunner, mock subprocess |
| gh CLI calls | Mock subprocess.run responses |
| End-to-end | Sample tasks.md files |

### 5.3 Test Fixtures
```python
# conftest.py
@pytest.fixture
def sample_tasks_md(tmp_path) -> Path:
    """Create sample tasks.md file."""
    
@pytest.fixture
def mock_gh_cli(mocker):
    """Mock gh CLI subprocess calls."""
```

---

## 6. Error Handling Strategy

### 6.1 Error Categories

| Category | Handling |
|----------|----------|
| File errors | Rich error message with path |
| Parse errors | Show line number and context |
| Auth errors | Prompt `gh auth login` |
| Network errors | Retry with backoff, then fail |
| Rate limits | Show wait time, optionally wait |

### 6.2 User Feedback
```python
from rich.console import Console
console = Console(stderr=True)

# Error
console.print("[red]Error:[/red] File not found: specs/tasks.md")

# Warning
console.print("[yellow]Warning:[/yellow] Skipping T001 (already exists)")

# Success
console.print("[green]✓[/green] Created: [T001] Task title")
```

---

## 7. CLI Output Design

### 7.1 Progress Display
```
📋 Parsing: specs/002-weather-frontend/tasks.md
   Found 24 tasks (22 incomplete)

🚀 Creating issues in owner/repo...
   ✅ [T001] Create static directory structure
   ✅ [T002] Update FastAPI to serve static files
   ⏭️  [T003] Already exists (#42)
   ⏭️  [T004] Task complete (skipped)
   ❌ [T005] Failed: Rate limited
   ...
```

### 7.2 Summary Display
```
📊 Summary
┌──────────────────┬───────┐
│ Status           │ Count │
├──────────────────┼───────┤
│ Created          │    18 │
│ Skipped (exists) │     3 │
│ Skipped (done)   │     2 │
│ Failed           │     1 │
└──────────────────┴───────┘
```

### 7.3 Status Command
```
📋 Sync Status: specs/002-weather-frontend/tasks.md
┌───────┬────────────────────────────────┬──────────┬─────────────┐
│ Task  │ Title                          │ Status   │ Issue       │
├───────┼────────────────────────────────┼──────────┼─────────────┤
│ T001  │ Create static directory        │ ✅ Synced │ #42         │
│ T002  │ Update FastAPI                 │ ✅ Synced │ #43         │
│ T003  │ Create base HTML               │ ❌ Missing│             │
│ T004  │ Create page layout             │ 📦 Closed │ #44         │
└───────┴────────────────────────────────┴──────────┴─────────────┘
```

---

## 8. Package Distribution

### 8.1 pyproject.toml Structure
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "speckit-to-issue"
version = "0.1.0"
description = "Convert speckit tasks to GitHub issues"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[project.scripts]
speckit-to-issue = "speckit_to_issue.cli:app"
```

### 8.2 Installation Methods
```bash
# From PyPI (after publishing)
pip install speckit-to-issue

# From source
pip install -e .

# Via uvx (after publishing)
uvx speckit-to-issue create specs/tasks.md
```

---

## 9. Success Criteria Checklist

- [ ] Parse valid tasks.md files accurately
- [ ] Create issues with correct title format
- [ ] Generate appropriate labels
- [ ] Detect and skip duplicates
- [ ] Support --dry-run preview
- [ ] Support --skip-complete flag
- [ ] Support --assign-copilot formatting
- [ ] Show clear progress and summary
- [ ] Handle errors gracefully
- [ ] Work on Windows, macOS, Linux
- [ ] 80%+ test coverage
- [ ] Installable via pip

---

## 10. Timeline

| Day | Phase | Deliverables |
|-----|-------|--------------|
| 1 AM | Setup + Models | pyproject.toml, models.py, exceptions.py |
| 1 PM | Parser | parser.py with tests |
| 1 PM | GitHub | github.py with mocked tests |
| 2 AM | Mapper + Labels | mapper.py, labels.py with tests |
| 2 AM | CLI | cli.py with integration tests |
| 2 PM | Polish | Error handling, README, packaging |

**Estimated Total: 1-2 days**
