"""MCP server for speckit-to-issue.

Exposes tools for creating GitHub issues from speckit specification folders.
Run with: python -m speckit_to_issue.mcp_server
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "speckit-to-issue",
    instructions=(
        "Convert speckit specification folders into comprehensive GitHub issues. "
        "Point to a spec folder containing tasks.md, spec.md, plan.md, etc. "
        "The tool reads all spec files and creates a verbose feature issue "
        "with full specification context."
    ),
)


@mcp.tool()
def create_feature_issue(
    spec_folder: str,
    repo: str = "",
    assign_copilot: bool = True,
    dry_run: bool = False,
) -> str:
    """Create a comprehensive GitHub issue from a speckit specification folder.

    Reads all spec files (spec.md, plan.md, tasks.md, research.md,
    data-model.md, quickstart.md) and the project constitution, then
    creates a detailed GitHub issue containing the full specification
    context organized with collapsible sections.

    Args:
        spec_folder: Absolute path to the spec folder containing tasks.md
                     and other spec files (spec.md, plan.md, etc.)
        repo: GitHub repository in owner/repo format. Leave empty to
              auto-detect from the current git repository.
        assign_copilot: Whether to assign the issue to GitHub Copilot
                        coding agent (default: True)
        dry_run: If True, return a preview of the issue without
                 actually creating it on GitHub.

    Returns:
        The URL of the created issue, or a formatted preview if dry_run.
    """
    from .exceptions import AuthenticationError, GitHubCLIError, RepositoryError
    from .feature_builder import build_feature_issue
    from .github import (
        check_authenticated,
        check_gh_available,
        create_issue,
        get_current_repo,
    )
    from .labels import ensure_labels
    from .parser import parse_tasks_file
    from .spec_reader import read_spec_context

    folder = Path(spec_folder)
    tasks_file = folder / "tasks.md"

    if not tasks_file.exists():
        return f"Error: tasks.md not found in {spec_folder}"

    # Parse tasks
    try:
        parse_result = parse_tasks_file(tasks_file)
    except Exception as e:
        return f"Error parsing tasks.md: {e}"

    # Read full spec context
    spec_context = read_spec_context(tasks_file)

    # Build the issue
    issue = build_feature_issue(
        spec_name=parse_result.spec_name,
        spec_context=spec_context,
        tasks=parse_result.tasks,
        copilot_mode=assign_copilot,
        feature_title=parse_result.feature_title,
    )

    if dry_run:
        lines = [
            "# Issue Preview\n",
            f"**Title:** {issue.title}",
            f"**Labels:** {', '.join(issue.labels)}",
            f"**Assignee:** {issue.assignee or 'None'}",
            f"**Tasks:** {len(parse_result.tasks)}",
            f"**Phases:** {len(parse_result.phases)}",
            f"**Spec files loaded:** {', '.join(spec_context.files_found)}",
            "",
            "---",
            "",
            issue.body,
        ]
        return "\n".join(lines)

    # Pre-flight checks
    if not check_gh_available():
        return (
            "Error: GitHub CLI (gh) is not installed. "
            "Install from https://cli.github.com"
        )

    try:
        check_authenticated()
    except AuthenticationError:
        return "Error: Not authenticated with GitHub. Run 'gh auth login'."

    if not repo:
        try:
            repo = get_current_repo()
        except RepositoryError as e:
            return f"Error: {e}"

    # Ensure labels exist
    try:
        ensure_labels(list(set(issue.labels)), repo)
    except GitHubCLIError:
        pass  # Non-fatal: labels may already exist

    # Create the issue
    try:
        url = create_issue(issue, repo)
        return (
            f"Issue created successfully!\n\n"
            f"**URL:** {url}\n"
            f"**Title:** {issue.title}\n"
            f"**Tasks:** {len(parse_result.tasks)}\n"
            f"**Labels:** {', '.join(issue.labels)}"
        )
    except GitHubCLIError as e:
        return f"Error creating issue: {e}"


@mcp.tool()
def preview_feature_issue(
    spec_folder: str,
    assign_copilot: bool = True,
) -> str:
    """Preview a GitHub issue that would be created from a speckit spec folder.

    This is a read-only operation that does NOT create any issue.
    Use this to review the issue content before creating it.

    Args:
        spec_folder: Absolute path to the spec folder containing tasks.md
        assign_copilot: Whether Copilot-specific instructions would be included

    Returns:
        A formatted preview of the issue title, labels, and body.
    """
    return create_feature_issue(
        spec_folder=spec_folder,
        assign_copilot=assign_copilot,
        dry_run=True,
    )


@mcp.tool()
def list_spec_folders(
    workspace_path: str,
) -> str:
    """Discover speckit specification folders in a workspace.

    Searches for directories containing a tasks.md file, which indicates
    a speckit spec folder.

    Args:
        workspace_path: Absolute path to the workspace root to search

    Returns:
        A list of discovered spec folders with their available files.
    """
    root = Path(workspace_path)
    if not root.exists():
        return f"Error: Path does not exist: {workspace_path}"

    found: list[str] = []
    spec_files = {"spec.md", "plan.md", "tasks.md", "research.md", "data-model.md", "quickstart.md"}

    for tasks_file in root.rglob("tasks.md"):
        folder = tasks_file.parent
        # Skip node_modules, .git, etc.
        if any(part.startswith(".") or part == "node_modules" for part in folder.parts):
            continue

        available = [f for f in spec_files if (folder / f).exists()]
        found.append(f"- **{folder}**\n  Files: {', '.join(sorted(available))}")

    if not found:
        return "No spec folders found (no tasks.md files discovered)."

    return f"## Spec Folders Found ({len(found)})\n\n" + "\n\n".join(found)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
