#!/usr/bin/env python3
"""
Task: biome-docs-break-down-skills-improve
Repo: biomejs/biome @ eb57e3a1df36bf1bbe612f84a68ded658d9b7d00
PR:   9613

Break down and improve agent skills: extract changeset and pull-request
into dedicated skills, add Code Comments guidance to biome-developer,
add non-interactive changeset command to justfile.
"""

import subprocess

REPO = "/workspace/biome"


def _run_validator(script: str) -> subprocess.CompletedProcess:
    """Run a validation script as a subprocess and return the result."""
    return subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )


# ── Pass-to-pass tests ──────────────────────────────────────────────

def test_justfile_syntax():
    """justfile must be parseable and retain existing recipes."""
    r = _run_validator(r"""
import re, sys
text = open("/workspace/biome/justfile").read()
recipes = set(re.findall(r'^([a-zA-Z_][\w-]*):', text, re.MULTILINE))
required = {'new-changeset', 'ready'}
missing = required - recipes
if missing:
    print(f"Missing recipes: {sorted(missing)}", file=sys.stderr)
    sys.exit(1)
print(f"OK: found {len(recipes)} recipes")
""")
    assert r.returncode == 0, f"justfile recipe check failed: {r.stderr}"


def test_justfile_valid_structure():
    """Repo justfile has valid structure with no unclosed blocks (pass_to_pass)."""
    r = _run_validator(r"""
import sys
text = open("/workspace/biome/justfile").read()
lines = text.split('\n')
errors = []
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        continue
    single_braces = stripped.replace('{{', '').replace('}}', '')
    if single_braces.count('{') != single_braces.count('}'):
        errors.append(f"Line {i}: Unmatched braces")
if errors:
    for e in errors:
        print(e, file=sys.stderr)
    sys.exit(1)
print("OK")
""")
    assert r.returncode == 0, f"justfile structure validation failed:\n{r.stderr}"


def test_existing_skills_intact():
    """Other existing skill files should still be present."""
    r = _run_validator(r"""
import os, sys
skills_dir = "/workspace/biome/.claude/skills"
required = ["biome-developer", "testing-codegen", "lint-rule-development",
            "formatter-development", "parser-development"]
missing = [d for d in required
           if not os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))]
if missing:
    print(f"Missing: {missing}", file=sys.stderr)
    sys.exit(1)
print(f"OK: all {len(required)} skills present")
""")
    assert r.returncode == 0, f"Missing skills: {r.stderr}"


def test_skill_files_valid_frontmatter():
    """All skill files have valid YAML frontmatter with required fields (pass_to_pass)."""
    r = _run_validator(r"""
import re, os, yaml, sys, json

skills_dir = "/workspace/biome/.claude/skills"
errors = []
results = {}

for skill_name in sorted(os.listdir(skills_dir)):
    skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
    if not os.path.isfile(skill_path):
        continue
    text = open(skill_path).read()
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        errors.append(f"{skill_name}: No YAML frontmatter")
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        errors.append(f"{skill_name}: Invalid YAML: {e}")
        continue
    if not isinstance(fm, dict):
        errors.append(f"{skill_name}: Frontmatter not a mapping")
        continue
    for field in ['name', 'description', 'compatibility']:
        if field not in fm:
            errors.append(f"{skill_name}: Missing '{field}'")
    if fm.get('name') != skill_name:
        errors.append(f"{skill_name}: name mismatch '{fm.get('name')}'")
    results[skill_name] = True

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(json.dumps(results))
""")
    assert r.returncode == 0, f"Frontmatter validation failed:\n{r.stderr}"


def test_readme_valid_structure():
    """Skills README.md has valid structure and required sections (pass_to_pass)."""
    r = _run_validator(r"""
import re, sys
text = open("/workspace/biome/.claude/skills/README.md").read()
headings = re.findall(r'^##\s+(.+)$', text, re.MULTILINE)
required = {"What Are Skills?", "Available Skills", "Quick Workflow Guide", "File Organization"}
found = set(headings)
missing = required - found
if missing:
    print(f"Missing sections: {missing}", file=sys.stderr)
    sys.exit(1)
table_lines = [l for l in text.split('\n') if l.strip().startswith('|') and l.count('|') >= 3]
if not table_lines:
    print("No markdown table found", file=sys.stderr)
    sys.exit(1)
print(f"OK: {len(headings)} sections, {len(table_lines)} table rows")
""")
    assert r.returncode == 0, f"README structure failed:\n{r.stderr}"


def test_cargo_toml_valid():
    """Cargo.toml has valid workspace structure (pass_to_pass)."""
    r = _run_validator(r"""
import sys
text = open("/workspace/biome/Cargo.toml").read()
for required in ['[workspace]', 'members']:
    if required not in text:
        print(f"Missing: {required}", file=sys.stderr)
        sys.exit(1)
for dep in ['biome_analyze', 'biome_cli', 'biome_formatter']:
    if dep not in text:
        print(f"Missing dep: {dep}", file=sys.stderr)
        sys.exit(1)
print("OK")
""")
    assert r.returncode == 0, f"Cargo.toml check failed:\n{r.stderr}"


