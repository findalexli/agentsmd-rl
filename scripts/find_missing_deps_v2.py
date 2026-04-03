#!/usr/bin/env python3
"""
Extended analysis: also check test.sh for pip/pytest invocations,
and show ALL non-stdlib imports (not just known third-party).
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TASKS_DIR = Path("/home/alex/agentsmd-rl/harbor_tasks")

# Python stdlib modules
STDLIB = {
    "os", "sys", "re", "ast", "json", "pathlib", "subprocess", "shutil",
    "tempfile", "unittest", "typing", "collections", "functools", "itertools",
    "copy", "io", "abc", "math", "random", "hashlib", "base64", "hmac",
    "time", "datetime", "calendar", "logging", "warnings", "traceback",
    "inspect", "types", "dataclasses", "enum", "contextlib", "textwrap",
    "string", "struct", "codecs", "unicodedata", "difflib", "pprint",
    "reprlib", "operator", "decimal", "fractions", "statistics",
    "array", "bisect", "heapq", "queue", "weakref",
    "threading", "multiprocessing", "concurrent", "asyncio",
    "socket", "http", "urllib", "email", "html", "xml", "csv",
    "configparser", "argparse", "getopt", "optparse",
    "signal", "errno", "ctypes", "platform", "resource", "pty", "tty",
    "glob", "fnmatch", "stat", "fileinput", "linecache", "tokenize",
    "dis", "compileall", "py_compile", "pdb", "profile", "cProfile",
    "timeit", "trace", "gc", "site", "sysconfig",
    "importlib", "pkgutil", "zipimport", "zipfile", "gzip", "bz2", "lzma",
    "tarfile", "shelve", "dbm", "sqlite3", "pickle", "marshal",
    "select", "selectors", "mmap", "fcntl", "termios",
    "token", "keyword", "builtins", "_thread", "posixpath",
    "tomllib", "graphlib", "zoneinfo", "secrets", "contextvars",
    "numbers", "ssl", "uuid", "__future__",
    "typing_extensions",  # often bundled
}

# Import name -> pip package
KNOWN_MAPPING = {
    "torch": "torch",
    "transformers": "transformers",
    "numpy": "numpy",
    "scipy": "scipy",
    "httpx": "httpx",
    "pydantic": "pydantic",
    "ruff": "ruff",
    "yaml": "pyyaml",
    "toml": "toml",
    "tomli": "tomli",
    "requests": "requests",
    "aiohttp": "aiohttp",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pytest": "pytest",
    "accelerate": "accelerate",
    "datasets": "datasets",
    "tokenizers": "tokenizers",
    "safetensors": "safetensors",
    "tqdm": "tqdm",
    "PIL": "pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
    "flask": "flask",
    "click": "click",
    "attrs": "attrs",
    "attr": "attrs",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "msgpack": "msgpack",
    "packaging": "packaging",
    "setuptools": "setuptools",
    "black": "black",
    "isort": "isort",
    "mypy": "mypy",
    "rich": "rich",
    "starlette": "starlette",
    "peft": "peft",
    "wandb": "wandb",
    "regex": "regex",
    "filelock": "filelock",
    "huggingface_hub": "huggingface-hub",
    "sentencepiece": "sentencepiece",
    "psutil": "psutil",
    "docker": "docker",
    "openai": "openai",
    "tiktoken": "tiktoken",
    "gradio": "gradio",
    "gradio_client": "gradio-client",
    "_pytest": "pytest",
}


def get_failing_gold_tasks():
    """Return set of task names where latest verdict is fail/fail_gold with gold=0."""
    tasks = []
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir():
            continue
        status_path = task_dir / "status.json"
        if not status_path.exists():
            continue
        try:
            data = json.loads(status_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        for entry in reversed(data.get("validations", [])):
            verdict = entry.get("verdict")
            if verdict:
                gold = entry.get("gold_score") or entry.get("gold")
                if verdict in ("fail", "fail_gold") and gold in (0, 0.0, "0", "0.0"):
                    tasks.append(task_dir.name)
                break
    return tasks


def extract_imports(py_path: Path):
    """Extract top-level module names from import statements."""
    if not py_path.exists():
        return set()
    imports = set()
    text = py_path.read_text()
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'^import\s+([\w.]+)', line)
        if m:
            imports.add(m.group(1).split('.')[0])
        m = re.match(r'^from\s+([\w.]+)\s+import', line)
        if m:
            imports.add(m.group(1).split('.')[0])
    return imports


def extract_pip_installs(dockerfile_path: Path):
    """Extract package names installed via pip in a Dockerfile."""
    if not dockerfile_path.exists():
        return set(), False
    text = dockerfile_path.read_text()
    text_joined = re.sub(r'\\\n', ' ', text)

    installed = set()
    has_editable = False

    for line in text_joined.splitlines():
        if 'pip install' in line and '-e' in line:
            has_editable = True
        pips = re.findall(r'(?:pip3?|python3?\s+-m\s+pip)\s+install\s+([^&|;]+)', line)
        for pip_args in pips:
            tokens = pip_args.split()
            for tok in tokens:
                if tok.startswith('-'):
                    continue
                if tok.startswith('http'):
                    continue
                pkg = re.split(r'[=><!\[;]', tok)[0].strip().lower()
                if pkg and not pkg.startswith('/') and not pkg.startswith('.'):
                    installed.add(pkg)
    return installed, has_editable


def check_test_sh(task_dir: Path):
    """Check test.sh for clues about what's being invoked."""
    test_sh = task_dir / "tests" / "test.sh"
    if not test_sh.exists():
        return {}
    text = test_sh.read_text()
    info = {}
    if "pytest" in text or "python -m pytest" in text:
        info["uses_pytest"] = True
    if "pip install" in text:
        info["pip_in_test_sh"] = True
    return info


