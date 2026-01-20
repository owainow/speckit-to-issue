"""Pytest fixtures for speckit-to-issue tests."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from speckit_to_issue.models import Priority, Task


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="T001",
        title="Create project structure",
        priority=Priority.MUST,
        estimate="10 min",
        dependencies="None",
        file_path="src/main.py",
        fr_refs="FR-001",
        nfr_refs=None,
        phase="Phase 1: Setup",
        spec_name="001-feature",
        acceptance_criteria=[
            "Create src/ directory",
            "Add __init__.py file",
            "Create tests/ directory",
        ],
        is_complete=False,
    )


@pytest.fixture
def complete_task() -> Task:
    """Create a completed task for testing."""
    return Task(
        id="T002",
        title="Add configuration",
        priority=Priority.SHOULD,
        estimate="15 min",
        dependencies="T001",
        file_path="src/config.py",
        phase="Phase 1: Setup",
        spec_name="001-feature",
        acceptance_criteria=["Create config module"],
        is_complete=True,
    )


@pytest.fixture
def sample_tasks_md(tmp_path: Path) -> Path:
    """Create a sample tasks.md file."""
    content = """# Tasks: Sample Feature

> **Spec:** sample-feature
> **Created:** 2026-01-20

---

## Phase 1: Setup

### T001: Create project structure
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `src/main.py`
- **FR:** FR-001
- **Acceptance Criteria:**
  - [ ] Create src/ directory
  - [ ] Add __init__.py file

### T002: Add configuration ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T001
- **File:** `src/config.py`
- **Acceptance Criteria:**
  - [x] Create config module
  - [x] Add environment support

## Phase 2: Implementation

### T003: Implement core logic
- **Priority:** Must
- **Estimate:** 30 min
- **Dependencies:** T001, T002
- **Acceptance Criteria:**
  - [ ] Create main function
  - [ ] Add error handling
"""
    tasks_file = tmp_path / "specs" / "sample-feature" / "tasks.md"
    tasks_file.parent.mkdir(parents=True)
    tasks_file.write_text(content, encoding="utf-8")
    return tasks_file


@pytest.fixture
def mock_gh_cli(mocker: Any) -> MagicMock:
    """Mock subprocess.run for gh CLI calls."""
    mock_run = mocker.patch("subprocess.run")

    def configure_response(
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        mock_run.return_value = MagicMock(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )

    mock_run.configure = configure_response
    mock_run.configure()

    return mock_run


@pytest.fixture
def mock_existing_issues() -> list[dict[str, Any]]:
    """Sample existing issues data."""
    return [
        {"number": 1, "title": "[T001] Create project structure", "state": "open", "url": "https://github.com/owner/repo/issues/1"},
        {"number": 2, "title": "[T002] Add configuration", "state": "closed", "url": "https://github.com/owner/repo/issues/2"},
    ]


@pytest.fixture
def mock_gh_list_issues(mocker: Any, mock_existing_issues: list[dict[str, Any]]) -> MagicMock:
    """Mock gh issue list command."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps(mock_existing_issues),
        stderr="",
    )
    return mock_run


@pytest.fixture
def sample_spec_md(tmp_path: Path) -> Path:
    """Create a sample spec.md file for testing."""
    content = """# Feature Spec: Sample Feature

## Feature Overview

### Description
This is a sample feature for testing.
It provides core functionality.

## User Stories

### US-001: User can do something
As a user, I want to do something so that I can achieve a goal.

## Functional Requirements

### FR-001: Basic functionality
The system must provide basic functionality.

### Success Criteria
- All tests pass
- Documentation complete
- Performance meets targets

## Non-Functional Requirements

### NFR-001: Performance
Response time under 200ms.
"""
    spec_file = tmp_path / "specs" / "sample-feature" / "spec.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(content, encoding="utf-8")
    return spec_file


@pytest.fixture
def sample_plan_md(tmp_path: Path) -> Path:
    """Create a sample plan.md file for testing."""
    content = """# Architecture & Implementation Plan

## Architecture Overview
The system follows a modular architecture with three main components:
- API Layer
- Business Logic
- Data Access

## Target State
Clean, maintainable code with full test coverage.

## Technical Approach
We will use Python with FastAPI for the backend.

## Key Decisions
- Use SQLAlchemy for ORM
- Implement caching with Redis
- Deploy to Azure Container Apps
"""
    plan_file = tmp_path / "specs" / "sample-feature" / "plan.md"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(content, encoding="utf-8")
    return plan_file


@pytest.fixture
def sample_research_md(tmp_path: Path) -> Path:
    """Create a sample research.md file for testing."""
    content = """# Technical Research

## Data Models
We need three main models:
- User: id, name, email
- Order: id, user_id, items
- Product: id, name, price

## API Endpoints
- GET /users
- POST /orders
- GET /products
"""
    research_file = tmp_path / "specs" / "sample-feature" / "research.md"
    research_file.parent.mkdir(parents=True, exist_ok=True)
    research_file.write_text(content, encoding="utf-8")
    return research_file


@pytest.fixture
def sample_spec_folder(
    sample_tasks_md: Path,
    sample_spec_md: Path,
    sample_plan_md: Path,
    sample_research_md: Path,
) -> Path:
    """Create a complete spec folder with all files."""
    return sample_tasks_md.parent
