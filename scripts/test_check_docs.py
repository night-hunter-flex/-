import tempfile
import unittest
from pathlib import Path

from check_docs import check, iter_links


class LinkCheckerTests(unittest.TestCase):
    def test_missing_relative_target_is_reported_with_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")
            errors, files, links = check(root)
            self.assertEqual((files, links), (1, 1))
            self.assertIn("README.md:1: missing local target", errors[0])

    def test_paths_spaces_fragments_and_external_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs" / "a file.md").write_text("# A\n", encoding="utf-8")
            (root / "README.md").write_text(
                '[a](docs/a%20file.md#section)\n[b](<docs/a file.md>)\n'
                '[c](/docs/a%20file.md)\n[d](https://example.com/a)\n[e](#section)\n',
                encoding="utf-8",
            )
            errors, _, links = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(links, 3)

    def test_fenced_and_inline_code_are_ignored(self):
        content = (chr(96) * 3 + "\n[x](missing.md)\n" + chr(96) * 3 + "\n"
                   "~~~text\n[y](missing.md)\n~~~\n" + chr(96)
                   + "[z](missing.md)" + chr(96) + "\n[real](exists.md)")
        self.assertEqual(list(iter_links(content)), [(8, "exists.md")])

    def test_link_cannot_leave_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "README.md").write_text("[outside](../other.md)", encoding="utf-8")
            errors, _, _ = check(root)
            self.assertIn("target leaves repository", errors[0])

    def test_ignored_directories_do_not_add_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / ".git" / "ignored.md").write_text("[x](missing.md)", encoding="utf-8")
            self.assertEqual(check(root), ([], 0, 0))


if __name__ == "__main__":
    unittest.main()
