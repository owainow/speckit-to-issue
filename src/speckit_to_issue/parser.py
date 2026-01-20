"""Parser for speckit tasks.md files."""

import re
from pathlib import Path

from .exceptions import ParseError
from .models import ParseResult, Priority, Task

# Pattern for task header: ### T001: Task title or ### T001: Task title ✅
TASK_HEADER_PATTERN = re.compile(r"^### (T\d+): (.+?)(?:\s*✅)?$", re.MULTILINE)

# Pattern for phase header: ## Phase 1: Setup
PHASE_PATTERN = re.compile(r"^## (Phase \d+: .+)$", re.MULTILINE)

# Pattern for field extraction
FIELD_PATTERNS = {
    "priority": re.compile(r"^\s*-\s*\*\*Priority:\*\*\s*(\w+)", re.MULTILINE),
    "estimate": re.compile(r"^\s*-\s*\*\*Estimate:\*\*\s*(.+?)$", re.MULTILINE),
    "dependencies": re.compile(r"^\s*-\s*\*\*Dependencies:\*\*\s*(.+?)$", re.MULTILINE),
    "file": re.compile(r"^\s*-\s*\*\*File:\*\*\s*`?(.+?)`?$", re.MULTILINE),
    "fr": re.compile(r"^\s*-\s*\*\*FR:\*\*\s*(.+?)$", re.MULTILINE),
    "nfr": re.compile(r"^\s*-\s*\*\*NFR:\*\*\s*(.+?)$", re.MULTILINE),
}

# Pattern for acceptance criteria
CRITERIA_PATTERN = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.+?)$", re.MULTILINE)


def extract_spec_name(file_path: Path) -> str:
    """Extract spec name from file path.

    Expects path like: specs/001-feature-name/tasks.md
    Returns: 001-feature-name
    """
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "specs" and i + 1 < len(parts):
            return parts[i + 1]
    # Fallback: use parent directory name
    return file_path.parent.name


def parse_task_block(content: str, phase: str, spec_name: str) -> Task:
    """Parse a single task block into a Task object."""
    # Extract header
    header_match = TASK_HEADER_PATTERN.search(content)
    if not header_match:
        raise ParseError(f"Invalid task block: no header found in:\n{content[:100]}")

    task_id = header_match.group(1)
    title = header_match.group(2).strip()
    is_complete = "✅" in content.split("\n")[0]

    # Extract priority
    priority_match = FIELD_PATTERNS["priority"].search(content)
    priority = Priority.from_string(priority_match.group(1)) if priority_match else Priority.SHOULD

    # Extract estimate
    estimate_match = FIELD_PATTERNS["estimate"].search(content)
    estimate = estimate_match.group(1).strip() if estimate_match else "Unknown"

    # Extract optional fields
    deps_match = FIELD_PATTERNS["dependencies"].search(content)
    dependencies = deps_match.group(1).strip() if deps_match else "None"

    file_match = FIELD_PATTERNS["file"].search(content)
    file_path = file_match.group(1).strip().strip("`") if file_match else None

    fr_match = FIELD_PATTERNS["fr"].search(content)
    fr_refs = fr_match.group(1).strip() if fr_match else None

    nfr_match = FIELD_PATTERNS["nfr"].search(content)
    nfr_refs = nfr_match.group(1).strip() if nfr_match else None

    # Extract acceptance criteria
    criteria_matches = CRITERIA_PATTERN.findall(content)
    acceptance_criteria = [criterion.strip() for _, criterion in criteria_matches]

    # Check if all criteria are completed
    all_criteria_complete = all(check.lower() == "x" for check, _ in criteria_matches)
    if criteria_matches and all_criteria_complete:
        is_complete = True

    return Task(
        id=task_id,
        title=title,
        priority=priority,
        estimate=estimate,
        dependencies=dependencies,
        file_path=file_path,
        fr_refs=fr_refs,
        nfr_refs=nfr_refs,
        phase=phase,
        spec_name=spec_name,
        acceptance_criteria=acceptance_criteria,
        is_complete=is_complete,
    )


def parse_tasks_file(file_path: Path) -> ParseResult:
    """Parse a tasks.md file and return structured data.

    Args:
        file_path: Path to the tasks.md file

    Returns:
        ParseResult with tasks and metadata

    Raises:
        ParseError: If file cannot be parsed
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Tasks file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    spec_name = extract_spec_name(file_path)

    # Find all phases
    phase_matches = list(PHASE_PATTERN.finditer(content))
    phases = [m.group(1) for m in phase_matches]

    # Find all task headers
    task_headers = list(TASK_HEADER_PATTERN.finditer(content))

    if not task_headers:
        raise ParseError(f"No tasks found in {file_path}")

    tasks: list[Task] = []
    errors: list[str] = []

    for i, header_match in enumerate(task_headers):
        # Determine task block boundaries
        start = header_match.start()
        end = task_headers[i + 1].start() if i + 1 < len(task_headers) else len(content)
        task_content = content[start:end]

        # Determine which phase this task belongs to
        current_phase = ""
        for phase_match in phase_matches:
            if phase_match.start() < start:
                current_phase = phase_match.group(1)

        try:
            task = parse_task_block(task_content, current_phase, spec_name)
            tasks.append(task)
        except ParseError as e:
            errors.append(f"Error parsing task at position {start}: {e}")

    return ParseResult(
        spec_name=spec_name,
        tasks=tasks,
        phases=phases,
        errors=errors,
    )
