# Tasks: Spec Context Injection

> **Spec:** 002-spec-context-injection  
> **Created:** 2026-01-20  
> **Total Tasks:** 23  
> **Estimated Effort:** 4-5 hours

---

## Summary

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| Phase 1 | Core Models | T001-T003 | ✅ Complete |
| Phase 2 | Spec Reader Module | T004-T011 | ✅ Complete |
| Phase 3 | Mapper Integration | T012-T015 | ✅ Complete |
| Phase 4 | CLI Integration | T016-T019 | ✅ Complete |
| Phase 5 | Testing & Polish | T020-T023 | ✅ Complete |

---

## Phase 1: Core Models

### T001: Add SpecContext dataclass to models.py ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** None
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-001, FR-014

**Description:**
Create the SpecContext dataclass to hold extracted spec context from spec files.

**Acceptance Criteria:**
- [ ] SpecContext dataclass with fields: feature_overview, success_criteria, architecture_overview, target_state, technical_approach, key_decisions, data_models
- [ ] All fields are str type with empty string defaults
- [ ] Metadata fields: spec_folder, files_found, files_missing, extraction_warnings
- [ ] Proper type hints and docstrings

**Implementation Notes:**
```python
@dataclass
class SpecContext:
    """Extracted context from spec folder files."""
    feature_overview: str = ""
    success_criteria: str = ""
    architecture_overview: str = ""
    target_state: str = ""
    technical_approach: str = ""
    key_decisions: str = ""
    data_models: str = ""
    spec_folder: str = ""
    files_found: list[str] = field(default_factory=list)
    files_missing: list[str] = field(default_factory=list)
```

---

### T002: Implement SpecContext.is_empty() method ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T001
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-010

**Description:**
Add method to check if any meaningful context was extracted.

**Acceptance Criteria:**
- [ ] Returns True if all key content fields are empty
- [ ] Returns False if any of feature_overview, architecture_overview, or technical_approach has content
- [ ] Used to skip context injection when no context available

**Implementation Notes:**
```python
def is_empty(self) -> bool:
    return not any([
        self.feature_overview,
        self.architecture_overview,
        self.technical_approach,
    ])
```

---

### T003: Implement SpecContext.to_markdown() method ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T001
- **File:** `src/speckit_to_issue/models.py`
- **FR:** FR-014

**Description:**
Add method to format extracted context as markdown for issue body insertion.

**Acceptance Criteria:**
- [ ] Returns formatted markdown string with section headers
- [ ] Uses emoji icons for visual clarity (📋, 🏗️, 🔬, 📊)
- [ ] Only includes non-empty sections
- [ ] Sections separated by horizontal rules

**Implementation Notes:**
```python
def to_markdown(self) -> str:
    sections = []
    if self.feature_overview:
        sections.append(f"## 📋 Feature Specification\n\n{self.feature_overview}")
    if self.architecture_overview or self.target_state:
        arch = "## 🏗️ Architecture\n\n"
        if self.target_state:
            arch += f"### Target State\n\n{self.target_state}\n\n"
        if self.architecture_overview:
            arch += self.architecture_overview
        sections.append(arch)
    # ... more sections
    return "\n\n---\n\n".join(sections)
```

---

## Phase 2: Spec Reader Module

### T004: Create spec_reader.py module skeleton ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** None
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-001

**Description:**
Create the new spec_reader.py module with imports and docstring.

**Acceptance Criteria:**
- [ ] File created at `src/speckit_to_issue/spec_reader.py`
- [ ] Module docstring describing purpose
- [ ] Imports: re, pathlib.Path, typing.Optional
- [ ] Import SpecContext from models

---

### T005: Implement discover_spec_files() function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T004
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-001

**Description:**
Create function to discover available spec files in the spec folder.

**Acceptance Criteria:**
- [ ] Takes tasks_file Path as input
- [ ] Returns dict mapping filenames to Optional[Path]
- [ ] Checks for: spec.md, plan.md, research.md, data-model.md
- [ ] Returns None for missing files, Path for existing files

