"""Check expected behavior in deterministic fixtures; not an LLM benchmark."""
from __future__ import annotations

import json
import math
from pathlib import Path

from demo import run_expression


def evaluate(cases: list[dict]) -> dict:
    rows = []
    for case in cases:
        result = run_expression(case["expression"], **case.get("options", {}))
        passed = (result["status"] == case["expected_status"]
                  and result["reason"] == case["expected_reason"])
        if "expected_result" in case:
            observations = [e["result"] for e in result["events"]
                            if e["type"] == "tool_result"]
            passed = passed and bool(observations) and math.isclose(
                observations[-1], case["expected_result"], rel_tol=1e-9, abs_tol=1e-9
            )
            passed = passed and result["output"] == f"result={observations[-1]:g}"
        rows.append({"id": case["id"], "passed": bool(passed),
                     "status": result["status"], "reason": result["reason"],
                     "tool_calls": result["tool_calls"]})
    return {"case_count": len(rows), "behavior_passed": sum(r["passed"] for r in rows),
            "completed_count": sum(r["status"] == "completed" for r in rows),
            "scope": "deterministic harness fixtures, not LLM task capability",
            "cases": rows}


def main() -> int:
    cases_path = Path(__file__).with_name("cases.json")
    report = evaluate(json.loads(cases_path.read_text(encoding="utf-8")))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["behavior_passed"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
