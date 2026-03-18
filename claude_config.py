from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_SERVER_NAME = "demoMcp"


def find_project_root() -> Path:
    return Path(__file__).resolve().parent


def detect_python_path(project_root: Path) -> Path:
    candidates = [
        project_root / ".venv" / "Scripts" / "python.exe",
        project_root / ".venv" / "bin" / "python",
        Path(sys.executable),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not find a Python interpreter. Create .venv first or pass --python-path."
    )


def detect_server_path(project_root: Path) -> Path:
    server_path = project_root / "server.py"
    if not server_path.exists():
        raise FileNotFoundError(f"Could not find server.py at {server_path}")
    return server_path.resolve()


def build_server_config(
    project_root: Path,
    python_path: Path | None = None,
) -> dict[str, Any]:
    command_path = python_path.resolve() if python_path else detect_python_path(project_root)
    server_path = detect_server_path(project_root)

    return {
        "command": str(command_path),
        "args": [
            str(server_path),
            "--transport",
            "stdio",
        ],
    }


def build_config(
    project_root: Path,
    server_name: str = DEFAULT_SERVER_NAME,
    python_path: Path | None = None,
) -> dict[str, Any]:
    return {
        "mcpServers": {
            server_name: build_server_config(project_root, python_path=python_path),
        }
    }


def merge_config(
    existing_config: dict[str, Any],
    server_name: str,
    server_config: dict[str, Any],
) -> dict[str, Any]:
    merged_config = dict(existing_config)
    existing_servers = merged_config.get("mcpServers", {})
    if not isinstance(existing_servers, dict):
        raise ValueError("Existing config has a non-object mcpServers value.")

    merged_servers = dict(existing_servers)
    merged_servers[server_name] = server_config
    merged_config["mcpServers"] = merged_servers
    return merged_config


def load_config(path: Path) -> dict[str, Any]:
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} does not contain valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level JSON object.")

    return data


def write_json(path: Path, data: dict[str, Any], indent: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Claude Desktop MCP config for this repo."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Write the config to a file. If the file already exists, the server entry "
            "is merged into its mcpServers object unless --replace is set."
        ),
    )
    parser.add_argument(
        "--python-path",
        type=Path,
        help="Override the Python interpreter used in the generated config.",
    )
    parser.add_argument(
        "--server-name",
        default=DEFAULT_SERVER_NAME,
        help=f"Claude Desktop server name to generate. Default: {DEFAULT_SERVER_NAME}",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace the output file instead of merging with an existing config.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for generated JSON. Default: 2",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = find_project_root()

    try:
        generated_config = build_config(
            project_root=project_root,
            server_name=args.server_name,
            python_path=args.python_path,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not args.output:
        json.dump(generated_config, sys.stdout, indent=args.indent)
        sys.stdout.write("\n")
        return 0

    final_config = generated_config
    if args.output.exists() and not args.replace:
        try:
            existing_config = load_config(args.output)
            server_config = generated_config["mcpServers"][args.server_name]
            final_config = merge_config(existing_config, args.server_name, server_config)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    write_json(args.output, final_config, args.indent)
    print(f"Wrote Claude Desktop config to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
