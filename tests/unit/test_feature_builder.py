"""Unit tests for feature_builder module."""

import pytest

from speckit_to_issue.feature_builder import FeatureIssueBuilder, build_feature_issue
from speckit_to_issue.models import Priority, SpecContext, Task


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Create sample tasks for testing."""
    return [
        Task(
            id="T001",
            title="Create project structure",
            priority=Priority.MUST,
            estimate="10 min",
            phase="Phase 1: Setup",
            spec_name="003-help-faq-page",
            file_path="static/index.html",
            acceptance_criteria=["Create folder structure", "Add base files"],
        ),
        Task(
            id="T002",
            title="Add help button",
            priority=Priority.MUST,
            estimate="15 min",
            phase="Phase 1: Setup",
            spec_name="003-help-faq-page",
            file_path="static/index.html",
            acceptance_criteria=["Button displays in header", "Has correct ID"],
        ),
        Task(
            id="T003",
            title="Style the button",
            priority=Priority.SHOULD,
            estimate="20 min",
            phase="Phase 2: Styling",
            spec_name="003-help-faq-page",
            file_path="static/styles.css",
            acceptance_criteria=["Button styled correctly"],
        ),
    ]


@pytest.fixture
def sample_spec_context() -> SpecContext:
    """Create sample spec context for testing."""
    return SpecContext(
        feature_overview="A help page for the Weather App that provides FAQ.",
        success_criteria="- Users can navigate to help\n- FAQ sections work",
        architecture_overview="Single page app with view switching",
        target_state="```\nHeader + Help Button\nFAQ Accordion\n```",
        key_decisions="| Decision | Choice |\n|---|---|\n| View | SPA |",
    )


class TestFeatureIssueBuilder:
    """Tests for FeatureIssueBuilder class."""

    def test_format_title(self) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        assert builder._format_title() == "Feature: Help Faq Page"

    def test_format_title_simple(self) -> None:
        builder = FeatureIssueBuilder("001-weather")
        assert builder._format_title() == "Feature: Weather"

    def test_build_overview_section_with_context(
        self, sample_spec_context: SpecContext
    ) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_overview_section(sample_spec_context)

        assert "## Overview" in section
        assert "help page for the Weather App" in section
        assert "### Success Criteria" in section
        assert "Users can navigate to help" in section

    def test_build_overview_section_no_context(self) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_overview_section(None)

        assert "## Overview" in section
        assert "003-help-faq-page" in section

    def test_build_architecture_section(
        self, sample_spec_context: SpecContext
    ) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_architecture_section(sample_spec_context)

        assert "## Architecture" in section
        assert "### Target State" in section
        assert "### Key Decisions" in section

    def test_build_architecture_section_empty_context(self) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_architecture_section(SpecContext())

        assert section == ""

    def test_build_tasks_by_phase(self, sample_tasks: list[Task]) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_tasks_by_phase(sample_tasks)

        assert "## Implementation Tasks" in section
        assert "### Phase 1: Setup" in section
        assert "### Phase 2: Styling" in section
        assert "**T001**" in section
        assert "**T002**" in section
        assert "**T003**" in section
        assert "- [ ]" in section  # Checkboxes
        assert "(10 min)" in section

    def test_build_tasks_by_phase_with_completed(
        self, sample_tasks: list[Task]
    ) -> None:
        sample_tasks[0].is_complete = True
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_tasks_by_phase(sample_tasks)

        assert "- [x]" in section  # Completed checkbox

    def test_build_files_section(self, sample_tasks: list[Task]) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        section = builder._build_files_section(sample_tasks)

        assert "## Files to Modify" in section
        assert "`static/index.html`" in section
        assert "`static/styles.css`" in section

    def test_build_files_section_deduplication(self) -> None:
        tasks = [
            Task(id="T001", title="Task 1", priority=Priority.MUST, 
                 estimate="5 min", file_path="src/main.py"),
            Task(id="T002", title="Task 2", priority=Priority.MUST, 
                 estimate="5 min", file_path="src/main.py"),  # Duplicate
        ]
        builder = FeatureIssueBuilder("test")
        section = builder._build_files_section(tasks)

        # Should only appear once
        assert section.count("src/main.py") == 1

    def test_build_copilot_instructions(self) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page", copilot_mode=True)
        section = builder._build_copilot_instructions()

        assert "## Instructions for Copilot" in section
        assert "phases sequentially" in section
        assert "Single PR" in section

    def test_get_labels(self, sample_tasks: list[Task]) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page")
        labels = builder._get_labels(sample_tasks)

        assert "feature" in labels
        assert "speckit" in labels
        assert "spec:003-help-faq-page" in labels
        assert "priority:high" in labels  # Has MUST priority tasks

    def test_build_full_issue(
        self,
        sample_tasks: list[Task],
        sample_spec_context: SpecContext,
    ) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page", copilot_mode=True)
        issue = builder.build(sample_spec_context, sample_tasks)

        assert issue.title == "Feature: Help Faq Page"
        assert "## Overview" in issue.body
        assert "## Architecture" in issue.body
        assert "## Implementation Tasks" in issue.body
        assert "## Files to Modify" in issue.body
        assert "## Instructions for Copilot" in issue.body
        assert "feature" in issue.labels
        assert issue.assignee == "copilot"

    def test_build_without_copilot_mode(
        self,
        sample_tasks: list[Task],
        sample_spec_context: SpecContext,
    ) -> None:
        builder = FeatureIssueBuilder("003-help-faq-page", copilot_mode=False)
        issue = builder.build(sample_spec_context, sample_tasks)

        assert "Instructions for Copilot" not in issue.body
        assert issue.assignee is None


class TestBuildFeatureIssue:
    """Tests for build_feature_issue convenience function."""

    def test_build_feature_issue(
        self,
        sample_tasks: list[Task],
        sample_spec_context: SpecContext,
    ) -> None:
        issue = build_feature_issue(
            spec_name="003-help-faq-page",
            spec_context=sample_spec_context,
            tasks=sample_tasks,
            copilot_mode=True,
        )

        assert issue.title == "Feature: Help Faq Page"
        assert issue.assignee == "copilot"
        assert "feature" in issue.labels

    def test_build_feature_issue_without_context(
        self, sample_tasks: list[Task]
    ) -> None:
        issue = build_feature_issue(
            spec_name="003-help-faq-page",
            spec_context=None,
            tasks=sample_tasks,
            copilot_mode=False,
        )

        assert issue.title == "Feature: Help Faq Page"
        assert "## Overview" in issue.body
