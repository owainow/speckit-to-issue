# Research: Tasks to GitHub Issues

> **Spec:** 001-tasks-to-issues  
> **Created:** 2026-01-20

---

## 1. GitHub CLI (gh) Integration

### 1.1 Issue Creation
```bash
gh issue create \
  --title "[T001] Task title" \
  --body "Issue body content" \
  --label "priority:high" \
  --label "phase-1" \
  --repo "owner/repo"
```

**Output on success:**
```
https://github.com/owner/repo/issues/42
```

**Python subprocess:**
```python
import subprocess
import json

result = subprocess.run(
    ["gh", "issue", "create", "--title", title, "--body", body, "--label", label],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    issue_url = result.stdout.strip()
```

### 1.2 List Existing Issues
```bash
gh issue list --repo owner/repo --json number,title --limit 1000
```

**Response:**
```json
[
  {"number": 42, "title": "[T001] Create static directory"},
  {"number": 43, "title": "[T002] Update FastAPI"}
]
```

### 1.3 Label Management
```bash
# Create label if not exists
gh label create "priority:high" --color "d73a4a" --description "High priority task" --repo owner/repo

# List labels
gh label list --repo owner/repo --json name
```

### 1.4 Authentication Check
```bash
gh auth status
```

**Exit code 0 = authenticated, non-zero = not authenticated**

### 1.5 Get Current Repository
```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

**Output:** `owner/repo`

---

## 2. Speckit Tasks.md Format Analysis

### 2.1 Task Block Pattern
```markdown
### T001: Create static directory structure
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** None
- **File:** `static/index.html`
- **FR:** FR-F01
- **NFR:** NFR-F04
- **Acceptance Criteria:**
  - [ ] Criterion one
  - [ ] Criterion two
  - [x] Completed criterion
```

### 2.2 Regex Pattern for Parsing
```python
TASK_PATTERN = re.compile(
    r"### (T\d+): (.+?)(?:\s*✅)?\n"
    r"- \*\*Priority:\*\* (\w+)\n"
    r"- \*\*Estimate:\*\* (.+?)\n"
    r"(?:- \*\*Dependencies:\*\* (.+?)\n)?"
    r"(?:- \*\*File:\*\* (.+?)\n)?"
    r"(?:- \*\*FR:\*\* (.+?)\n)?"
    r"(?:- \*\*NFR:\*\* (.+?)\n)?"
    r"- \*\*Acceptance Criteria:\*\*\n((?:\s+- \[[ x]\] .+\n)+)",
    re.MULTILINE
)
```

### 2.3 Phase Detection
```python
PHASE_PATTERN = re.compile(r"## (Phase \d+: .+)")
```

### 2.4 Completion Detection
- Title contains ✅ emoji
- All acceptance criteria are `[x]`

---

## 3. Typer CLI Framework

### 3.1 Basic Structure
```python
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(
    name="speckit-to-issue",
    help="Convert speckit tasks to GitHub issues"
)

@app.command()
def create(
    tasks_file: Path = typer.Argument(..., help="Path to tasks.md"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview only"),
    skip_complete: bool = typer.Option(False, "--skip-complete", "-s"),
    assign_copilot: bool = typer.Option(False, "--assign-copilot", "-c"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r"),
):
    """Create GitHub issues from tasks.md"""
    pass

@app.command()
def status(
    tasks_file: Path = typer.Argument(..., help="Path to tasks.md"),
):
    """Show sync status between tasks and issues"""
    pass

if __name__ == "__main__":
    app()
```

### 3.2 Rich Integration for Output
```python
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

console = Console()

# Progress bar
with Progress() as progress:
    task = progress.add_task("Creating issues...", total=len(tasks))
    for t in tasks:
        create_issue(t)
        progress.advance(task)

# Table output
table = Table(title="Sync Status")
table.add_column("Task", style="cyan")
table.add_column("Status", style="green")
table.add_column("Issue", style="blue")
console.print(table)
```

---

## 4. Copilot Coding Agent Integration

### 4.1 Issue Format for Copilot
Copilot Coding Agent works best with:
- Clear objective statement
- Specific files to modify
- Checkable acceptance criteria
- Context about the codebase

### 4.2 Recommended Body Template
```markdown
## Objective
{task_title}

## Files to Modify
- `{file_path}`

## Acceptance Criteria
{acceptance_criteria_as_checkboxes}

## Context
- **Spec:** {spec_name}
- **Phase:** {phase}
- **Dependencies:** {dependencies}
- **Estimate:** {estimate}

## Instructions
Implement this task following the acceptance criteria.
Create a pull request when complete.
```

### 4.3 Triggering Copilot
After issue creation, Copilot can be triggered via:
1. Issue assignment to `@copilot`
2. Comment `@copilot implement this`
3. GitHub Actions workflow

---

## 5. Duplicate Detection Strategy

### 5.1 Title Prefix Matching
```python
def find_existing_issue(task_id: str, issues: list[dict]) -> Optional[int]:
    """Find issue with matching [TXXX] prefix."""
    prefix = f"[{task_id}]"
    for issue in issues:
        if issue["title"].startswith(prefix):
            return issue["number"]
    return None
```

### 5.2 Caching Issue List
```python
@functools.lru_cache(maxsize=1)
def get_existing_issues(repo: str) -> list[dict]:
    """Fetch and cache existing issues."""
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--json", "number,title", "--limit", "1000"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

---

## 6. Error Handling

### 6.1 gh CLI Errors
| Exit Code | Meaning | Handling |
|-----------|---------|----------|
| 0 | Success | Continue |
| 1 | General error | Parse stderr |
| 4 | Not authenticated | Prompt gh auth login |

### 6.2 Common Error Patterns
```python
if "not logged in" in result.stderr.lower():
    raise AuthenticationError("Run 'gh auth login' first")
if "Could not resolve" in result.stderr:
    raise RepositoryError(f"Repository not found: {repo}")
if "rate limit" in result.stderr.lower():
    raise RateLimitError("GitHub API rate limited")
```

---

## 7. Package Distribution

### 7.1 pyproject.toml Entry Point
```toml
[project.scripts]
speckit-to-issue = "speckit_to_issue.cli:app"
```

### 7.2 uvx Compatibility
Package must be on PyPI for uvx:
```bash
uvx speckit-to-issue create specs/tasks.md
```

Or from git:
```bash
uvx --from git+https://github.com/user/speckit-to-issue.git speckit-to-issue create specs/tasks.md
```

---

## 8. References

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Copilot Coding Agent](https://docs.github.com/en/copilot)
- [Python Subprocess](https://docs.python.org/3/library/subprocess.html)
