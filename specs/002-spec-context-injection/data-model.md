# Data Model: Spec Context Injection

> **Spec:** 002-spec-context-injection  
> **Date:** 2026-01-20

---

## 1. Core Models

### 1.1 SpecContext

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SpecContext:
    """Extracted context from spec folder files.
    
    Contains summarized content from spec.md, plan.md, research.md,
    and data-model.md to provide context for issue bodies.
    """
    
    # From spec.md
    feature_overview: str = ""
    success_criteria: str = ""
    user_stories: str = ""
    functional_requirements: str = ""
    
    # From plan.md
    architecture_overview: str = ""
    target_state: str = ""
    technical_approach: str = ""
    
    # From research.md
    key_decisions: str = ""
    recommended_patterns: str = ""
    
    # From data-model.md
    data_models: str = ""
    
    # Metadata
    spec_folder: str = ""
    files_found: list[str] = field(default_factory=list)
    files_missing: list[str] = field(default_factory=list)
    extraction_warnings: list[str] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        """Check if any meaningful context was extracted."""
        return not any([
            self.feature_overview,
            self.architecture_overview,
            self.technical_approach,
            self.data_models,
        ])
    
    def has_architecture(self) -> bool:
        """Check if architecture context is available."""
        return bool(self.architecture_overview or self.target_state)
    
    def has_technical(self) -> bool:
        """Check if technical context is available."""
        return bool(self.key_decisions or self.recommended_patterns)
    
    @property
    def total_lines(self) -> int:
        """Total lines of context content."""
        all_content = "\n".join([
            self.feature_overview,
            self.success_criteria,
            self.architecture_overview,
            self.target_state,
            self.technical_approach,
            self.key_decisions,
            self.data_models,
        ])
        return len(all_content.split("\n"))
```

### 1.2 ExtractedSection

```python
@dataclass
class ExtractedSection:
    """A section extracted from a spec file."""
    
    name: str                    # Section name (e.g., "Feature Overview")
    content: str                 # Extracted markdown content
    source_file: str             # Source file (e.g., "spec.md")
    line_count: int              # Number of lines
    was_truncated: bool = False  # True if content was truncated
    
    @classmethod
    def empty(cls, name: str, source_file: str) -> "ExtractedSection":
        """Create an empty section."""
        return cls(name=name, content="", source_file=source_file, line_count=0)
```

---

## 2. Configuration Models

### 2.1 ExtractionConfig

```python
@dataclass
class ExtractionConfig:
    """Configuration for spec context extraction."""
    
    # Max lines per section
    max_feature_overview: int = 30
    max_success_criteria: int = 15
    max_user_stories: int = 50
    max_architecture: int = 40
    max_target_state: int = 30
    max_technical: int = 30
    max_decisions: int = 30
    max_data_models: int = 50
    
    # Total budget
    max_total_lines: int = 200
    
    # Files to include
    include_spec: bool = True
    include_plan: bool = True
    include_research: bool = True
    include_data_model: bool = True
    
    @classmethod
    def default(cls) -> "ExtractionConfig":
        """Default extraction configuration."""
        return cls()
    
    @classmethod
    def minimal(cls) -> "ExtractionConfig":
        """Minimal context (just overview and architecture)."""
        return cls(
            include_research=False,
            include_data_model=False,
            max_total_lines=100,
        )
```

### 2.2 SpecFiles

```python
@dataclass
class SpecFiles:
    """Discovered spec files in a spec folder."""
    
    folder: Path
    spec_md: Optional[Path] = None
    plan_md: Optional[Path] = None
    research_md: Optional[Path] = None
    data_model_md: Optional[Path] = None
    tasks_md: Optional[Path] = None
    
    @classmethod
    def discover(cls, tasks_file: Path) -> "SpecFiles":
        """Discover spec files from tasks.md path."""
        folder = tasks_file.parent
        return cls(
            folder=folder,
            spec_md=cls._if_exists(folder / "spec.md"),
            plan_md=cls._if_exists(folder / "plan.md"),
            research_md=cls._if_exists(folder / "research.md"),
            data_model_md=cls._if_exists(folder / "data-model.md"),
            tasks_md=tasks_file if tasks_file.exists() else None,
        )
    
    @staticmethod
    def _if_exists(path: Path) -> Optional[Path]:
        return path if path.exists() else None
    
    @property
    def found(self) -> list[str]:
        """List of found file names."""
        files = []
        if self.spec_md: files.append("spec.md")
        if self.plan_md: files.append("plan.md")
        if self.research_md: files.append("research.md")
        if self.data_model_md: files.append("data-model.md")
        return files
    
    @property
    def missing(self) -> list[str]:
        """List of missing file names."""
        all_files = ["spec.md", "plan.md", "research.md", "data-model.md"]
        return [f for f in all_files if f not in self.found]
```

---

## 3. Section Patterns

### 3.1 SectionPattern

```python
from typing import Pattern


@dataclass
class SectionPattern:
    """Pattern for extracting a section from markdown."""
    
    name: str                    # Human-readable name
    heading_patterns: list[str]  # Possible heading text patterns
    required: bool = False       # Whether section must be found
    max_lines: int = 30          # Maximum lines to extract
    
    def compile_regex(self) -> Pattern:
        """Compile regex for this section."""
        # Match any of the heading patterns
        alternatives = "|".join(re.escape(p) for p in self.heading_patterns)
        return re.compile(
            rf"^## \d*\.?\s*({alternatives}).*?$\n(.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE
        )
