"""Custom exceptions for speckit-to-issue."""


class SpeckitToIssueError(Exception):
    """Base exception for speckit-to-issue."""

    pass


class ParseError(SpeckitToIssueError):
    """Error parsing tasks.md file."""

    pass


class GitHubCLIError(SpeckitToIssueError):
    """Error from GitHub CLI."""

    pass


class AuthenticationError(GitHubCLIError):
    """Not authenticated with GitHub.

    Run 'gh auth login' to authenticate.
    """

    pass


class RepositoryError(GitHubCLIError):
    """Repository not found or no access."""

    pass


class RateLimitError(GitHubCLIError):
    """GitHub API rate limited."""

    pass


class IssueCreationError(GitHubCLIError):
    """Failed to create issue."""

    pass
