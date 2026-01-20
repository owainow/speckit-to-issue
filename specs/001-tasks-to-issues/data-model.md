# Data Model: Tasks to GitHub Issues

> **Spec:** 001-tasks-to-issues  
> **Created:** 2026-01-20

---

## 1. Core Models

### 1.1 Task (Parsed from tasks.md)
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Priority(Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    WONT = "wont"


@dataclass
class Task:
    """Represents a parsed task from tasks.md."""
    
    id: str                          # e.g., "T001"
    title: str                       # e.g., "Create static directory structure"
    priority: Priority               # Must, Should, Could, Won't
    estimate: str                    # e.g., "5 min", "2 hours"
    dependencies: str = "None"       # e.g., "T001, T002" or "None"
    file_path: Optional[str] = None  # e.g., "static/index.html"
    fr_refs: Optional[str] = None    # e.g., "FR-F01, FR-F02"
    nfr_refs: Optional[str] = None   # e.g., "NFR-F04"
    phase: str = ""                  # e.g., "Phase 1: Infrastructure Setup"
    spec_name: str = ""              # e.g., "002-weather-frontend"
    acceptance_criteria: list[str] = field(default_factory=list)
    is_complete: bool = False        # True if ✅ or all criteria checked
    
    @property
    def full_title(self) -> str:
        """Issue title format: [T001] Task title"""
        return f"[{self.id}] {self.title}"
    
    @property
    def priority_label(self) -> str:
        """Convert priority to label."""
        mapping = {
            Priority.MUST: "priority:high",
            Priority.SHOULD: "priority:medium",
            Priority.COULD: "priority:low",
            Priority.WONT: "priority:wont",
        }
        return mapping.get(self.priority, "priority:medium")
    
    @property
    def phase_label(self) -> Optional[str]:
        """Extract phase number for label."""
        import re
        match = re.search(r"Phase (\d+)", self.phase)
        if match:
            return f"phase-{match.group(1)}"
        return None
    
    @property
    def spec_label(self) -> str:
        """Spec name as label."""
        return f"spec:{self.spec_name}"
```

### 1.2 Issue (GitHub Issue Representation)
```python
@dataclass
class Issue:
    """Represents a GitHub issue to create or that exists."""
    
    number: Optional[int] = None     # Issue number if exists
    title: str = ""                  # Issue title
    body: str = ""                   # Issue body (markdown)
    labels: list[str] = field(default_factory=list)
    url: Optional[str] = None        # Issue URL after creation
    assignee: Optional[str] = None   # GitHub username
    milestone: Optional[str] = None  # Milestone name


@dataclass
class ExistingIssue:
    """Minimal representation from gh issue list."""
    
    number: int
    title: str
    state: str = "open"  # "open" or "closed"
    url: str = ""
```

### 1.3 Sync Status
```python
from enum import Enum


class SyncState(Enum):
    MISSING = "missing"      # Task has no issue
    SYNCED = "synced"        # Task has open issue
    CLOSED = "closed"        # Task has closed issue
    COMPLETE = "complete"    # Task marked complete in spec


@dataclass
class TaskSyncStatus:
    """Sync status for a single task."""
    
    task: Task
    state: SyncState
    issue_number: Optional[int] = None
    issue_url: Optional[str] = None


@dataclass
class SyncReport:
    """Overall sync status report."""
    
    total_tasks: int
    synced: int
    missing: int
    closed: int
    complete: int
    statuses: list[TaskSyncStatus] = field(default_factory=list)
```

---

## 2. Configuration

### 2.1 CLI Config
```python
@dataclass
class CreateConfig:
    """Configuration for create command."""
    
    tasks_file: Path
    repo: str
    dry_run: bool = False
    skip_complete: bool = False
    assign_copilot: bool = False
    force: bool = False
    milestone: Optional[str] = None
    verbose: bool = False


@dataclass
class StatusConfig:
    """Configuration for status command."""
    
    tasks_file: Path
    repo: str
    verbose: bool = False
```

---

## 3. Result Models

### 3.1 Creation Result
```python
from enum import Enum


class CreateResult(Enum):
    CREATED = "created"
    SKIPPED_EXISTS = "skipped_exists"
    SKIPPED_COMPLETE = "skipped_complete"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Result of processing a single task."""
    
    task: Task
    result: CreateResult
    issue_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CreateSummary:
    """Summary of create operation."""
    
    total: int
    created: int
    skipped_exists: int
    skipped_complete: int
    failed: int
    results: list[TaskResult] = field(default_factory=list)
```

---

## 4. Issue Body Templates

### 4.1 Standard Template
```python
STANDARD_TEMPLATE = """## Task: {task_id}

**Spec:** {spec_name}  
**Phase:** {phase}  
**Priority:** {priority}  
**Estimate:** {estimate}  
**Dependencies:** {dependencies}  
{file_section}
{requirements_section}

## Acceptance Criteria

{acceptance_criteria}
"""
```

### 4.2 Copilot Agent Template
```python
COPILOT_TEMPLATE = """## Objective

{title}

{file_section}

## Acceptance Criteria

{acceptance_criteria}

## Context

| Field | Value |
|-------|-------|
| Spec | {spec_name} |
| Phase | {phase} |
| Priority | {priority} |
| Estimate | {estimate} |
| Dependencies | {dependencies} |

## Instructions for Copilot

Implement this task following the acceptance criteria above.
- Follow existing code patterns in the repository
- Add appropriate tests if applicable
- Create a pull request when complete
"""
```

---

## 5. Label Definitions

### 5.1 Auto-Generated Labels
```python
LABEL_DEFINITIONS = {
    "priority:high": {
        "color": "d73a4a",
        "description": "High priority - Must have"
    },
    "priority:medium": {
        "color": "fbca04",
        "description": "Medium priority - Should have"
    },
    "priority:low": {
        "color": "0e8a16",
        "description": "Low priority - Could have"
    },
    "task": {
        "color": "1d76db",
        "description": "Implementation task from speckit"
    },
}

# Phase labels are dynamic: phase-1, phase-2, etc.
PHASE_LABEL_COLOR = "5319e7"

# Spec labels are dynamic: spec:001-feature-name
SPEC_LABEL_COLOR = "c5def5"
```

---

## 6. Parsing Output

### 6.1 Parse Result
```python
@dataclass
class ParseResult:
    """Result of parsing a tasks.md file."""
    
    spec_name: str                    # Extracted from file path
    tasks: list[Task]                 # All parsed tasks
    phases: list[str]                 # List of phase names
    errors: list[str] = field(default_factory=list)  # Parse warnings
    
    @property
    def complete_count(self) -> int:
        return sum(1 for t in self.tasks if t.is_complete)
    
    @property
    def incomplete_count(self) -> int:
        return len(self.tasks) - self.complete_count
```

---

## 7. Error Types

```python
class SpeckitToIssueError(Exception):
    """Base exception for speckit-to-issue."""
    pass


class ParseError(SpeckitToIssueError):
    """Error parsing tasks.md file."""
    pass


class GitHubCLIError(SpeckitToIssueError):
    """Error from GitHub CLI."""
    pass


class AuthenticationError(GitHubCLIError):
    """Not authenticated with GitHub."""
    pass


class RepositoryError(GitHubCLIError):
    """Repository not found or no access."""
    pass


class RateLimitError(GitHubCLIError):
    """GitHub API rate limited."""
    pass


class IssueCreationError(GitHubCLIError):
    """Failed to create issue."""
    pass
```

---

## 8. Type Aliases

```python
from typing import TypeAlias

TaskId: TypeAlias = str           # "T001", "T002", etc.
IssueNumber: TypeAlias = int      # 42, 43, etc.
RepoName: TypeAlias = str         # "owner/repo"
LabelName: TypeAlias = str        # "priority:high"
```
