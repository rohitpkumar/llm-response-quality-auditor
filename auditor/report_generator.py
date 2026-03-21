# report_generator.py
# Formats evaluation results into a structured audit report.
# Saves the report as a .md file in the /reports folder and
# prints a rich-formatted summary to the terminal.

import os
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from auditor.dimensions import DIMENSIONS

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

console = Console()

# Verdict display config
VERDICT_STYLES = {
    "PASS":         {"color": "green",  "icon": "✅"},
    "NEEDS REVIEW": {"color": "yellow", "icon": "⚠️"},
    "FAIL":         {"color": "red",    "icon": "❌"},
}


def _score_bar(score: float, max_score: int = 10) -> str:
    """Return a simple ASCII progress bar for a score."""
    filled = round(score)
    return "█" * filled + "░" * (max_score - filled)


def _build_markdown(test_case: dict, result: dict, timestamp: str) -> str:
    """Build the markdown content for the audit report file."""
    tc_id = test_case.get("id", "N/A")
    category = test_case.get("category", "N/A")
    prompt = test_case.get("prompt", "")
    response = test_case.get("response", "")
    expected = test_case.get("expected_verdict", "N/A")

    verdict = result["verdict"]
    average = result["average_score"]
    scores = result["scores"]

    verdict_icon = VERDICT_STYLES.get(verdict, {}).get("icon", "")

    lines = [
        f"# Audit Report — {tc_id}",
        f"",
        f"**Generated:** {timestamp}  ",
        f"**Category:** {category}  ",
        f"**Expected Verdict:** {expected}  ",
        f"",
        f"---",
        f"",
        f"## Prompt",
        f"",
        f"> {prompt}",
        f"",
        f"## Response Audited",
        f"",
        f"> {response}",
        f"",
        f"---",
        f"",
        f"## Dimension Scores",
        f"",
        f"| Dimension | Score | Reasoning |",
        f"|---|---|---|",
    ]

    for dim in DIMENSIONS:
        key = dim["name"]
        label = dim["label"]
        score = scores[key]["score"]
        reasoning = scores[key]["reasoning"]
        lines.append(f"| {label} | {score}/10 | {reasoning} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Overall Result",
        f"",
        f"| Average Score | Verdict |",
        f"|---|---|",
        f"| {average}/10 | {verdict_icon} {verdict} |",
    ]

    return "\n".join(lines)


def save_report(test_case: dict, result: dict) -> str:
    """
    Save the audit report as a .md file in /reports.

    Args:
        test_case: The original test case dict (id, prompt, response, etc.)
        result:    The evaluation result from evaluator.evaluate()

    Returns:
        The absolute path to the saved report file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    tc_id = test_case.get("id", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{tc_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    content = _build_markdown(test_case, result, timestamp)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return os.path.abspath(filepath)


def print_summary(test_case: dict, result: dict) -> None:
    """Print a rich-formatted audit summary to the terminal."""
    tc_id = test_case.get("id", "N/A")
    verdict = result["verdict"]
    average = result["average_score"]
    scores = result["scores"]
    style = VERDICT_STYLES.get(verdict, {"color": "white", "icon": ""})

    # Dimension scores table
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Dimension", style="bold")
    table.add_column("Score", justify="center")
    table.add_column("Bar", justify="left")
    table.add_column("Reasoning", style="dim")

    for dim in DIMENSIONS:
        key = dim["name"]
        score = scores[key]["score"]
        reasoning = scores[key]["reasoning"]
        table.add_row(
            dim["label"],
            f"{score}/10",
            _score_bar(score),
            reasoning,
        )

    console.print()
    console.print(Panel(table, title=f"[bold]{tc_id} — Dimension Scores[/bold]", border_style="cyan"))

    # Verdict panel
    verdict_text = (
        f"{style['icon']}  [bold {style['color']}]{verdict}[/bold {style['color']}]"
        f"   Average: [bold]{average}/10[/bold]"
    )
    console.print(Panel(verdict_text, title="[bold]Verdict[/bold]", border_style=style["color"]))
    console.print()
