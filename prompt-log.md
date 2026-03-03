# Prompt Development Log

## The Problem

The initial prompt was underspecified:

```
Compare West Elm and CB2. Be extremely detailed.
```

**Issues:**
- No structure for comparable outputs
- No guidance on null cases
- No source requirements
- "Detailed" is subjective

---

## The Solution

A structured prompt designed for consistency and verifiability:

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
Structure your analysis as:

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

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Role assignment | Sets context; signals comparative analysis purpose |
| Explicit dimensions | Ensures consistent coverage across competitors |
| Null-case handling | Forces explicit reporting of absence vs. hallucination |
| Required sources | Every claim must be verifiable |
| Structured output | Executive summary table fits on one slide |

---

## Usage

Works with any AI that has web search:
- **ChatGPT** — Enable "Browse with Bing"
- **Gemini** — Built-in
- **Perplexity** — Built-in
- **Claude** — With web search enabled

Replace `{COMPETITOR_A}` and `{COMPETITOR_B}`, paste, review output.

---

## Results

When run with "West Elm" and "CB2":
- Identified positioning differences (lifestyle vs. editorial)
- Surfaced loyalty program mechanics (Key Rewards cross-brand vs. CB2 Visa Signature)
- Discovered AI investments not visible on homepages:
  - West Elm: OpenAI ChatGPT Ad Pilot, Salesforce Agentforce, 3D Room Planner
  - CB2: App-free AR via Vertebrae (21% revenue lift)

See `competitive-analysis.md` for full output.
