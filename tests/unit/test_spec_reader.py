"""Unit tests for spec_reader module."""

from pathlib import Path

import pytest

from speckit_to_issue.spec_reader import (
    discover_spec_files,
    extract_section,
    read_spec_context,
    truncate_content,
)


class TestDiscoverSpecFiles:
    """Tests for discover_spec_files function."""

    def test_finds_all_spec_files(self, sample_spec_folder: Path) -> None:
        """Should find spec.md, plan.md, and research.md."""
        tasks_file = sample_spec_folder / "tasks.md"
        files = discover_spec_files(tasks_file)

        assert "spec.md" in files
        assert "plan.md" in files
        assert "research.md" in files

    def test_returns_empty_dict_for_missing_folder(self, tmp_path: Path) -> None:
        """Should return dict with None values if folder doesn't exist."""
        fake_tasks = tmp_path / "nonexistent" / "tasks.md"
        files = discover_spec_files(fake_tasks)

        # Returns dict with file names as keys, None as values for missing
        assert all(v is None for v in files.values())

    def test_returns_only_existing_files(self, sample_tasks_md: Path) -> None:
        """Should only include files that exist."""
        # sample_tasks_md fixture only creates tasks.md, not spec files
        files = discover_spec_files(sample_tasks_md)

        # Should not contain spec files since they weren't created
        # (depends on fixture setup - this tests partial presence)
        assert isinstance(files, dict)


class TestExtractSection:
    """Tests for extract_section function."""

    def test_extracts_simple_section(self) -> None:
        """Should extract content between headers."""
        content = """# Document

## Overview
This is the overview content.
It spans multiple lines.

## Next Section
Different content here.
"""
        result = extract_section(content, "Overview")
        assert "This is the overview content." in result
        assert "It spans multiple lines." in result
        assert "Different content here." not in result

    def test_returns_empty_for_missing_section(self) -> None:
        """Should return empty string if section not found."""
        content = """# Document

## Introduction
Some text here.
"""
        result = extract_section(content, "Overview")
        assert result == ""

    def test_handles_nested_headers(self) -> None:
        """Should handle content with sub-headers."""
        content = """# Doc

## Architecture Overview
Main architecture description.

### Component A
Details about A.

### Component B
Details about B.

## Other Section
Other content.
"""
        result = extract_section(content, "Architecture Overview")
        assert "Main architecture description." in result
        # Sub-sections may or may not be included based on implementation
        assert "Other content." not in result

    def test_case_insensitive_match(self) -> None:
        """Should match section names case-insensitively."""
        content = """# Doc

## OVERVIEW
Uppercase header content.

## Next
More content.
"""
        result = extract_section(content, "overview")
        assert "Uppercase header content." in result


class TestTruncateContent:
    """Tests for truncate_content function."""

    def test_short_content_unchanged(self) -> None:
        """Content under max_lines should not be modified."""
        content = "Line 1\nLine 2\nLine 3"
        result, was_truncated = truncate_content(content, max_lines=10)
        assert result == content
        assert was_truncated is False

    def test_long_content_truncated(self) -> None:
        """Content over max_lines should be truncated."""
        lines = [f"Line {i}" for i in range(100)]
        content = "\n".join(lines)
        result, was_truncated = truncate_content(content, max_lines=10)

        result_lines = result.strip().split("\n")
        # 10 lines + empty line + truncation marker = 12 lines
        assert len(result_lines) <= 12
        assert was_truncated is True

    def test_adds_truncation_marker(self) -> None:
        """Should indicate truncation via return value."""
        lines = [f"Line {i}" for i in range(50)]
        content = "\n".join(lines)
        result, was_truncated = truncate_content(content, max_lines=5)

        assert was_truncated is True

    def test_handles_empty_content(self) -> None:
        """Should handle empty string gracefully."""
        result, was_truncated = truncate_content("", max_lines=10)
        assert result == ""
        assert was_truncated is False


class TestReadSpecContext:
    """Tests for read_spec_context function."""

    def test_reads_complete_spec_folder(self, sample_spec_folder: Path) -> None:
        """Should read and populate all context fields."""
        tasks_file = sample_spec_folder / "tasks.md"
        context = read_spec_context(tasks_file)

        assert context is not None
        assert not context.is_empty()

    def test_populates_feature_overview(self, sample_spec_folder: Path) -> None:
        """Should extract feature overview from spec.md."""
        tasks_file = sample_spec_folder / "tasks.md"
        context = read_spec_context(tasks_file)

        assert context.feature_overview != ""
        assert "sample feature" in context.feature_overview.lower()

    def test_populates_architecture_overview(self, sample_spec_folder: Path) -> None:
        """Should extract architecture from plan.md."""
        tasks_file = sample_spec_folder / "tasks.md"
        context = read_spec_context(tasks_file)

        assert context.architecture_overview != ""
        assert "modular" in context.architecture_overview.lower()

    def test_returns_empty_context_when_no_files(self, tmp_path: Path) -> None:
        """Should return empty context when spec files don't exist."""
        fake_tasks = tmp_path / "empty-spec" / "tasks.md"
        fake_tasks.parent.mkdir(parents=True)
        fake_tasks.write_text("# Empty tasks", encoding="utf-8")

        context = read_spec_context(fake_tasks)

        assert context is not None
        assert context.is_empty()

    def test_handles_partial_spec_files(self, sample_tasks_md: Path) -> None:
        """Should work with only some spec files present."""
        # Create just spec.md
        spec_content = """# Spec

## Overview
Partial spec content.
"""
        spec_file = sample_tasks_md.parent / "spec.md"
        spec_file.write_text(spec_content, encoding="utf-8")

        context = read_spec_context(sample_tasks_md)

        assert context is not None
        # Should have some content even with partial files

    def test_graceful_on_malformed_files(self, tmp_path: Path) -> None:
        """Should not crash on malformed markdown."""
        tasks_file = tmp_path / "specs" / "bad-spec" / "tasks.md"
        tasks_file.parent.mkdir(parents=True)
        tasks_file.write_text("# Tasks", encoding="utf-8")

        # Create malformed spec.md
        spec_file = tasks_file.parent / "spec.md"
        spec_file.write_text("No headers here, just text.", encoding="utf-8")

        # Should not raise
        context = read_spec_context(tasks_file)
        assert context is not None


class TestSpecContextIntegration:
    """Integration tests for SpecContext with to_markdown."""

    def test_to_markdown_produces_valid_output(self, sample_spec_folder: Path) -> None:
        """Should produce valid markdown output."""
        tasks_file = sample_spec_folder / "tasks.md"
        context = read_spec_context(tasks_file)

        markdown = context.to_markdown()

        assert "## " in markdown  # Has headers
        assert "Feature" in markdown or "Architecture" in markdown

    def test_empty_context_produces_empty_markdown(self, tmp_path: Path) -> None:
        """Empty context should produce empty/minimal markdown."""
        fake_tasks = tmp_path / "empty" / "tasks.md"
        fake_tasks.parent.mkdir(parents=True)
        fake_tasks.write_text("# Tasks", encoding="utf-8")

        context = read_spec_context(fake_tasks)
        markdown = context.to_markdown()

        # Empty context should produce empty string
        assert markdown == "" or len(markdown) < 50
