# Architecture: Feature-Level Issue Creation

## 1. Current State

```
┌─────────────────────────────────────────────────────────────┐
│  speckit-to-issue create                                    │
├─────────────────────────────────────────────────────────────┤
│  Input: specs/003-feature/tasks.md                          │
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ Task 1  │    │ Task 2  │    │ Task N  │                 │
│  └────┬────┘    └────┬────┘    └────┬────┘                 │
│       │              │              │                       │
│       ▼              ▼              ▼                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ Issue 1 │    │ Issue 2 │    │ Issue N │  (N issues)     │
│  └─────────┘    └─────────┘    └─────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## 2. Target State

```
┌─────────────────────────────────────────────────────────────┐
│  speckit-to-issue create                                    │
├─────────────────────────────────────────────────────────────┤
│  Input: specs/003-feature/                                  │
│         ├── spec.md                                         │
│         ├── architecture.md                                 │
│         └── tasks.md                                        │
│                                                             │
│  ┌──────────────────────────────────────────┐               │
│  │           SpecContext                     │               │
│  │  ┌─────────┬─────────────┬─────────────┐ │               │
│  │  │ spec.md │architecture │  tasks.md   │ │               │
│  │  └─────────┴─────────────┴─────────────┘ │               │
│  └────────────────────┬─────────────────────┘               │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────┐               │
│  │         Single Feature Issue              │               │
│  │  ┌────────────────────────────────────┐  │               │
│  │  │ ## Feature: Help & FAQ Page        │  │               │
│  │  │ ### Overview                       │  │               │
│  │  │ ### Architecture                   │  │               │
│  │  │ ### Phase 1: HTML Structure        │  │               │
│  │  │ - [ ] T001: Add help button        │  │               │
│  │  │ - [ ] T002: Create help view       │  │               │
│  │  │ ### Phase 2: CSS Styling           │  │               │
│  │  │ - [ ] T007: Style help button      │  │               │
│  │  │ ### Acceptance Criteria            │  │               │
│  │  │ ### Files to Modify                │  │               │
│  │  └────────────────────────────────────┘  │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## 3. Component Changes

### 3.1 New: FeatureIssueBuilder

```python
class FeatureIssueBuilder:
    """Builds a single comprehensive issue from a full spec."""
    
    def build(self, spec_context: SpecContext, tasks: list[Task]) -> Issue:
        """Build feature-level issue from spec context and tasks."""
        pass
    
    def _build_overview_section(self, spec_context: SpecContext) -> str:
        """Extract and format overview from spec.md."""
        pass
    
    def _build_architecture_section(self, spec_context: SpecContext) -> str:
        """Extract key architecture decisions."""
        pass
    
    def _build_tasks_by_phase(self, tasks: list[Task]) -> str:
        """Group tasks by phase with checkboxes."""
        pass
    
    def _build_acceptance_criteria(self, tasks: list[Task]) -> str:
        """Consolidate all acceptance criteria."""
        pass
    
    def _build_files_section(self, tasks: list[Task]) -> str:
        """List all files to modify."""
        pass
```

### 3.2 Modified: CLI (cli.py)

```python
@app.command()
def create(
    tasks_file: Path,
    granular: bool = Option(False, "--granular", help="Create individual task issues"),
    assign_copilot: bool = Option(False, "--assign-copilot", help="Assign to Copilot"),
    ...
):
    """Create GitHub issues from a spec.
    
    By default, creates a single feature issue with all tasks.
    Use --granular to create individual issues per task.
    """
    if granular:
        # Existing behavior: one issue per task
        ...
    else:
        # New behavior: one issue per feature
        ...
```

### 3.3 Modified: Mapper (mapper.py)

Add new function alongside existing `task_to_issue`:

```python
def spec_to_feature_issue(
    spec_context: SpecContext,
    tasks: list[Task],
    copilot_mode: bool = False,
) -> Issue:
    """Convert entire spec to a single feature issue."""
    pass
```

## 4. Issue Body Template

```markdown
## Feature: {spec_name}

### Overview
{spec.md description section}

### Architecture
{architecture.md key decisions - condensed}

---

## Implementation Tasks

### Phase 1: {phase_name}
- [ ] **T001**: {title} ({estimate})
  - {acceptance_criterion_1}
  - {acceptance_criterion_2}
  
- [ ] **T002**: {title} ({estimate})
  - {acceptance_criterion_1}

### Phase 2: {phase_name}
- [ ] **T007**: {title} ({estimate})
  - {acceptance_criterion_1}

---

## Files to Modify
- `static/index.html`
- `static/styles.css`
- `static/app.js`

---

## Instructions for Copilot

Implement this feature following the tasks in order by phase.
- Complete all tasks in Phase 1 before moving to Phase 2
- Follow the architecture patterns described above
- Check off each task as you complete it
- Add appropriate tests if applicable
- Create a pull request when all tasks are complete

---
*Generated by [speckit-to-issue](https://github.com/speckit/speckit-to-issue)*
```

## 5. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default behavior | Feature-level | Better for Copilot agent, less clutter |
| Backward compat | `--granular` flag | Preserve existing workflow option |
| Task grouping | By phase | Natural implementation order |
| AC placement | Under each task | Keeps context close to task |
| Architecture content | Condensed | Full content too long, key decisions only |
