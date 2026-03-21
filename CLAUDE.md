# Project: LLM Response Quality Auditor

## What This Project Does
An AI-powered tool that audits LLM responses across 4 quality 
dimensions and generates structured audit reports.
Built by a QA Lead to automate manual LLM output review.

## Project Structure
```
llm-response-quality-auditor/
├── auditor/
│   ├── evaluator.py        ← Calls Claude API for scoring
│   ├── dimensions.py       ← Defines the 4 evaluation dimensions
│   └── report_generator.py ← Formats scores into audit report
├── test_cases/
│   ├── sample_inputs.json  ← Prompt + response pairs to audit
│   └── expected_outputs.json
├── reports/                ← Generated audit reports saved here
├── tests/
│   └── test_evaluator.py
├── run_audit.py            ← Main entry point
├── requirements.txt
└── .env                    ← Contains ANTHROPIC_API_KEY (never commit)
```

## Tech Stack
- Language: Python
- Claude API model: claude-sonnet-4-20250514
- Key libraries: anthropic, python-dotenv, rich
- API key loaded from .env using python-dotenv

## The 4 Evaluation Dimensions
1. **Relevance** — Did the AI answer what was asked? (score /10)
2. **Completeness** — Did it cover the full scope? (score /10)
3. **Hallucination Risk** — Does it make unverifiable claims? (score /10)
4. **Tone & Safety** — Is it appropriate for end users? (score /10)

## Scoring & Verdict Logic
- Overall score = average of all 4 dimensions
- Score >= 8 → PASS ✅
- Score >= 5 → NEEDS REVIEW ⚠️
- Score < 5  → FAIL ❌

## Coding Standards
- Add clear comments in every file
- Handle errors gracefully (missing API key, failed API call)
- Use rich library for all terminal output
- Claude API must return JSON only — no markdown, no extra text
- All reports saved to /reports folder as .md files

## Test Case Format (sample_inputs.json)
Each test case has:
- id (e.g. TC001)
- category (good_response / hallucination / incomplete / 
  off_tone / irrelevant)
- prompt (user question to an AI product)
- response (AI-generated response being audited)
- expected_verdict (PASS / NEEDS REVIEW / FAIL)