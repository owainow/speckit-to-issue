# Tasks: Tasks to GitHub Issues

> **Spec:** 001-tasks-to-issues  
> **Created:** 2026-01-20  
> **Total Tasks:** 35  
> **Estimated Time:** 6-8 hours

---

## Phase 1: Project Setup ✅

### T001: Create pyproject.toml with dependencies ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `pyproject.toml`
- **FR:** FR-001
- **Acceptance Criteria:**
  - [x] Create pyproject.toml with hatchling build backend
  - [x] Add typer>=0.9.0 and rich>=13.0.0 as dependencies
  - [x] Add dev dependencies: pytest, pytest-cov, ruff, mypy
  - [x] Define entry point: speckit-to-issue = speckit_to_issue.cli:app
  - [x] Set requires-python = ">=3.11"

### T002: Create source directory structure ✅
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T001
- **File:** `src/speckit_to_issue/__init__.py`
- **FR:** FR-001
- **Acceptance Criteria:**
  - [x] Create src/speckit_to_issue/ directory
  - [x] Create __init__.py with __version__ = "0.1.0"
  - [x] Create empty module files: cli.py, models.py, parser.py, github.py, mapper.py, labels.py, exceptions.py

### T003: Create test directory structure ✅
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T002
- **File:** `tests/conftest.py`
- **FR:** FR-001
- **Acceptance Criteria:**
  - [x] Create tests/ directory
  - [x] Create tests/unit/ directory
  - [x] Create tests/integration/ directory
  - [x] Create empty conftest.py

### T004: Create README with basic documentation ✅
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T001
- **File:** `README.md`
- **Acceptance Criteria:**
  - [x] Add project title and description
  - [x] Add installation instructions
  - [x] Add basic usage examples
  - [x] Add development setup section

---

## Phase 2: Core Models ✅

### T005: Implement Priority enum and Task dataclass ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T002
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-002
- **Acceptance Criteria:**
  - [x] Create Priority enum with MUST, SHOULD, COULD, WONT values
  - [x] Create Task dataclass with all fields from data-model.md
  - [x] Implement full_title property returning "[T001] Title" format
  - [x] Implement priority_label property mapping to label names
  - [x] Implement phase_label property extracting phase number

### T006: Implement Issue and ExistingIssue dataclasses ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T005
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-002
- **Acceptance Criteria:**
  - [x] Create Issue dataclass with number, title, body, labels, url, assignee, milestone
  - [x] Create ExistingIssue dataclass with number, title, state, url

### T007: Implement SyncState enum and status dataclasses ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T006
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-012
- **Acceptance Criteria:**
  - [x] Create SyncState enum with MISSING, SYNCED, CLOSED, COMPLETE
  - [x] Create TaskSyncStatus dataclass
  - [x] Create SyncReport dataclass with summary counts

### T008: Implement result dataclasses ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T007
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-002
- **Acceptance Criteria:**
  - [x] Create CreateResult enum with CREATED, SKIPPED_EXISTS, SKIPPED_COMPLETE, FAILED
  - [x] Create TaskResult dataclass
  - [x] Create CreateSummary dataclass with counts and results list
  - [x] Create ParseResult dataclass

### T009: Implement custom exceptions ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T002
- **File:** `src/speckit_to_issue/exceptions.py`
- **FR:** FR-017
- **Acceptance Criteria:**
  - [x] Create SpeckitToIssueError base exception
  - [x] Create ParseError for parsing failures
  - [x] Create GitHubCLIError base for gh errors
  - [x] Create AuthenticationError, RepositoryError, RateLimitError, IssueCreationError

### T010: Write unit tests for models ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T008
- **File:** `tests/unit/test_models.py`
- **Acceptance Criteria:**
  - [x] Test Task.full_title returns correct format
  - [x] Test Task.priority_label mapping
  - [x] Test Task.phase_label extraction
  - [x] Test CreateSummary counts

---

## Phase 3: Parser Implementation ✅

### T011: Implement task block regex patterns ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T008
- **File:** `src/speckit_to_issue/parser.py`
- **FR:** FR-002
- **Acceptance Criteria:**
  - [x] Define TASK_PATTERN regex for task blocks
  - [x] Define PHASE_PATTERN regex for phase headers
  - [x] Define CRITERIA_PATTERN for acceptance criteria lines
  - [x] Handle optional fields (File, FR, NFR, Dependencies)

### T012: Implement parse_tasks_file function ✅
- **Priority:** Must
- **Estimate:** 25 min
- **Dependencies:** T011
- **File:** `src/speckit_to_issue/parser.py`
- **FR:** FR-002
- **Acceptance Criteria:**
  - [x] Read file content with UTF-8 encoding
  - [x] Extract spec name from file path
  - [x] Parse all phases and tasks
  - [x] Return ParseResult with tasks and metadata
  - [x] Raise ParseError for invalid files

