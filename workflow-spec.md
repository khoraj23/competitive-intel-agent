# Workflow Spec: `/competitive-intel`

## Overview

A repeatable workflow for generating executive-ready competitive analysis. Works with any AI that has web search — no special infrastructure required.

---

## The Workflow

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│   1. OPEN any AI with web search                       │
│      (ChatGPT, Gemini, Claude, Perplexity)             │
│                                                        │
│                         ↓                              │
│                                                        │
│   2. PASTE the prompt                                  │
│      Replace {COMPETITOR_A} and {COMPETITOR_B}         │
│                                                        │
│                         ↓                              │
│                                                        │
│   3. REVIEW output                                     │
│      Check sources, verify key claims                  │
│                                                        │
│                         ↓                              │
│                                                        │
│   4. DISTRIBUTE                                        │
│      Export and share with stakeholders                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Time to complete:** 5-10 minutes

---

## The Prompt

```
### Role and Objective
You are a competitive intelligence analyst specializing in e-commerce UX. Your goal is to produce structured competitive analysis that can be directly compared across competitors.

### Task
Compare {COMPETITOR_A} and {COMPETITOR_B} across four dimensions using web search to gather current information. For each dimension, cite your sources.

### Dimension 1: Homepage Messaging & Visual Hierarchy
- Hero: What is the primary headline/tagline? What imagery style dominates?
- Visual hierarchy: What's emphasized above the fold?
- Brand tone: Warm/aspirational vs. editorial/dramatic vs. discount-forward?

### Dimension 2: Promotional Placement & Offers
- Current promotions: What offers are running? (discount codes, free shipping, sales)
- Loyalty programs: What rewards programs exist? What are the tiers and benefits?
- Promo strategy: Is the brand discount-forward or brand-protection focused?

### Dimension 3: Product Discovery
- Navigation structure: How are products organized?
- Search capabilities: What search/filter features exist?
- Entry points: How many paths into product browsing are available?

### Dimension 4: AI-Powered Features
- Customer-facing AI: Chatbots, AR/3D visualization, personalized recommendations, visual search
- Behind-the-scenes AI: What AI investments has the company announced? (search for press releases, tech partnerships)
- If NO AI features found, explicitly state "No AI features identified"

### Output Format
## Executive Summary
| | {COMPETITOR_A} | {COMPETITOR_B} |
|---|---|---|
| Positioning | [1 sentence] | [1 sentence] |
| Key Differentiator | [1 sentence] | [1 sentence] |

## Site: {COMPETITOR_A}
### Dimension 1-4 (with bullet points and source links)

## Site: {COMPETITOR_B}
### Dimension 1-4 (with bullet points and source links)

## Strategic Implications
- [3-5 bullets on what this means competitively]

## Sources
- [List all URLs cited]
```

---

## Where to Run It

| Tool | Web Search | Setup |
|------|------------|-------|
| **ChatGPT** | Enable "Browse with Bing" | Paste directly or create Custom GPT |
| **Gemini** | Built-in | Paste directly or save as Gem |
| **Perplexity** | Built-in | Paste directly |
| **Claude** | Requires MCP or manual | Paste directly |

---

## Output

The prompt produces:

1. **Executive Summary** — Side-by-side table (fits on one slide)
2. **Per-Site Analysis** — Findings across 4 dimensions with sources
3. **Strategic Implications** — "So what" for decision-makers
4. **Sources** — All URLs for verification

---

## Why Web Search Matters

The most valuable findings come from behind-the-scenes intelligence:

| Without Web Search | With Web Search |
|-------------------|-----------------|
| "No AI features visible" | WSI testing ads in ChatGPT via OpenAI pilot |
| Unknown loyalty details | Key Rewards spans 8 brands; CB2 Visa launched Oct 2025 |
| Surface-level only | CB2 has app-free AR with 21% revenue lift |

---

## Use Cases

- **Quarterly review** — Understand competitive positioning before strategy planning
- **Pre-launch research** — See how competitors position similar offerings
- **Exec briefing** — One-page competitive landscape summary
- **Merchandising** — Understand competitor promo strategies
