"""Integration tests for CLI module."""

from pathlib import Path

from typer.testing import CliRunner

from speckit_to_issue.cli import app

runner = CliRunner()


class TestVersionCommand:
    """Tests for version command."""

    def test_version_command(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "speckit-to-issue" in result.stdout
        assert "0.1.0" in result.stdout

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout


class TestCreateCommand:
    """Tests for create command."""

    def test_create_dry_run(self, sample_tasks_md: Path) -> None:
        result = runner.invoke(app, ["create", str(sample_tasks_md), "--dry-run"])

        assert result.exit_code == 0
        assert "Parsing" in result.stdout
        assert "Dry run" in result.stdout
        assert "T001" in result.stdout
        assert "Summary" in result.stdout

    def test_create_dry_run_skip_complete(self, sample_tasks_md: Path) -> None:
        result = runner.invoke(
            app,
            ["create", str(sample_tasks_md), "--dry-run", "--skip-complete"],
        )

        assert result.exit_code == 0
        assert "(complete)" in result.stdout or "skipped" in result.stdout.lower()

    def test_create_file_not_found(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "nonexistent.md"
        result = runner.invoke(app, ["create", str(nonexistent), "--dry-run"])

        # Typer validates file exists before our code runs
        assert result.exit_code != 0

    def test_create_verbose(self, sample_tasks_md: Path) -> None:
        result = runner.invoke(
            app,
            ["create", str(sample_tasks_md), "--dry-run", "--verbose"],
        )

        assert result.exit_code == 0


class TestStatusCommand:
    """Tests for status command with mocked gh."""

    def test_status_file_not_found(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "nonexistent.md"
        result = runner.invoke(app, ["status", str(nonexistent)])

        assert result.exit_code != 0


class TestHelpOutput:
    """Tests for help output."""

    def test_main_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "create" in result.stdout
        assert "status" in result.stdout

    def test_create_help(self) -> None:
        result = runner.invoke(app, ["create", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.stdout
        assert "--skip-complete" in result.stdout
        assert "--assign-copilot" in result.stdout

    def test_status_help(self) -> None:
        result = runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0
        assert "--repo" in result.stdout