```

### 3.2 Predefined Patterns

```python
SPEC_PATTERNS = [
    SectionPattern(
        name="feature_overview",
        heading_patterns=["Feature Overview", "Overview", "Description"],
        max_lines=30,
    ),
    SectionPattern(
        name="success_criteria", 
        heading_patterns=["Success Criteria"],
        max_lines=15,
    ),
    SectionPattern(
        name="functional_requirements",
        heading_patterns=["Functional Requirements", "Requirements"],
        max_lines=30,
    ),
]

PLAN_PATTERNS = [
    SectionPattern(
        name="architecture_overview",
        heading_patterns=["Architecture Overview", "Architecture", "System Design"],
        max_lines=40,
    ),
    SectionPattern(
        name="target_state",
        heading_patterns=["Target State", "Future State", "Proposed Architecture"],
        max_lines=30,
    ),
    SectionPattern(
        name="technical_approach",
        heading_patterns=["Technical Approach", "Implementation Approach", "Approach"],
        max_lines=30,
    ),
]

RESEARCH_PATTERNS = [
    SectionPattern(
        name="key_decisions",
        heading_patterns=["Decisions", "Key Decisions", "Summary of Decisions"],
        max_lines=30,
    ),
]
```

---

## 4. Updated Models

### 4.1 Task Extension

```python
# No changes to Task model - context is passed separately
```

### 4.2 Issue Extension

```python
# Issue model unchanged - body contains the context
```

---

## 5. Template Updates

### 5.1 COPILOT_TEMPLATE_WITH_CONTEXT

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
*Generated by [speckit-to-issue](https://github.com/speckit/speckit-to-issue)*
"""
```

---

## 6. Function Signatures

### 6.1 spec_reader.py

```python
def read_spec_context(
    tasks_file: Path,
    config: ExtractionConfig = None
) -> SpecContext:
    """Read and extract context from spec folder.
    
    Args:
        tasks_file: Path to tasks.md file
        config: Extraction configuration (uses default if None)
    
    Returns:
        SpecContext with extracted content
    """

def discover_spec_files(tasks_file: Path) -> SpecFiles:
    """Discover available spec files."""

def extract_section(
    content: str,
    pattern: SectionPattern
) -> ExtractedSection:
    """Extract a single section from markdown content."""

def truncate_content(content: str, max_lines: int) -> tuple[str, bool]:
    """Truncate content to max lines.
    
    Returns:
        Tuple of (truncated_content, was_truncated)
    """
```

### 6.2 mapper.py Updates

```python
def build_issue_body(
    task: Task,
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None  # NEW
) -> str:
    """Generate issue body markdown from a task.
    
    Args:
        task: Task object
        copilot_mode: If True, use Copilot-optimized template
        spec_context: Optional spec context to include
    
    Returns:
        Markdown string for issue body
    """

def task_to_issue(
    task: Task,
    copilot_mode: bool = False,
    spec_context: Optional[SpecContext] = None  # NEW
) -> Issue:
    """Convert a Task to an Issue.
    
    Args:
        task: Task object to convert
        copilot_mode: If True, use Copilot-optimized body
        spec_context: Optional spec context to include
    
    Returns:
        Issue object ready for creation
    """
```

---

## 7. CLI Options Model

### 7.1 ContextOptions

```python
@dataclass
class ContextOptions:
    """CLI options related to context inclusion."""
    
    include_context: bool = False  # --include-context flag
    no_context: bool = False       # --no-context flag
    assign_copilot: bool = False   # --assign-copilot flag
    
    @property
    def should_include_context(self) -> bool:
        """Determine if context should be included."""
        if self.no_context:
            return False
        return self.assign_copilot or self.include_context
    
    def validate(self) -> None:
        """Validate flag combinations."""
        if self.include_context and self.no_context:
            raise ValueError("Cannot use both --include-context and --no-context")
```

---

## 8. Error Types

### 8.1 New Exceptions

```python
class SpecReadError(Exception):
    """Error reading spec files."""
    pass

class SectionExtractionError(Exception):
    """Error extracting a section from markdown."""
    pass
```

Note: These are informational - actual errors should be handled gracefully without raising exceptions that stop issue creation.

---

## 9. Entity Relationships

```
┌─────────────────┐
│   tasks.md      │
└────────┬────────┘
         │ discover
         ▼
┌─────────────────┐     ┌─────────────────┐
│   SpecFiles     │────►│   spec.md       │
│                 │     │   plan.md       │
│                 │     │   research.md   │
│                 │     │   data-model.md │
└────────┬────────┘     └─────────────────┘
         │ extract
         ▼
┌─────────────────┐
│  SpecContext    │
├─────────────────┤
│ feature_overview│
│ architecture    │
│ technical       │
│ data_models     │
└────────┬────────┘
         │ inject
         ▼
┌─────────────────┐
│     Issue       │
│  (body includes │
│   context)      │
└─────────────────┘
```
