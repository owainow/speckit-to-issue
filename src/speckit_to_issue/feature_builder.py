"""Feature-level issue builder for speckit-to-issue.

This module builds a single comprehensive GitHub issue from an entire
feature specification, including overview, architecture, and all tasks.
"""

import re
from collections import defaultdict
from typing import Optional

from .models import Issue, SpecContext, Task


class FeatureIssueBuilder:
    """Builds a single comprehensive issue from a full spec.
    
    This creates a feature-level issue that contains all the context
    needed for an AI coding agent (like GitHub Copilot) to implement
    the entire feature systematically.
    """

    def __init__(self, spec_name: str, copilot_mode: bool = False):
        """Initialize the builder.
        
        Args:
            spec_name: Name of the spec (e.g., "003-help-faq-page")
            copilot_mode: If True, include Copilot-specific instructions
        """
        self.spec_name = spec_name
        self.copilot_mode = copilot_mode

    def build(
        self,
        spec_context: Optional[SpecContext],
        tasks: list[Task],
    ) -> Issue:
        """Build a feature-level issue from spec context and tasks.
        
        Args:
            spec_context: Extracted context from spec files (may be None)
            tasks: List of all tasks for this feature
            
        Returns:
            Issue object ready for creation
        """
        sections = []
        
        # Title from spec name
        title = self._format_title()
        
        # Build each section
        sections.append(self._build_overview_section(spec_context))
        
        arch_section = self._build_architecture_section(spec_context)
        if arch_section:
            sections.append(arch_section)
        
        sections.append(self._build_tasks_by_phase(tasks))
        
        files_section = self._build_files_section(tasks)
        if files_section:
            sections.append(files_section)
        
        if self.copilot_mode:
            sections.append(self._build_copilot_instructions())
        
        sections.append(self._build_footer())
        
        body = "\n\n".join(filter(None, sections))
        
        return Issue(
            title=title,
            body=body,
            labels=self._get_labels(tasks),
            assignee="copilot" if self.copilot_mode else None,
        )

    def _format_title(self) -> str:
        """Format the issue title from spec name.
        
        Converts "003-help-faq-page" to "Feature: Help FAQ Page"
        """
        # Remove leading number and dashes
        name = re.sub(r"^\d+-", "", self.spec_name)
        # Convert dashes to spaces and title case
        name = name.replace("-", " ").title()
        return f"Feature: {name}"

    def _build_overview_section(self, spec_context: Optional[SpecContext]) -> str:
        """Build the overview section from spec.md content.
        
        Args:
            spec_context: Extracted spec context
            
        Returns:
            Formatted overview section
        """
        lines = ["## Overview"]
        
        if spec_context and spec_context.feature_overview:
            lines.append("")
            lines.append(spec_context.feature_overview)
        else:
            lines.append("")
            lines.append(f"Implementation of the {self.spec_name} feature.")
        
        if spec_context and spec_context.success_criteria:
            lines.append("")
            lines.append("### Success Criteria")
            lines.append("")
            lines.append(spec_context.success_criteria)
        
        return "\n".join(lines)

    def _build_architecture_section(self, spec_context: Optional[SpecContext]) -> str:
        """Build the architecture section from plan.md/architecture.md content.
        
        Args:
            spec_context: Extracted spec context
            
        Returns:
            Formatted architecture section, or empty string if no content
        """
        if not spec_context:
            return ""
        
        has_content = any([
            spec_context.architecture_overview,
            spec_context.target_state,
            spec_context.key_decisions,
        ])
        
        if not has_content:
            return ""
        
        lines = ["## Architecture"]
        
        if spec_context.target_state:
            lines.append("")
            lines.append("### Target State")
            lines.append("")
            lines.append(spec_context.target_state)
        
        if spec_context.key_decisions:
            lines.append("")
            lines.append("### Key Decisions")
            lines.append("")
            lines.append(spec_context.key_decisions)
        
        if spec_context.architecture_overview and not spec_context.target_state:
            # Only include if we don't have target_state (avoid duplication)
            lines.append("")
            lines.append(spec_context.architecture_overview)
        
        return "\n".join(lines)

    def _build_tasks_by_phase(self, tasks: list[Task]) -> str:
        """Build the tasks section organized by phase.
        
        Each task includes checkbox, ID, title, estimate, and nested
        acceptance criteria.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            Formatted tasks section
        """
        lines = ["## Implementation Tasks"]
        
        # Group tasks by phase
        phases: dict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            phase = task.phase if task.phase else "Ungrouped"
            phases[phase].append(task)
        
        # Sort phases (Phase 1 before Phase 2, etc.)
        def phase_sort_key(phase_name: str) -> tuple[int, str]:
            match = re.search(r"Phase (\d+)", phase_name)
            if match:
                return (int(match.group(1)), phase_name)
            return (999, phase_name)  # Ungrouped goes last
        
        sorted_phases = sorted(phases.keys(), key=phase_sort_key)
        
        for phase in sorted_phases:
            phase_tasks = phases[phase]
            lines.append("")
            lines.append(f"### {phase}")
            lines.append("")
            
            for task in phase_tasks:
                # Task line with checkbox
                checkbox = "x" if task.is_complete else " "
                estimate = f" ({task.estimate})" if task.estimate else ""
                lines.append(f"- [{checkbox}] **{task.id}**: {task.title}{estimate}")
                
                # Nested acceptance criteria
                if task.acceptance_criteria:
                    for criterion in task.acceptance_criteria:
                        # Remove any existing checkbox from criterion
                        criterion_text = re.sub(r"^\[[ x]\]\s*", "", criterion)
                        lines.append(f"  - {criterion_text}")
                
                # File path if present
                if task.file_path:
                    lines.append(f"  - 📁 `{task.file_path}`")
        
        return "\n".join(lines)

    def _build_files_section(self, tasks: list[Task]) -> str:
        """Build the files to modify section.
        
        Collects all unique file paths from tasks.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            Formatted files section, or empty string if no files
        """
        # Collect unique file paths
        files = set()
        for task in tasks:
            if task.file_path:
                # Handle comma-separated files
                for f in task.file_path.split(","):
                    f = f.strip()
                    if f:
                        files.add(f)
        
        if not files:
            return ""
        
        lines = ["## Files to Modify"]
        lines.append("")
        
        # Sort files for consistent output
        for filepath in sorted(files):
            lines.append(f"- `{filepath}`")
        
        return "\n".join(lines)

    def _build_copilot_instructions(self) -> str:
        """Build the Copilot-specific instructions section.
        
        Returns:
            Formatted instructions for Copilot agent
        """
        return """## Instructions for Copilot

Implement this feature by completing the tasks in order by phase.

1. **Work through phases sequentially** - Complete all tasks in Phase 1 before moving to Phase 2
2. **Check off tasks** - Mark each task complete as you finish it
3. **Follow existing patterns** - Match the code style and patterns in the repository
4. **Test your changes** - Add appropriate tests if applicable
5. **Single PR** - Create one pull request with all changes when complete

Use the architecture section above for guidance on structure and key decisions."""

    def _build_footer(self) -> str:
        """Build the issue footer."""
        return "---\n*Generated by [speckit-to-issue](https://github.com/speckit/speckit-to-issue)*"

    def _get_labels(self, tasks: list[Task]) -> list[str]:
        """Get labels for the feature issue.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            List of label strings
        """
        labels = ["feature", "speckit"]
        
        # Add spec label
        if self.spec_name:
            labels.append(f"spec:{self.spec_name}")
        
        # Add priority based on highest priority task
        priorities = [t.priority.value for t in tasks]
        if "must" in priorities:
            labels.append("priority:high")
        elif "should" in priorities:
            labels.append("priority:medium")
        elif "could" in priorities:
            labels.append("priority:low")
        
        return labels


def build_feature_issue(
    spec_name: str,
    spec_context: Optional[SpecContext],
    tasks: list[Task],
    copilot_mode: bool = False,
) -> Issue:
    """Convenience function to build a feature issue.
    
    Args:
        spec_name: Name of the spec (e.g., "003-help-faq-page")
        spec_context: Extracted context from spec files
        tasks: List of all tasks
        copilot_mode: If True, include Copilot instructions and assign
        
    Returns:
        Issue object ready for creation
    """
    builder = FeatureIssueBuilder(spec_name, copilot_mode=copilot_mode)
    return builder.build(spec_context, tasks)
