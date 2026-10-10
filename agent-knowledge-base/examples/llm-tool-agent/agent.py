"""Minimal real-LLM tool-calling demo (OpenAI Responses API, standard library).

Educational example: no filesystem, shell, web tools, or external side effects.
The only tool is the safe arithmetic calculator from ../minimal-agent/demo.py.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

# Reuse the validated AST calculator; do not execute model-supplied Python.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "minimal-agent"))
from demo import ToolError, calculator_tool  # noqa: E402

API_URL = "https://api.openai.com/v1/responses"
INSTRUCTIONS = (
    "You are a calculator assistant. For every requested calculation, use the "
    "calculator tool. Do not calculate from memory. If the tool rejects an "
    "expression, explain the limitation rather than guessing a result."
)
CALCULATOR = {
    "type": "function",
    "name": "calculator",
    "description": "Calculate bounded arithmetic with +, -, *, / and parentheses.",
    "parameters": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
        "additionalProperties": False,
    },
    "strict": True,
}


def request_openai(payload: dict, *, api_key: str, timeout: float = 20.0) -> dict:
    """Issue one Responses API request; never print request headers or secrets."""
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required")
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Model API returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("Model API network request failed") from None
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("Model API returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Model API returned a non-object response")
    return data


def final_text(items: list) -> str:
    """Parse REST output items (SDK-only convenience output_text is not assumed)."""
    texts = []
    for item in items:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    texts.append(text)
    return "\n".join(texts).strip()


def run_agent(
    expression: str,
    *,
    call_model: Callable[[dict], dict],
    model: str = "gpt-4.1-mini",
    max_steps: int = 4,
    max_tool_calls: int = 3,
) -> dict:
    """Return bounded event trace and explicit success/failure status."""
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 200:
        raise ValueError("expression must be 1-200 characters")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be non-empty")
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    if type(max_tool_calls) is not int or max_tool_calls < 1:
        raise ValueError("max_tool_calls must be a positive integer")

    events = []
    calls_used = 0
    prior_id = None
    next_input = [{"role": "user", "content": f"Calculate: {expression}"}]

    def stop(status: str, reason: str, answer: str = "") -> dict:
        events.append({"type": "stop", "status": status, "reason": reason})
        return {
            "status": status, "reason": reason, "output": answer,
            "tool_calls": calls_used, "events": events,
        }

    for step in range(1, max_steps + 1):
        payload = {
            "model": model, "instructions": INSTRUCTIONS,
            "tools": [CALCULATOR], "input": next_input,
            "max_output_tokens": 256,
        }
        if prior_id:
            payload["previous_response_id"] = prior_id
        try:
            response = call_model(payload)
        except Exception:
            return stop("failed", "model_request_failed")
        if not isinstance(response, dict):
            return stop("failed", "invalid_model_response")
        if response.get("status") not in (None, "completed"):
            return stop("failed", "incomplete_model_response")
        output = response.get("output")
        if not isinstance(output, list):
            return stop("failed", "invalid_model_response")
        requested = [
            item for item in output
            if isinstance(item, dict) and item.get("type") == "function_call"
        ]
        if not requested:
            answer = final_text(output)
            if not calls_used:
                return stop("failed", "missing_tool_observation")
            if not answer:
                return stop("failed", "empty_final_answer")
            return stop("completed", "model_finished", answer)

        if calls_used + len(requested) > max_tool_calls:
            return stop("budget_exceeded", "max_tool_calls")
        response_id = response.get("id")
        if not isinstance(response_id, str) or not response_id:
            return stop("failed", "missing_response_id")
        next_input = []
        for item in requested:
            call_id = item.get("call_id")
            if not isinstance(call_id, str) or not call_id:
                return stop("failed", "invalid_call_id")
            if item.get("name") != "calculator":
                return stop("failed", "unknown_tool")
            calls_used += 1
            try:
                arguments = json.loads(item.get("arguments", ""))
                result = calculator_tool(arguments)
                tool_output = {"result": result}
                events.append({"type": "tool_result", "step": step, "tool": "calculator"})
            except (ValueError, TypeError, ToolError) as exc:
                code = exc.code if isinstance(exc, ToolError) else "invalid_arguments"
                tool_output = {"error": {"code": code}}
                events.append({"type": "tool_error", "step": step, "code": code})
            # Do not include raw tool arguments or user content in the trace.
            next_input.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(tool_output),
            })
        prior_id = response_id
    return stop("budget_exceeded", "max_steps")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression", default="(12 + 8) * 3")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-steps", type=int, default=4)
    parser.add_argument("--max-tool-calls", type=int, default=3)
    args = parser.parse_args()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        parser.error("Set OPENAI_API_KEY in your environment; do not commit keys")
    if not 0 < args.timeout <= 120:
        parser.error("--timeout must be > 0 and <= 120")
    try:
        result = run_agent(
            args.expression,
            model=args.model,
            max_steps=args.max_steps,
            max_tool_calls=args.max_tool_calls,
            call_model=lambda payload: request_openai(
                payload, api_key=api_key, timeout=args.timeout
            ),
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
