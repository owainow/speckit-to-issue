# Research: Spec Context Injection

> **Spec:** 002-spec-context-injection  
> **Date:** 2026-01-20

---

## 1. Markdown Section Extraction

### 1.1 Approach: Heading-Based Parsing

Spec files use standard markdown with heading hierarchy:
```markdown
## 1. Feature Overview      ← Level 2 heading (section)
### 1.1 Description         ← Level 3 heading (subsection)
```

**Strategy:** Parse by heading level and extract content between headings.

### 1.2 Regex Patterns

```python
# Match level 2 headings: ## Section Name
SECTION_PATTERN = re.compile(r"^## \d*\.?\s*(.+?)$", re.MULTILINE)

# Match level 3 headings: ### Subsection Name  
SUBSECTION_PATTERN = re.compile(r"^### \d*\.?\s*(.+?)$", re.MULTILINE)

# Extract section by name
def extract_section(content: str, section_name: str) -> str:
    """Extract content under a specific heading."""
    pattern = re.compile(
        rf"^## \d*\.?\s*{re.escape(section_name)}.*?$\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""
```

### 1.3 Alternative: Markdown Parser Library

Could use `mistune` or `markdown-it-py` for robust parsing, but:
- Adds dependency
- Overkill for heading extraction
- Current parser.py uses regex successfully

**Decision:** Use regex patterns (consistent with existing codebase).

---

## 2. Spec File Discovery

### 2.1 Path Resolution

Tasks file path: `specs/002-feature/tasks.md`  
Spec folder: `specs/002-feature/`

```python
def get_spec_folder(tasks_file: Path) -> Path:
    """Get spec folder from tasks.md path."""
    return tasks_file.parent

def get_spec_file(tasks_file: Path, filename: str) -> Optional[Path]:
    """Get a specific spec file if it exists."""
    spec_file = tasks_file.parent / filename
    return spec_file if spec_file.exists() else None
```

### 2.2 File Priority & Existence

```python
SPEC_FILES = {
    "spec.md": True,        # Required for context
    "plan.md": True,        # Required for context
    "research.md": False,   # Optional
    "data-model.md": False, # Optional
}

def discover_spec_files(tasks_file: Path) -> dict[str, Optional[Path]]:
    """Discover available spec files."""
    folder = tasks_file.parent
    return {
        name: folder / name if (folder / name).exists() else None
        for name in SPEC_FILES.keys()
    }
```

---

## 3. Section Extraction Strategy

### 3.1 Spec.md Sections

| Section | Extraction Method | Max Lines |
|---------|-------------------|-----------|
| Feature Overview | Full section under "## 1. Feature Overview" | 30 |
| Success Criteria | Look for "Success Criteria" subsection | 15 |
| User Stories | Extract all "### USx" subsections | 50 |
| Functional Requirements | Extract markdown table | 30 |

### 3.2 Plan.md Sections

| Section | Extraction Method | Max Lines |
|---------|-------------------|-----------|
| Architecture Overview | "## 2. Architecture" section | 40 |
| Target State | Look for "Target State" code block/diagram | 30 |
| Technical Approach | "## 3. Technical Approach" section | 30 |

### 3.3 Research.md Sections

| Section | Extraction Method | Max Lines |
|---------|-------------------|-----------|
| Key Decisions | Look for "Decision" subsections | 30 |
| Recommended Patterns | Code blocks with patterns | 30 |

### 3.4 Data-model.md Sections

| Section | Extraction Method | Max Lines |
|---------|-------------------|-----------|
| Core Models | Extract Python code blocks | 50 |

---

## 4. Content Truncation

### 4.1 Line-Based Truncation

```python
def truncate_content(content: str, max_lines: int) -> str:
    """Truncate content to max lines with indicator."""
    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content
    truncated = lines[:max_lines]
    truncated.append("...")
    truncated.append(f"*({len(lines) - max_lines} more lines)*")
    return "\n".join(truncated)
```

### 4.2 Smart Truncation (Preserve Structure)

