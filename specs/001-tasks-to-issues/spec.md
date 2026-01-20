# Feature Specification: Tasks to GitHub Issues

> **Spec ID:** 001-tasks-to-issues  
> **Created:** 2026-01-20  
> **Status:** Draft  
> **Parent Constitution:** [constitution.md](../constitution.md)

---

## 1. Feature Overview

### 1.1 Description
A CLI tool that parses speckit `tasks.md` files and creates corresponding GitHub issues, enabling developers to track implementation progress in GitHub Projects and assign tasks to GitHub Copilot Coding Agent as part of an AI-driven Software Development Lifecycle (AI SDLC).

### 1.2 Business Value
- **Bridges planning and execution** - Connects speckit's structured planning to GitHub's issue tracking
- **Enables AI SDLC** - Tasks can be assigned to Copilot Coding Agent for autonomous implementation
- **Maintains traceability** - Links between specs and issues provide audit trail
- **Reduces manual work** - Automates the tedious process of creating issues from specs

### 1.3 Success Criteria
- Parse any valid speckit tasks.md file with 100% accuracy
- Create GitHub issues in < 2 seconds per task
- Detect and skip duplicate issues
- Support assignment to Copilot Coding Agent
- Provide clear CLI feedback and dry-run capability

---

## 2. User Stories

### US1: Create Issues from Tasks
**As a** developer using speckit  
**I want to** convert my tasks.md file into GitHub issues  
**So that** I can track implementation progress in GitHub Projects  

**Acceptance Criteria:**
- [ ] CLI accepts path to tasks.md file
- [ ] Each task becomes a separate GitHub issue
- [ ] Issue title includes task ID (e.g., `[T001] Task title`)
- [ ] Issue body contains all task metadata
- [ ] Labels are auto-generated from priority and phase
- [ ] Command provides progress feedback
- [ ] Summary shows created/skipped/failed counts

### US2: Preview Before Creating
**As a** developer  
**I want to** preview what issues will be created before actually creating them  
**So that** I can verify the mapping is correct  

**Acceptance Criteria:**
- [ ] `--dry-run` flag shows issues without creating
- [ ] Preview displays title, labels, and body excerpt
- [ ] Clear indication that no issues were created
- [ ] Same output format as actual creation

### US3: Skip Completed Tasks
**As a** developer  
**I want to** skip tasks marked as complete (✅)  
**So that** I only create issues for remaining work  

**Acceptance Criteria:**
- [ ] `--skip-complete` flag excludes completed tasks
- [ ] Completed tasks identified by ✅ in title or all checked criteria
- [ ] Summary shows how many were skipped
- [ ] Default behavior includes all tasks

### US4: Assign to Copilot Coding Agent
**As a** developer practicing AI SDLC  
**I want to** assign created issues to GitHub Copilot Coding Agent  
**So that** the agent can autonomously implement the tasks  

**Acceptance Criteria:**
- [ ] `--assign-copilot` flag triggers Copilot assignment
- [ ] Issues are formatted for Copilot Coding Agent consumption
- [ ] Acceptance criteria formatted as checkboxes
- [ ] Dependencies noted in issue body
- [ ] File paths included when specified in task

### US5: Detect Duplicate Issues
**As a** developer  
**I want to** avoid creating duplicate issues when running the command multiple times  
**So that** I don't clutter my issue tracker  

**Acceptance Criteria:**
- [ ] Tool checks for existing issues with same `[TXXX]` prefix
- [ ] Existing issues are skipped with notification
- [ ] `--force` flag overrides duplicate detection
- [ ] Summary shows duplicate count

### US6: Check Sync Status
**As a** developer  
**I want to** see which tasks have issues and which don't  
**So that** I can understand the sync state  

**Acceptance Criteria:**
- [ ] `status` command shows sync overview
- [ ] Lists tasks with their issue status (created/missing/closed)
- [ ] Shows issue URLs for linked tasks
- [ ] Provides summary statistics

---

## 3. Functional Requirements

