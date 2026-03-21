# evaluator.py
# Scores a prompt+response pair across 4 quality dimensions.
# Supports two providers, selected via ACTIVE_PROVIDER in .env:
#   - "claude"  → Anthropic Claude API (claude-sonnet-4-20250514)
#   - "gemini"  → Google Gemini API    (gemini-2.0-flash, google-genai SDK)
# Both return the same dict structure so report_generator works unchanged.

import json
import os

import anthropic
from google import genai
from dotenv import load_dotenv

from auditor.dimensions import DIMENSIONS, get_verdict

load_dotenv()

CLAUDE_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.0-flash"


def _build_prompt(prompt: str, response: str) -> str:
    """Build the shared evaluation prompt for either provider."""
    dimensions_text = ""
    for dim in DIMENSIONS:
        dimensions_text += (
            f"\n- **{dim['label']}** (`{dim['name']}`): {dim['description']}\n"
            f"  Scoring guide: {dim['scoring_guide']}"
        )

    return f"""You are an expert LLM response quality auditor. Evaluate the AI response below across the following dimensions:{dimensions_text}

---
USER PROMPT:
{prompt}

AI RESPONSE:
{response}
---

Return a JSON object with exactly this structure (no markdown, no extra text):
{{
  "relevance":         {{"score": <0-10>, "reasoning": "<one sentence>"}},
  "completeness":      {{"score": <0-10>, "reasoning": "<one sentence>"}},
  "hallucination_risk":{{"score": <0-10>, "reasoning": "<one sentence>"}},
  "tone_and_safety":   {{"score": <0-10>, "reasoning": "<one sentence>"}}
}}"""


def _parse_and_validate(raw: str, provider: str) -> dict:
    """Parse the raw JSON string from a provider and validate dimension keys."""
    # Strip markdown code fences if the provider wrapped its output
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        scores = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"{provider} returned non-JSON output. Raw response:\n{raw}"
        ) from e

    expected_keys = {dim["name"] for dim in DIMENSIONS}
    missing = expected_keys - scores.keys()
    if missing:
        raise ValueError(f"{provider} response is missing dimension keys: {missing}")

    return scores


def _evaluate_claude(prompt: str, response: str) -> dict:
    """Call the Anthropic Claude API and return raw scores dict."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": _build_prompt(prompt, response)}],
    )

    raw = message.content[0].text.strip()
    return _parse_and_validate(raw, "Claude")


def _evaluate_gemini(prompt: str, response: str) -> dict:
    """Call the Google Gemini API and return raw scores dict."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    client = genai.Client(api_key=api_key)
    result = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=_build_prompt(prompt, response),
    )
    raw = result.text.strip()
    return _parse_and_validate(raw, "Gemini")


def evaluate(prompt: str, response: str) -> dict:
    """
    Score an LLM response using the active provider.

    Reads ACTIVE_PROVIDER from .env ("claude" or "gemini", defaults to "claude").

    Args:
        prompt:   The original user question that was sent to the AI.
        response: The AI-generated response being audited.

    Returns:
        A dict with keys:
          - scores: dict of dimension name → {score, reasoning}
          - average_score: float
          - verdict: "PASS" | "NEEDS REVIEW" | "FAIL"
          - provider: the provider used ("claude" or "gemini")

    Raises:
        EnvironmentError: if the required API key is not set.
        ValueError: if the provider returns malformed JSON or unknown provider name.
    """
    provider = os.getenv("ACTIVE_PROVIDER", "claude").strip().lower()

    if provider == "claude":
        scores = _evaluate_claude(prompt, response)
    elif provider == "gemini":
        scores = _evaluate_gemini(prompt, response)
    else:
        raise ValueError(
            f"Unknown ACTIVE_PROVIDER '{provider}'. Must be 'claude' or 'gemini'."
        )

    total = sum(scores[dim["name"]]["score"] for dim in DIMENSIONS)
    average_score = total / len(DIMENSIONS)

    return {
        "scores": scores,
        "average_score": round(average_score, 2),
        "verdict": get_verdict(average_score),
        "provider": provider,
    }