def main():
    failing_tasks = get_failing_gold_tasks()
    print(f"Total tasks with gold=0 (fail/fail_gold): {len(failing_tasks)}\n")

    # Track all non-stdlib imports across failing tasks
    all_imports = defaultdict(list)  # import_name -> [task_names]
    missing_by_package = defaultdict(list)  # pip_pkg -> [task_names]
    task_details = {}

    for task_name in failing_tasks:
        task_dir = TASKS_DIR / task_name
        test_py = task_dir / "tests" / "test_outputs.py"
        dockerfile = task_dir / "environment" / "Dockerfile"

        if not test_py.exists():
            continue

        imports = extract_imports(test_py)
        pip_installed, has_editable = extract_pip_installs(dockerfile)
        test_sh_info = check_test_sh(task_dir)

        non_stdlib = {i for i in imports if i not in STDLIB}

        for imp in non_stdlib:
            all_imports[imp].append(task_name)

        # Check known third-party
        missing = set()
        for imp in non_stdlib:
            if imp in KNOWN_MAPPING:
                pip_name = KNOWN_MAPPING[imp]
                if pip_name.lower() not in pip_installed and imp.lower() not in pip_installed:
                    missing.add(f"{pip_name} (import {imp})")

        task_details[task_name] = {
            "imports": non_stdlib,
            "pip_installed": pip_installed,
            "has_editable": has_editable,
            "missing_known": missing,
            "test_sh": test_sh_info,
        }

        for m in missing:
            pkg = m.split(" (")[0]
            missing_by_package[pkg].append(task_name)

    # Summary table
    print(f"{'='*90}")
    print("MISSING KNOWN THIRD-PARTY PACKAGES (in test_outputs.py imports vs Dockerfile pip)")
    print(f"{'='*90}")

    sorted_pkgs = sorted(missing_by_package.items(), key=lambda x: -len(x[1]))
    print(f"\n{'Package':<25} {'Count':<8} {'Tasks'}")
    print(f"{'-'*25} {'-'*8} {'-'*55}")
    for pkg, tasks in sorted_pkgs:
        task_list = ", ".join(tasks[:8])
        if len(tasks) > 8:
            task_list += f", ... (+{len(tasks)-8} more)"
        print(f"{pkg:<25} {len(tasks):<8} {task_list}")

    # All non-stdlib imports frequency
    print(f"\n{'='*90}")
    print("ALL NON-STDLIB IMPORTS in test_outputs.py across gold=0 tasks")
    print(f"{'='*90}")
    sorted_imports = sorted(all_imports.items(), key=lambda x: -len(x[1]))
    print(f"\n{'Import':<25} {'Count':<8} {'Sample tasks'}")
    print(f"{'-'*25} {'-'*8} {'-'*55}")
    for imp, tasks in sorted_imports:
        sample = ", ".join(tasks[:5])
        if len(tasks) > 5:
            sample += f", ... (+{len(tasks)-5} more)"
        print(f"{imp:<25} {len(tasks):<8} {sample}")

    # Tasks with editable installs (likely have repo deps covered)
    editable_count = sum(1 for d in task_details.values() if d["has_editable"])
    print(f"\n{'='*90}")
    print(f"Tasks with `pip install -e` (editable): {editable_count} / {len(task_details)}")
    print(f"{'='*90}")

    # Show tasks that have NO editable install and import non-trivial packages
    print(f"\n{'='*90}")
    print("TASKS WITHOUT EDITABLE INSTALL importing repo-specific modules")
    print("(These might need `pip install -e .` or explicit deps)")
    print(f"{'='*90}")
    for task_name, info in sorted(task_details.items()):
        if not info["has_editable"]:
            unknown = info["imports"] - set(KNOWN_MAPPING.keys())
            if unknown:
                print(f"  {task_name}: unknown imports = {', '.join(sorted(unknown))}")

    # Per-task detail for tasks with missing known deps
    print(f"\n{'='*90}")
    print("PER-TASK: MISSING KNOWN DEPS")
    print(f"{'='*90}")
    for task_name, info in sorted(task_details.items()):
        if info["missing_known"]:
            print(f"  {task_name}:")
            print(f"    missing: {', '.join(sorted(info['missing_known']))}")
            print(f"    installed: {', '.join(sorted(info['pip_installed']))}")


if __name__ == "__main__":
    main()