**Implementation Notes:**
```python
SPEC_FILES = ["spec.md", "plan.md", "research.md", "data-model.md"]

def discover_spec_files(tasks_file: Path) -> dict[str, Optional[Path]]:
    folder = tasks_file.parent
    return {
        name: folder / name if (folder / name).exists() else None
        for name in SPEC_FILES
    }
```

---

### T006: Implement extract_section() regex function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T004
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-002, FR-005

**Description:**
Create core function to extract content under a markdown heading.

**Acceptance Criteria:**
- [ ] Takes content string and section name as input
- [ ] Uses regex to find heading and extract content until next heading
- [ ] Handles numbered headings (## 1. Feature Overview)
- [ ] Handles plain headings (## Feature Overview)
- [ ] Returns empty string if section not found
- [ ] Case-insensitive matching

**Implementation Notes:**
```python
def extract_section(content: str, section_name: str) -> str:
    pattern = re.compile(
        rf"^## \d*\.?\s*{re.escape(section_name)}.*?$\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""
```

---

### T007: Implement extract_from_spec() function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T006
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-002, FR-003, FR-004

**Description:**
Extract relevant sections from spec.md file.

**Acceptance Criteria:**
- [ ] Extracts Feature Overview section
- [ ] Extracts Success Criteria (from within Feature Overview or separate)
- [ ] Extracts User Stories summary (optional)
- [ ] Extracts Functional Requirements table (optional)
- [ ] Returns dict with extracted sections
- [ ] Handles missing sections gracefully

---

### T008: Implement extract_from_plan() function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T006
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-005, FR-006, FR-007

**Description:**
Extract relevant sections from plan.md file.

**Acceptance Criteria:**
- [ ] Extracts Architecture Overview section
- [ ] Extracts Target State section/diagram
- [ ] Extracts Technical Approach section
- [ ] Returns dict with extracted sections
- [ ] Handles missing sections gracefully

---

### T009: Implement extract_from_research() function ✅
- **Status:** ✅ Complete
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T006
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-008

**Description:**
Extract key decisions from research.md file.

**Acceptance Criteria:**
- [ ] Extracts Summary of Decisions section (if present)
- [ ] Extracts Key Decisions section (if present)
- [ ] Returns dict with extracted sections
- [ ] Handles missing file/sections gracefully

---

### T010: Implement truncate_content() function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T004
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-015

**Description:**
Create function to truncate content to maximum lines.

**Acceptance Criteria:**
- [ ] Takes content string and max_lines as input
- [ ] Returns content unchanged if under limit
- [ ] Truncates and adds indicator if over limit
- [ ] Returns tuple of (content, was_truncated)

**Implementation Notes:**
```python
def truncate_content(content: str, max_lines: int = 30) -> tuple[str, bool]:
    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content, False
    truncated = lines[:max_lines]
    truncated.append("")
    truncated.append(f"*...({len(lines) - max_lines} more lines)*")
    return "\n".join(truncated), True
```

---

### T011: Implement read_spec_context() main function ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T005, T007, T008, T009, T010
- **File:** `src/speckit_to_issue/spec_reader.py`
- **FR:** FR-001, FR-010

**Description:**
Create main entry point function that orchestrates spec reading.

**Acceptance Criteria:**
- [ ] Takes tasks_file Path as input
- [ ] Discovers available spec files
- [ ] Reads and extracts from each file
- [ ] Applies truncation to each section
- [ ] Returns populated SpecContext object
- [ ] Logs warnings for missing files
- [ ] Never raises exceptions (graceful degradation)

**Implementation Notes:**
```python
def read_spec_context(tasks_file: Path) -> SpecContext:
    context = SpecContext()
    context.spec_folder = str(tasks_file.parent)
    
    files = discover_spec_files(tasks_file)
    context.files_found = [k for k, v in files.items() if v]
    context.files_missing = [k for k, v in files.items() if not v]
    
    # Extract from each file with error handling
    if files.get("spec.md"):
        try:
            sections = extract_from_spec(files["spec.md"])
            context.feature_overview = truncate_content(sections.get("overview", ""), 30)[0]
            # ... more
        except Exception as e:
            context.extraction_warnings.append(f"spec.md: {e}")
    
    return context
```

---

## Phase 3: Mapper Integration

### T012: Update build_issue_body() signature ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T001
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-011

**Description:**
Add spec_context parameter to build_issue_body function.

**Acceptance Criteria:**
- [ ] Add `spec_context: Optional[SpecContext] = None` parameter
- [ ] Update function docstring
- [ ] Import SpecContext from models
- [ ] Existing behavior unchanged when spec_context is None

---

### T013: Create COPILOT_TEMPLATE_WITH_CONTEXT constant ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T003
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-014

**Description:**
Create new template string that includes placeholder for spec context.

**Acceptance Criteria:**
- [ ] Template includes {spec_context} placeholder
- [ ] Context placed after Acceptance Criteria, before Task Context
- [ ] Separated by horizontal rules
- [ ] Instructions section updated to reference spec context

**Implementation Notes:**
```python
COPILOT_TEMPLATE_WITH_CONTEXT = """## Objective

{title}

{file_section}

## Acceptance Criteria

{acceptance_criteria}

---

{spec_context}

---

## Task Context
...
```

---

### T014: Implement context injection in build_issue_body() ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T012, T013
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-011, FR-014

**Description:**
Add logic to inject spec context into issue body when available.

**Acceptance Criteria:**
- [ ] If spec_context provided and not empty, use context template
- [ ] Call spec_context.to_markdown() to get formatted content
- [ ] If spec_context is None or empty, use existing template
- [ ] Standard (non-Copilot) mode ignores spec_context

---

### T015: Update task_to_issue() signature ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T012
- **File:** `src/speckit_to_issue/mapper.py`
- **FR:** FR-011

**Description:**
Add spec_context parameter to task_to_issue function.

**Acceptance Criteria:**
- [ ] Add `spec_context: Optional[SpecContext] = None` parameter
- [ ] Pass spec_context to build_issue_body()
- [ ] Update function docstring

---

## Phase 4: CLI Integration

### T016: Add --no-context CLI flag ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** None
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-012

**Description:**
Add flag to disable spec context inclusion.

**Acceptance Criteria:**
- [ ] Add `--no-context` option to create command
- [ ] Default value is False
- [ ] Help text: "Disable spec context inclusion"
- [ ] Works independently of --assign-copilot

---

### T017: Add --include-context CLI flag ✅
- **Status:** ✅ Complete (via default behavior)
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T016
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-013

**Description:**
Add flag to enable context for non-Copilot issues.

**Acceptance Criteria:**
- [ ] Add `--include-context` option to create command
- [ ] Default value is False
- [ ] Help text: "Include spec context in issues"
- [ ] Allows context in standard (non-Copilot) mode

---

### T018: Integrate spec reading in CLI create command ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T011, T015, T016, T017
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-011

**Description:**
Add logic to read spec context and pass to mapper.

**Acceptance Criteria:**
- [ ] Import read_spec_context from spec_reader
- [ ] Determine if context should be included based on flags
- [ ] Read spec context once before task loop
- [ ] Display warning if context is empty
- [ ] Pass spec_context to task_to_issue()

**Implementation Notes:**
```python
# Determine if context should be included
include_context = (assign_copilot or include_context_flag) and not no_context

# Read spec context if needed
spec_context = None
if include_context:
    spec_context = read_spec_context(tasks_file)
    if spec_context.is_empty():
        console.print("[yellow]Warning: No spec context found[/yellow]")

# In task loop
issue = task_to_issue(task, copilot_mode=assign_copilot, spec_context=spec_context)
```

---

### T019: Add flag validation ✅
- **Status:** ✅ Complete
- **Priority:** Should
- **Estimate:** 5 min
- **Dependencies:** T016, T017
- **File:** `src/speckit_to_issue/cli.py`
- **FR:** FR-012, FR-013

**Description:**
Add validation for conflicting flag combinations.

**Acceptance Criteria:**
- [ ] Error if both --include-context and --no-context are provided
- [ ] Clear error message explaining conflict
- [ ] Exit with error code

---

## Phase 5: Testing & Polish

### T020: Create test fixtures for spec files ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** None
- **File:** `tests/fixtures/sample-spec/`

**Description:**
Create sample spec files for testing.

**Acceptance Criteria:**
- [ ] Create `tests/fixtures/sample-spec/` directory
- [ ] Create spec.md with Feature Overview, User Stories, Requirements
- [ ] Create plan.md with Architecture, Target State, Technical Approach
- [ ] Create research.md with Key Decisions
- [ ] Create tasks.md with sample tasks
- [ ] Files contain realistic content for testing

---

### T021: Write unit tests for spec_reader module ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T011, T020
- **File:** `tests/unit/test_spec_reader.py`
- **NFR:** NFR-005

**Description:**
Create comprehensive unit tests for spec_reader.py.

**Acceptance Criteria:**
- [ ] Test discover_spec_files with all files present
- [ ] Test discover_spec_files with partial files
- [ ] Test discover_spec_files with no files
- [ ] Test extract_section with found section
- [ ] Test extract_section with numbered heading
- [ ] Test extract_section with not found
- [ ] Test truncate_content under limit
- [ ] Test truncate_content over limit
- [ ] Test read_spec_context full extraction
- [ ] Test read_spec_context with missing files
- [ ] Test read_spec_context graceful error handling

---

### T022: Update mapper tests for context parameter ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T014
- **File:** `tests/unit/test_mapper.py`
- **NFR:** NFR-005

**Description:**
Add tests for spec context injection in mapper.

**Acceptance Criteria:**
- [ ] Test build_issue_body with spec_context=None (existing behavior)
- [ ] Test build_issue_body with empty SpecContext
- [ ] Test build_issue_body with populated SpecContext
- [ ] Test copilot_mode=True includes context sections
- [ ] Test context sections are properly formatted
- [ ] Existing tests continue to pass

---

### T023: Integration and manual testing ✅
- **Status:** ✅ Complete
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T018, T021, T022
- **File:** N/A (Manual Testing)

**Description:**
End-to-end testing of the feature.

**Test Cases:**
- [ ] `speckit-to-issue create tasks.md --assign-copilot --dry-run` includes context
- [ ] `speckit-to-issue create tasks.md --assign-copilot --no-context --dry-run` excludes context
- [ ] `speckit-to-issue create tasks.md --include-context --dry-run` includes context
- [ ] `speckit-to-issue create tasks.md --dry-run` excludes context (standard)
- [ ] Missing spec files show warning but don't fail
- [ ] Context sections render correctly in issue preview
- [ ] Run against real speckit project (002-spec-context-injection itself!)

---

## Task Dependencies

```
T001 ──► T002
    └──► T003 ──────────────────────────────────────────┐
                                                         │
T004 ──┬──► T005 ──────────────────────────────────────┐│
       │                                                ││
       ├──► T006 ──┬──► T007 ──┐                       ││
       │           ├──► T008 ──┼──► T011 ──────────────┼┼──► T018 ──► T023
       │           └──► T009 ──┘         │             ││
       │                                 │             ││
       └──► T010 ────────────────────────┘             ││
                                                        ││
T001 ──────────────────────────────────► T012 ──► T014 ─┼┤
                                              │         ││
T003 ──────────────────────────────────► T013 ┘         ││
                                                        ││
T012 ──────────────────────────────────► T015 ─────────┘│
                                                        │
T016 ──┬──► T017                                        │
       │                                                │
       └──► T019                                        │
                                                        │
T020 ──────────────────────────────────► T021 ──► T023  │
                                                        │
T014 ──────────────────────────────────► T022 ──► T023  │
                                                        │
T018 ◄──────────────────────────────────────────────────┘
```

---

## Notes

- New module `spec_reader.py` is the main addition
- Existing tests must continue to pass (backwards compatibility)
- All extraction should use graceful degradation (never crash)
- Context is only included with `--assign-copilot` by default
- Test the feature on itself (use 002-spec-context-injection specs!)