### T013: Implement completion detection ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T012
- **File:** `src/speckit_to_issue/parser.py`
- **FR:** FR-006
- **Acceptance Criteria:**
  - [x] Detect ✅ emoji in task title
  - [x] Check if all acceptance criteria are [x]
  - [x] Set is_complete flag on Task objects

### T014: Write unit tests for parser ✅
- **Priority:** Must
- **Estimate:** 25 min
- **Dependencies:** T013
- **File:** `tests/unit/test_parser.py`
- **Acceptance Criteria:**
  - [x] Create sample tasks.md fixture
  - [x] Test parsing complete task block
  - [x] Test parsing task with optional fields missing
  - [x] Test phase extraction
  - [x] Test completion detection for ✅ and [x] criteria
  - [x] Test error handling for invalid format

---

## Phase 4: GitHub CLI Integration ✅

### T015: Implement gh CLI availability check ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T009
- **File:** `src/speckit_to_issue/github.py`
- **FR:** FR-014
- **Acceptance Criteria:**
  - [x] Implement check_gh_available() using subprocess
  - [x] Return True if gh command exists
  - [x] Handle FileNotFoundError gracefully

### T016: Implement authentication check ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T015
- **File:** `src/speckit_to_issue/github.py`
- **FR:** FR-015
- **Acceptance Criteria:**
  - [x] Implement check_authenticated() calling `gh auth status`
  - [x] Return True if exit code is 0
  - [x] Raise AuthenticationError with helpful message

### T017: Implement get_current_repo function ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T016
- **File:** `src/speckit_to_issue/github.py`
- **FR:** FR-003
- **Acceptance Criteria:**
  - [x] Run `gh repo view --json nameWithOwner`
  - [x] Parse JSON response
  - [x] Return owner/repo string
  - [x] Raise RepositoryError if not in a git repo

### T018: Implement list_issues function ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T017
- **File:** `src/speckit_to_issue/github.py`
- **FR:** FR-009
- **Acceptance Criteria:**
  - [x] Run `gh issue list --json number,title,state --limit 1000`
  - [x] Parse JSON into list of ExistingIssue
  - [x] Accept optional repo parameter
  - [x] Handle empty repository

### T019: Implement create_issue function ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T018
- **File:** `src/speckit_to_issue/github.py`
- **FR:** FR-003
- **Acceptance Criteria:**
  - [x] Build gh issue create command with title, body, labels
  - [x] Execute subprocess and capture output
  - [x] Return issue URL on success
  - [x] Raise IssueCreationError on failure
  - [x] Handle rate limiting errors

### T020: Write unit tests for github module ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T019
- **File:** `tests/unit/test_github.py`
- **Acceptance Criteria:**
  - [x] Mock subprocess.run for all tests
  - [x] Test check_gh_available returns correct boolean
  - [x] Test check_authenticated raises on failure
  - [x] Test list_issues parses JSON correctly
  - [x] Test create_issue returns URL

---

## Phase 5: Label Management ✅

### T021: Implement label definitions ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T019
- **File:** `src/speckit_to_issue/labels.py`
- **FR:** FR-004
- **Acceptance Criteria:**
  - [x] Define LABEL_DEFINITIONS dict with priority labels
  - [x] Define PHASE_LABEL_COLOR constant
  - [x] Define SPEC_LABEL_COLOR constant
  - [x] Add "task" label for all speckit tasks

### T022: Implement ensure_labels function ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T021
- **File:** `src/speckit_to_issue/labels.py`
- **FR:** FR-004
- **Acceptance Criteria:**
  - [x] Accept list of label names
  - [x] Check existing labels via `gh label list`
  - [x] Create missing labels with appropriate colors
  - [x] Handle label creation errors gracefully

---

## Phase 6: Issue Mapper ✅

### T023: Implement standard issue body template ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T008
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-003
- **Acceptance Criteria:**
  - [x] Create STANDARD_TEMPLATE string constant
  - [x] Include task metadata section
  - [x] Include acceptance criteria as checkboxes
  - [x] Format file path if present

### T024: Implement Copilot-optimized template ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T023
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-007
- **Acceptance Criteria:**
  - [x] Create COPILOT_TEMPLATE string constant
  - [x] Include clear Objective section
  - [x] Add Files to Modify section
  - [x] Add Instructions for Copilot section

### T025: Implement task_to_issue function ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T024
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-003, FR-007
- **Acceptance Criteria:**
  - [x] Accept Task and copilot_mode flag
  - [x] Generate issue body from appropriate template
  - [x] Build labels list including priority, phase, spec
  - [x] Return Issue object ready for creation