# ── Fail-to-pass tests ─────────────────────────────────────────────

def test_justfile_recipe_runs():
    """new-changeset-empty recipe must exist and invoke pnpm changeset --empty."""
    # Verify recipe is registered (fails on base where recipe doesn't exist)
    r = subprocess.run(
        ["just", "--list"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "new-changeset-empty" in r.stdout, \
        f"Recipe 'new-changeset-empty' not found in just --list: {r.stdout[:500]}"

    # Verify the recipe actually invokes pnpm (may fail if pnpm not installed,
    # but the recipe must at least attempt the right program)
    r2 = subprocess.run(
        ["just", "new-changeset-empty"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    combined = r2.stdout + r2.stderr
    assert "pnpm" in combined.lower(), \
        f"Recipe did not invoke pnpm. Output: {combined[:500]}"
    print(f"OK: recipe listed and executed (exit={r2.returncode})")


def test_justfile_new_changeset_empty_recipe():
    """justfile must define new-changeset-empty recipe invoking pnpm changeset --empty."""
    r = _run_validator(r"""
import re, sys
text = open("/workspace/biome/justfile").read()
pattern = r'^(new-changeset-empty)\s*:\s*\n((?:[ \t]+.*\n)*)'
m = re.search(pattern, text, re.MULTILINE)
if not m:
    print("Recipe 'new-changeset-empty' not found", file=sys.stderr)
    sys.exit(1)
body = m.group(2)
missing = []
if 'pnpm' not in body: missing.append('pnpm')
if 'changeset' not in body: missing.append('changeset')
if '--empty' not in body: missing.append('--empty')
if missing:
    print(f"Recipe body missing: {missing}", file=sys.stderr)
    sys.exit(1)
print(f"OK: recipe body = {body.strip()!r}")
""")
    assert r.returncode == 0, f"Recipe validation failed: {r.stderr}"


def test_changeset_skill_valid_frontmatter():
    """changeset/SKILL.md must exist with valid YAML frontmatter and reference the just command."""
    r = _run_validator(r"""
import re, yaml, sys

path = "/workspace/biome/.claude/skills/changeset/SKILL.md"
try:
    text = open(path).read()
except FileNotFoundError:
    print("changeset/SKILL.md does not exist", file=sys.stderr)
    sys.exit(1)

m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
if not m:
    print("No YAML frontmatter", file=sys.stderr)
    sys.exit(1)

fm = yaml.safe_load(m.group(1))
if not isinstance(fm, dict):
    print("Frontmatter is not a mapping", file=sys.stderr)
    sys.exit(1)

errors = []
if fm.get('name') != 'changeset':
    errors.append(f"name should be 'changeset', got '{fm.get('name')}'")
if not fm.get('description'):
    errors.append("missing description")
if not fm.get('compatibility'):
    errors.append("missing compatibility")

body = text[m.end():]
if not re.search(r'just\s+\S*changeset', body):
    errors.append("body does not reference a 'just *changeset*' command")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK: name={fm['name']}, desc length={len(fm['description'])}")
""")
    assert r.returncode == 0, f"changeset skill validation failed: {r.stderr}"


def test_pull_request_skill_valid_frontmatter():
    """pull-request/SKILL.md must exist with valid YAML frontmatter and required sections."""
    r = _run_validator(r"""
import re, yaml, sys

path = "/workspace/biome/.claude/skills/pull-request/SKILL.md"
try:
    text = open(path).read()
except FileNotFoundError:
    print("pull-request/SKILL.md does not exist", file=sys.stderr)
    sys.exit(1)

m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
if not m:
    print("No YAML frontmatter", file=sys.stderr)
    sys.exit(1)

fm = yaml.safe_load(m.group(1))
if not isinstance(fm, dict):
    print("Frontmatter not a mapping", file=sys.stderr)
    sys.exit(1)

errors = []
if fm.get('name') != 'pull-request':
    errors.append(f"name should be 'pull-request', got '{fm.get('name')}'")
if not fm.get('description'):
    errors.append("missing description")
if not fm.get('compatibility'):
    errors.append("missing compatibility")

body = text[m.end():]
headings = [h.strip().lower() for h in re.findall(r'^##\s+(.+)$', body, re.MULTILINE)]

required_topics = {
    'ai': False,
    'branch': False,
    'title': False,
    'checklist': False,
}
for h in headings:
    if 'ai' in h or 'disclos' in h:
        required_topics['ai'] = True
    if 'branch' in h or 'target' in h:
        required_topics['branch'] = True
    if 'title' in h:
        required_topics['title'] = True
    if 'checklist' in h or 'pre-pr' in h:
        required_topics['checklist'] = True

missing = [k for k, v in required_topics.items() if not v]
if missing:
    errors.append(f"missing section topics: {missing} (headings: {headings})")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK: name={fm['name']}, sections={len(headings)}")
""")
    assert r.returncode == 0, f"pull-request skill validation failed: {r.stderr}"


def test_changeset_skill_has_writing_guidelines():
    """changeset/SKILL.md must cover writing guidelines including all three change types."""
    r = _run_validator(r"""
import re, sys

path = "/workspace/biome/.claude/skills/changeset/SKILL.md"
try:
    text = open(path).read()
except FileNotFoundError:
    print("changeset/SKILL.md does not exist", file=sys.stderr)
    sys.exit(1)

headings = re.findall(r'^##\s+(.+)$', text, re.MULTILINE)
if len(headings) < 3:
    print(f"Expected >=3 H2 sections, found {len(headings)}: {headings}", file=sys.stderr)
    sys.exit(1)

lower = text.lower()
missing_types = [ct for ct in ('patch', 'minor', 'major') if ct not in lower]
if missing_types:
    print(f"Missing change type coverage: {missing_types}", file=sys.stderr)
    sys.exit(1)

print(f"OK: {len(headings)} sections, all change types covered")
""")
    assert r.returncode == 0, f"changeset writing guidelines check failed: {r.stderr}"


def test_biome_developer_code_comments_section():
    """biome-developer/SKILL.md must have Code Comments guidance with do/don't and examples."""
    r = _run_validator(r"""
import re, sys

text = open("/workspace/biome/.claude/skills/biome-developer/SKILL.md").read()

# Find the Code Comments heading (single-line match, no DOTALL)
heading_match = re.search(r'(?i)^(#{2,3})\s+[^\n]*comment[^\n]*$', text, re.MULTILINE)
if not heading_match:
    print("No heading about code comments found", file=sys.stderr)
    sys.exit(1)

# Extract section content: from after the heading to the next heading of same or higher level
heading_level = len(heading_match.group(1))
remaining = text[heading_match.end():]
next_heading = re.search(r'^#{2,' + str(heading_level) + r'}\s+', remaining, re.MULTILINE)
section = remaining[:next_heading.start()] if next_heading else remaining
section_lower = section.lower()

errors = []

has_positive = bool(re.search(r'(?i)\bdo\b.*:', section))
has_negative = bool(re.search(r"(?i)don['\u2019]?t.*:", section))
if not (has_positive and has_negative):
    errors.append(f"Missing do/don't guidance (do={has_positive}, dont={has_negative})")

if not re.search(r'future|next\s+developer', section_lower):
    errors.append("Should reference future readers or next developers")

has_wrong = bool(re.search(r'(?i)wrong', section))
has_correct = bool(re.search(r'(?i)correct', section))
if not (has_wrong and has_correct):
    errors.append(f"Missing wrong/correct examples (wrong={has_wrong}, correct={has_correct})")

if '```' not in section:
    errors.append("No code block found in comments section")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print("OK: code comments section with do/don't guidance and examples")
""")
    assert r.returncode == 0, f"Code comments section check failed: {r.stderr}"


def test_testing_codegen_changeset_section_removed():
    """testing-codegen must not have Create Changeset section, must reference changeset skill."""
    r = _run_validator(r"""
import re, yaml, sys

text = open("/workspace/biome/.claude/skills/testing-codegen/SKILL.md").read()
errors = []

if re.search(r'^###\s+.*create.*changeset', text, re.IGNORECASE | re.MULTILINE):
    errors.append("Still has a 'Create Changeset' subsection")

if 'changeset/SKILL.md' not in text:
    errors.append("Does not reference changeset/SKILL.md")

m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
if m:
    fm = yaml.safe_load(m.group(1))
    if isinstance(fm, dict):
        desc = (fm.get('description') or '').lower()
        if 'changeset' in desc:
            errors.append(f"Description still mentions 'changeset': {fm.get('description')}")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print("OK: changeset section removed, skill referenced, description clean")
""")
    assert r.returncode == 0, f"testing-codegen cleanup check failed: {r.stderr}"


def test_readme_lists_new_skills():
    """Skills README.md must list new skills in table and directory tree."""
    r = _run_validator(r"""
import re, sys

text = open("/workspace/biome/.claude/skills/README.md").read()
errors = []

table_lines = [l.strip() for l in text.split('\n') if l.strip().startswith('|')]
table_skills = set()
for line in table_lines:
    for match in re.finditer(r'\[([^\]]+)\]\(', line):
        table_skills.add(match.group(1).lower())

for skill in ['changeset', 'pull-request']:
    if skill not in table_skills:
        errors.append(f"'{skill}' not in skills table (found: {sorted(table_skills)})")

for line in table_lines:
    if 'testing-codegen' in line.lower() and 'create changeset' in line.lower():
        errors.append("testing-codegen table entry still mentions 'create changeset'")

if 'changeset/' not in text:
    errors.append("Directory tree missing 'changeset/'")
if 'pull-request/' not in text:
    errors.append("Directory tree missing 'pull-request/'")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK: table has {len(table_skills)} skills, directory tree updated")
""")
    assert r.returncode == 0, f"README skills check failed: {r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
# Dropped: cargo fmt/check/test/clippy/udeps — all require Rust toolchain
# (cargo: not found in slim image). These PR changes only touch .claude/skills/
# markdown files + justfile — no Rust code changed, so full workspace cargo
# commands are irrelevant and constitute unavailable infra.
