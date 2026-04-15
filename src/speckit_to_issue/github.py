"""GitHub CLI wrapper for issue operations."""

import json
import os
import platform
import shutil
import subprocess
import tempfile
from typing import Optional

from .exceptions import (
    AuthenticationError,
    GitHubCLIError,
    IssueCreationError,
    RateLimitError,
    RepositoryError,
)
from .models import ExistingIssue, Issue

# Cached resolved path to gh executable
_gh_path: Optional[str] = None


def _resolve_gh() -> Optional[str]:
    """Resolve the full path to the gh CLI executable.

    Checks shutil.which first, then falls back to common installation
    directories (useful when the process PATH is incomplete, e.g. when
    spawned as an MCP server by VS Code).

    Returns:
        Absolute path to gh executable, or None if not found.
    """
    global _gh_path
    if _gh_path is not None:
        return _gh_path

    # 1. Standard PATH lookup
    found = shutil.which("gh")
    if found:
        _gh_path = found
        return _gh_path

    # 2. Check common install locations by platform
    candidates: list[str] = []
    system = platform.system()
    if system == "Windows":
        for pf in [
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
        ]:
            if pf:
                candidates.append(os.path.join(pf, "GitHub CLI", "gh.exe"))
        # Also check scoop / winget common locations
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            candidates.append(os.path.join(userprofile, "scoop", "shims", "gh.exe"))
    elif system == "Darwin":
        candidates = ["/opt/homebrew/bin/gh", "/usr/local/bin/gh"]
    else:  # Linux
        candidates = ["/usr/bin/gh", "/usr/local/bin/gh", "/snap/bin/gh"]

    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            _gh_path = candidate
            return _gh_path

    return None


def _gh() -> str:
    """Return the path to gh, raising if not found."""
    path = _resolve_gh()
    if path is None:
        raise GitHubCLIError(
            "GitHub CLI (gh) is not installed or not on PATH. "
            "Install from https://cli.github.com"
        )
    return path