### T026: Write unit tests for mapper ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T025
- **File:** `tests/unit/test_mapper.py`
- **Acceptance Criteria:**
  - [x] Test standard template generation
  - [x] Test Copilot template generation
  - [x] Test label generation
  - [x] Verify acceptance criteria formatting

---

## Phase 7: CLI Commands ✅

### T027: Implement create command ✅
- **Priority:** Must
- **Estimate:** 30 min
- **Dependencies:** T025, T022
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-001, FR-003, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010
- **Acceptance Criteria:**
  - [x] Create Typer app with create command
  - [x] Accept tasks_file as required argument
  - [x] Implement --dry-run flag to preview without creating
  - [x] Implement --skip-complete flag to skip completed tasks
  - [x] Implement --assign-copilot flag for Copilot-optimized body
  - [x] Implement --force flag to recreate existing issues
  - [x] Implement --repo flag for target repository
  - [x] Implement --milestone flag
  - [x] Display progress with Rich
  - [x] Show summary table on completion

### T028: Implement status command ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T027
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-012
- **Acceptance Criteria:**
  - [x] Add status command to Typer app
  - [x] Parse tasks.md file
  - [x] Fetch existing issues
  - [x] Compare and determine sync state for each task
  - [x] Display Rich table with Task, Status, Issue columns
  - [x] Show summary counts

### T029: Implement version command ✅
- **Priority:** Should
- **Estimate:** 5 min
- **Dependencies:** T027
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-013
- **Acceptance Criteria:**
  - [x] Add version command
  - [x] Display package version from __init__.py
  - [x] Add --version flag to main app

### T030: Write integration tests for CLI ✅
- **Priority:** Must
- **Estimate:** 25 min
- **Dependencies:** T029
- **File:** `tests/integration/test_cli.py`
- **Acceptance Criteria:**
  - [x] Use typer.testing.CliRunner
  - [x] Test create --dry-run with sample tasks.md
  - [x] Test status command output
  - [x] Test version command
  - [x] Mock subprocess calls to gh

---

## Phase 8: Polish & Packaging ✅

### T031: Add comprehensive error handling ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T030
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-017, FR-018
- **Acceptance Criteria:**
  - [x] Catch and display FileNotFoundError nicely
  - [x] Handle AuthenticationError with `gh auth login` prompt
  - [x] Handle RepositoryError with helpful message
  - [x] Handle RateLimitError with wait suggestion
  - [x] Use Rich console for colored error output

### T032: Add verbose logging option ✅
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T031
- **File:** `src/speckit_to_issue/cli.py`
- **NFR:** NFR-006
- **Acceptance Criteria:**
  - [x] Add --verbose / -v flag to create and status
  - [x] Show debug output when verbose enabled
  - [x] Log gh commands being executed

### T033: Create pytest fixtures ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T030
- **File:** `tests/conftest.py`
- **Acceptance Criteria:**
  - [x] Create sample_tasks_md fixture generating temp file
  - [x] Create mock_gh_cli fixture for mocking subprocess
  - [x] Create sample_task fixture with Task object

### T034: Ensure 80%+ test coverage ✅
- **Priority:** Must
- **Estimate:** 30 min
- **Dependencies:** T033
- **File:** `tests/`
- **NFR:** NFR-003
- **Acceptance Criteria:**
  - [x] Run pytest --cov and identify gaps
  - [x] Add missing test cases
  - [x] Achieve 80%+ coverage
  - [x] Add coverage config to pyproject.toml

### T035: Final documentation and cleanup ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T034
- **File:** `README.md`
- **Acceptance Criteria:**
  - [x] Update README with all CLI options
  - [x] Add troubleshooting section
  - [x] Add contributing guidelines
  - [x] Verify pyproject.toml metadata is complete

---

## Summary ✅

| Phase | Tasks | Estimate | Status |
|-------|-------|----------|--------|
| Phase 1: Project Setup | T001-T004 | 30 min | ✅ Complete |
| Phase 2: Core Models | T005-T010 | 70 min | ✅ Complete |
| Phase 3: Parser | T011-T014 | 85 min | ✅ Complete |
| Phase 4: GitHub CLI | T015-T020 | 85 min | ✅ Complete |
| Phase 5: Labels | T021-T022 | 25 min | ✅ Complete |
| Phase 6: Mapper | T023-T026 | 60 min | ✅ Complete |
| Phase 7: CLI Commands | T027-T030 | 80 min | ✅ Complete |
| Phase 8: Polish | T031-T035 | 90 min | ✅ Complete |
| **Total** | **35 tasks** | **~8.5 hours** | **✅ All Complete** |
