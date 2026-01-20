# Implementation Plan: Spec Context Injection

> **Spec:** 002-spec-context-injection  
> **Date:** 2026-01-20  
> **Priority:** High  
> **Estimated Effort:** 4-5 hours

---

## 1. Executive Summary

This plan outlines the implementation of automatic spec context injection for speckit-to-issue. When creating GitHub issues with `--assign-copilot`, the tool will read companion spec files (spec.md, plan.md, research.md) and inject summarized context into issue bodies, giving AI coding agents the architectural and business context needed for accurate implementations.

---

## 2. Architecture Overview

### Current State

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   tasks.md     │────►│    parser.py   │────►│    mapper.py   │
│                │     │                │     │                │
│  Parse tasks   │     │  Task objects  │     │  Issue body    │
└────────────────┘     └────────────────┘     └────────────────┘
                                                     │
                                                     ▼
                                              ┌────────────────┐
                                              │   github.py    │
                                              │                │
                                              │  Create issue  │
                                              └────────────────┘
```

### Target State

```
┌────────────────┐     ┌────────────────┐
│   tasks.md     │────►│    parser.py   │
└────────────────┘     └───────┬────────┘
                               │
┌────────────────┐             │
│   spec.md      │             │
│   plan.md      │─────────────┼─────────────────┐
│   research.md  │             │                 │
│   data-model   │             │                 ▼
└────────────────┘             │        ┌────────────────┐
        │                      │        │ spec_reader.py │  ← NEW
        │                      │        │                │
        └──────────────────────┼───────►│  SpecContext   │
                               │        └───────┬────────┘
                               │                │
                               ▼                ▼
                       ┌────────────────────────────────┐
                       │           mapper.py            │
                       │                                │
                       │  build_issue_body(task,        │
                       │    copilot_mode, spec_context) │
                       └───────────────┬────────────────┘
                                       │
                                       ▼
                               ┌────────────────┐
                               │   github.py    │
                               │  Create issue  │
                               └────────────────┘
```

---

## 3. Technical Approach

### 3.1 New Module: spec_reader.py

**Purpose:** Read spec files and extract relevant sections.

**Key Functions:**
- `read_spec_context(tasks_file)` - Main entry point
- `discover_spec_files(tasks_file)` - Find available spec files
- `extract_section(content, heading)` - Extract markdown section
- `truncate_content(content, max_lines)` - Limit section length

**Pattern:** Follow existing parser.py conventions (regex-based, dataclass output).

### 3.2 Model Extension: SpecContext

**Location:** `models.py`

```python
@dataclass
class SpecContext:
    feature_overview: str = ""
    success_criteria: str = ""
    architecture_overview: str = ""
    target_state: str = ""
    technical_approach: str = ""
    key_decisions: str = ""
    data_models: str = ""
    
    def is_empty(self) -> bool: ...
    def to_markdown(self) -> str: ...
