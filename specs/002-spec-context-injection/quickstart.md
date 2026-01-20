# Quickstart Guide: Spec Context Injection

> **Spec:** 002-spec-context-injection  
> **Date:** 2026-01-20

---

## 1. What You're Building

Enhance speckit-to-issue to automatically include spec context in generated issues:

**Before:**
```markdown
## Objective
Create FAQ accordion HTML

## Acceptance Criteria
- [ ] Use <details>/<summary> elements
```

**After:**
```markdown
## Objective
Create FAQ accordion HTML

## Acceptance Criteria
- [ ] Use <details>/<summary> elements

---

## 📋 Feature Specification

### Overview
A help page for the Weather App frontend that provides users with 
a comprehensive FAQ section...

## 🏗️ Architecture

### Target State
┌─────────────────────────────────────────┐
│  HELP VIEW (hidden by default)          │
│  ├─ Back Button                         │
│  ├─ Quick Tips                          │
│  └─ FAQ Accordion                       │
└─────────────────────────────────────────┘

## Instructions for Copilot
...
```

---

## 2. Prerequisites

### Required
- ✅ Existing speckit-to-issue installation
- ✅ Python 3.11+
- ✅ pytest for testing

### Knowledge
- Python dataclasses
- Regex for markdown parsing
- Existing codebase patterns (parser.py, mapper.py)

---

## 3. Project Location

```
speckit-to-issue/
├── src/speckit_to_issue/
│   ├── spec_reader.py    ← NEW FILE
│   ├── mapper.py         ← MODIFY
│   ├── cli.py            ← MODIFY
│   └── models.py         ← MODIFY (add SpecContext)
└── tests/
    ├── unit/
    │   ├── test_spec_reader.py  ← NEW FILE
    │   └── test_mapper.py       ← UPDATE
    └── fixtures/
        └── sample-spec/         ← NEW FIXTURES
```

---

## 4. Quick Implementation Overview

### Step 1: Add SpecContext Model

```python
# src/speckit_to_issue/models.py

@dataclass
class SpecContext:
    """Extracted context from spec files."""
    feature_overview: str = ""
    architecture_overview: str = ""
    technical_approach: str = ""
    data_models: str = ""
    
    def is_empty(self) -> bool:
        return not any([self.feature_overview, self.architecture_overview])
    
    def to_markdown(self) -> str:
        # Format sections as markdown
        ...
```

### Step 2: Create spec_reader.py

```python
# src/speckit_to_issue/spec_reader.py

def read_spec_context(tasks_file: Path) -> SpecContext:
    """Read and extract context from spec folder."""
    context = SpecContext()
    folder = tasks_file.parent
    
    # Extract from spec.md
    if (folder / "spec.md").exists():
        context.feature_overview = extract_section(
            (folder / "spec.md").read_text(),
            "Feature Overview"
        )
    
    # Extract from plan.md
    if (folder / "plan.md").exists():
        context.architecture_overview = extract_section(
            (folder / "plan.md").read_text(),
            "Architecture"
        )
    
    return context

def extract_section(content: str, section_name: str) -> str:
    """Extract content under a heading."""
    pattern = re.compile(
        rf"^## \d*\.?\s*{re.escape(section_name)}.*?$\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(content)
    return match.group(1).strip()[:2000] if match else ""
```

### Step 3: Update mapper.py

```python
# src/speckit_to_issue/mapper.py

def build_issue_body(
    task: Task,
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None
) -> str:
    # ... existing code ...
    
    if copilot_mode and spec_context and not spec_context.is_empty():
        # Insert context section before Instructions
        context_md = spec_context.to_markdown()
        body = body.replace(
            "## Instructions for Copilot",
            f"{context_md}\n\n---\n\n## Instructions for Copilot"
        )
    
    return body
```

### Step 4: Update CLI

```python
# src/speckit_to_issue/cli.py

@app.command()
def create(
    # ... existing args ...
    no_context: bool = typer.Option(False, "--no-context"),
):
    # Determine if context should be included
    include_context = assign_copilot and not no_context
    
    # Read context once
    spec_context = None
    if include_context:
        spec_context = read_spec_context(tasks_file)
    
    # Pass to mapper
    for task in tasks:
        issue = task_to_issue(task, assign_copilot, spec_context)
```

---

## 5. Testing the Feature

### Manual Test

```bash
# Create a spec folder with files
mkdir -p test-spec
echo "## 1. Feature Overview\nTest feature" > test-spec/spec.md
echo "## 2. Architecture\nTest arch" > test-spec/plan.md
echo "### T001: Test task" > test-spec/tasks.md

# Run with --assign-copilot (context auto-included)
speckit-to-issue create test-spec/tasks.md --assign-copilot --dry-run

# Verify context appears in output
```

### Unit Test

```python
def test_read_spec_context(tmp_path):
    # Create test files
    spec_folder = tmp_path / "test-spec"
    spec_folder.mkdir()
    (spec_folder / "spec.md").write_text("## 1. Feature Overview\n\nTest description")
    (spec_folder / "tasks.md").write_text("### T001: Test")
    
    # Read context
    context = read_spec_context(spec_folder / "tasks.md")
    
    assert "Test description" in context.feature_overview
    assert not context.is_empty()
```

---

## 6. Key Patterns

### Section Extraction Regex

```python
# Match: ## 1. Feature Overview or ## Feature Overview
pattern = re.compile(
    r"^## \d*\.?\s*Feature Overview.*?$\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL
)
```

### Graceful Degradation

```python
def safe_extract(file_path: Path, section: str) -> str:
    """Extract section, return empty string on any error."""
    try:
        if not file_path.exists():
            return ""
        content = file_path.read_text(encoding="utf-8")
        return extract_section(content, section)
    except Exception:
        return ""  # Never fail
```

### Content Truncation

```python
def truncate(content: str, max_lines: int = 30) -> str:
    """Truncate to max lines."""
    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content
    return "\n".join(lines[:max_lines]) + "\n\n*(...truncated)*"
```

---

## 7. Files Changed Summary

| File | Action | Description |
|------|--------|-------------|
| `models.py` | Modify | Add SpecContext dataclass |
| `spec_reader.py` | Create | New module for reading spec files |
| `mapper.py` | Modify | Accept and inject spec_context |
| `cli.py` | Modify | Add --no-context flag, read context |
| `test_spec_reader.py` | Create | Unit tests for spec_reader |
| `test_mapper.py` | Modify | Tests with spec_context |

---

## 8. Local Development

### Run Tests

```bash
cd speckit-to-issue
pytest tests/unit/test_spec_reader.py -v
pytest tests/unit/test_mapper.py -v
```

### Test Full Flow

```bash
# Use existing spec folder
speckit-to-issue create specs/001-tasks-to-issues/tasks.md --assign-copilot --dry-run
```

---

## 9. Success Criteria

✅ `--assign-copilot` includes context by default  
✅ `--no-context` disables context inclusion  
✅ Missing spec files don't cause errors  
✅ Context is well-formatted in issue body  
✅ Existing tests continue to pass  
✅ New tests cover spec_reader module
