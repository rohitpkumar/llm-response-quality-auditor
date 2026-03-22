# 🔍 LLM Response Quality Auditor

> Built with Claude Code · Powered by Claude API · Designed by a QA Engineer

An AI-powered audit tool that automatically evaluates LLM responses across 
4 quality dimensions — relevance, completeness, hallucination risk, and tone.

Built to solve a real problem: **manually reviewing AI feature outputs is 
slow, inconsistent, and doesn't scale.** This tool automates that process.

---

## 🎯 Why I Built This

As a QA Lead validating AI-powered product features, I spent significant time 
manually reviewing LLM responses for quality issues — hallucinations, 
incomplete answers, off-tone outputs.

This tool automates that review pipeline end-to-end:
- No more manual spot-checking of AI responses
- Consistent scoring across every response
- Structured audit reports ready for the team

---

## 🧠 How It Works
```
Input: A prompt + an LLM response
          ↓
Evaluated across 4 quality dimensions via Claude API
          ↓
Output: Scored audit report with pass/fail + reasoning
```

### 4 Evaluation Dimensions

| Dimension | What It Checks |
|---|---|
| ✅ **Relevance** | Did the AI actually answer what was asked? |
| ✅ **Completeness** | Did it cover the full scope or dodge parts? |
| ⚠️ **Hallucination Risk** | Does it make unverifiable or fabricated claims? |
| ✅ **Tone & Safety** | Is the response appropriate for end users? |

---

## 📊 Sample Audit Report
```
=============================
 LLM RESPONSE AUDIT REPORT
=============================
Prompt        : "What is the refund policy for premium plans?"
Model Audited : GPT-4 response

DIMENSION SCORES:
✅ Relevance         : 9/10 — Directly addresses the question
⚠️  Completeness     : 6/10 — Does not mention edge case exceptions
❌ Hallucination Risk: 4/10 — References a policy doc with no citation
✅ Tone & Safety     : 9/10 — Professional and user-appropriate

OVERALL SCORE  : 7/10
VERDICT        : ⚠️  NEEDS REVIEW

RECOMMENDATION : Response should be fact-checked before production use.
=============================
```

---

## 📈 Results

5 real-world test scenarios executed covering:
- ✅ Good response (expected: PASS)
- ❌ Hallucination response (expected: FAIL)
- ⚠️ Incomplete response (expected: NEEDS REVIEW)
- ❌ Off-tone response (expected: FAIL)
- ❌ Irrelevant response (expected: FAIL)

| Test Case | Category | Score | Verdict | Expected | Match |
|---|---|---|---|---|---|
| TC001 | Good Response | 9.5/10 | PASS | PASS | ✓ |
| TC002 | Hallucination | 7.5/10 | NEEDS REVIEW | FAIL | ✗ |
| TC003 | Incomplete | 7.75/10 | NEEDS REVIEW | NEEDS REVIEW | ✓ |
| TC004 | Off-tone | 3.5/10 | FAIL | FAIL | ✓ |
| TC005 | Irrelevant | 4.5/10 | FAIL | FAIL | ✓ |

**4 out of 5 verdicts matched expected outcomes on first run.**

> TC002 returned NEEDS REVIEW instead of FAIL — highlighting that 
> hallucination detection requires nuance, not binary scoring. The 
> response contained some valid information mixed with unverifiable 
> claims. This finding led to refinement of the hallucination risk 
> evaluation dimension.

---

## 🗂️ Project Structure
```
llm-response-quality-auditor/
│
├── auditor/
│   ├── evaluator.py          ← Sends response to Claude API for scoring
│   ├── dimensions.py         ← Defines the 4 evaluation dimensions
│   └── report_generator.py   ← Formats scores into audit report
│
├── test_cases/
│   ├── sample_inputs.json    ← Real prompt + response pairs
│   └── expected_outputs.json ← Expected audit outcomes
│
├── reports/
│   └── sample_report.md      ← Pre-generated audit report
│
├── tests/
│   └── test_evaluator.py     ← Unit tests for the auditor
│
├── run_audit.py              ← Main entry point
├── requirements.txt          ← Python dependencies
└── .env.example              ← API key template
```

---

## 🚀 How To Run

### 1. Clone the repo
```bash
git clone https://github.com/rohitpkumar/llm-response-quality-auditor.git
cd llm-response-quality-auditor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
# Open .env and add your Anthropic API key
```

### 4. Run the auditor
```bash
python run_audit.py
```

---

## 🛠️ Built With

| Tool | Role |
|---|---|
| **Claude Code** | Used as AI coding agent to architect and build this tool |
| **Claude API** | Powers the evaluation engine inside the auditor |
| **Python** | Core language |
| **Promptfoo** | Inspiration for evaluation framework design |

---

## 📈 How I Built This (AI-Native Workflow)

This project was built entirely using **Claude Code** as an AI coding agent:

1. Created `CLAUDE.md` — a project briefing file giving Claude Code 
   full context about the project before writing any code
2. Used short, precise prompts to generate each file — Claude Code 
   read CLAUDE.md automatically so no repeated context was needed
3. Debugged API errors and provider switching entirely via Claude Code
4. Iterated on evaluation dimensions based on real test run results

> This is the same AI-native workflow used by engineering teams 
> at AI-first companies today.

---

## 👤 About

Built by **Rohit Kumar** — QA Lead with 12+ years experience, specialising 
in AI/LLM quality validation, test automation, and release delivery.

- 🔗 [LinkedIn](https://linkedin.com/in/rohit-kumar-b7356aa8)
- 📧 rohitkumar.p271@gmail.com
- 🗂️ [Other Projects](https://github.com/rohitpkumar)

---

## 📄 License

MIT License — free to use and adapt.