```

### 3.3 Mapper Updates

**Changes to mapper.py:**
- Update `build_issue_body()` signature to accept `spec_context`
- Update `task_to_issue()` signature to accept `spec_context`
- Create new template `COPILOT_TEMPLATE_WITH_CONTEXT`
- Insert context sections before "Instructions for Copilot"

### 3.4 CLI Updates

**Changes to cli.py:**
- Add `--no-context` flag
- Add `--include-context` flag (for non-Copilot)
- Read spec context once before task loop
- Pass context to mapper

---

## 4. Implementation Phases

### Phase 1: Core Models (30 min)

**Tasks:**
1. Add SpecContext dataclass to models.py
2. Add is_empty() method
3. Add to_markdown() method for formatting

**Deliverable:** SpecContext model ready for use

### Phase 2: Spec Reader Module (1.5 hours)

**Tasks:**
1. Create spec_reader.py
2. Implement discover_spec_files()
3. Implement extract_section() with regex
4. Implement section extractors for each file type
5. Implement truncate_content()
6. Implement read_spec_context() main function

**Deliverable:** Working spec reader with tests

### Phase 3: Mapper Integration (1 hour)

**Tasks:**
1. Update build_issue_body() signature
2. Create COPILOT_TEMPLATE_WITH_CONTEXT
3. Implement context injection logic
4. Update task_to_issue() signature
5. Update unit tests

**Deliverable:** Mapper generates context-enriched bodies

### Phase 4: CLI Integration (45 min)

**Tasks:**
1. Add --no-context flag
2. Add --include-context flag
3. Add context reading logic
4. Add validation for conflicting flags
5. Update help text

**Deliverable:** CLI supports context flags

### Phase 5: Testing & Polish (1 hour)

**Tasks:**
1. Create test fixtures (sample spec files)
2. Write unit tests for spec_reader
3. Write integration tests
4. Update existing mapper tests
5. Test edge cases (missing files, malformed content)
6. Manual end-to-end testing

**Deliverable:** Full test coverage, production-ready

---

## 5. Detailed Task Breakdown

| ID | Task | Phase | Est. | Dependencies |
|----|------|-------|------|--------------|
| T001 | Add SpecContext to models.py | 1 | 15 min | None |
| T002 | Implement SpecContext.is_empty() | 1 | 5 min | T001 |
| T003 | Implement SpecContext.to_markdown() | 1 | 10 min | T001 |
| T004 | Create spec_reader.py module | 2 | 5 min | None |
| T005 | Implement discover_spec_files() | 2 | 15 min | T004 |
| T006 | Implement extract_section() regex | 2 | 20 min | T004 |
| T007 | Implement extract_from_spec() | 2 | 15 min | T006 |
| T008 | Implement extract_from_plan() | 2 | 15 min | T006 |
| T009 | Implement extract_from_research() | 2 | 10 min | T006 |
| T010 | Implement truncate_content() | 2 | 10 min | T004 |
| T011 | Implement read_spec_context() | 2 | 15 min | T005-T010 |
| T012 | Update build_issue_body() signature | 3 | 10 min | T001 |
| T013 | Create context template | 3 | 15 min | T003 |
| T014 | Implement context injection | 3 | 20 min | T012, T013 |
| T015 | Update task_to_issue() signature | 3 | 10 min | T012 |
| T016 | Add --no-context CLI flag | 4 | 15 min | None |
| T017 | Add --include-context CLI flag | 4 | 10 min | T016 |
| T018 | Integrate spec reading in CLI | 4 | 15 min | T011, T015 |
| T019 | Add flag validation | 4 | 5 min | T016, T017 |
| T020 | Create test fixtures | 5 | 15 min | None |
| T021 | Write spec_reader unit tests | 5 | 20 min | T011, T020 |
| T022 | Update mapper tests | 5 | 15 min | T014 |
| T023 | Integration testing | 5 | 15 min | All |

---

## 6. File Changes

### 6.1 New Files

| File | Purpose |
|------|---------|
| `src/speckit_to_issue/spec_reader.py` | Spec file reading and extraction |
| `tests/unit/test_spec_reader.py` | Unit tests for spec_reader |
| `tests/fixtures/sample-spec/spec.md` | Test fixture |
| `tests/fixtures/sample-spec/plan.md` | Test fixture |
| `tests/fixtures/sample-spec/research.md` | Test fixture |
| `tests/fixtures/sample-spec/tasks.md` | Test fixture |

### 6.2 Modified Files

| File | Changes |
|------|---------|
| `src/speckit_to_issue/models.py` | Add SpecContext dataclass |
| `src/speckit_to_issue/mapper.py` | Update signatures, add context template |
| `src/speckit_to_issue/cli.py` | Add flags, integrate spec reading |
| `tests/unit/test_mapper.py` | Add tests for context inclusion |

---

## 7. API Changes

### 7.1 New Public Functions

```python
# spec_reader.py
def read_spec_context(tasks_file: Path) -> SpecContext
def discover_spec_files(tasks_file: Path) -> dict[str, Optional[Path]]
```

### 7.2 Modified Function Signatures

```python
# mapper.py
def build_issue_body(
    task: Task,
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None  # NEW
) -> str

def task_to_issue(
    task: Task,
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None  # NEW
) -> Issue
```

### 7.3 New CLI Options

```bash
speckit-to-issue create tasks.md --no-context      # Disable context
speckit-to-issue create tasks.md --include-context # Enable for non-Copilot
```

---

## 8. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Regex doesn't match all heading formats | Medium | Medium | Test with real spec files, add fallback patterns |
| Large spec files slow down processing | Low | Low | Implement truncation, lazy loading |
| Breaking existing tests | Medium | Low | Run full test suite frequently |
| Malformed markdown crashes extraction | High | Medium | Wrap all extraction in try/except |

---

## 9. Testing Strategy

### 9.1 Unit Tests

**test_spec_reader.py:**
- `test_discover_spec_files_all_present`
- `test_discover_spec_files_partial`
- `test_discover_spec_files_none`
- `test_extract_section_found`
- `test_extract_section_not_found`
- `test_extract_section_numbered_heading`
- `test_truncate_content`
- `test_read_spec_context_full`
- `test_read_spec_context_missing_files`

**test_mapper.py updates:**
- `test_build_issue_body_with_context`
- `test_build_issue_body_empty_context`
- `test_copilot_mode_includes_context`

### 9.2 Integration Tests

- Create issues from real spec folder
- Verify context appears in dry-run output
- Test --no-context flag behavior

### 9.3 Edge Cases

- Empty spec files
- Spec files with only headers
- Very large spec files (>1000 lines)
- Non-UTF8 encoded files
- Missing spec folder

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage (spec_reader.py) | >90% |
| Existing tests pass | 100% |
| Context extraction time | <500ms |
| Issue body size with context | <300 lines |

---

## 11. Dependencies

### Internal
- Existing parser.py patterns
- Existing models.py structure
- Existing mapper.py templates

### External
- No new dependencies required
- Uses Python re, pathlib (stdlib)

---

## 12. Backwards Compatibility

| Aspect | Compatibility |
|--------|---------------|
| Existing CLI commands | ✅ Unchanged |
| Existing issue format | ✅ Unchanged (without flags) |
| Existing tests | ✅ Will pass |
| API signatures | ⚠️ New optional parameters |

---

## 13. Rollout Plan

1. **Development:** Implement all phases
2. **Testing:** Run full test suite
3. **Documentation:** Update README with new flags
4. **Release:** Bump version, update changelog
5. **Verify:** Test with real speckit projects

---

## 14. Summary

This implementation:
- ✅ Adds spec context injection with minimal code changes
- ✅ Uses familiar patterns from existing codebase
- ✅ Maintains backwards compatibility
- ✅ Gracefully handles missing/malformed files
- ✅ Can be completed in ~5 hours
- ✅ Significantly improves AI agent context
