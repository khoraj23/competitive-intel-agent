# Prompt Evaluation

## Overview

Using [promptfoo](https://promptfoo.dev) to systematically test and hill-climb the competitive analysis prompt. This ensures the prompt works across different competitor pairs and catches regressions.

---

## Results

| Test Case | Competitors | Result |
|-----------|-------------|--------|
| Baseline | West Elm vs CB2 | PASS |
| Different vertical | Wayfair vs Overstock | PASS |
| Different models | IKEA vs Target Home | PASS |

**Overall: 3/3 passed (100%)**

---

## Test Cases

### Test 1: Baseline (West Elm vs CB2)
Our original use case. Tests that the prompt produces:
- Executive Summary table
- Sources section
- All 4 dimensions covered
- At least 3 source URLs

### Test 2: Different Vertical (Wayfair vs Overstock)
Mass-market furniture retailers. Tests that:
- Analysis is specific to the named competitors
- Not generic furniture industry content
- Identifies key positioning differences

### Test 3: Different Business Models (IKEA vs Target Home)
Tests handling of competitors with fundamentally different business models:
- Pure-play furniture (IKEA) vs department store home section (Target)
- Correctly handles null cases if AI features absent

---

## Assertions

| Assertion Type | What It Checks |
|----------------|----------------|
| `contains: "Executive Summary"` | Output has required structure |
| `contains: "Sources"` | Sources are cited |
| `llm-rubric` | LLM-as-judge evaluates content quality |

**LLM-as-judge criteria:**
- Covers all 4 dimensions
- Contains at least 3 source URLs
- Analysis is specific (not generic)
- Null cases explicitly stated

---

## Setup

### Install
```bash
npm install -g promptfoo
# or
npx promptfoo@latest
```

### Run Eval
```bash
export GEMINI_API_KEY="your-api-key"
npx promptfoo eval
```

### View Results
```bash
npx promptfoo view  # Opens web UI
```

---

## Config File

`promptfooconfig.yaml`:
```yaml
description: Competitive Analysis Prompt Evaluation

providers:
  - id: google:gemini-2.5-flash
    config:
      apiKey: ${GEMINI_API_KEY}

prompts:
  - file://prompt.txt

tests:
  - description: "Baseline: West Elm vs CB2"
    vars:
      COMPETITOR_A: West Elm
      COMPETITOR_B: CB2
    assert:
      - type: contains
        value: "Executive Summary"
      - type: contains
        value: "Sources"
      - type: llm-rubric
        value: "Output covers all 4 dimensions"

  - description: "Different vertical: Wayfair vs Overstock"
    vars:
      COMPETITOR_A: Wayfair
      COMPETITOR_B: Overstock
    assert:
      - type: llm-rubric
        value: "Analysis is specific to the competitors named"

  - description: "Null case: IKEA vs Target Home"
    vars:
      COMPETITOR_A: IKEA
      COMPETITOR_B: Target Home
    assert:
      - type: llm-rubric
        value: "Explicitly states absence if AI features not found"
```

---

## Hill-Climbing Workflow

1. **Add test case** for failure mode you want to fix
2. **Run eval** — see which assertions fail
3. **Modify prompt** to address failure
4. **Re-run eval** — confirm fix doesn't break other tests
5. **Commit** when all tests pass

### Example: Adding a New Test Case

If the prompt fails on international competitors:
```yaml
- description: "International: Muji vs Zara Home"
  vars:
    COMPETITOR_A: Muji
    COMPETITOR_B: Zara Home
  assert:
    - type: llm-rubric
      value: "Handles non-US retailers correctly"
```

---

## Stats

- **Duration:** 44 seconds for 3 test cases
- **Tokens:** ~41K total (18K eval, 23K grading)
- **Cost:** ~$0.02 per run (Gemini 2.5 Flash pricing)
