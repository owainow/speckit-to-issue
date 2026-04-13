"""Parser for speckit tasks.md files.

Supports two formats:
- **New format** (checklist): ``- [ ] T001 [markers] Description in path/to/file.ext``
- **Old format** (header): ``### T001: Task title`` with field blocks

The parser auto-detects the format and parses accordingly.
"""

import re
from pathlib import Path

from .exceptions import ParseError
from .models import ParseResult, Priority, Task

# ---------------------------------------------------------------------------
# Shared patterns
# ---------------------------------------------------------------------------

# Phase header: ## Phase 1: Setup or ## Phase 1: Setup (Priority: P1) 🎯 MVP
PHASE_PATTERN = re.compile(r"^## (Phase \d+:.+?)$", re.MULTILINE)

# Priority embedded in phase header: (Priority: P1)
PHASE_PRIORITY_PATTERN = re.compile(r"\(Priority:\s*(P\d+)\)")

# Feature title from top-level heading: # Tasks: 5-Day Weather Forecast
TITLE_PATTERN = re.compile(r"^# Tasks:\s*(.+)$", re.MULTILINE)

# ---------------------------------------------------------------------------
# New format patterns (checklist style)
# ---------------------------------------------------------------------------

# Task line: - [ ] T001 ... or - [x] T001 ...
NEW_TASK_PATTERN = re.compile(
    r"^\s*-\s*\[([ xX])\]\s*(T\d+)\s+(.*?)$",
    re.MULTILINE,
)

# File path at end of description: "in src/path/to/file.ext" (requires /)
FILE_IN_PATTERN = re.compile(r"\s+in\s+((?:\S+/)+\S+\.\w{1,10})(?:\s|$)")

# Inline markers: [P], [US1], [US2], etc.
MARKER_PATTERN = re.compile(r"^\[([A-Za-z][A-Za-z0-9]*)\]\s*")

# ---------------------------------------------------------------------------
# Old format patterns (header style)
# ---------------------------------------------------------------------------

TASK_HEADER_PATTERN = re.compile(r"^### (T\d+): (.+?)(?:\s*✅)?$", re.MULTILINE)

OLD_FIELD_PATTERNS = {
    "priority": re.compile(r"^\s*-\s*\*\*Priority:\*\*\s*(\w+)", re.MULTILINE),
    "estimate": re.compile(r"^\s*-\s*\*\*Estimate:\*\*\s*(.+?)$", re.MULTILINE),
    "dependencies": re.compile(r"^\s*-\s*\*\*Dependencies:\*\*\s*(.+?)$", re.MULTILINE),
    "file": re.compile(r"^\s*-\s*\*\*File:\*\*\s*`?(.+?)`?$", re.MULTILINE),
    "fr": re.compile(r"^\s*-\s*\*\*FR:\*\*\s*(.+?)$", re.MULTILINE),
    "nfr": re.compile(r"^\s*-\s*\*\*NFR:\*\*\s*(.+?)$", re.MULTILINE),
}

CRITERIA_PATTERN = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.+?)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def extract_spec_name(file_path: Path) -> str:
    """Extract spec name from file path.

    Expects path like: specs/001-feature-name/tasks.md
    Returns: 001-feature-name
    """
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "specs" and i + 1 < len(parts):
            return parts[i + 1]
    return file_path.parent.name


def extract_feature_title(content: str) -> str:
    """Extract feature title from ``# Tasks: ...`` header."""
    match = TITLE_PATTERN.search(content)
    return match.group(1).strip() if match else ""


def _is_new_format(content: str) -> bool:
    """Detect whether the content uses the new checklist format."""
    return bool(NEW_TASK_PATTERN.search(content))


# ---------------------------------------------------------------------------
# New format parsing
# ---------------------------------------------------------------------------


def _extract_phase_priority(phase_header: str) -> str:
    """Extract priority from a phase header like ``Phase 3: ... (Priority: P1)``."""
    match = PHASE_PRIORITY_PATTERN.search(phase_header)
    return match.group(1) if match else ""


def _priority_from_code(code: str) -> Priority:
    """Map P1/P2/P3 codes to Priority enum."""
    mapping = {"P1": Priority.MUST, "P2": Priority.SHOULD, "P3": Priority.COULD}
    return mapping.get(code, Priority.SHOULD)


def _parse_new_task_line(line_text: str, phase: str, spec_name: str, phase_priority: str) -> Task:
    """Parse a single checklist-style task line."""
    match = re.match(r"\s*-\s*\[([ xX])\]\s*(T\d+)\s+(.*)", line_text)
    if not match:
        raise ParseError(f"Invalid task line: {line_text}")

    is_complete = match.group(1).lower() == "x"
    task_id = match.group(2)
    remainder = match.group(3).strip()

    # Extract inline markers e.g. [P], [US1]
    markers: list[str] = []
    while True:
        m = MARKER_PATTERN.match(remainder)
        if m:
            markers.append(m.group(1))
            remainder = remainder[m.end():]
        else:
            break

    # Extract file path from trailing "in path/to/file.ext"
    file_path = None
    file_match = FILE_IN_PATTERN.search(remainder)
    if file_match:
        file_path = file_match.group(1)
        title = remainder[: file_match.start()].strip()
    else:
        title = remainder.strip()

    # Priority from phase header
    priority = _priority_from_code(phase_priority) if phase_priority else Priority.SHOULD

    return Task(
        id=task_id,
        title=title,
        priority=priority,
        estimate="",
        file_path=file_path,
        phase=phase,
        spec_name=spec_name,
        markers=markers,
        is_complete=is_complete,
    )


