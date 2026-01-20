# Project Constitution: Speckit-to-Issue

> **Project:** speckit-to-issue  
> **Created:** 2026-01-20  
> **Status:** Active

---

## 1. Project Vision

A CLI tool that bridges speckit specifications with GitHub Issues, enabling seamless conversion of structured spec files (tasks.md, spec.md) into trackable GitHub issues. This tool completes the speckit workflow by connecting planning artifacts to project management.

---

## 2. Core Principles

### 2.1 Seamless Integration
- Works naturally with existing speckit file structures
- Leverages GitHub CLI (`gh`) for authentication and issue creation
- No additional authentication setup required beyond `gh auth`

### 2.2 Spec Fidelity
- Preserves all task metadata (priority, estimates, dependencies, acceptance criteria)
- Maintains traceability between specs and issues
- Links issues back to source spec files

### 2.3 Developer Experience
- Simple, intuitive CLI interface
- Sensible defaults with flexible overrides
- Clear feedback and dry-run capabilities

### 2.4 Idempotency
- Detects existing issues to prevent duplicates
- Supports updating issues when specs change
- Provides sync status reporting

---

## 3. Technical Foundation

### 3.1 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Matches speckit ecosystem, excellent CLI libraries |
| CLI Framework | Click or Typer | Modern, type-safe CLI building |
| GitHub Integration | GitHub CLI (gh) | Already authenticated, standard tooling |
| Parsing | Regex + Markdown parsing | Handle speckit task format |
| Package Manager | uv / pip | Modern Python packaging |

### 3.2 Architecture Pattern

```
┌─────────────────────────────────────────┐
│              CLI Interface              │
│         (speckit-to-issue)              │
├─────────────────────────────────────────┤
│            Command Layer                │
│   sync | create | status | link         │
├─────────────────────────────────────────┤
│            Core Services                │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Parser  │  │  GitHub  │  │ Mapper │ │
│  │ (specs)  │  │   API    │  │        │ │
│  └──────────┘  └──────────┘  └────────┘ │
├─────────────────────────────────────────┤
│           GitHub CLI (gh)               │
└─────────────────────────────────────────┘
```

### 3.3 Distribution
- Installable via `pip install speckit-to-issue`
- Runnable via `uvx speckit-to-issue`
- Single command entry point

---

## 4. Design Decisions

### 4.1 GitHub CLI over REST API
**Decision:** Use `gh` CLI subprocess calls instead of direct GitHub API  
**Rationale:** 
- Leverages existing user authentication
- No token management required
- Consistent with GitHub's recommended tooling
- Simpler implementation

### 4.2 Task-Centric Focus
**Decision:** Primary focus on tasks.md, with spec.md as context  
**Rationale:**
- Tasks are the actionable units that map to issues
- Specs provide context but aren't directly issueable
- Clear 1:1 mapping: Task → Issue

### 4.3 Label Strategy
**Decision:** Auto-generate labels from task metadata  
**Rationale:**
- Priority → `priority:high`, `priority:medium`, `priority:low`
- Phase → `phase-1`, `phase-2`, etc.
- Spec → `spec:001-feature-name`
- Type → `task`

### 4.4 Duplicate Detection
**Decision:** Use title prefix `[T001]` for matching  
**Rationale:**
- Task IDs are unique within a spec
- Simple string matching
- Works across renames

---

## 5. Project Structure

```
speckit-to-issue/
├── src/
│   └── speckit_to_issue/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── parser.py           # Spec/task parsing
│       ├── github.py           # GitHub CLI wrapper
│       ├── mapper.py           # Task → Issue mapping
│       └── models.py           # Data models
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── README.md
└── specs/
    └── constitution.md
```

---

## 6. Quality Standards

### 6.1 Code Quality
- Type hints on all public functions
- Docstrings for modules and public APIs
- Ruff for linting and formatting
- mypy for type checking

### 6.2 Testing
- Unit tests for parser and mapper
- Integration tests with mock `gh` responses
- Minimum 80% code coverage

### 6.3 Documentation
- README with quick start guide
- CLI help text for all commands
- Examples for common workflows

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Parse accuracy | 100% of valid tasks.md files |
| Issue creation | < 2 seconds per issue |
| Duplicate detection | 100% accuracy |
| CLI response time | < 500ms for status commands |

---

## 8. Scope Boundaries

### 8.1 In Scope
- Parse speckit tasks.md files
- Create GitHub issues from tasks
- Detect and skip duplicates
- Dry-run mode for preview
- Label management
- Link issues to milestones (optional)
- Sync status reporting

### 8.2 Out of Scope (v1)
- GitHub Projects integration
- Issue updates/sync (future)
- Bidirectional sync (issues → specs)
- Web UI
- Non-GitHub platforms (GitLab, Jira)

---

## 9. Commands (Planned)

```bash
# Create issues from tasks
speckit-to-issue create specs/001-feature/tasks.md

# Preview without creating (dry-run)
speckit-to-issue create specs/001-feature/tasks.md --dry-run

# Check sync status
speckit-to-issue status specs/001-feature/tasks.md

# Create issues for all specs
speckit-to-issue create specs/ --recursive

# Skip completed tasks
speckit-to-issue create specs/001-feature/tasks.md --skip-complete
```

---

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Copilot | Initial constitution |
