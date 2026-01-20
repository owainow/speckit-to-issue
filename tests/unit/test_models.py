"""Unit tests for models module."""

import pytest

from speckit_to_issue.models import (
    CreateResult,
    CreateSummary,
    ParseResult,
    Priority,
    SyncState,
    Task,
)


class TestPriority:
    """Tests for Priority enum."""

    def test_from_string_must(self) -> None:
        assert Priority.from_string("Must") == Priority.MUST
        assert Priority.from_string("must") == Priority.MUST
        assert Priority.from_string("MUST") == Priority.MUST

    def test_from_string_should(self) -> None:
        assert Priority.from_string("Should") == Priority.SHOULD
        assert Priority.from_string("should") == Priority.SHOULD

    def test_from_string_could(self) -> None:
        assert Priority.from_string("Could") == Priority.COULD
        assert Priority.from_string("could") == Priority.COULD

    def test_from_string_wont(self) -> None:
        assert Priority.from_string("Won't") == Priority.WONT
        assert Priority.from_string("wont") == Priority.WONT

    def test_from_string_unknown_defaults_to_should(self) -> None:
        assert Priority.from_string("unknown") == Priority.SHOULD
        assert Priority.from_string("") == Priority.SHOULD


class TestTask:
    """Tests for Task dataclass."""

    def test_full_title(self, sample_task: Task) -> None:
        assert sample_task.full_title == "[T001] Create project structure"

    def test_priority_label_must(self, sample_task: Task) -> None:
        sample_task.priority = Priority.MUST
        assert sample_task.priority_label == "priority:high"

    def test_priority_label_should(self, sample_task: Task) -> None:
        sample_task.priority = Priority.SHOULD
        assert sample_task.priority_label == "priority:medium"

    def test_priority_label_could(self, sample_task: Task) -> None:
        sample_task.priority = Priority.COULD
        assert sample_task.priority_label == "priority:low"

    def test_phase_label_with_phase(self, sample_task: Task) -> None:
        sample_task.phase = "Phase 1: Setup"
        assert sample_task.phase_label == "phase-1"

    def test_phase_label_phase_2(self, sample_task: Task) -> None:
        sample_task.phase = "Phase 2: Implementation"
        assert sample_task.phase_label == "phase-2"

    def test_phase_label_no_phase(self, sample_task: Task) -> None:
        sample_task.phase = ""
        assert sample_task.phase_label is None

    def test_spec_label(self, sample_task: Task) -> None:
        sample_task.spec_name = "001-feature"
        assert sample_task.spec_label == "spec:001-feature"


class TestCreateSummary:
    """Tests for CreateSummary dataclass."""

    def test_empty_summary(self) -> None:
        summary = CreateSummary(
            total=0,
            created=0,
            skipped_exists=0,
            skipped_complete=0,
            failed=0,
        )
        assert summary.total == 0

    def test_summary_counts(self) -> None:
        summary = CreateSummary(
            total=10,
            created=5,
            skipped_exists=3,
            skipped_complete=1,
            failed=1,
        )
        assert summary.created + summary.skipped_exists + summary.skipped_complete + summary.failed == 10


class TestParseResult:
    """Tests for ParseResult dataclass."""

    def test_complete_count(self, sample_task: Task, complete_task: Task) -> None:
        result = ParseResult(
            spec_name="test",
            tasks=[sample_task, complete_task],
        )
        assert result.complete_count == 1
        assert result.incomplete_count == 1

    def test_empty_tasks(self) -> None:
        result = ParseResult(spec_name="test")
        assert result.complete_count == 0
        assert result.incomplete_count == 0


class TestSyncState:
    """Tests for SyncState enum."""

    def test_sync_states(self) -> None:
        assert SyncState.MISSING.value == "missing"
        assert SyncState.SYNCED.value == "synced"
        assert SyncState.CLOSED.value == "closed"
        assert SyncState.COMPLETE.value == "complete"


class TestCreateResult:
    """Tests for CreateResult enum."""

    def test_create_results(self) -> None:
        assert CreateResult.CREATED.value == "created"
        assert CreateResult.SKIPPED_EXISTS.value == "skipped_exists"
        assert CreateResult.SKIPPED_COMPLETE.value == "skipped_complete"
        assert CreateResult.FAILED.value == "failed"
