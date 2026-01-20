# Feature Specification: Spec Context Injection

> **Spec ID:** 002-spec-context-injection  
> **Created:** 2026-01-20  
> **Status:** Draft  
> **Parent Constitution:** [constitution.md](../constitution.md)

---

## 1. Feature Overview

### 1.1 Description
Enhance speckit-to-issue to automatically include relevant specification context in generated GitHub issues. When creating issues (especially for AI coding agents), the tool will read companion spec files (spec.md, research.md, plan.md, data-model.md) and inject key sections into the issue body. This provides coding agents with the architectural context and business requirements they need to implement tasks correctly.

### 1.2 Problem Statement
Currently, issues created from tasks.md contain only task-level information:
- Task description and acceptance criteria
- Basic metadata (priority, estimate, dependencies)
- File path hints

This is insufficient for AI coding agents because they lack:
- **Why** the feature exists (business value, user stories)
- **How** it fits into the architecture (target state, design decisions)
- **What** patterns to follow (technical research, recommended approaches)
- **Which** data structures to use (models, schemas)

### 1.3 Business Value
- **Better AI agent output** - Agents produce more accurate implementations with full context
- **Fewer iterations** - Less back-and-forth between human review and agent fixes
- **Consistent implementations** - Agents follow documented architectural decisions
- **Self-documenting workflow** - Issues contain all relevant context in one place

### 1.4 Success Criteria
- Issues include summarized context from spec files when `--assign-copilot` is used
- Context extraction is smart (key sections, not full files)
- Issue body remains readable and well-structured
- Tool gracefully handles missing spec files
- Existing functionality continues to work unchanged

---

## 2. User Stories

### US1: Automatic Context Inclusion
**As a** developer using speckit-to-issue with `--assign-copilot`  
**I want** the generated issues to automatically include spec context  
**So that** the coding agent has all the information it needs to implement correctly  

**Acceptance Criteria:**
- [ ] When `--assign-copilot` flag is used, spec context is included in issue body
- [ ] Context includes key sections from spec.md, research.md, plan.md
- [ ] Missing spec files are handled gracefully (skipped with no error)
- [ ] Issue body is well-formatted with clear section headers

### US2: Feature Overview Context
**As a** coding agent receiving an issue  
**I want** to understand the feature's purpose and requirements  
**So that** I can implement the task in alignment with business goals  

**Acceptance Criteria:**
- [ ] Issue includes Feature Overview section from spec.md
- [ ] Issue includes relevant User Stories (at least the related one)
- [ ] Issue includes applicable Functional Requirements
- [ ] Success criteria are visible

### US3: Architecture Context
**As a** coding agent receiving an issue  
**I want** to understand the target architecture and design decisions  
**So that** my implementation fits the planned structure  

**Acceptance Criteria:**
- [ ] Issue includes Architecture Overview from plan.md
- [ ] Issue includes Target State diagram/description
- [ ] Technical approach section is included
- [ ] Key decisions from research.md are visible

### US4: Data Model Context
**As a** coding agent working on a data-related task  
**I want** to see relevant data structures and models  
**So that** I use the correct schemas in my implementation  

**Acceptance Criteria:**
- [ ] Issue includes relevant data models from data-model.md (if present)
- [ ] Models are formatted as code blocks
- [ ] Only relevant models are included (not the entire file)

### US5: Optional Context Flag
**As a** developer  
**I want** to control whether context is included  
**So that** I can create lighter issues when full context isn't needed  

**Acceptance Criteria:**
- [ ] `--assign-copilot` enables context inclusion by default
- [ ] `--no-context` flag disables context inclusion
- [ ] `--include-context` flag enables context for non-Copilot issues
- [ ] Standard (non-Copilot) issues don't include context by default

---

## 3. Functional Requirements

| ID | Requirement | Priority | User Story |
|----|-------------|----------|------------|
| FR-001 | Tool shall detect spec folder from tasks.md path | Must | US1 |
| FR-002 | Tool shall read spec.md and extract Feature Overview section | Must | US2 |
| FR-003 | Tool shall read spec.md and extract relevant User Stories | Should | US2 |
| FR-004 | Tool shall read spec.md and extract Functional Requirements table | Should | US2 |
| FR-005 | Tool shall read plan.md and extract Architecture Overview | Must | US3 |
| FR-006 | Tool shall read plan.md and extract Target State section | Should | US3 |
| FR-007 | Tool shall read plan.md and extract Technical Approach | Should | US3 |
| FR-008 | Tool shall read research.md and extract key decisions | Should | US3 |
| FR-009 | Tool shall read data-model.md and extract relevant models | Could | US4 |
| FR-010 | Tool shall gracefully handle missing spec files | Must | US1 |
| FR-011 | Tool shall include context by default with `--assign-copilot` | Must | US5 |
| FR-012 | Tool shall support `--no-context` flag to disable context | Should | US5 |
| FR-013 | Tool shall support `--include-context` flag for non-Copilot issues | Could | US5 |
| FR-014 | Tool shall format context sections with clear markdown headers | Must | US1 |
| FR-015 | Tool shall limit context size to prevent excessively large issues | Should | US1 |

