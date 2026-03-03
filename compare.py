"""
Sequential vs Parallel competitive analysis comparison.

Runs both approaches for a given competitor pair, measures:
- Wall-clock latency
- Source count (factuality proxy)
- Dimension coverage
- Output length (depth proxy)

Then uses LLM-as-judge to compare overall quality.

Usage:
    python3 compare.py [--competitor-a "West Elm"] [--competitor-b "CB2"] [--runs 1]
"""

import argparse
import asyncio
import json
import re
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
API_KEY = "AIzaSyCp7-4EUG9I8RcufAJ_yi7uy9ckbB9siyU"
MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"


def load_prompt(filename: str) -> str:
    return (SCRIPT_DIR / filename).read_text()


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def count_sources(text: str) -> int:
    """Count unique URLs in the output."""
    urls = re.findall(r'https?://[^\s\)\]>]+', text)
    return len(set(urls))


def check_dimensions(text: str) -> dict:
    """Check which dimensions are covered."""
    return {
        "Homepage Messaging": bool(re.search(r'dimension\s*1|homepage\s*messaging|visual\s*hierarchy', text, re.I)),
        "Promotional Placement": bool(re.search(r'dimension\s*2|promotional|offers|loyalty', text, re.I)),
        "Product Discovery": bool(re.search(r'dimension\s*3|product\s*discovery|navigation', text, re.I)),
        "AI Features": bool(re.search(r'dimension\s*4|ai[- ]powered|ai\s*features', text, re.I)),
    }


def has_section(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def compute_metrics(output: str, latency: float) -> dict:
    dims = check_dimensions(output)
    return {
        "latency_s": round(latency, 2),
        "output_chars": len(output),
        "source_count": count_sources(output),
        "dimensions_covered": sum(dims.values()),
        "dimensions": dims,
        "has_executive_summary": has_section(output, r'executive\s*summary'),
        "has_strategic_implications": has_section(output, r'strategic\s*implications'),
    }


# ---------------------------------------------------------------------------
# Gemini REST API
# ---------------------------------------------------------------------------

def call_gemini(prompt: str, use_search: bool = True) -> str:
    """Call Gemini via REST API with optional Google Search grounding."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
    }
    if use_search:
        payload["tools"] = [{"google_search": {}}]

    resp = requests.post(API_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if "candidates" not in data:
        raise RuntimeError(f"Gemini API error: {json.dumps(data, indent=2)}")

    # Extract text from all parts
    parts = data["candidates"][0]["content"]["parts"]
    text_parts = [p["text"] for p in parts if "text" in p]
    return "\n".join(text_parts)


async def call_gemini_async(prompt: str, use_search: bool = True) -> str:
    """Run Gemini call in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, call_gemini, prompt, use_search)


# ---------------------------------------------------------------------------
# Sequential approach
# ---------------------------------------------------------------------------

async def run_sequential(comp_a: str, comp_b: str) -> dict:
    """Single prompt, both competitors at once."""
    prompt_template = load_prompt("prompt.txt")
    prompt = prompt_template.replace("{{COMPETITOR_A}}", comp_a).replace("{{COMPETITOR_B}}", comp_b)

    start = time.time()
    output = await call_gemini_async(prompt)
    latency = time.time() - start

    return {
        "approach": "sequential",
        "output": output,
        "metrics": compute_metrics(output, latency),
    }


# ---------------------------------------------------------------------------
# Parallel approach
# ---------------------------------------------------------------------------

async def run_parallel(comp_a: str, comp_b: str) -> dict:
    """Two research calls in parallel, then one synthesis call."""
    research_template = load_prompt("prompt-research.txt")
    synth_template = load_prompt("prompt-synthesize.txt")

    prompt_a = research_template.replace("{{COMPETITOR}}", comp_a)
    prompt_b = research_template.replace("{{COMPETITOR}}", comp_b)

    # Phase 1: parallel research (both use web search)
    start = time.time()
    research_a, research_b = await asyncio.gather(
        call_gemini_async(prompt_a, use_search=True),
        call_gemini_async(prompt_b, use_search=True),
    )
    research_latency = time.time() - start

    # Phase 2: synthesis (no web search needed — just merging)
    synth_start = time.time()
    synth_prompt = (
        synth_template
        .replace("{{RESEARCH_A}}", research_a)
        .replace("{{RESEARCH_B}}", research_b)
        .replace("{{COMPETITOR_A}}", comp_a)
        .replace("{{COMPETITOR_B}}", comp_b)
    )
    synth_output = await call_gemini_async(synth_prompt, use_search=False)
    synth_latency = time.time() - synth_start

    total_latency = time.time() - start

    # Combine all outputs for metrics computation
    full_output = f"{research_a}\n\n---\n\n{research_b}\n\n---\n\n{synth_output}"

    return {
        "approach": "parallel",
        "output": full_output,
        "synthesis_only": synth_output,
        "research_a": research_a,
        "research_b": research_b,
        "metrics": {
            **compute_metrics(full_output, total_latency),
            "research_latency_s": round(research_latency, 2),
            "synthesis_latency_s": round(synth_latency, 2),
        },
    }


