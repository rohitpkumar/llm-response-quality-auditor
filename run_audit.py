# run_audit.py
# Main entry point for the LLM Response Quality Auditor.
# Loads test cases from test_cases/sample_inputs.json, evaluates
# each one using the Claude API, prints a rich summary, and saves
# a markdown report to /reports for every test case.

import json
import os
import sys

from rich.console import Console
from rich.rule import Rule

from auditor.evaluator import evaluate
from auditor.report_generator import print_summary, save_report

console = Console()

SAMPLE_INPUTS = os.path.join(os.path.dirname(__file__), "test_cases", "sample_inputs.json")


def load_test_cases(path: str) -> list[dict]:
    """Load and return test cases from a JSON file."""
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Test cases file not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        try:
            cases = json.load(f)
        except json.JSONDecodeError as e:
            console.print(f"[bold red]Error:[/bold red] Failed to parse {path}: {e}")
            sys.exit(1)

    if not cases:
        console.print("[yellow]Warning:[/yellow] No test cases found in sample_inputs.json")
        sys.exit(0)

    return cases


def run() -> None:
    console.print()
    console.print(Rule("[bold cyan]LLM Response Quality Auditor[/bold cyan]"))

    test_cases = load_test_cases(SAMPLE_INPUTS)
    total = len(test_cases)
    console.print(f"[dim]Loaded {total} test case(s) from {SAMPLE_INPUTS}[/dim]\n")

    results_summary = []

    for i, test_case in enumerate(test_cases, start=1):
        tc_id = test_case.get("id", f"TC{i:03d}")
        category = test_case.get("category", "unknown")

        console.print(Rule(f"[bold]{i}/{total}  {tc_id}[/bold]  [dim]{category}[/dim]"))

        try:
            result = evaluate(
                prompt=test_case["prompt"],
                response=test_case["response"],
            )
        except EnvironmentError as e:
            console.print(f"[bold red]Configuration error:[/bold red] {e}")
            sys.exit(1)
        except ValueError as e:
            console.print(f"[bold red]Evaluation error for {tc_id}:[/bold red] {e}")
            results_summary.append({"id": tc_id, "verdict": "ERROR", "report": None})
            continue
        except Exception as e:
            console.print(f"[bold red]Unexpected error for {tc_id}:[/bold red] {e}")
            results_summary.append({"id": tc_id, "verdict": "ERROR", "report": None})
            continue

        # Print rich terminal summary
        print_summary(test_case, result)

        # Save markdown report
        try:
            report_path = save_report(test_case, result)
            console.print(f"[dim]Report saved → {report_path}[/dim]\n")
        except OSError as e:
            console.print(f"[yellow]Warning:[/yellow] Could not save report for {tc_id}: {e}\n")
            report_path = None

        results_summary.append({
            "id": tc_id,
            "verdict": result["verdict"],
            "average": result["average_score"],
            "expected": test_case.get("expected_verdict"),
            "report": report_path,
        })

    # Final summary table
    console.print(Rule("[bold cyan]Audit Complete[/bold cyan]"))
    _print_final_summary(results_summary)


def _print_final_summary(results: list[dict]) -> None:
    """Print a one-line result per test case and overall pass rate."""
    from rich.table import Table
    from rich import box

    verdict_styles = {
        "PASS":         "green",
        "NEEDS REVIEW": "yellow",
        "FAIL":         "red",
        "ERROR":        "bright_red",
    }

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("Verdict", justify="center")
    table.add_column("Score", justify="center")
    table.add_column("Expected", justify="center")
    table.add_column("Match", justify="center")

    passed = 0
    for r in results:
        verdict = r.get("verdict", "ERROR")
        expected = r.get("expected", "")
        average = r.get("average")
        style = verdict_styles.get(verdict, "white")

        match = ""
        if expected and verdict != "ERROR":
            if verdict == expected:
                match = "[green]✓[/green]"
                passed += 1
            else:
                match = "[red]✗[/red]"

        table.add_row(
            r["id"],
            f"[{style}]{verdict}[/{style}]",
            f"{average}/10" if average is not None else "—",
            expected or "—",
            match,
        )

    console.print(table)

    graded = [r for r in results if r.get("expected") and r.get("verdict") != "ERROR"]
    if graded:
        console.print(
            f"[bold]Expected verdict match:[/bold] {passed}/{len(graded)}\n"
        )


if __name__ == "__main__":
    run()
