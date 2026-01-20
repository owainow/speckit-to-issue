"""CLI entry point for speckit-to-issue."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .exceptions import (
    AuthenticationError,
    GitHubCLIError,
    ParseError,
    RateLimitError,
    RepositoryError,
)
from .feature_builder import build_feature_issue
from .github import (
    check_authenticated,
    check_gh_available,
    create_issue,
    find_existing_issue,
    get_current_repo,
    list_issues,
)
from .labels import ensure_labels, get_all_labels_for_tasks
from .mapper import task_to_issue
from .models import CreateResult, CreateSummary, SyncReport, SyncState, TaskResult, TaskSyncStatus
from .parser import parse_tasks_file
from .spec_reader import read_spec_context

app = typer.Typer(
    name="speckit-to-issue",
    help="Convert speckit tasks.md files to GitHub issues",
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"speckit-to-issue v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Convert speckit tasks.md files to GitHub issues."""
    pass


@app.command()
def create(
    tasks_file: Path = typer.Argument(
        ...,
        help="Path to tasks.md file",
        exists=True,
        readable=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Preview without creating issues",
    ),
    granular: bool = typer.Option(
        False,
        "--granular",
        "-g",
        help="Create individual issues per task (default: single feature issue)",
    ),
    skip_complete: bool = typer.Option(
        False,
        "--skip-complete",
        "-s",
        help="Skip tasks marked as complete (only with --granular)",
    ),
    assign_copilot: bool = typer.Option(
        False,
        "--assign-copilot",
        "-c",
        help="Format issues for Copilot Coding Agent and assign to Copilot",
    ),
    no_context: bool = typer.Option(
        False,
        "--no-context",
        help="Disable spec context injection",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Create issues even if they already exist",
    ),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Target repository (owner/repo format)",
    ),
    milestone: Optional[str] = typer.Option(
        None,
        "--milestone",
        "-m",
        help="Milestone to assign issues to",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Create GitHub issues from tasks.md file.
    
    By default, creates a single feature issue containing all tasks.
    Use --granular to create individual issues per task.
    """
    try:
        # Validate flag combinations
        if skip_complete and not granular:
            error_console.print(
                "[yellow]Warning:[/yellow] --skip-complete only applies with --granular"
            )

        # Read spec context
        spec_context = None
        if not no_context:
            spec_context = read_spec_context(tasks_file)
            if spec_context and not spec_context.is_empty():
                if verbose:
                    console.print("[dim]📚 Loaded spec context for issues[/dim]")
            else:
                spec_context = None
                if verbose:
                    console.print("[dim]No spec context found[/dim]")

        # Pre-flight checks (skip for dry-run)
        if not dry_run:
            if not check_gh_available():
                error_console.print(
                    "[red]Error:[/red] GitHub CLI (gh) is not installed.\n"
                    "Install from: https://cli.github.com"
                )
                raise typer.Exit(1)

            check_authenticated()

            if not repo:
                repo = get_current_repo()
                if verbose:
                    console.print(f"[dim]Using repository: {repo}[/dim]")

        # Parse tasks file
        console.print(f"\n📋 Parsing: [cyan]{tasks_file}[/cyan]")
        parse_result = parse_tasks_file(tasks_file)

        task_count = len(parse_result.tasks)
        complete_count = parse_result.complete_count
        incomplete_count = parse_result.incomplete_count

        console.print(
            f"   Found [bold]{task_count}[/bold] tasks "
            f"([green]{complete_count}[/green] complete, "
            f"[yellow]{incomplete_count}[/yellow] incomplete)"
        )

        if parse_result.errors:
            for err in parse_result.errors:
                error_console.print(f"[yellow]Warning:[/yellow] {err}")

        # Get existing issues (skip for dry-run)
        existing_issues = []
        if not dry_run and not force:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Fetching existing issues...", total=None)
                existing_issues = list_issues(repo)

        # Ensure labels exist
        if not dry_run:
            if granular:
                all_labels = get_all_labels_for_tasks(parse_result.tasks)
            else:
                # Feature-level labels
                all_labels = {"feature", "speckit", f"spec:{parse_result.spec_name}"}
                if any(t.priority.value == "must" for t in parse_result.tasks):
                    all_labels.add("priority:high")
                elif any(t.priority.value == "should" for t in parse_result.tasks):
                    all_labels.add("priority:medium")
            if verbose:
                console.print(f"[dim]Ensuring labels: {', '.join(sorted(all_labels))}[/dim]")
            ensure_labels(list(all_labels), repo)

        # Process based on mode
        if dry_run:
            console.print(f"\n🔍 [bold]Dry run[/bold] - no issues will be created\n")
        else:
            console.print(f"\n🚀 Creating issues in [bold]{repo}[/bold]\n")

        if granular:
            # GRANULAR MODE: One issue per task (original behavior)
            _create_granular_issues(
                parse_result=parse_result,
                spec_context=spec_context,
                existing_issues=existing_issues,
                assign_copilot=assign_copilot,
                skip_complete=skip_complete,
                force=force,
                dry_run=dry_run,
                repo=repo,
                milestone=milestone,
                verbose=verbose,
            )
        else:
            # FEATURE MODE: Single comprehensive issue (new default)
            _create_feature_issue(
                parse_result=parse_result,
                spec_context=spec_context,
                existing_issues=existing_issues,
                assign_copilot=assign_copilot,
                force=force,
                dry_run=dry_run,
                repo=repo,
                milestone=milestone,
                verbose=verbose,
            )

    except FileNotFoundError as e:
        error_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ParseError as e:
        error_console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(1)
    except AuthenticationError:
        error_console.print(
            "[red]Error:[/red] Not authenticated with GitHub.\n"
            "Run: [bold]gh auth login[/bold]"
        )
        raise typer.Exit(1)
    except RepositoryError as e:
        error_console.print(f"[red]Repository error:[/red] {e}")
        raise typer.Exit(1)
    except RateLimitError:
        error_console.print(
            "[red]Error:[/red] GitHub API rate limit exceeded.\n"
            "Wait a few minutes and try again."
        )
        raise typer.Exit(1)


def _create_feature_issue(
    parse_result,
    spec_context,
    existing_issues,
    assign_copilot: bool,
    force: bool,
    dry_run: bool,
    repo,
    milestone,
    verbose: bool,
) -> None:
    """Create a single feature-level issue containing all tasks."""
    # Check if feature issue already exists
    feature_title_prefix = f"Feature: "
    if not force:
        for existing in existing_issues:
            if existing.title.startswith(feature_title_prefix) and parse_result.spec_name in existing.title.lower().replace(" ", "-"):
                console.print(
                    f"   ⏭️  Feature issue already exists: "
                    f"[dim]#{existing.number}[/dim]"
                )
                console.print(f"      {existing.url}")
                return

    # Build the feature issue
    issue = build_feature_issue(
        spec_name=parse_result.spec_name,
        spec_context=spec_context,
        tasks=parse_result.tasks,
        copilot_mode=assign_copilot,
    )
    
    if milestone:
        issue.milestone = milestone

    if dry_run:
        console.print(f"   ✅ Would create: [bold]{issue.title}[/bold]")
        console.print(f"      Tasks: {len(parse_result.tasks)}")
        console.print(f"      Labels: {', '.join(issue.labels)}")
        if assign_copilot:
            console.print(f"      Assignee: copilot")
    else:
        try:
            url = create_issue(issue, repo)
            console.print(f"   ✅ Created: [bold]{issue.title}[/bold]")
            console.print(f"      {url}")
            if verbose:
                console.print(f"      Tasks: {len(parse_result.tasks)}")
        except GitHubCLIError as e:
            console.print(f"   ❌ Failed to create feature issue: [red]{e}[/red]")
            raise typer.Exit(1)

    # Summary
    console.print()
    table = Table(title="📊 Summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Feature Issue", "[green]1[/green]" if not dry_run else "[dim]1 (dry run)[/dim]")
    table.add_row("Tasks Included", str(len(parse_result.tasks)))
    table.add_row("Phases", str(len(parse_result.phases)))
    console.print(table)


def _create_granular_issues(
    parse_result,
    spec_context,
    existing_issues,
    assign_copilot: bool,
    skip_complete: bool,
    force: bool,
    dry_run: bool,
    repo,
    milestone,
    verbose: bool,
) -> None:
    """Create individual issues per task (original behavior)."""
    task_count = len(parse_result.tasks)
    summary = CreateSummary(
        total=task_count,
        created=0,
        skipped_exists=0,
        skipped_complete=0,
        failed=0,
        results=[],
    )

    for task in parse_result.tasks:
        # Skip complete tasks if requested
        if skip_complete and task.is_complete:
            console.print(f"   ⏭️  [{task.id}] {task.title} [dim](complete)[/dim]")
            summary.skipped_complete += 1
            summary.results.append(
                TaskResult(task=task, result=CreateResult.SKIPPED_COMPLETE)
            )
            continue

        # Check if issue already exists
        if not force:
            existing = find_existing_issue(task.id, existing_issues)
            if existing:
                console.print(
                    f"   ⏭️  [{task.id}] {task.title} "
                    f"[dim](exists: #{existing.number})[/dim]"
                )
                summary.skipped_exists += 1
                summary.results.append(
                    TaskResult(
                        task=task,
                        result=CreateResult.SKIPPED_EXISTS,
                        issue_url=existing.url,
                    )
                )
                continue

        # Create issue
        issue = task_to_issue(task, copilot_mode=assign_copilot, spec_context=spec_context)
        if milestone:
            issue.milestone = milestone

        if dry_run:
            console.print(f"   ✅ [{task.id}] {task.title} [dim](would create)[/dim]")
            summary.created += 1
            summary.results.append(TaskResult(task=task, result=CreateResult.CREATED))
        else:
            try:
                url = create_issue(issue, repo)
                console.print(f"   ✅ [{task.id}] {task.title}")
                if verbose:
                    console.print(f"      [dim]{url}[/dim]")
                summary.created += 1
                summary.results.append(
                    TaskResult(task=task, result=CreateResult.CREATED, issue_url=url)
                )
            except GitHubCLIError as e:
                console.print(f"   ❌ [{task.id}] {task.title} [red]({e})[/red]")
                summary.failed += 1
                summary.results.append(
                    TaskResult(task=task, result=CreateResult.FAILED, error=str(e))
                )

    # Summary
    console.print()
    table = Table(title="📊 Summary")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")

    table.add_row("Created", f"[green]{summary.created}[/green]")
    table.add_row("Skipped (exists)", f"[yellow]{summary.skipped_exists}[/yellow]")
    table.add_row("Skipped (complete)", f"[dim]{summary.skipped_complete}[/dim]")
    table.add_row("Failed", f"[red]{summary.failed}[/red]")

    console.print(table)


@app.command()
def status(
    tasks_file: Path = typer.Argument(
        ...,
        help="Path to tasks.md file",
        exists=True,
        readable=True,
    ),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Target repository (owner/repo format)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Show sync status between tasks and GitHub issues."""
    try:
        # Pre-flight checks
        if not check_gh_available():
            error_console.print(
                "[red]Error:[/red] GitHub CLI (gh) is not installed.\n"
                "Install from: https://cli.github.com"
            )
            raise typer.Exit(1)

        check_authenticated()

        if not repo:
            repo = get_current_repo()

        # Parse tasks
        console.print(f"\n📋 Checking: [cyan]{tasks_file}[/cyan]")
        parse_result = parse_tasks_file(tasks_file)

        # Fetch issues
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Fetching issues from {repo}...", total=None)
            existing_issues = list_issues(repo)

        # Build sync report
        report = SyncReport(
            total_tasks=len(parse_result.tasks),
            synced=0,
            missing=0,
            closed=0,
            complete=0,
        )

        for task in parse_result.tasks:
            existing = find_existing_issue(task.id, existing_issues)

            if task.is_complete:
                state = SyncState.COMPLETE
                report.complete += 1
            elif existing is None:
                state = SyncState.MISSING
                report.missing += 1
            elif existing.state == "closed":
                state = SyncState.CLOSED
                report.closed += 1
            else:
                state = SyncState.SYNCED
                report.synced += 1

            report.statuses.append(
                TaskSyncStatus(
                    task=task,
                    state=state,
                    issue_number=existing.number if existing else None,
                    issue_url=existing.url if existing else None,
                )
            )

        # Display table
        console.print()
        table = Table(title=f"📋 Sync Status: {repo}")
        table.add_column("Task", style="cyan", width=8)
        table.add_column("Title", max_width=40)
        table.add_column("Status", width=12)
        table.add_column("Issue", width=8)

        state_icons = {
            SyncState.SYNCED: "[green]✅ Synced[/green]",
            SyncState.MISSING: "[red]❌ Missing[/red]",
            SyncState.CLOSED: "[blue]📦 Closed[/blue]",
            SyncState.COMPLETE: "[dim]✓ Done[/dim]",
        }

        for status in report.statuses:
            issue_col = f"#{status.issue_number}" if status.issue_number else ""
            table.add_row(
                status.task.id,
                status.task.title[:40],
                state_icons[status.state],
                issue_col,
            )

        console.print(table)

        # Summary
        console.print()
        summary = Table(title="Summary")
        summary.add_column("State", style="bold")
        summary.add_column("Count", justify="right")

        summary.add_row("Synced", f"[green]{report.synced}[/green]")
        summary.add_row("Missing", f"[red]{report.missing}[/red]")
        summary.add_row("Closed", f"[blue]{report.closed}[/blue]")
        summary.add_row("Complete", f"[dim]{report.complete}[/dim]")
        summary.add_row("Total", f"[bold]{report.total_tasks}[/bold]")

        console.print(summary)

    except FileNotFoundError as e:
        error_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ParseError as e:
        error_console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(1)
    except AuthenticationError:
        error_console.print(
            "[red]Error:[/red] Not authenticated with GitHub.\n"
            "Run: [bold]gh auth login[/bold]"
        )
        raise typer.Exit(1)
    except RepositoryError as e:
        error_console.print(f"[red]Repository error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"speckit-to-issue v{__version__}")


if __name__ == "__main__":
    app()
