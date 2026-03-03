"""
ADK multi-agent competitive analysis.

Architecture:
    SequentialAgent (root)
    ├── ParallelAgent (research)
    │   ├── LlmAgent (researcher_a) → output_key: "research_a"
    │   └── LlmAgent (researcher_b) → output_key: "research_b"
    └── LlmAgent (synthesizer) → reads {research_a}, {research_b} from state

Usage:
    python3 agent.py --competitor-a "West Elm" --competitor-b "CB2"
"""

import argparse
import asyncio
import json
import re
import time
from pathlib import Path

import requests
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

SCRIPT_DIR = Path(__file__).parent
MODEL = "gemini-2.5-flash"
API_KEY = "REDACTED"
GROUNDING_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"


# ---------------------------------------------------------------------------
# Custom tool: grounded research via REST API
# ---------------------------------------------------------------------------

def grounded_research(query: str) -> str:
    """Research a topic using Google Search grounding.

    Sends the query to Gemini with automatic Google Search grounding enabled,
    which exhaustively searches the web and returns a grounded response with
    source citations. Use this for each research question or dimension.

    Args:
        query: The research question or topic to investigate.

    Returns:
        A detailed, source-cited response grounded in current web results.
    """
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "tools": [{"google_search": {}}],
    }
    resp = requests.post(GROUNDING_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if "candidates" not in data:
        return f"Search failed: {json.dumps(data)}"

    candidate = data["candidates"][0]

    # Extract text content
    parts = candidate["content"]["parts"]
    text = "\n".join(p["text"] for p in parts if "text" in p)

    # Extract source URLs from grounding metadata and append them
    grounding = candidate.get("groundingMetadata", {})
    chunks = grounding.get("groundingChunks", [])
    sources = []
    for chunk in chunks:
        web = chunk.get("web", {})
        title = web.get("title", "")
        uri = web.get("uri", "")
        if title and uri:
            sources.append(f"- [{title}]({uri})")

    if sources:
        text += "\n\n### Grounding Sources\n" + "\n".join(sources)

    return text

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

RESEARCH_INSTRUCTION = """You are a competitive intelligence analyst specializing in e-commerce UX.

Analyze {competitor} across four dimensions. Use the `grounded_research` tool for EACH
dimension separately — that's at least 4 tool calls. For Dimension 4 (AI), make an additional
call specifically searching for "{competitor} AI partnerships press releases tech investments."
Be thorough. Cite your sources.

Compile the results into your final output.
Include ALL source URLs from the tool responses. Do not drop any citations.

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

Output your findings with bullet points and source links for each dimension.
End with a Sources section listing all URLs cited.
"""

SYNTHESIS_INSTRUCTION = """You are a competitive intelligence analyst. You have received two
independent research profiles from your research team.

### Research on {competitor_a}:
{research_a}

### Research on {competitor_b}:
{research_b}

Synthesize these into a single comparative analysis. Do NOT conduct additional research —
work only with what's provided. Focus on:
1. Where the competitors differ most sharply
2. Structural advantages one has over the other
3. Strategic implications for decision-makers

### Output Format

## Executive Summary
| | {competitor_a} | {competitor_b} |
|---|---|---|
| Positioning | [1 sentence] | [1 sentence] |
| Core Audience | [1 sentence] | [1 sentence] |
| Key Differentiator | [1 sentence] | [1 sentence] |

[1-2 sentence bottom line]

## Comparative Analysis
| Dimension | {competitor_a} | {competitor_b} |
|-----------|----------|-----|
| Hero approach | | |
| Above-fold density | | |
| Photography style | | |
| Navigation depth | | |
| Promo prominence | | |
| Loyalty program | | |
| AI visibility | | |
| AI strategy | | |

## Strategic Implications
| Theme | Implication |
|-------|-------------|
[3-5 rows]

## Sources
[Combine all sources from both research profiles]
"""


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(output: str, latency: float) -> dict:
    urls = re.findall(r'https?://[^\s\)\]>]+', output)
    dims = {
        "Homepage Messaging": bool(re.search(r'homepage\s*messaging|visual\s*hierarchy|dimension\s*1', output, re.I)),
        "Promotional": bool(re.search(r'promotional|offers|loyalty|dimension\s*2', output, re.I)),
        "Product Discovery": bool(re.search(r'product\s*discovery|navigation|dimension\s*3', output, re.I)),
        "AI Features": bool(re.search(r'ai[- ]powered|ai\s*features|dimension\s*4', output, re.I)),
    }
    return {
        "latency_s": round(latency, 2),
        "output_chars": len(output),
        "source_count": len(set(urls)),
        "dimensions_covered": sum(dims.values()),
        "has_executive_summary": bool(re.search(r'executive\s*summary', output, re.I)),
        "has_strategic_implications": bool(re.search(r'strategic\s*implications', output, re.I)),
    }


# ---------------------------------------------------------------------------
# Agent construction
# ---------------------------------------------------------------------------

def build_agent(comp_a: str, comp_b: str) -> SequentialAgent:
    """Build the full SequentialAgent: parallel research → LLM synthesis."""

    researcher_a = LlmAgent(
        name="researcher_a",
        description=f"Researches {comp_a} across 4 competitive dimensions",
        model=MODEL,
        instruction=RESEARCH_INSTRUCTION.replace("{competitor}", comp_a),
        tools=[grounded_research],
        output_key="research_a",
    )

    researcher_b = LlmAgent(
        name="researcher_b",
        description=f"Researches {comp_b} across 4 competitive dimensions",
        model=MODEL,
        instruction=RESEARCH_INSTRUCTION.replace("{competitor}", comp_b),
        tools=[grounded_research],
        output_key="research_b",
    )

    parallel_research = ParallelAgent(
        name="parallel_research",
        description="Runs both competitor research agents in parallel",
        sub_agents=[researcher_a, researcher_b],
    )

    synthesizer = LlmAgent(
        name="synthesizer",
        description="Synthesizes two research profiles into a comparative analysis",
        model=MODEL,
        instruction=SYNTHESIS_INSTRUCTION.replace("{competitor_a}", comp_a).replace("{competitor_b}", comp_b),
        output_key="synthesis",
    )

    return SequentialAgent(
        name="competitive_analysis",
        description=f"Competitive analysis of {comp_a} vs {comp_b}",
        sub_agents=[parallel_research, synthesizer],
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_agent(comp_a: str, comp_b: str) -> dict:
    """Execute SequentialAgent: parallel research → LLM synthesis."""
    agent = build_agent(comp_a, comp_b)
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="competitive_intel",
        agent=agent,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="competitive_intel",
        user_id="user",
    )

    start = time.time()

    message = types.Content(
        role="user",
        parts=[types.Part(text=f"Analyze {comp_a} vs {comp_b}")],
    )

    research_a_text = ""
    research_b_text = ""
    synthesis_text = ""

    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=message,
    ):
        # Grab outputs from state
        if event.actions and event.actions.state_delta:
            if "research_a" in event.actions.state_delta:
                research_a_text = event.actions.state_delta["research_a"]
            if "research_b" in event.actions.state_delta:
                research_b_text = event.actions.state_delta["research_b"]
            if "synthesis" in event.actions.state_delta:
                synthesis_text = event.actions.state_delta["synthesis"]

    total_latency = time.time() - start

    return {
        "approach": "adk_llm_synthesis",
        "output": synthesis_text,
        "research_a": research_a_text,
        "research_b": research_b_text,
        "synthesis": synthesis_text,
        "metrics": compute_metrics(synthesis_text, total_latency),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    parser = argparse.ArgumentParser(description="ADK multi-agent competitive analysis")
    parser.add_argument("--competitor-a", default="West Elm")
    parser.add_argument("--competitor-b", default="CB2")
    args = parser.parse_args()

    comp_a, comp_b = args.competitor_a, args.competitor_b

    print(f"{'='*60}")
    print(f"ADK Agent: {comp_a} vs {comp_b}")
    print(f"{'='*60}")
    print(f"\nArchitecture:")
    print(f"  SequentialAgent (root)")
    print(f"  ├── ParallelAgent (research)")
    print(f"  │   ├── LlmAgent (researcher_a) → {comp_a} [grounded_research tool]")
    print(f"  │   └── LlmAgent (researcher_b) → {comp_b} [grounded_research tool]")
    print(f"  └── LlmAgent (synthesizer) → reads research_a, research_b from state")
    print(f"\nRunning...\n")

    result = run_agent(comp_a, comp_b)
    # Handle both coroutine and direct result
    if asyncio.iscoroutine(result):
        result = await result

    m = result["metrics"]
    print(f"Latency:    {m['latency_s']}s")
    print(f"Sources:    {m['source_count']}")
    print(f"Dimensions: {m['dimensions_covered']}/4")
    print(f"Length:     {m['output_chars']} chars")
    print(f"Exec Sum:   {m['has_executive_summary']}")
    print(f"Strat Impl: {m['has_strategic_implications']}")

    # Save results
    out_path = SCRIPT_DIR / "adk-results.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nFull results saved to {out_path}")

    # Print synthesis output
    if result["synthesis"]:
        print(f"\n{'='*60}")
        print("SYNTHESIS OUTPUT")
        print(f"{'='*60}")
        print(result["synthesis"][:3000])


if __name__ == "__main__":
    asyncio.run(main())