For tables and code blocks, truncate at natural boundaries:
- End of code block (```)
- End of table row
- End of list item

---

## 5. Context Assembly

### 5.1 SpecContext Data Class

```python
@dataclass
class SpecContext:
    """Extracted context from spec files."""
    
    feature_overview: str = ""
    success_criteria: str = ""
    user_stories: str = ""
    functional_requirements: str = ""
    architecture_overview: str = ""
    target_state: str = ""
    technical_approach: str = ""
    key_decisions: str = ""
    data_models: str = ""
    
    def is_empty(self) -> bool:
        """Check if any context was extracted."""
        return not any([
            self.feature_overview,
            self.architecture_overview,
            self.technical_approach,
        ])
    
    def to_markdown(self) -> str:
        """Format context as markdown for issue body."""
        sections = []
        
        if self.feature_overview:
            sections.append(f"## 📋 Feature Specification\n\n{self.feature_overview}")
        
        if self.architecture_overview or self.target_state:
            arch = "## 🏗️ Architecture\n\n"
            if self.target_state:
                arch += f"### Target State\n{self.target_state}\n\n"
            if self.architecture_overview:
                arch += f"{self.architecture_overview}"
            sections.append(arch)
        
        if self.key_decisions or self.technical_approach:
            tech = "## 🔬 Technical Context\n\n"
            if self.technical_approach:
                tech += f"{self.technical_approach}\n\n"
            if self.key_decisions:
                tech += f"{self.key_decisions}"
            sections.append(tech)
        
        if self.data_models:
            sections.append(f"## 📊 Data Models\n\n{self.data_models}")
        
        return "\n\n---\n\n".join(sections)
```

---

## 6. Integration with Existing Code

### 6.1 New Module: spec_reader.py

```python
# src/speckit_to_issue/spec_reader.py

def read_spec_context(tasks_file: Path) -> SpecContext:
    """Read and extract context from spec files."""
    
def extract_from_spec(spec_path: Path) -> dict[str, str]:
    """Extract sections from spec.md."""
    
def extract_from_plan(plan_path: Path) -> dict[str, str]:
    """Extract sections from plan.md."""
    
def extract_from_research(research_path: Path) -> dict[str, str]:
    """Extract sections from research.md."""
    
def extract_from_data_model(data_model_path: Path) -> dict[str, str]:
    """Extract sections from data-model.md."""
```

### 6.2 Mapper Changes

```python
# mapper.py changes

def build_issue_body(
    task: Task, 
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None  # NEW
) -> str:
    """Generate issue body with optional spec context."""
    
    base_body = build_base_body(task, copilot_mode)
    
    if spec_context and not spec_context.is_empty():
        context_section = spec_context.to_markdown()
        # Insert context after acceptance criteria, before instructions
        base_body = inject_context(base_body, context_section)
    
    return base_body
```

### 6.3 CLI Changes

```python
# cli.py changes

@app.command()
def create(
    # ... existing args ...
    no_context: bool = typer.Option(
        False,
        "--no-context",
        help="Disable spec context inclusion",
    ),
    include_context: bool = typer.Option(
        False,
        "--include-context",
        help="Include spec context in issues",
    ),
):
    # Determine if context should be included
    include_spec_context = (assign_copilot or include_context) and not no_context
    
    # Read spec context if needed
    spec_context = None
    if include_spec_context:
        spec_context = read_spec_context(tasks_file)
        if spec_context.is_empty():
            console.print("[yellow]Warning: No spec context found[/yellow]")
    
    # Pass to mapper
    issue = task_to_issue(task, copilot_mode=assign_copilot, spec_context=spec_context)
```

---

## 7. Error Handling

### 7.1 Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| File not found | Skip file, log warning |
| Parse error | Skip section, log warning |
| Empty extraction | Skip section |
| Encoding error | Try UTF-8 with error handling |

### 7.2 Warning Messages

```python
def read_spec_context(tasks_file: Path) -> SpecContext:
    context = SpecContext()
    
    spec_file = tasks_file.parent / "spec.md"
    if not spec_file.exists():
        logger.warning(f"spec.md not found in {tasks_file.parent}")
    else:
        try:
            context = extract_from_spec(spec_file, context)
        except Exception as e:
            logger.warning(f"Failed to parse spec.md: {e}")
    
    # ... similar for other files
    return context
```

---

## 8. Performance Considerations

### 8.1 File I/O

- Read files once, cache content
- Lazy loading (only read files if context is requested)
- Don't read files in dry-run unless needed for output

### 8.2 Regex Compilation

```python
# Compile patterns once at module level
SECTION_PATTERNS = {
    "feature_overview": re.compile(r"^## \d*\.?\s*Feature Overview.*?$\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL),
    # ... other patterns
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

- `test_spec_reader.py` - Section extraction functions
- `test_spec_context.py` - SpecContext class methods
- Update `test_mapper.py` - Context injection

### 9.2 Test Fixtures

Create sample spec files in `tests/fixtures/sample-spec/`:
- spec.md
- plan.md
- research.md
- data-model.md
- tasks.md

### 9.3 Edge Cases

- Empty spec files
- Missing sections
- Malformed markdown
- Very large files
- Non-UTF8 encoding

---

## 10. Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Markdown parsing | Regex | Consistent with existing parser.py |
| File discovery | Path-based | Simple, reliable |
| Content truncation | Line-based | Easy to implement, predictable |
| Context assembly | Dataclass | Type-safe, clear structure |
| Error handling | Graceful degradation | Never fail issue creation |
| New module | spec_reader.py | Separation of concerns |