def _parse_new_format(content: str, spec_name: str) -> ParseResult:
    """Parse the new checklist-style tasks.md format."""
    feature_title = extract_feature_title(content)

    # Find all phases and their positions
    phase_matches = list(PHASE_PATTERN.finditer(content))
    phases = [m.group(1) for m in phase_matches]

    # Build a list of (start, phase_text, priority_code)
    phase_ranges: list[tuple[int, str, str]] = []
    for m in phase_matches:
        phase_ranges.append((m.start(), m.group(1), _extract_phase_priority(m.group(1))))

    # Find all task lines
    task_matches = list(NEW_TASK_PATTERN.finditer(content))

    if not task_matches:
        raise ParseError("No tasks found (new format)")

    tasks: list[Task] = []
    errors: list[str] = []

    for tm in task_matches:
        line_text = tm.group(0)
        pos = tm.start()

        # Determine which phase this task belongs to
        current_phase = ""
        current_priority = ""
        for start, phase_text, priority_code in phase_ranges:
            if start < pos:
                current_phase = phase_text
                current_priority = priority_code

        try:
            task = _parse_new_task_line(line_text, current_phase, spec_name, current_priority)
            tasks.append(task)
        except ParseError as e:
            errors.append(str(e))

    return ParseResult(
        spec_name=spec_name,
        feature_title=feature_title,
        tasks=tasks,
        phases=phases,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Old format parsing (backward compatibility)
# ---------------------------------------------------------------------------


def _parse_old_task_block(content: str, phase: str, spec_name: str) -> Task:
    """Parse a single old-format task block (### T001: Title …)."""
    header_match = TASK_HEADER_PATTERN.search(content)
    if not header_match:
        raise ParseError(f"Invalid task block: no header found in:\n{content[:100]}")

    task_id = header_match.group(1)
    title = header_match.group(2).strip()
    is_complete = "✅" in content.split("\n")[0]

    priority_match = OLD_FIELD_PATTERNS["priority"].search(content)
    priority = Priority.from_string(priority_match.group(1)) if priority_match else Priority.SHOULD

    estimate_match = OLD_FIELD_PATTERNS["estimate"].search(content)
    estimate = estimate_match.group(1).strip() if estimate_match else "Unknown"

    deps_match = OLD_FIELD_PATTERNS["dependencies"].search(content)
    dependencies = deps_match.group(1).strip() if deps_match else "None"

    file_match = OLD_FIELD_PATTERNS["file"].search(content)
    file_path = file_match.group(1).strip().strip("`") if file_match else None

    fr_match = OLD_FIELD_PATTERNS["fr"].search(content)
    fr_refs = fr_match.group(1).strip() if fr_match else None

    nfr_match = OLD_FIELD_PATTERNS["nfr"].search(content)
    nfr_refs = nfr_match.group(1).strip() if nfr_match else None

    criteria_matches = CRITERIA_PATTERN.findall(content)
    acceptance_criteria = [criterion.strip() for _, criterion in criteria_matches]

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


def _parse_old_format(content: str, spec_name: str) -> ParseResult:
    """Parse the old header-style tasks.md format."""
    feature_title = extract_feature_title(content)

    phase_matches = list(PHASE_PATTERN.finditer(content))
    phases = [m.group(1) for m in phase_matches]

    task_headers = list(TASK_HEADER_PATTERN.finditer(content))
    if not task_headers:
        raise ParseError("No tasks found (old format)")

    tasks: list[Task] = []
    errors: list[str] = []

    for i, header_match in enumerate(task_headers):
        start = header_match.start()
        end = task_headers[i + 1].start() if i + 1 < len(task_headers) else len(content)
        task_content = content[start:end]

        current_phase = ""
        for pm in phase_matches:
            if pm.start() < start:
                current_phase = pm.group(1)

        try:
            task = _parse_old_task_block(task_content, current_phase, spec_name)
            tasks.append(task)
        except ParseError as e:
            errors.append(f"Error parsing task at position {start}: {e}")

    return ParseResult(
        spec_name=spec_name,
        feature_title=feature_title,
        tasks=tasks,
        phases=phases,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_tasks_file(file_path: Path) -> ParseResult:
    """Parse a tasks.md file and return structured data.

    Auto-detects whether the file uses the new checklist format
    or the old header-style format.

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

    if _is_new_format(content):
        return _parse_new_format(content, spec_name)
    else:
        return _parse_old_format(content, spec_name)
