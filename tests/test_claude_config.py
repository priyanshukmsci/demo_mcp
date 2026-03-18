import shutil
import unittest
from pathlib import Path

from claude_config import DEFAULT_SERVER_NAME, build_config, merge_config

TEST_TMP_ROOT = Path(__file__).resolve().parent / ".tmp"


class ClaudeConfigTests(unittest.TestCase):
    def make_project_root(self, name: str) -> Path:
        TEST_TMP_ROOT.mkdir(exist_ok=True)
        project_root = TEST_TMP_ROOT / name
        if project_root.exists():
            shutil.rmtree(project_root)
        project_root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(project_root, ignore_errors=True))
        return project_root

    def test_build_config_uses_absolute_repo_paths(self) -> None:
        project_root = self.make_project_root("project_one")
        python_path = project_root / "venv" / "Scripts" / "python.exe"
        server_path = project_root / "server.py"

        python_path.parent.mkdir(parents=True)
        python_path.write_text("", encoding="utf-8")
        server_path.write_text("print('demo')\n", encoding="utf-8")

        config = build_config(project_root, python_path=python_path)
        server_config = config["mcpServers"][DEFAULT_SERVER_NAME]

        self.assertEqual(server_config["command"], str(python_path.resolve()))
        self.assertEqual(
            server_config["args"],
            [str(server_path.resolve()), "--transport", "stdio"],
        )

    def test_merge_config_preserves_other_settings(self) -> None:
        project_root = self.make_project_root("project_two")
        python_path = project_root / "venv" / "Scripts" / "python.exe"
        server_path = project_root / "server.py"

        python_path.parent.mkdir(parents=True)
        python_path.write_text("", encoding="utf-8")
        server_path.write_text("print('demo')\n", encoding="utf-8")

        generated = build_config(project_root, python_path=python_path)
        server_config = generated["mcpServers"][DEFAULT_SERVER_NAME]
        existing = {
            "theme": "light",
            "mcpServers": {
                "otherServer": {
                    "command": "python",
                    "args": ["other_server.py"],
                }
            },
        }

        merged = merge_config(existing, DEFAULT_SERVER_NAME, server_config)

        self.assertEqual(merged["theme"], "light")
        self.assertIn("otherServer", merged["mcpServers"])
        self.assertEqual(merged["mcpServers"][DEFAULT_SERVER_NAME], server_config)


if __name__ == "__main__":
    unittest.main()
