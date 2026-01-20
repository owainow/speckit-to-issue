# 003: Feature-Level Issue Creation

## 1. Overview

### 1.1 Description
Refactor speckit-to-issue to create a single comprehensive GitHub issue per feature specification, rather than individual issues per task. This approach provides the Copilot coding agent with full context to implement an entire feature systematically.

### 1.2 Business Value
- **Better AI Agent Performance**: Copilot coding agent works more effectively with comprehensive context in a single issue
- **Reduced Issue Clutter**: One issue per feature vs 15-20 small task issues
- **Coherent Implementation**: Agent can see the full picture and make consistent architectural decisions
- **Simpler Tracking**: Track feature completion rather than individual tasks

### 1.3 Success Criteria
- Single issue contains full spec context (overview, architecture, all tasks)
- Tasks are organized by phase with checkboxes
- All acceptance criteria consolidated
- Files to modify listed comprehensively
- Issue can be assigned to Copilot coding agent
- Backward compatibility: `--granular` flag preserves old task-per-issue behavior

## 2. User Stories

### 2.1 Primary User Story
**As a** developer using speckit-to-issue  
**I want to** create a single feature issue from my spec  
**So that** the Copilot coding agent has complete context to implement the entire feature

### 2.2 Secondary User Stories

**As a** developer  
**I want to** see all tasks organized by phase in the issue  
**So that** I can track implementation progress

**As a** developer  
**I want to** optionally create individual task issues  
**So that** I can use the granular approach when needed

## 3. Scope

### 3.1 In Scope
- New `create` command behavior (feature-level by default)
- Feature issue body builder consolidating spec + architecture + tasks
- Phase-organized task sections with checkboxes
- Consolidated acceptance criteria
- `--granular` flag for old behavior
- Copilot agent assignment via REST API

### 3.2 Out of Scope
- Changes to spec parsing (tasks.md, spec.md, architecture.md formats)
- Multi-spec batch processing
- Issue update/sync functionality
- GitHub Projects integration

## 4. Dependencies
- Existing spec_reader.py module
- Existing parser.py for tasks.md parsing
- GitHub CLI (gh) for issue creation
