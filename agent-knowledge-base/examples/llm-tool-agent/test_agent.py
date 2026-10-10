"""Offline mock-response tests. No network or paid API calls."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("agent.py")
SPEC = importlib.util.spec_from_file_location("llm_tool_agent", MODULE)
agent = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agent
SPEC.loader.exec_module(agent)


def call(arguments, *, id="resp_1", call_id="calc_1"):
    return {
        "id": id, "status": "completed",
        "output": [{
            "type": "function_call", "name": "calculator",
            "call_id": call_id, "arguments": arguments,
        }],
    }


def finish(message):
    return {
        "id": "resp_2", "status": "completed",
        "output": [{"type": "message", "content": [
            {"type": "output_text", "text": message},
        ]}],
    }


class AgentTests(unittest.TestCase):
    def test_tool_round_trip(self):
        seen = []
        responses = iter([call('{"expression":"(12+8)*3"}'), finish("The answer is 60.")])

        def mock(payload):
            seen.append(payload)
            return next(responses)

        result = agent.run_agent("(12+8)*3", call_model=mock)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["tool_calls"], 1)
        self.assertIn("60", result["output"])
        self.assertEqual(seen[1]["previous_response_id"], "resp_1")
        tool_output = seen[1]["input"][0]
        self.assertEqual(tool_output["type"], "function_call_output")
        self.assertEqual(json.loads(tool_output["output"]), {"result": 60.0})

    def test_no_tool_call_is_not_success(self):
        result = agent.run_agent("1 + 1", call_model=lambda _: finish("2"))
        self.assertEqual(result["reason"], "missing_tool_observation")

    def test_tool_budget(self):
        result = agent.run_agent("1+1", max_tool_calls=1,
                                 call_model=lambda _: {"id": "r", "output": [
                                     {"type": "function_call", "name": "calculator",
                                      "call_id": "a", "arguments": '{"expression":"1+1"}'},
                                     {"type": "function_call", "name": "calculator",
                                      "call_id": "b", "arguments": '{"expression":"1+1"}'},
                                 ]})
        self.assertEqual(result["status"], "budget_exceeded")
        self.assertEqual(result["tool_calls"], 0)

    def test_invalid_tool_arguments_can_be_reported(self):
        seen = []
        responses = iter([call('{"expression":"__import__(1)"}'), finish("Unsupported expression")])
        def mock(payload):
            seen.append(payload)
            return next(responses)
        result = agent.run_agent("1+1", call_model=mock)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["events"][0]["type"], "tool_error")
        output = json.loads(seen[1]["input"][0]["output"])
        self.assertEqual(output["error"]["code"], "invalid_expression")

    def test_missing_response_id(self):
        r = call('{"expression":"1+1"}')
        del r["id"]
        self.assertEqual(agent.run_agent("1+1", call_model=lambda _: r)["reason"],
                         "missing_response_id")

    def test_model_error_fails_closed(self):
        def error(_):
            raise RuntimeError("no connection")
        self.assertEqual(agent.run_agent("1+1", call_model=error)["reason"],
                         "model_request_failed")

    def test_step_budget(self):
        result = agent.run_agent("1+1", max_steps=1,
                                 call_model=lambda _: call('{"expression":"1+1"}'))
        self.assertEqual(result["reason"], "max_steps")

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            agent.run_agent(" " * 2, call_model=lambda _: {})
        with self.assertRaises(ValueError):
            agent.run_agent("1+1", max_steps=0, call_model=lambda _: {})


if __name__ == "__main__":
    unittest.main()
