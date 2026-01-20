"""Reader for speckit spec files to extract context.

This module reads companion spec files (spec.md, plan.md, research.md, data-model.md)
and extracts relevant sections to provide context for GitHub issues.
"""

import re
from pathlib import Path
from typing import Optional

from .models import SpecContext

# Spec files to look for in the spec folder
SPEC_FILES = ["spec.md", "plan.md", "research.md", "data-model.md"]

# Maximum lines per section (for truncation)
MAX_LINES = {
    "feature_overview": 30,
    "success_criteria": 15,
    "architecture_overview": 40,
    "target_state": 30,
    "technical_approach": 30,
    "key_decisions": 30,
    "data_models": 50,
}


def discover_spec_files(tasks_file: Path) -> dict[str, Optional[Path]]:
    """Discover available spec files in the spec folder.

    Args:
        tasks_file: Path to the tasks.md file

    Returns:
        Dict mapping filename to Path (if exists) or None (if missing)
    """
    folder = tasks_file.parent
    return {
        name: folder / name if (folder / name).exists() else None
        for name in SPEC_FILES
    }


def extract_section(content: str, section_name: str) -> str:
    """Extract content under a markdown heading.

    Handles both numbered headings (## 1. Feature Overview) and
    plain headings (## Feature Overview). Case-insensitive.

    Args:
        content: Full markdown content
        section_name: Name of section to extract (without ## prefix)

    Returns:
        Extracted section content, or empty string if not found
    """
    # Pattern matches: ## 1. Section Name or ## Section Name
    # Captures content until next ## heading or end of string
    pattern = re.compile(
        rf"^##\s+\d*\.?\s*{re.escape(section_name)}.*?$\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def extract_subsection(content: str, subsection_name: str) -> str:
    """Extract content under a level 3 heading.

    Args:
        content: Markdown content (can be full file or section)
        subsection_name: Name of subsection to extract (without ### prefix)

    Returns:
        Extracted subsection content, or empty string if not found
    """
    pattern = re.compile(
        rf"^###\s+\d*\.?\s*{re.escape(subsection_name)}.*?$\n(.*?)(?=^###\s|^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def truncate_content(content: str, max_lines: int = 30) -> tuple[str, bool]:
    """Truncate content to maximum lines.

    Args:
        content: Content to truncate
        max_lines: Maximum number of lines to keep

    Returns:
        Tuple of (truncated_content, was_truncated)
    """
    if not content:
        return "", False

    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content, False

    truncated = lines[:max_lines]
    remaining = len(lines) - max_lines
    truncated.append("")
    truncated.append(f"*...({remaining} more lines)*")
    return "\n".join(truncated), True


def extract_from_spec(spec_path: Path) -> dict[str, str]:
    """Extract relevant sections from spec.md.

    Args:
        spec_path: Path to spec.md file

    Returns:
        Dict with extracted sections: feature_overview, success_criteria
    """
    try:
        content = spec_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    result = {}

    # Extract Feature Overview section
    overview_section = extract_section(content, "Feature Overview")
    if overview_section:
        # Try to get just the description subsection
        description = extract_subsection(overview_section, "Description")
        if description:
            result["feature_overview"] = description
        else:
            # Fall back to first part of overview
            result["feature_overview"] = overview_section

    # Try to extract Success Criteria
    success = extract_subsection(content, "Success Criteria")
    if success:
        result["success_criteria"] = success

    return result


def extract_from_plan(plan_path: Path) -> dict[str, str]:
    """Extract relevant sections from plan.md.

    Args:
        plan_path: Path to plan.md file

    Returns:
        Dict with extracted sections: architecture_overview, target_state, technical_approach
    """
    try:
        content = plan_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    result = {}

    # Extract Architecture Overview
    arch = extract_section(content, "Architecture Overview")
    if not arch:
        arch = extract_section(content, "Architecture")
    if arch:
        result["architecture_overview"] = arch

    # Extract Target State (subsection or section)
    target = extract_subsection(content, "Target State")
    if not target:
        target = extract_section(content, "Target State")
    if target:
        result["target_state"] = target

    # Extract Technical Approach
    approach = extract_section(content, "Technical Approach")
    if approach:
        result["technical_approach"] = approach

    return result


def extract_from_research(research_path: Path) -> dict[str, str]:
    """Extract key decisions from research.md.

    Args:
        research_path: Path to research.md file

    Returns:
        Dict with extracted sections: key_decisions
    """
    try:
        content = research_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    result = {}

    # Try different heading variations
    decisions = extract_section(content, "Summary of Decisions")
    if not decisions:
        decisions = extract_section(content, "Key Decisions")
    if not decisions:
        decisions = extract_section(content, "Decisions")

    if decisions:
        result["key_decisions"] = decisions

    return result


def extract_from_data_model(data_model_path: Path) -> dict[str, str]:
    """Extract core models from data-model.md.

    Args:
        data_model_path: Path to data-model.md file

    Returns:
        Dict with extracted sections: data_models
    """
    try:
        content = data_model_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    result = {}

    # Extract Core Models section
    models = extract_section(content, "Core Models")
    if not models:
        models = extract_section(content, "Models")

    if models:
        result["data_models"] = models

    return result


def read_spec_context(tasks_file: Path) -> SpecContext:
    """Read and extract context from spec folder files.

    This is the main entry point for reading spec context.
    It discovers available spec files, extracts relevant sections,
    and returns a populated SpecContext object.

    Args:
        tasks_file: Path to the tasks.md file

    Returns:
        SpecContext with extracted content (may be empty if no files found)
    """
    context = SpecContext()
    context.spec_folder = str(tasks_file.parent)

    # Discover available files
    files = discover_spec_files(tasks_file)
    context.files_found = [k for k, v in files.items() if v is not None]
    context.files_missing = [k for k, v in files.items() if v is None]

    # Extract from spec.md
    if files.get("spec.md"):
        try:
            sections = extract_from_spec(files["spec.md"])
            if "feature_overview" in sections:
                content, _ = truncate_content(
                    sections["feature_overview"],
                    MAX_LINES["feature_overview"]
                )
                context.feature_overview = content
            if "success_criteria" in sections:
                content, _ = truncate_content(
                    sections["success_criteria"],
                    MAX_LINES["success_criteria"]
                )
                context.success_criteria = content
        except Exception as e:
            context.extraction_warnings.append(f"spec.md: {e}")

    # Extract from plan.md
    if files.get("plan.md"):
        try:
            sections = extract_from_plan(files["plan.md"])
            if "architecture_overview" in sections:
                content, _ = truncate_content(
                    sections["architecture_overview"],
                    MAX_LINES["architecture_overview"]
                )
                context.architecture_overview = content
            if "target_state" in sections:
                content, _ = truncate_content(
                    sections["target_state"],
                    MAX_LINES["target_state"]
                )
                context.target_state = content
            if "technical_approach" in sections:
                content, _ = truncate_content(
                    sections["technical_approach"],
                    MAX_LINES["technical_approach"]
                )
                context.technical_approach = content
        except Exception as e:
            context.extraction_warnings.append(f"plan.md: {e}")

    # Extract from research.md
    if files.get("research.md"):
        try:
            sections = extract_from_research(files["research.md"])
            if "key_decisions" in sections:
                content, _ = truncate_content(
                    sections["key_decisions"],
                    MAX_LINES["key_decisions"]
                )
                context.key_decisions = content
        except Exception as e:
            context.extraction_warnings.append(f"research.md: {e}")

    # Extract from data-model.md
    if files.get("data-model.md"):
        try:
            sections = extract_from_data_model(files["data-model.md"])
            if "data_models" in sections:
                content, _ = truncate_content(
                    sections["data_models"],
                    MAX_LINES["data_models"]
                )
                context.data_models = content
        except Exception as e:
            context.extraction_warnings.append(f"data-model.md: {e}")

    return context
