"""Unit tests for mapper module."""

import pytest

from speckit_to_issue.mapper import (
    build_issue_body,
    format_acceptance_criteria,
    get_labels_for_task,
    task_to_issue,
)
from speckit_to_issue.models import Priority, Task


class TestFormatAcceptanceCriteria:
    """Tests for format_acceptance_criteria function."""

    def test_format_single_criterion(self) -> None:
        criteria = ["Create project structure"]
        result = format_acceptance_criteria(criteria)
        assert result == "- [ ] Create project structure"

    def test_format_multiple_criteria(self) -> None:
        criteria = ["First item", "Second item", "Third item"]
        result = format_acceptance_criteria(criteria)
        lines = result.split("\n")
        assert len(lines) == 3
        assert all(line.startswith("- [ ] ") for line in lines)

    def test_format_empty_criteria(self) -> None:
        result = format_acceptance_criteria([])
        assert "No acceptance criteria defined" in result


class TestBuildIssueBody:
    """Tests for build_issue_body function."""

    def test_standard_template(self, sample_task: Task) -> None:
        body = build_issue_body(sample_task, copilot_mode=False)

        assert "## Task: T001" in body
        assert "001-feature" in body
        assert "Phase 1: Setup" in body
        assert "Must" in body
        assert "10 min" in body
        assert "src/main.py" in body
        assert "- [ ] Create src/ directory" in body

    def test_copilot_template(self, sample_task: Task) -> None:
        body = build_issue_body(sample_task, copilot_mode=True)

        assert "## Objective" in body
        assert "Create project structure" in body
        assert "## Files to Modify" in body
        assert "`src/main.py`" in body
        assert "## Instructions for Copilot" in body
        assert "- [ ] Create src/ directory" in body

    def test_copilot_template_no_file(self, sample_task: Task) -> None:
        sample_task.file_path = None
        body = build_issue_body(sample_task, copilot_mode=True)

        assert "## Files to Modify" not in body

    def test_standard_template_optional_fields(self) -> None:
        task = Task(
            id="T001",
            title="Simple task",
            priority=Priority.SHOULD,
            estimate="5 min",
            acceptance_criteria=["Do something"],
        )
        body = build_issue_body(task, copilot_mode=False)

        # Should not have file/FR/NFR rows if not set
        assert "**File**" not in body or "`None`" not in body


class TestGetLabelsForTask:
    """Tests for get_labels_for_task function."""

    def test_basic_labels(self, sample_task: Task) -> None:
        labels = get_labels_for_task(sample_task)

        assert "task" in labels
        assert "speckit" in labels
        assert "priority:high" in labels  # Must = high

    def test_phase_label(self, sample_task: Task) -> None:
        labels = get_labels_for_task(sample_task)
        assert "phase-1" in labels

    def test_spec_label(self, sample_task: Task) -> None:
        labels = get_labels_for_task(sample_task)
        assert "spec:001-feature" in labels

    def test_no_phase_label_when_empty(self) -> None:
        task = Task(
            id="T001",
            title="Task",
            priority=Priority.SHOULD,
            estimate="5 min",
            phase="",
        )
        labels = get_labels_for_task(task)
        assert not any(l.startswith("phase-") for l in labels)


class TestTaskToIssue:
    """Tests for task_to_issue function."""

    def test_creates_issue_with_title(self, sample_task: Task) -> None:
        issue = task_to_issue(sample_task)
        assert issue.title == "[T001] Create project structure"

    def test_creates_issue_with_body(self, sample_task: Task) -> None:
        issue = task_to_issue(sample_task)
        assert issue.body is not None
        assert len(issue.body) > 0

    def test_creates_issue_with_labels(self, sample_task: Task) -> None:
        issue = task_to_issue(sample_task)
        assert len(issue.labels) > 0
        assert "task" in issue.labels

    def test_copilot_mode_affects_body(self, sample_task: Task) -> None:
        standard = task_to_issue(sample_task, copilot_mode=False)
        copilot = task_to_issue(sample_task, copilot_mode=True)

        assert "## Task:" in standard.body
        assert "## Objective" in copilot.body
        assert "Instructions for Copilot" in copilot.body

    def test_copilot_mode_assigns_to_copilot(self, sample_task: Task) -> None:
        standard = task_to_issue(sample_task, copilot_mode=False)
        copilot = task_to_issue(sample_task, copilot_mode=True)

        assert standard.assignee is None
        assert copilot.assignee == "copilot"
