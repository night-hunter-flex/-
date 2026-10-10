"""Offline evidence-agent tests: no API key or network required."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("research_agent", Path(__file__).with_name("research_agent.py"))
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def action(name, params, index=1):
    return {"id": f"response_{index}", "status": "completed",
            "output": [{"type": "function_call", "name": name,
                        "call_id": f"call_{index}", "arguments": json.dumps(params)}]}


def search(index=1):
    return action("search_docs", {"query": "Harness budget", "max_hits": 3}, index)


def read(index=2, path="harness.md"):
    return action("read_document", {"path": path, "start_line": 1, "max_lines": 2}, index)


def claim(quote="Harness enforces tool-call budgets"):
    return {"claim": "The Harness enforces tool budgets.", "source": "harness.md",
            "line": 1, "quote": quote}


def report(index=3, claims=None):
    return action("submit_report", {
        "summary": "The harness controls execution budgets.",
        "claims": [claim()] if claims is None else claims,
        "limitations": "Demonstration corpus only.",
    }, index)


class ResearchAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "harness.md").write_text(
            "Harness enforces tool-call budgets and a maximum step count.\n"
            "Every step has a status and event.\n", encoding="utf-8"
        )
        (self.root / "other.md").write_text(
            "Evaluation measures task success and citation quality.\n", encoding="utf-8"
        )
        self.corpus = mod.Corpus(self.root)

    def run_responses(self, responses, **options):
        iterator = iter(responses)
        payloads = []
        def model(payload, timeout):
            payloads.append(payload)
            self.assertGreater(timeout, 0)
            return next(iterator)
        result = mod.run_research("Explain the Harness budget.", self.corpus,
                                  call_model=model, **options)
        return result, payloads

    def test_multi_step_verified_report(self):
        result, payloads = self.run_responses([search(), read(), report()])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["metrics"]["model_calls"], 3)
        self.assertEqual(result["metrics"]["tool_calls"], 3)
        self.assertEqual(result["metrics"]["verified_claims"], 1)
        self.assertEqual(payloads[1]["previous_response_id"], "response_1")
        self.assertEqual(payloads[2]["previous_response_id"], "response_2")
        self.assertEqual(json.loads(payloads[2]["input"][0]["output"])["path"],
                         "harness.md")
        self.assertEqual(result["report"]["claims"][0]["line"], 1)

    def test_read_requires_discovery(self):
        result, _ = self.run_responses([read(1), search(2), read(3), report(4)])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["events"][0]["code"], "path_not_discovered_or_allowed")

    def test_quote_must_match_exact_line(self):
        result, payloads = self.run_responses(
            [search(), read(), report(3, [claim("Invented quote is not in document")]), report(4)]
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["events"][-3]["code"], "quote_not_found")
        self.assertEqual(json.loads(payloads[3]["input"][0]["output"]),
                         {"error": "quote_not_found"})

    def test_unread_citation_fails_closed(self):
        result, _ = self.run_responses([search(), report(2)], max_steps=2)
        self.assertEqual(result["status"], "budget_exceeded")
        self.assertEqual(result["events"][-2]["code"], "source_not_observed")

    def test_path_traversal_denied(self):
        self.corpus.search_docs("budget", 3)
        for path in ("../secret.md", "/etc/passwd", "subdir/../../harness.md"):
            with self.assertRaises(mod.ToolFault):
                self.corpus.read_document(path, 1, 2)

    def test_symlink_file_not_indexed(self):
        outside = self.root.parent / ("external-" + self.root.name + ".md")
        outside.write_text("SECRET NEVER INDEX\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        link = self.root / "external.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable to this user / OS")
        indexed = mod.Corpus(self.root)
        self.assertNotIn("external.md", indexed.docs)

    def test_tool_budget(self):
        result, _ = self.run_responses([search(), read()], max_tool_calls=1)
        self.assertEqual(result["status"], "budget_exceeded")
        self.assertEqual(result["metrics"]["tool_calls"], 1)

    def test_model_request_error(self):
        def fail(_, timeout):
            raise ConnectionError("secret input")
        result = mod.run_research("hello", self.corpus, call_model=fail)
        self.assertEqual(result["reason"], "model_request_failed")
        self.assertNotIn("secret input", json.dumps(result))

    def test_no_plain_message_completion(self):
        response = {"id": "r1", "status": "completed", "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "unsupported answer"}]}
        ]}
        result, _ = self.run_responses([response])
        self.assertEqual(result["reason"], "final_without_verified_report")

    def test_unsupported_tool_cannot_execute(self):
        result, _ = self.run_responses([
            action("run_shell", {"command": "echo SHOULD_NOT_RUN"}, 1)
        ], max_steps=1)
        self.assertEqual(result["status"], "budget_exceeded")
        self.assertEqual(result["events"][-2]["code"], "unknown_tool")

    def test_event_redaction(self):
        result, _ = self.run_responses([search(), read(), report()])
        for event in result["events"]:
            self.assertNotIn("arguments", event)
            self.assertNotIn("quote", event)

    def test_validation_and_tokenizer(self):
        self.assertTrue(mod.word_tokens("工具调用预算"))
        with self.assertRaises(ValueError):
            mod.run_research(" ", self.corpus, call_model=lambda *_: {})
        for limit in (0, True, 301):
            with self.assertRaises(ValueError):
                mod.run_research("question", self.corpus, call_model=lambda *_: {},
                                 max_seconds=limit)
        with self.assertRaises(mod.ToolFault):
            self.corpus.search_docs("budget", 0)

    def test_no_corpus_index_outside_root(self):
        self.assertEqual(set(self.corpus.docs), {"harness.md", "other.md"})
        self.assertTrue(self.corpus.search_docs("budget", 3)["hits"])


if __name__ == "__main__":
    unittest.main()
