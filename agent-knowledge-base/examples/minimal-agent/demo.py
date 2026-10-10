"""Offline harness demo. A deterministic policy replaces the language model."""
from __future__ import annotations

import argparse
import ast
import copy
import json
import math
import operator
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Action:
    kind: str
    tool: str = ""
    arguments: dict = field(default_factory=dict)
    output: str = ""


class ToolError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


def calculate(expression: str) -> float:
    """Evaluate a bounded arithmetic AST, never Python eval/exec."""
    if not isinstance(expression, str) or not expression.strip():
        raise ToolError("invalid_expression", "Expected a non-empty string")
    if len(expression) > 200:
        raise ToolError("invalid_expression", "Expression exceeds 200 characters")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ToolError("invalid_expression", "Invalid arithmetic syntax") from exc
    if sum(1 for _ in ast.walk(tree)) > 64:
        raise ToolError("invalid_expression", "Expression exceeds 64 AST nodes")
    operations = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
    }

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](visit(node.left), visit(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            value = visit(node.operand)
            if isinstance(node.op, ast.USub):
                value = -value
        else:
            raise ToolError("invalid_expression", "Only numbers and + - * / are allowed")
        if not math.isfinite(value) or abs(value) > 1e12:
            raise ToolError("invalid_expression", "Number is non-finite or exceeds 1e12")
        return float(value)

    try:
        return visit(tree.body)
    except ZeroDivisionError as exc:
        raise ToolError("division_by_zero", "Division by zero") from exc


def calculator_tool(arguments: dict) -> float:
    if not isinstance(arguments, dict) or set(arguments) != {"expression"}:
        raise ToolError("invalid_arguments", "Expected exactly the expression field")
    return calculate(arguments["expression"])


def scripted_policy(expression: str) -> Callable[[list[dict]], Action]:
    """A rule-based policy: request the tool, then finish from its observation."""
    def choose(events: list[dict]) -> Action:
        observations = [e for e in events if e["type"] == "tool_result"]
        if observations:
            return Action("finish", output=f"result={observations[-1]['result']:g}")
        return Action("tool", "calculator", {"expression": expression})
    return choose


def run_agent(
    policy: Callable[[list[dict]], Action], *,
    max_steps: int = 4, max_tool_calls: int = 3, max_retries: int = 1,
    tools: dict[str, Callable[[dict], float]] | None = None,
) -> dict:
    for name, limit in (
        ("max_steps", max_steps), ("max_tool_calls", max_tool_calls),
        ("max_retries", max_retries),
    ):
        if type(limit) is not int or limit < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    registry = {"calculator": calculator_tool} if tools is None else tools
    events: list[dict] = []
    calls = 0

    def stop(status: str, reason: str, output: str = "") -> dict:
        events.append({"type": "stop", "status": status, "reason": reason})
        return {"status": status, "reason": reason, "output": output,
                "tool_calls": calls, "events": events}

    for step in range(1, max_steps + 1):
        # Give the policy observations without letting it rewrite the trace.
        try:
            action = policy(copy.deepcopy(events))
        except Exception as exc:
            events.append({"type": "policy_error", "step": step,
                           "error": type(exc).__name__})
            return stop("failed", "policy_error")
        if not isinstance(action, Action):
            return stop("failed", "invalid_action")
        events.append({"type": "decision", "step": step, "kind": action.kind,
                       "tool": action.tool})
        if action.kind == "finish":
            if not isinstance(action.output, str) or not action.output.strip():
                return stop("failed", "empty_output")
            if not any(e["type"] == "tool_result" for e in events):
                return stop("failed", "missing_observation")
            # This demo only verifies there is an observation, not factual quality.
            return stop("completed", "policy_finished", action.output)
        if action.kind != "tool":
            return stop("failed", "invalid_action")
        if not isinstance(action.tool, str) or action.tool not in registry:
            return stop("failed", "unknown_tool")
        if not isinstance(action.arguments, dict):
            return stop("failed", "invalid_arguments")
        # Validate this demo's calculator contract before counting an execution.
        if action.tool == "calculator" and (
            set(action.arguments) != {"expression"}
            or not isinstance(action.arguments["expression"], str)
        ):
            return stop("failed", "invalid_arguments")

        for attempt in range(max_retries + 1):
            if calls >= max_tool_calls:
                return stop("budget_exceeded", "max_tool_calls")
            calls += 1
            events.append({"type": "tool_call", "step": step, "tool": action.tool,
                           "attempt": attempt + 1,
                           "arguments": copy.deepcopy(action.arguments)})
            try:
                result = registry[action.tool](copy.deepcopy(action.arguments))
                if type(result) not in (int, float) or not math.isfinite(result):
                    raise ToolError("invalid_result", "Expected a finite number")
            except ToolError as exc:
                events.append({"type": "tool_error", "step": step, "code": exc.code,
                               "message": str(exc), "retryable": exc.retryable})
                if not exc.retryable or attempt == max_retries:
                    return stop("failed", exc.code)
            except Exception as exc:
                events.append({"type": "tool_error", "step": step,
                               "code": "unexpected_tool_error",
                               "error": type(exc).__name__, "retryable": False})
                return stop("failed", "unexpected_tool_error")
            else:
                events.append({"type": "tool_result", "step": step,
                               "tool": action.tool, "result": result})
                break
    return stop("budget_exceeded", "max_steps")


def run_expression(expression: str, *, fail_first: bool = False, **limits) -> dict:
    first = True

    def tool(arguments: dict) -> float:
        nonlocal first
        if first and fail_first:
            first = False
            raise ToolError("temporary_unavailable", "Simulated transient failure", True)
        return calculator_tool(arguments)

    return run_agent(scripted_policy(expression), tools={"calculator": tool}, **limits)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression", default="(12 + 8) * 3")
    parser.add_argument("--fail-first", action="store_true")
    parser.add_argument("--max-steps", type=int, default=4)
    parser.add_argument("--max-tool-calls", type=int, default=3)
    parser.add_argument("--max-retries", type=int, default=1)
    args = parser.parse_args()
    try:
        result = run_expression(
            args.expression, fail_first=args.fail_first,
            max_steps=args.max_steps, max_tool_calls=args.max_tool_calls,
            max_retries=args.max_retries,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
