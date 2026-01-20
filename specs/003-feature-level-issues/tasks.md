# Tasks: Feature-Level Issue Creation

## Phase 1: Core Feature Builder

### T001: Create FeatureIssueBuilder class
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] New module `feature_builder.py` created
  - [ ] `FeatureIssueBuilder` class with `build()` method
  - [ ] Takes `SpecContext` and `list[Task]` as inputs
  - [ ] Returns `Issue` object

### T002: Implement overview section builder
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: T001
- **Acceptance Criteria**:
  - [ ] `_build_overview_section()` extracts description from spec.md
  - [ ] Includes business value if present
  - [ ] Formats as markdown with ## header

### T003: Implement architecture section builder
- **Priority**: Must
- **Estimate**: 15 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: T001
- **Acceptance Criteria**:
  - [ ] `_build_architecture_section()` extracts key decisions
  - [ ] Includes target state diagram if present
  - [ ] Condenses to essential information (not full doc)

### T004: Implement tasks-by-phase builder
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: T001
- **Acceptance Criteria**:
  - [ ] `_build_tasks_by_phase()` groups tasks by phase
  - [ ] Each task has checkbox, ID, title, estimate
  - [ ] Acceptance criteria nested under each task
  - [ ] Phases in order (Phase 1, Phase 2, etc.)

### T005: Implement files section builder
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: T001
- **Acceptance Criteria**:
  - [ ] `_build_files_section()` collects all file_path from tasks
  - [ ] Deduplicates file list
  - [ ] Formats as bullet list with backticks

### T006: Add Copilot instructions section
- **Priority**: Must
- **Estimate**: 5 min
- **File**: `src/speckit_to_issue/feature_builder.py`
- **Dependencies**: T001
- **Acceptance Criteria**:
  - [ ] Standard instructions block for Copilot agent
  - [ ] Includes guidance on phase order, testing, PR

## Phase 2: CLI Integration

### T007: Add --granular flag to create command
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `src/speckit_to_issue/cli.py`
- **Dependencies**: T001-T006
- **Acceptance Criteria**:
  - [ ] `--granular` flag added to create command
  - [ ] Default behavior (no flag) = feature-level issue
  - [ ] With `--granular` = individual task issues (existing behavior)
  - [ ] Help text explains the difference

### T008: Integrate FeatureIssueBuilder into create command
- **Priority**: Must
- **Estimate**: 15 min
- **File**: `src/speckit_to_issue/cli.py`
- **Dependencies**: T007
- **Acceptance Criteria**:
  - [ ] Import FeatureIssueBuilder
  - [ ] When not granular: build single feature issue
  - [ ] Load full spec context (spec.md, architecture.md, tasks.md)
  - [ ] Create issue and display URL

### T009: Update spec_to_feature_issue in mapper
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `src/speckit_to_issue/mapper.py`
- **Dependencies**: T001-T006
- **Acceptance Criteria**:
  - [ ] Add `spec_to_feature_issue()` function
  - [ ] Uses FeatureIssueBuilder internally
  - [ ] Returns Issue with appropriate labels

## Phase 3: Testing

### T010: Unit tests for FeatureIssueBuilder
- **Priority**: Must
- **Estimate**: 25 min
- **File**: `tests/unit/test_feature_builder.py`
- **Dependencies**: T001-T006
- **Acceptance Criteria**:
  - [ ] Test overview section generation
  - [ ] Test architecture section generation
  - [ ] Test tasks grouped by phase
  - [ ] Test files deduplication
  - [ ] Test full issue body assembly

### T011: Integration test for feature-level create
- **Priority**: Should
- **Estimate**: 15 min
- **File**: `tests/integration/test_cli_feature.py`
- **Dependencies**: T008
- **Acceptance Criteria**:
  - [ ] Test create command without --granular
  - [ ] Verify single issue created
  - [ ] Verify issue body contains all sections

### T012: Test --granular backward compatibility
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `tests/integration/test_cli_feature.py`
- **Dependencies**: T008
- **Acceptance Criteria**:
  - [ ] Test create command with --granular
  - [ ] Verify multiple issues created (one per task)
  - [ ] Existing tests still pass

## Phase 4: Cleanup

### T013: Update README with new usage
- **Priority**: Should
- **Estimate**: 10 min
- **File**: `README.md`
- **Dependencies**: T008
- **Acceptance Criteria**:
  - [ ] Document feature-level issue creation (default)
  - [ ] Document --granular option
  - [ ] Update example commands
  - [ ] Add example of generated issue body

### T014: Delete obsolete 19 task issues from test repo
- **Priority**: Could
- **Estimate**: 5 min
- **File**: N/A (manual or script)
- **Dependencies**: T008
- **Acceptance Criteria**:
  - [ ] Issues 20-38 deleted from end-to-end-ai-sdlc repo
  - [ ] New single feature issue created for 003-help-faq-page