def check_gh_available() -> bool:
    """Check if gh CLI is installed.

    Returns:
        True if gh command is available
    """
    try:
        result = subprocess.run(
            [_gh(), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, GitHubCLIError):
        return False
    except subprocess.TimeoutExpired:
        return False


def check_authenticated() -> bool:
    """Check if user is authenticated with GitHub.

    Returns:
        True if authenticated

    Raises:
        AuthenticationError: If not authenticated
    """
    try:
        result = subprocess.run(
            [_gh(), "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise AuthenticationError(
                "Not logged in to GitHub. Run 'gh auth login' to authenticate."
            )
        return True
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed. Install from https://cli.github.com")


def get_current_repo() -> str:
    """Get current repository (owner/repo).

    Returns:
        Repository name in owner/repo format

    Raises:
        RepositoryError: If not in a git repository or no remote
    """
    try:
        result = subprocess.run(
            [_gh(), "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RepositoryError(
                "Could not determine repository. "
                "Make sure you're in a git repository with a GitHub remote."
            )
        return result.stdout.strip()
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed.")


def list_issues(repo: Optional[str] = None, limit: int = 1000) -> list[ExistingIssue]:
    """List all issues in repository.

    Args:
        repo: Repository in owner/repo format (uses current if None)
        limit: Maximum number of issues to retrieve

    Returns:
        List of ExistingIssue objects
    """
    cmd = [
        _gh(), "issue", "list",
        "--json", "number,title,state,url",
        "--limit", str(limit),
        "--state", "all",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            if "rate limit" in result.stderr.lower():
                raise RateLimitError("GitHub API rate limit exceeded. Wait a few minutes.")
            return []

        issues_data = json.loads(result.stdout)
        return [
            ExistingIssue(
                number=issue["number"],
                title=issue["title"],
                state=issue.get("state", "open"),
                url=issue.get("url", ""),
            )
            for issue in issues_data
        ]
    except json.JSONDecodeError:
        return []
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed.")


def find_existing_issue(task_id: str, issues: list[ExistingIssue]) -> Optional[ExistingIssue]:
    """Find an existing issue matching a task ID.

    Args:
        task_id: Task ID (e.g., "T001")
        issues: List of existing issues

    Returns:
        Matching ExistingIssue or None
    """
    prefix = f"[{task_id}]"
    for issue in issues:
        if issue.title.startswith(prefix):
            return issue
    return None


def create_issue(issue: Issue, repo: Optional[str] = None) -> str:
    """Create a GitHub issue.

    Args:
        issue: Issue object to create
        repo: Repository in owner/repo format (uses current if None)

    Returns:
        URL of created issue

    Raises:
        IssueCreationError: If creation fails
    """
    # Check if we need to assign to Copilot (requires special API handling)
    assign_to_copilot = issue.assignee == "copilot"
    
    # Use --body-file with a temp file instead of --body to avoid hitting
    # the Windows CreateProcess command-line limit (~32,767 chars).
    # subprocess.run raises a misleading FileNotFoundError when exceeded.
    body_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    try:
        body_file.write(issue.body)
        body_file.close()

        cmd = [
            _gh(), "issue", "create",
            "--title", issue.title,
            "--body-file", body_file.name,
        ]

        for label in issue.labels:
            cmd.extend(["--label", label])

        # Only use --assignee for non-copilot assignees
        if issue.assignee and not assign_to_copilot:
            cmd.extend(["--assignee", issue.assignee])

        if issue.milestone:
            cmd.extend(["--milestone", issue.milestone])

        if repo:
            cmd.extend(["--repo", repo])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                stderr = result.stderr.lower()
                if "rate limit" in stderr:
                    raise RateLimitError("GitHub API rate limit exceeded.")
                if "not found" in stderr or "could not resolve" in stderr:
                    raise RepositoryError(f"Repository not found: {repo}")
                raise IssueCreationError(f"Failed to create issue: {result.stderr}")

            # Output is the issue URL
            issue_url = result.stdout.strip()
            
            # If we need to assign to Copilot, do it via REST API
            if assign_to_copilot and issue_url:
                _assign_issue_to_copilot(issue_url, repo)
            
            return issue_url
        except FileNotFoundError:
            raise GitHubCLIError("GitHub CLI (gh) is not installed.")
    finally:
        os.unlink(body_file.name)


def _assign_issue_to_copilot(issue_url: str, repo: Optional[str] = None) -> bool:
    """Assign an issue to Copilot coding agent via REST API.
    
    The standard gh issue --assignee doesn't work for Copilot.
    We need to use the REST API with copilot-swe-agent[bot].
    
    Args:
        issue_url: The URL of the issue (e.g., https://github.com/owner/repo/issues/123)
        repo: Repository in owner/repo format
        
    Returns:
        True if assignment succeeded
    """
    import re
    
    # Extract issue number from URL
    match = re.search(r'/issues/(\d+)$', issue_url)
    if not match:
        return False
    
    issue_number = match.group(1)
    
    # Determine repo from URL if not provided
    if not repo:
        repo_match = re.search(r'github\.com/([^/]+/[^/]+)/issues', issue_url)
        if repo_match:
            repo = repo_match.group(1)
        else:
            return False
    
    cmd = [
        _gh(), "api",
        "--method", "POST",
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2022-11-28",
        f"/repos/{repo}/issues/{issue_number}/assignees",
        "-f", "assignees[]=copilot-swe-agent[bot]",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ensure_label_exists(label: str, color: str, repo: Optional[str] = None) -> bool:
    """Ensure a label exists, creating it if necessary.

    Args:
        label: Label name
        color: Hex color code (without #)
        repo: Repository in owner/repo format

    Returns:
        True if label exists or was created
    """
    cmd = [_gh(), "label", "create", label, "--color", color, "--force"]
    if repo:
        cmd.extend(["--repo", repo])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
