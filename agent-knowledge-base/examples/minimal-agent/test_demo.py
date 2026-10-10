import json
import unittest
from pathlib import Path

from demo import Action, ToolError, calculate, run_agent, run_expression
from run_eval import evaluate


class CalculatorTests(unittest.TestCase):
    def test_arithmetic_and_whitespace(self):
        self.assertEqual(calculate("  (12 + 8) * 3  "), 60)
        self.assertEqual(calculate("-2.5 + 4 / 2"), -0.5)

    def test_code_and_non_numeric_syntax_are_rejected(self):
        for expression in ("abs(-1)", "x + 1", "'abc'", "True", "[1]",
                           "2 ** 999999", "1 // 2", "__import__('os')"):
            with self.subTest(expression=expression), self.assertRaises(ToolError):
                calculate(expression)

    def test_size_and_value_limits(self):
        for expression in ("1" * 201, "1e309", "1000000000001",
                           "10000000 * 10000000", "1+" * 30 + "1"):
            with self.subTest(expression=expression), self.assertRaises(ToolError):
                calculate(expression)

    def test_zero_and_bad_syntax(self):
        for expression in ("1 / 0", "1 +", "", "\x00"):
            with self.subTest(expression=expression), self.assertRaises(ToolError):
                calculate(expression)


class HarnessTests(unittest.TestCase):
    def test_transient_failure_recovers_and_trace_is_ordered(self):
        result = run_expression("12 / 3", fail_first=True)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["output"], "result=4")
        self.assertEqual(result["tool_calls"], 2)
        self.assertEqual([e["type"] for e in result["events"]], [
            "decision", "tool_call", "tool_error", "tool_call",
            "tool_result", "decision", "stop",
        ])

    def test_permanent_failure_is_not_retried(self):
        result = run_expression("1 / 0", max_retries=5)
        self.assertEqual(result["reason"], "division_by_zero")
        self.assertEqual(result["tool_calls"], 1)

    def test_retry_and_call_budget_stop(self):
        failed = run_expression("1+1", fail_first=True, max_retries=0)
        limited = run_expression("1+1", fail_first=True, max_tool_calls=1)
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(limited["status"], "budget_exceeded")
        self.assertEqual(limited["tool_calls"], 1)

    def test_unknown_tool_and_schema_never_execute(self):
        calls = []
        registry = {"calculator": lambda args: calls.append(args)}
        actions = [
            Action("tool", "shell", {"command": "anything"}),
            Action("tool", "calculator", {"expression": "1", "extra": 2}),
            Action("tool", "calculator", {"expression": 1}),
            Action("tool", "calculator", []),
        ]
        for action in actions:
            with self.subTest(action=action):
                result = run_agent(lambda events: action, tools=registry)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["tool_calls"], 0)
        self.assertEqual(calls, [])

    def test_repeated_policy_hits_decision_budget(self):
        policy = lambda events: Action("tool", "calculator", {"expression": "1"})
        result = run_agent(policy, max_steps=2, max_tool_calls=20)
        self.assertEqual(result["reason"], "max_steps")
        self.assertEqual(result["tool_calls"], 2)

    def test_policy_cannot_mutate_observations(self):
        def policy(events):
            events.clear()
            return Action("tool", "calculator", {"expression": "1"})
        result = run_agent(policy, max_steps=2)
        self.assertEqual(sum(e["type"] == "tool_result" for e in result["events"]), 2)

    def test_finish_requires_observation_and_output(self):
        self.assertEqual(run_agent(lambda _: Action("finish", output="done"))["reason"],
                         "missing_observation")
        self.assertEqual(run_agent(lambda _: Action("finish"))["reason"], "empty_output")

    def test_unexpected_tool_failure_has_terminal_state(self):
        def broken(_):
            raise RuntimeError("broken")
        result = run_agent(lambda _: Action("tool", "calculator", {"expression": "1"}),
                           tools={"calculator": broken})
        self.assertEqual(result["reason"], "unexpected_tool_error")

    def test_invalid_policy_and_non_finite_result(self):
        self.assertEqual(run_agent(lambda _: None)["reason"], "invalid_action")
        result = run_agent(lambda _: Action("tool", "calculator", {"expression": "1"}),
                           tools={"calculator": lambda _: float("nan")})
        self.assertEqual(result["reason"], "invalid_result")

    def test_zero_and_invalid_budgets(self):
        self.assertEqual(run_expression("1", max_steps=0)["reason"], "max_steps")
        self.assertEqual(run_expression("1", max_tool_calls=0)["tool_calls"], 0)
        for value in (-1, True, 0.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run_expression("1", max_steps=value)


class EvaluationTests(unittest.TestCase):
    def test_all_fixtures_match_expected_behavior(self):
        cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
        report = evaluate(cases)
        self.assertEqual(report["behavior_passed"], 8)
        self.assertEqual(report["completed_count"], 3)

    def test_wrong_expected_value_is_detected(self):
        report = evaluate([{"id": "bad", "expression": "1 + 1",
                            "expected_status": "completed",
                            "expected_reason": "policy_finished", "expected_result": 3}])
        self.assertEqual(report["behavior_passed"], 0)


if __name__ == "__main__":
    unittest.main()