| ID | Requirement | Priority | User Story |
|----|-------------|----------|------------|
| FR-01 | CLI shall accept path to tasks.md file as argument | Must | US1 |
| FR-02 | CLI shall parse speckit tasks.md format including task ID, title, priority, estimate, dependencies, file, FR/NFR refs, and acceptance criteria | Must | US1 |
| FR-03 | CLI shall create GitHub issue for each parsed task | Must | US1 |
| FR-04 | Issue title shall follow format `[TXXX] Task Title` | Must | US1 |
| FR-05 | Issue body shall include spec name, phase, priority, estimate, dependencies, file path, requirements refs, and acceptance criteria as checkboxes | Must | US1 |
| FR-06 | CLI shall auto-generate labels: `priority:high/medium/low`, `phase-N`, `spec:spec-name`, `task` | Must | US1 |
| FR-07 | CLI shall create missing labels automatically | Should | US1 |
| FR-08 | CLI shall display progress during issue creation | Must | US1 |
| FR-09 | CLI shall provide `--dry-run` flag to preview without creating | Must | US2 |
| FR-10 | CLI shall provide `--skip-complete` flag to exclude completed tasks | Must | US3 |
| FR-11 | CLI shall detect completed tasks by ✅ marker or all-checked criteria | Must | US3 |
| FR-12 | CLI shall provide `--assign-copilot` flag for Coding Agent assignment | Must | US4 |
| FR-13 | When `--assign-copilot`, issue body shall be formatted for agent consumption | Must | US4 |
| FR-14 | CLI shall check for existing issues with matching `[TXXX]` in title | Must | US5 |
| FR-15 | CLI shall skip duplicate issues and report them | Must | US5 |
| FR-16 | CLI shall provide `--force` flag to create duplicates anyway | Should | US5 |
| FR-17 | CLI shall provide `status` command to show sync state | Should | US6 |
| FR-18 | CLI shall support `--repo` flag to specify target repository | Must | US1 |
| FR-19 | CLI shall use current repository if `--repo` not specified | Must | US1 |
| FR-20 | CLI shall provide `--milestone` flag to assign issues to milestone | Should | US1 |

---

## 4. Non-Functional Requirements

| ID | Requirement | Category | Target |
|----|-------------|----------|--------|
| NFR-01 | Issue creation shall complete in < 2 seconds per issue | Performance | < 2s |
| NFR-02 | CLI shall respond to `--help` in < 500ms | Performance | < 500ms |
| NFR-03 | CLI shall work on Windows, macOS, and Linux | Compatibility | 100% |
| NFR-04 | CLI shall require only GitHub CLI (`gh`) as external dependency | Dependency | gh only |
| NFR-05 | CLI shall provide clear error messages for common failures | Usability | Clear errors |
| NFR-06 | CLI shall be installable via pip and uvx | Distribution | pip/uvx |
| NFR-07 | Code shall have minimum 80% test coverage | Quality | 80% |
| NFR-08 | CLI shall handle UTF-8 encoded files correctly | Compatibility | UTF-8 |

---

## 5. Technical Approach

### 5.1 Technology Stack
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Modern features, speckit ecosystem |
| CLI Framework | Typer | Type-safe, auto-help, modern |
| GitHub Integration | subprocess + gh CLI | No token management |
| Parsing | Regex | Speckit format is consistent |
| Testing | pytest | Standard Python testing |
| Packaging | pyproject.toml + hatch | Modern Python packaging |

### 5.2 Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    CLI (Typer)                          │
│   create | status | version                             │
├─────────────────────────────────────────────────────────┤
│                   Core Services                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Parser    │  │   GitHub    │  │     Mapper      │  │
│  │ (tasks.md)  │  │  (gh CLI)   │  │ (Task→Issue)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                     Models                              │
│         Task | Issue | SyncStatus | Config              │
└─────────────────────────────────────────────────────────┘
```

### 5.3 GitHub CLI Integration
```python
# Issue creation via gh CLI
subprocess.run([
    "gh", "issue", "create",
    "--title", "[T001] Task title",
    "--body", body_content,
    "--label", "priority:high",
    "--label", "phase-1",
    "--repo", "owner/repo"
], capture_output=True)
```

### 5.4 Copilot Coding Agent Format
When `--assign-copilot` is used, issues are formatted for agent consumption:

```markdown
## Task: T001

**Objective:** Create static directory structure

**File(s) to modify:** `static/`

**Dependencies:** None

## Acceptance Criteria
- [ ] `static/` directory exists at project root
- [ ] Directory is empty and ready for frontend files

## Context
- **Spec:** 002-weather-frontend
- **Phase:** Phase 1: Infrastructure Setup
- **Priority:** Must
- **Estimate:** 5 min