---

## 4. Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-001 | Context extraction shall complete in under 500ms | Performance |
| NFR-002 | Tool shall handle spec files up to 10,000 lines | Performance |
| NFR-003 | Context sections shall use valid GitHub-flavored markdown | Compatibility |
| NFR-004 | Tool shall maintain backwards compatibility with existing CLI | Compatibility |
| NFR-005 | New code shall maintain 80%+ test coverage | Quality |

---

## 5. Spec Folder Structure

The tool expects this standard speckit folder structure:

```
specs/{spec-name}/
├── spec.md          # Feature specification (user stories, requirements)
├── research.md      # Technical research (patterns, decisions)
├── plan.md          # Implementation plan (architecture, phases)
├── data-model.md    # Data structures (optional)
├── quickstart.md    # Setup guide (not included in issues)
└── tasks.md         # Task breakdown (source for issues)
```

### File Priority

| File | Priority | Sections to Extract |
|------|----------|---------------------|
| `spec.md` | High | Feature Overview, User Stories, Functional Requirements |
| `plan.md` | High | Architecture Overview, Target State, Technical Approach |
| `research.md` | Medium | Key Decisions, Recommended Patterns |
| `data-model.md` | Low | Core Models (code blocks only) |
| `quickstart.md` | Skip | Not relevant for implementation |

---

## 6. Context Section Format

### 6.1 Issue Body Structure (with context)

```markdown
## Objective

{task title}

## Files to Modify

- `{file_path}`

## Acceptance Criteria

{checkboxes}

---

## 📋 Feature Specification

### Overview
{spec.md: Feature Overview description}

### Success Criteria
{spec.md: Success Criteria list}

---

## 🏗️ Architecture

### Target State
{plan.md: Target State section or diagram}

### Technical Approach
{plan.md: Key technical decisions}

---

## 🔬 Technical Context

{research.md: Key patterns and recommendations}

---

## 📊 Data Models

```python
{data-model.md: Relevant code blocks}
```

---

## Task Context

| Field | Value |
|-------|-------|
| Spec | {spec_name} |
| Phase | {phase} |
| Priority | {priority} |
| Estimate | {estimate} |
| Dependencies | {dependencies} |

## Instructions for Copilot

Implement this task following the acceptance criteria above.
- Follow the architecture and patterns described in the Feature Specification
- Use the data models as defined
- Follow existing code patterns in the repository
- Add appropriate tests if applicable
- Create a pull request when complete

---
*Generated by speckit-to-issue*
```

### 6.2 Section Length Guidelines

| Section | Max Lines | Truncation Strategy |
|---------|-----------|---------------------|
| Feature Overview | 20 | First paragraph only |
| Success Criteria | 10 | Full list |
| Target State | 30 | Include diagram/description |
| Technical Approach | 20 | Key points only |
| Technical Context | 30 | Decision summary |
| Data Models | 50 | Relevant models only |

**Total Context Budget:** ~150-200 lines maximum

---

## 7. CLI Changes

### 7.1 New Flags

```bash
# Context is auto-included with --assign-copilot (default behavior)
speckit-to-issue create tasks.md --assign-copilot

# Explicitly disable context
speckit-to-issue create tasks.md --assign-copilot --no-context

# Enable context for non-Copilot issues
speckit-to-issue create tasks.md --include-context
```

### 7.2 Flag Interactions

| Flags | Context Included? |
|-------|-------------------|
| (none) | No |
| `--assign-copilot` | Yes |
| `--assign-copilot --no-context` | No |
| `--include-context` | Yes |
| `--include-context --no-context` | Error (conflicting flags) |

---

## 8. Edge Cases

| Scenario | Behavior |
|----------|----------|
| No spec folder found | Warning message, continue without context |
| spec.md missing | Skip spec sections, include others |
| All spec files missing | Warning, create issue without context |
| Very large spec files | Truncate to max lines per section |
| Malformed markdown | Best-effort parsing, skip unparseable sections |
| Binary files in spec folder | Ignore non-.md files |

---

## 9. Out of Scope

- Parsing constitution.md (project-wide, not feature-specific)
- Interactive context selection
- Custom section extraction rules
- Multi-spec context (combining multiple specs)
- Context caching between runs

---

## 10. Dependencies

### Internal
- Existing parser.py for markdown parsing patterns
- Existing mapper.py for template formatting

### External
- No new external dependencies required
- Uses Python standard library for file I/O

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Copilot | Initial specification |
