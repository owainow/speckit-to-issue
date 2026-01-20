"""Unit tests for parser module."""

from pathlib import Path

import pytest

from speckit_to_issue.exceptions import ParseError
from speckit_to_issue.models import Priority
from speckit_to_issue.parser import (
    extract_spec_name,
    parse_task_block,
    parse_tasks_file,
)


class TestExtractSpecName:
    """Tests for extract_spec_name function."""

    def test_extract_from_specs_path(self) -> None:
        path = Path("specs/001-feature/tasks.md")
        assert extract_spec_name(path) == "001-feature"

    def test_extract_from_nested_path(self) -> None:
        path = Path("/home/user/project/specs/002-another/tasks.md")
        assert extract_spec_name(path) == "002-another"

    def test_fallback_to_parent(self) -> None:
        path = Path("some/other/path/tasks.md")
        assert extract_spec_name(path) == "path"


class TestParseTaskBlock:
    """Tests for parse_task_block function."""

    def test_parse_complete_task(self) -> None:
        content = """### T001: Create project structure
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `src/main.py`
- **FR:** FR-001
- **NFR:** NFR-001
- **Acceptance Criteria:**
  - [ ] Create src/ directory
  - [ ] Add __init__.py file
"""
        task = parse_task_block(content, "Phase 1: Setup", "001-feature")

        assert task.id == "T001"
        assert task.title == "Create project structure"
        assert task.priority == Priority.MUST
        assert task.estimate == "10 min"
        assert task.dependencies == "None"
        assert task.file_path == "src/main.py"
        assert task.fr_refs == "FR-001"
        assert task.nfr_refs == "NFR-001"
        assert task.phase == "Phase 1: Setup"
        assert task.spec_name == "001-feature"
        assert len(task.acceptance_criteria) == 2
        assert task.is_complete is False

    def test_parse_task_with_emoji_complete(self) -> None:
        content = """### T002: Add configuration ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T001
- **Acceptance Criteria:**
  - [x] Create config module
"""
        task = parse_task_block(content, "Phase 1: Setup", "001-feature")

        assert task.id == "T002"
        assert task.title == "Add configuration"
        assert task.is_complete is True

    def test_parse_task_all_criteria_complete(self) -> None:
        content = """### T003: Implement feature
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** None
- **Acceptance Criteria:**
  - [x] First criterion
  - [x] Second criterion
"""
        task = parse_task_block(content, "Phase 1: Setup", "001-feature")
        assert task.is_complete is True

    def test_parse_task_minimal_fields(self) -> None:
        content = """### T004: Simple task
- **Priority:** Could
- **Estimate:** 5 min
- **Acceptance Criteria:**
  - [ ] Do something
"""
        task = parse_task_block(content, "", "001-feature")

        assert task.id == "T004"
        assert task.title == "Simple task"
        assert task.priority == Priority.COULD
        assert task.dependencies == "None"
        assert task.file_path is None
        assert task.fr_refs is None
        assert task.nfr_refs is None

    def test_parse_invalid_block_raises(self) -> None:
        content = "This is not a valid task block"
        with pytest.raises(ParseError):
            parse_task_block(content, "", "001-feature")


class TestParseTasksFile:
    """Tests for parse_tasks_file function."""

    def test_parse_sample_file(self, sample_tasks_md: Path) -> None:
        result = parse_tasks_file(sample_tasks_md)

        assert result.spec_name == "sample-feature"
        assert len(result.tasks) == 3
        assert len(result.phases) == 2
        assert result.errors == []

    def test_parse_task_ids(self, sample_tasks_md: Path) -> None:
        result = parse_tasks_file(sample_tasks_md)

        task_ids = [t.id for t in result.tasks]
        assert task_ids == ["T001", "T002", "T003"]

    def test_parse_phases_assigned(self, sample_tasks_md: Path) -> None:
        result = parse_tasks_file(sample_tasks_md)

        assert result.tasks[0].phase == "Phase 1: Setup"
        assert result.tasks[1].phase == "Phase 1: Setup"
        assert result.tasks[2].phase == "Phase 2: Implementation"

    def test_parse_completion_status(self, sample_tasks_md: Path) -> None:
        result = parse_tasks_file(sample_tasks_md)

        assert result.tasks[0].is_complete is False  # T001
        assert result.tasks[1].is_complete is True   # T002 (has ✅ and [x])
        assert result.tasks[2].is_complete is False  # T003

    def test_complete_count(self, sample_tasks_md: Path) -> None:
        result = parse_tasks_file(sample_tasks_md)
        assert result.complete_count == 1
        assert result.incomplete_count == 2

    def test_file_not_found(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "nonexistent.md"
        with pytest.raises(FileNotFoundError):
            parse_tasks_file(nonexistent)

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("# No tasks here\n\nJust some text.")

        with pytest.raises(ParseError):
            parse_tasks_file(empty_file)
