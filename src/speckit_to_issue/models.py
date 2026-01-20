"""Data models for speckit-to-issue."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class Priority(Enum):
    """Task priority levels."""

    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    WONT = "wont"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Parse priority from string."""
        mapping = {
            "must": cls.MUST,
            "should": cls.SHOULD,
            "could": cls.COULD,
            "won't": cls.WONT,
            "wont": cls.WONT,
        }
        return mapping.get(value.lower(), cls.SHOULD)


@dataclass
class Task:
    """Represents a parsed task from tasks.md."""

    id: str  # e.g., "T001"
    title: str  # e.g., "Create static directory structure"
    priority: Priority  # Must, Should, Could, Won't
    estimate: str  # e.g., "5 min", "2 hours"
    dependencies: str = "None"  # e.g., "T001, T002" or "None"
    file_path: Optional[str] = None  # e.g., "static/index.html"
    fr_refs: Optional[str] = None  # e.g., "FR-F01, FR-F02"
    nfr_refs: Optional[str] = None  # e.g., "NFR-F04"
    phase: str = ""  # e.g., "Phase 1: Infrastructure Setup"
    spec_name: str = ""  # e.g., "002-weather-frontend"
    acceptance_criteria: list[str] = field(default_factory=list)
    is_complete: bool = False  # True if ✅ or all criteria checked

    @property
    def full_title(self) -> str:
        """Issue title format: [T001] Task title."""
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
        match = re.search(r"Phase (\d+)", self.phase)
        if match:
            return f"phase-{match.group(1)}"
        return None

    @property
    def spec_label(self) -> str:
        """Spec name as label."""
        return f"spec:{self.spec_name}"


@dataclass
class Issue:
    """Represents a GitHub issue to create or that exists."""

    number: Optional[int] = None  # Issue number if exists
    title: str = ""  # Issue title
    body: str = ""  # Issue body (markdown)
    labels: list[str] = field(default_factory=list)
    url: Optional[str] = None  # Issue URL after creation
    assignee: Optional[str] = None  # GitHub username
    milestone: Optional[str] = None  # Milestone name


@dataclass
class ExistingIssue:
    """Minimal representation from gh issue list."""

    number: int
    title: str
    state: str = "open"  # "open" or "closed"
    url: str = ""


class SyncState(Enum):
    """Sync state between task and issue."""

    MISSING = "missing"  # Task has no issue
    SYNCED = "synced"  # Task has open issue
    CLOSED = "closed"  # Task has closed issue
    COMPLETE = "complete"  # Task marked complete in spec


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


class CreateResult(Enum):
    """Result of creating an issue."""

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


@dataclass
class ParseResult:
    """Result of parsing a tasks.md file."""

    spec_name: str  # Extracted from file path
    tasks: list[Task] = field(default_factory=list)  # All parsed tasks
    phases: list[str] = field(default_factory=list)  # List of phase names
    errors: list[str] = field(default_factory=list)  # Parse warnings

    @property
    def complete_count(self) -> int:
        """Count of completed tasks."""
        return sum(1 for t in self.tasks if t.is_complete)

    @property
    def incomplete_count(self) -> int:
        """Count of incomplete tasks."""
        return len(self.tasks) - self.complete_count
