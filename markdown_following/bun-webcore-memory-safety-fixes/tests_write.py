#!/usr/bin/env python3
"""
Task: bun-webcore-memory-safety-fixes
Repo: oven-sh/bun @ 639bc4351cd7b5daa38b99d47a506dec68e95353
PR:   28494

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Bun's WebCore C++ requires Zig toolchain + custom build system,
so full compilation is not possible in the test container. Tests use:
  1. subprocess to compile standalone C++ concept programs (behavioral)
  2. subprocess to verify git diff against base commit (proves changes applied)
  3. Inline source analysis (verifies fix patterns are correct, without gold-specific details)
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
WEBCORE = f"{REPO}/src/bun.js/bindings/webcore"
BASE_COMMIT = "639bc4351cd7b5daa38b99d47a507dec68e95353"


def _compile_run_cpp(name: str, code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    src = Path(f"{REPO}/_eval_{name}.cpp")
    exe = Path(f"{REPO}/_eval_{name}")
    src.write_text(code)
    try:
        r = subprocess.run(["g++", "-std=c++17", "-o", str(exe), str(src)],
            capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            return r
        return subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
    finally:
        src.unlink(missing_ok=True)
        exe.unlink(missing_ok=True)


def _git_diff(filepath: str) -> str:
    r = subprocess.run(["git", "diff", BASE_COMMIT, "--", filepath],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    return r.stdout


def strip_comments(code: str) -> str:
    result = []
    i = 0
    in_string = None
    while i < len(code):
        c = code[i]
        if in_string:
            result.append(c)
            if c == '\' and i + 1 < len(code):
                result.append(code[i + 1])
                i += 2
                continue
            if c == in_string:
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            result.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < len(code) and code[i + 1] == '/':
            while i < len(code) and code[i] != '
':
                i += 1
            continue
        if c == '/' and i + 1 < len(code) and code[i + 1] == '*':
            i += 2
            while i + 1 < len(code) and not (code[i] == '*' and code[i + 1] == '/'):
                i += 2
            continue
        result.append(c)
        i += 1
    return ''.join(result)


def extract_function(text: str, name: str) -> str | None:
    pat = re.escape(name) + r'[^{]*\{'
    m = re.search(pat, text)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[m.end():i]
    return None


def read_stripped(path: str) -> str:
    return strip_comments(Path(path).read_text())