## Instructions for Copilot
Implement this task following the acceptance criteria above. 
Create a pull request when complete.
```

---

## 6. CLI Interface Design

### 6.1 Commands

```bash
# Main command - create issues
speckit-to-issue create <tasks.md> [options]

# Check sync status
speckit-to-issue status <tasks.md> [options]

# Show version
speckit-to-issue version
```

### 6.2 Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--dry-run` | `-n` | Preview without creating | false |
| `--skip-complete` | `-s` | Skip completed tasks | false |
| `--assign-copilot` | `-c` | Format and prep for Copilot | false |
| `--force` | `-f` | Create even if duplicates exist | false |
| `--repo` | `-r` | Target repository (owner/repo) | current |
| `--milestone` | `-m` | Assign to milestone | none |
| `--verbose` | `-v` | Show detailed output | false |

### 6.3 Output Examples

**Normal creation:**
```
📋 Parsing: specs/002-weather-frontend/tasks.md
   Found 24 tasks (22 incomplete)

🚀 Creating issues in owner/repo...
   ✅ [T001] Create static directory structure
   ✅ [T002] Update FastAPI to serve static files
   ⏭️  [T003] Already exists: #42
   ...

📊 Summary:
   Created: 21
   Skipped (exists): 2
   Skipped (complete): 1
   Failed: 0
```

**Dry run:**
```
📋 Parsing: specs/002-weather-frontend/tasks.md
   Found 24 tasks

🔍 DRY RUN - No issues will be created

   [T001] Create static directory structure
   Labels: priority:high, phase-1, spec:002-weather-frontend, task
   
   [T002] Update FastAPI to serve static files
   Labels: priority:high, phase-1, spec:002-weather-frontend, task
   ...

Would create 24 issues.
```

---

## 7. Error Handling

| Error | Cause | User Message |
|-------|-------|--------------|
| File not found | Invalid path | `Error: File not found: {path}` |
| Parse error | Invalid format | `Error: Could not parse tasks at line {n}: {details}` |
| gh not installed | Missing CLI | `Error: GitHub CLI (gh) not found. Install from https://cli.github.com` |
| Not authenticated | gh auth needed | `Error: Not authenticated. Run 'gh auth login' first.` |
| Repo not found | Invalid repo | `Error: Repository '{repo}' not found or no access.` |
| Rate limited | API limits | `Error: Rate limited. Try again in {n} seconds.` |
| Network error | Connectivity | `Error: Network error. Check your connection.` |

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Parser: Valid tasks.md files of varying complexity
- Parser: Edge cases (empty, malformed, unicode)
- Mapper: Task → Issue body generation
- Mapper: Label generation
- Duplicate detection logic

### 8.2 Integration Tests
- Mock gh CLI responses
- End-to-end with sample tasks.md
- Dry-run verification
- Error handling paths

### 8.3 Test Files
- Sample tasks.md from Weather App (real-world)
- Minimal tasks.md (edge case)
- Complex tasks.md (all features)

---

## 9. Dependencies

### 9.1 Runtime Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| Typer | 0.9+ | CLI framework |
| Rich | 13+ | Terminal output formatting |
| gh CLI | 2.0+ | GitHub integration |

### 9.2 Development Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| pytest | 7+ | Testing |
| pytest-cov | 4+ | Coverage |
| ruff | 0.1+ | Linting |
| mypy | 1.5+ | Type checking |

---

## 10. Delivery Milestones

| Milestone | Deliverables | Target |
|-----------|--------------|--------|
| M1: Core Parser | Parse tasks.md, extract all fields | Day 1 |
| M2: Issue Creation | Create issues via gh CLI | Day 1 |
| M3: Labels & Dedup | Label generation, duplicate detection | Day 1 |
| M4: CLI Polish | All flags, help text, error handling | Day 2 |
| M5: Copilot Mode | `--assign-copilot` formatting | Day 2 |
| M6: Status Command | Sync status reporting | Day 2 |
| M7: Packaging | pip/uvx installable | Day 2 |

---

## 11. Open Questions

| # | Question | Impact | Status |
|---|----------|--------|--------|
| 1 | Should we support spec.md → single "epic" issue? | Scope | Deferred to v2 |
| 2 | Add issue templates support? | Flexibility | Deferred to v2 |
| 3 | Support updating existing issues when spec changes? | Sync | Deferred to v2 |

---

## 12. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Copilot | Initial specification |
