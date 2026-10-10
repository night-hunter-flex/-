"""Deterministic harness acceptance scenarios, not an LLM quality benchmark."""
import json
from pathlib import Path
from research_agent import Corpus, run_research

FIXTURE = Path(__file__).with_name("fixtures")
QUOTE = "Tool budgets stop the task when maximum calls are reached."


def action(name, payload, index):
    return {"id": f"response_{index}", "status": "completed",
            "output": [{"type": "function_call", "call_id": f"call_{index}",
                        "name": name, "arguments": json.dumps(payload)}]}


def scenario(kind):
    first = action("search_docs", {"query": "tool budgets", "max_hits": 5}, 1)
    reading = action("read_document", {"path": "harness.md", "start_line": 3, "max_lines": 3}, 2)
    good = {"summary": "Budgets must stop exhausted tasks.",
            "claims": [{"claim": "Tool calls are bounded.", "source": "harness.md",
                        "line": 3, "quote": QUOTE}],
            "limitations": "The fixture is illustrative, not a production audit."}
    bad = {**good, "claims": [{**good["claims"][0], "quote": "Fabricated quote absent from source"}]}
    samples = {
        "grounded_success": ([first, reading, action("submit_report", good, 3)], {}),
        "bad_quote_recovered": ([first, reading, action("submit_report", bad, 3),
                                 action("submit_report", good, 4)], {}),
        "path_rejected": ([first, action("read_document",
                          {"path": "../../secret.md", "start_line": 1, "max_lines": 2}, 2)], {"max_steps": 2}),
        "tool_budget_exhausted": ([first, reading], {"max_tool_calls": 1}),
    }
    responses, limits = samples[kind]
    itr = iter(responses)
    result = run_research("How do tool budgets work?", Corpus(FIXTURE),
                          call_model=lambda _payload, _timeout: next(itr),
                          **limits)
    return result


def main() -> int:
    expected = {
        "grounded_success": ("completed", "verified_report_submitted"),
        "bad_quote_recovered": ("completed", "verified_report_submitted"),
        "path_rejected": ("budget_exceeded", "max_steps"),
        "tool_budget_exhausted": ("budget_exceeded", "max_tool_calls"),
    }
    records = []
    for name, (status, reason) in expected.items():
        result = scenario(name)
        ok = (result["status"], result["reason"]) == (status, reason)
        if name == "bad_quote_recovered":
            ok = ok and any(e.get("code") == "quote_not_found" for e in result["events"])
        if name == "path_rejected":
            ok = ok and any(e.get("code") == "path_not_discovered_or_allowed"
                            for e in result["events"])
        records.append({
            "scenario": name, "behavior_passed": ok,
            "status": result["status"], "reason": result["reason"],
            "metrics": result["metrics"],
        })
    summary = {
        "behavior_passed": sum(int(r["behavior_passed"]) for r in records),
        "total": len(records),
        "completed_tasks": sum(r["status"] == "completed" for r in records),
        "note": "Scripted policy replay; NOT a measurement of real LLM answer quality.",
        "results": records,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["behavior_passed"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
