"""Unit tests for github module."""

import json
from unittest.mock import MagicMock

import pytest

from speckit_to_issue.exceptions import (
    AuthenticationError,
    GitHubCLIError,
    IssueCreationError,
    RateLimitError,
)
from speckit_to_issue.github import (
    check_authenticated,
    check_gh_available,
    create_issue,
    find_existing_issue,
    list_issues,
)
from speckit_to_issue.models import ExistingIssue, Issue


class TestCheckGhAvailable:
    """Tests for check_gh_available function."""

    def test_available_when_installed(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(returncode=0)
        assert check_gh_available() is True

    def test_not_available_when_not_installed(self, mocker) -> None:
        mocker.patch("subprocess.run", side_effect=FileNotFoundError())
        assert check_gh_available() is False


class TestCheckAuthenticated:
    """Tests for check_authenticated function."""

    def test_authenticated(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(returncode=0)
        assert check_authenticated() is True

    def test_not_authenticated_raises(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(returncode=1, stderr="not logged in")
        with pytest.raises(AuthenticationError):
            check_authenticated()


class TestListIssues:
    """Tests for list_issues function."""

    def test_list_issues_success(self, mocker) -> None:
        issues_data = [
            {"number": 1, "title": "[T001] Task one", "state": "open", "url": "http://..."},
            {"number": 2, "title": "[T002] Task two", "state": "closed", "url": "http://..."},
        ]
        mocker.patch("subprocess.run", return_value=MagicMock(
            returncode=0,
            stdout=json.dumps(issues_data),
        ))

        issues = list_issues("owner/repo")

        assert len(issues) == 2
        assert issues[0].number == 1
        assert issues[0].title == "[T001] Task one"
        assert issues[1].state == "closed"

    def test_list_issues_empty_repo(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(returncode=0, stdout="[]")
        issues = list_issues("owner/repo")
        assert issues == []

    def test_list_issues_rate_limited(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(
            returncode=1,
            stderr="rate limit exceeded",
        )
        with pytest.raises(RateLimitError):
            list_issues("owner/repo")


class TestFindExistingIssue:
    """Tests for find_existing_issue function."""

    def test_find_existing(self) -> None:
        issues = [
            ExistingIssue(number=1, title="[T001] Create structure"),
            ExistingIssue(number=2, title="[T002] Add config"),
        ]
        result = find_existing_issue("T001", issues)
        assert result is not None
        assert result.number == 1

    def test_find_not_existing(self) -> None:
        issues = [
            ExistingIssue(number=1, title="[T001] Create structure"),
        ]
        result = find_existing_issue("T999", issues)
        assert result is None

    def test_find_empty_list(self) -> None:
        result = find_existing_issue("T001", [])
        assert result is None


class TestCreateIssue:
    """Tests for create_issue function."""

    def test_create_success(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo/issues/42\n",
            stderr="",
        )
        issue = Issue(
            title="[T001] Test task",
            body="Test body",
            labels=["task", "priority:high"],
        )
        url = create_issue(issue, "owner/repo")
        assert url == "https://github.com/owner/repo/issues/42"

    def test_create_with_labels(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo/issues/42\n",
            stderr="",
        )
        issue = Issue(
            title="[T001] Test",
            body="Body",
            labels=["task", "priority:high", "phase-1"],
        )
        create_issue(issue, "owner/repo")

        # Verify labels were passed
        call_args = mock_gh_cli.call_args[0][0]
        assert "--label" in call_args
        label_count = call_args.count("--label")
        assert label_count == 3

    def test_create_rate_limited(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(
            returncode=1,
            stderr="rate limit exceeded",
        )
        issue = Issue(title="Test", body="Body")
        with pytest.raises(RateLimitError):
            create_issue(issue, "owner/repo")

    def test_create_failure(self, mock_gh_cli: MagicMock) -> None:
        mock_gh_cli.return_value = MagicMock(
            returncode=1,
            stderr="Something went wrong",
        )
        issue = Issue(title="Test", body="Body")
        with pytest.raises(IssueCreationError):
            create_issue(issue, "owner/repo")