# ---------------------------------------------------------------------------
# LLM-as-judge comparison
# ---------------------------------------------------------------------------

async def judge_comparison(seq_output: str, par_output: str, comp_a: str, comp_b: str) -> str:
    """Use Gemini to compare the two outputs head-to-head."""
    judge_prompt = f"""You are evaluating two competitive analyses of {comp_a} vs {comp_b}.
Rate each on five criteria (1-5 scale), declare a winner, and explain why.

## Output A (Sequential — single prompt, single LLM call)
{seq_output}

## Output B (Parallel — independent per-competitor research merged by a synthesis step)
{par_output}

## Evaluation Criteria
1. **Depth of research**: Which found more specific, non-obvious facts? (press releases, partnerships, metrics)
2. **Source quality**: Which cited more verifiable, authoritative sources?
3. **Strategic insight**: Which produced more actionable "so what" implications?
4. **Factual consistency**: Any contradictions or unsupported claims?
5. **Completeness**: Which better covered all 4 dimensions for both competitors?

## Output Format
| Criterion | Sequential (A) | Parallel (B) |
|-----------|----------------|--------------|
| Depth | X/5 | X/5 |
| Source quality | X/5 | X/5 |
| Strategic insight | X/5 | X/5 |
| Factual consistency | X/5 | X/5 |
| Completeness | X/5 | X/5 |
| **Total** | XX/25 | XX/25 |

**Winner**: [A or B or Tie]
**Rationale**: [2-3 sentences explaining why]
"""
    return await call_gemini_async(judge_prompt, use_search=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def run_comparison(comp_a: str, comp_b: str, run_id: int) -> dict:
    """Run both approaches and compare."""
    print(f"\n{'='*60}")
    print(f"Run {run_id}: {comp_a} vs {comp_b}")
    print(f"{'='*60}")

    # Run both approaches concurrently (they're independent)
    print("Starting sequential and parallel approaches concurrently...")
    seq_result, par_result = await asyncio.gather(
        run_sequential(comp_a, comp_b),
        run_parallel(comp_a, comp_b),
    )

    print(f"\nSequential: {seq_result['metrics']['latency_s']}s | "
          f"{seq_result['metrics']['source_count']} sources | "
          f"{seq_result['metrics']['dimensions_covered']}/4 dims")

    print(f"Parallel:   {par_result['metrics']['latency_s']}s "
          f"(research: {par_result['metrics']['research_latency_s']}s + "
          f"synth: {par_result['metrics']['synthesis_latency_s']}s) | "
          f"{par_result['metrics']['source_count']} sources | "
          f"{par_result['metrics']['dimensions_covered']}/4 dims")

    # LLM-as-judge
    print("\nRunning LLM-as-judge comparison...")
    judge_result = await judge_comparison(
        seq_result["output"],
        par_result["synthesis_only"],
        comp_a, comp_b,
    )
    print(f"\n{judge_result}")

    return {
        "run_id": run_id,
        "competitors": {"a": comp_a, "b": comp_b},
        "sequential": {
            "metrics": seq_result["metrics"],
            "output": seq_result["output"],
        },
        "parallel": {
            "metrics": par_result["metrics"],
            "output": par_result["output"],
            "synthesis": par_result["synthesis_only"],
            "research_a": par_result["research_a"],
            "research_b": par_result["research_b"],
        },
        "judge": judge_result,
    }


async def main():
    parser = argparse.ArgumentParser(description="Compare sequential vs parallel competitive analysis")
    parser.add_argument("--competitor-a", default="West Elm")
    parser.add_argument("--competitor-b", default="CB2")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs (for variance)")
    args = parser.parse_args()

    results = []
    for i in range(1, args.runs + 1):
        result = await run_comparison(args.competitor_a, args.competitor_b, i)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for r in results:
        seq = r["sequential"]["metrics"]
        par = r["parallel"]["metrics"]
        speedup = seq["latency_s"] / par["latency_s"] if par["latency_s"] > 0 else 0
        print(f"\nRun {r['run_id']}:")
        print(f"  Latency    — Seq: {seq['latency_s']}s | Par: {par['latency_s']}s | Speedup: {speedup:.1f}x")
        print(f"  Sources    — Seq: {seq['source_count']} | Par: {par['source_count']}")
        print(f"  Dimensions — Seq: {seq['dimensions_covered']}/4 | Par: {par['dimensions_covered']}/4")
        print(f"  Length     — Seq: {seq['output_chars']} chars | Par: {par['output_chars']} chars")

    # Save full results
    out_path = SCRIPT_DIR / "comparison-results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
