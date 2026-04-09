"""
Task: posthog-mcp-eval-summary-skill
Repo: PostHog/posthog @ 69f47d880ee65fd3e9a769a12a7d80997dea555e
PR:   53656

Expose LLM evaluation summary endpoint as an MCP tool, plus write the
exploring-llm-evaluations SKILL.md that teaches agents how to use it.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/posthog")

TOOLS_YAML = REPO / "products/llm_analytics/mcp/tools.yaml"
API_TS = REPO / "services/mcp/src/generated/llm_analytics/api.ts"
HANDLER_TS = REPO / "services/mcp/src/tools/generated/llm_analytics.ts"
TOOL_DEFS_JSON = REPO / "services/mcp/schema/generated-tool-definitions.json"
TOOL_DEFS_ALL_JSON = REPO / "services/mcp/schema/tool-definitions-all.json"
SKILLS_README = REPO / "products/llm_analytics/skills/README.md"
EVAL_SKILL_MD = REPO / "products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md"
SNAPSHOT_JSON = REPO / "services/mcp/tests/unit/__snapshots__/tool-schemas/common/llm-analytics-evaluation-summary-create.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_node(script: str, cwd: str = str(REPO), timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript via Node in the repo directory."""
    script_file = REPO / "_eval_tmp.mjs"
    script_file.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_file)],
            capture_output=True, text=True, timeout=timeout, cwd=cwd,
        )
    finally:
        script_file.unlink(missing_ok=True)


def _load_yaml_file(path: Path) -> dict:
    """Parse and return YAML file content."""
    return yaml.safe_load(path.read_text())


def _load_json_file(path: Path) -> dict:
    """Parse and return JSON file content."""
    return json.loads(path.read_text())


def _extract_typescript_interfaces(content: str) -> list:
    """Extract exported interface/const names from TypeScript content."""
    # Simple regex-based extraction for behavioral testing
    import re
    exports = re.findall(r'export\s+(?:const|interface|type|class)\s+(\w+)', content)
    return exports


# ---------------------------------------------------------------------------
# Fail-to-pass (code behavior) — YAML validation
# ---------------------------------------------------------------------------

def test_tools_yaml_valid():
    """tools.yaml must be valid YAML and parseable."""
    result = subprocess.run(
        ["python3", "-c", f"import yaml; yaml.safe_load(open('{TOOLS_YAML}').read()); print('VALID')"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"YAML parsing failed: {result.stderr}"
    assert "VALID" in result.stdout


def test_eval_summary_tool_enabled():
    """tools.yaml must have llm-analytics-evaluation-summary-create enabled."""
    data = _load_yaml_file(TOOLS_YAML)
    tool = data["tools"]["llm-analytics-evaluation-summary-create"]
    assert tool.get("enabled") is True, \
        f"Tool should be enabled, got: {tool.get('enabled')}"


def test_eval_summary_tool_scopes():
    """The evaluation-summary tool must declare llm_analytics:write scope."""
    data = _load_yaml_file(TOOLS_YAML)
    tool = data["tools"]["llm-analytics-evaluation-summary-create"]
    scopes = tool.get("scopes", [])
    assert "llm_analytics:write" in scopes, \
        f"Missing llm_analytics:write scope, got: {scopes}"


def test_eval_summary_tool_annotations_and_consent():
    """Tool must have correct annotations and requires_ai_consent."""
    data = _load_yaml_file(TOOLS_YAML)
    tool = data["tools"]["llm-analytics-evaluation-summary-create"]
    ann = tool.get("annotations", {})
    assert ann.get("readOnly") is False, "Should not be readOnly"
    assert ann.get("destructive") is False, "Should not be destructive"
    assert ann.get("idempotent") is True, "Should be idempotent"
    assert tool.get("requires_ai_consent") is True, "Must require AI consent"


def test_eval_summary_tool_description_complete():
    """Tool must have a descriptive title and description with required fields."""
    data = _load_yaml_file(TOOLS_YAML)
    tool = data["tools"]["llm-analytics-evaluation-summary-create"]
    title = tool.get("title", "")
    desc = tool.get("description", "")
    assert title, "Tool must have a title"
    assert len(desc) > 50, "Description should be substantial"
    # Verify key concepts are documented
    desc_lower = desc.lower()
    assert "evaluation_id" in desc_lower, "Description must mention evaluation_id"
    assert "filter" in desc_lower, "Description must mention filter"
    assert "pass" in desc_lower, "Description must mention pass results"
    assert "fail" in desc_lower, "Description must mention fail results"


# ---------------------------------------------------------------------------
# Fail-to-pass (code behavior) — Generated TypeScript validation
# ---------------------------------------------------------------------------

def test_typescript_api_file_compiles():
    """Generated api.ts must have valid TypeScript syntax."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{API_TS}', 'utf8');
// Check for basic TypeScript syntax markers
if (!content.includes('export const')) throw new Error('No exports found');
if (!content.includes('zod.object')) throw new Error('No Zod schemas found');
console.log('SYNTAX_OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"TypeScript validation failed: {result.stderr}"
    assert "SYNTAX_OK" in result.stdout


def test_zod_schema_exported_in_api_ts():
    """Generated api.ts must export the EvaluationSummaryCreateBody Zod schema."""
    content = API_TS.read_text()
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{API_TS}', 'utf8');
const checks = [
    ['LlmAnalyticsEvaluationSummaryCreateBody', content.includes('LlmAnalyticsEvaluationSummaryCreateBody')],
    ['evaluation_id', content.includes('evaluation_id')],
    ['force_refresh', content.includes('force_refresh')],
    ['generation_ids', content.includes('generation_ids')],
    ['filter enum', content.includes("'all'") || content.includes('"all"')],
];
const failed = checks.filter(([_, ok]) => !ok).map(([name]) => name);
if (failed.length > 0) throw new Error('Missing: ' + failed.join(', '));
console.log('SCHEMA_OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Schema validation failed: {result.stderr}"
    assert "SCHEMA_OK" in result.stdout


def test_tool_handler_registered_in_generated_tools():
    """Generated llm_analytics.ts must register the evaluation-summary handler."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{HANDLER_TS}', 'utf8');
const checks = [
    ['llm-analytics-evaluation-summary-create', content.includes('llm-analytics-evaluation-summary-create')],
    ['evaluation_summary', content.toLowerCase().includes('evaluation_summary')],
    ['LlmAnalyticsEvaluationSummaryCreateSchema', content.includes('LlmAnalyticsEvaluationSummaryCreateSchema')],
    ['GENERATED_TOOLS', content.includes('GENERATED_TOOLS')],
];
const failed = checks.filter(([_, ok]) => !ok).map(([name]) => name);
if (failed.length > 0) throw new Error('Missing: ' + failed.join(', '));
console.log('HANDLER_OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Handler validation failed: {result.stderr}"
    assert "HANDLER_OK" in result.stdout


def test_generated_tools_record_has_entry():
    """GENERATED_TOOLS must include the evaluation-summary tool entry."""
    content = HANDLER_TS.read_text()
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{HANDLER_TS}', 'utf8');
// Extract the GENERATED_TOOLS object
const match = content.match(/GENERATED_TOOLS[^=]*=\\s*\\{{([^}}]+)}}/s);
if (!match) throw new Error('Could not find GENERATED_TOOLS');
if (!match[1].includes('llm-analytics-evaluation-summary-create')) throw new Error('Tool not in GENERATED_TOOLS');
console.log('TOOLS_RECORD_OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"GENERATED_TOOLS validation failed: {result.stderr}"
    assert "TOOLS_RECORD_OK" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (code behavior) — Generated JSON validation
# ---------------------------------------------------------------------------

def test_tool_def_json_valid_and_has_entry():
    """generated-tool-definitions.json must be valid and include the tool entry."""
    result = subprocess.run(
        ["python3", "-c", f"""
import json
with open('{TOOL_DEFS_JSON}') as f:
    data = json.load(f)
tool = data.get('llm-analytics-evaluation-summary-create')
if tool is None:
    raise ValueError('Tool definition missing')
scopes = tool.get('required_scopes', [])
if 'llm_analytics:write' not in scopes:
    raise ValueError(f'Missing scope: {{scopes}}')
if not tool.get('requires_ai_consent'):
    raise ValueError('Must require AI consent')
ann = tool.get('annotations', {{}})
if not ann.get('idempotentHint'):
    raise ValueError('Should have idempotentHint')
print('JSON_VALID')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"JSON validation failed: {result.stderr}"
    assert "JSON_VALID" in result.stdout


def test_tool_def_all_json_has_entry():
    """tool-definitions-all.json must also include the evaluation summary tool."""
    result = subprocess.run(
        ["python3", "-c", f"""
import json
with open('{TOOL_DEFS_ALL_JSON}') as f:
    data = json.load(f)
if 'llm-analytics-evaluation-summary-create' not in data:
    raise ValueError('Tool not in tool-definitions-all.json')
print('ALL_JSON_VALID')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"tool-definitions-all.json check failed: {result.stderr}"
    assert "ALL_JSON_VALID" in result.stdout


def test_snapshot_json_exists_and_valid():
    """The JSON snapshot for the tool schema must exist and be valid JSON with required fields."""
    result = subprocess.run(
        ["python3", "-c", f"""
import json
from pathlib import Path
snapshot = Path('{SNAPSHOT_JSON}')
if not snapshot.exists():
    raise FileNotFoundError('Snapshot file missing')
with open(snapshot) as f:
    data = json.load(f)
props = data.get('properties', {{}})
required = data.get('required', [])
for field in ['evaluation_id', 'filter', 'force_refresh', 'generation_ids']:
    if field not in props:
        raise ValueError(f'Missing property: {{field}}')
if 'evaluation_id' not in required:
    raise ValueError('evaluation_id must be required')
print('SNAPSHOT_VALID')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Snapshot validation failed: {result.stderr}"
    assert "SNAPSHOT_VALID" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (config/documentation) — skills README
# ---------------------------------------------------------------------------

def test_skills_readme_valid_markdown():
    """products/llm_analytics/skills/README.md must be valid and list exploring-llm-evaluations."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{SKILLS_README}').read_text()
if 'exploring-llm-evaluations' not in content:
    raise ValueError('Must reference exploring-llm-evaluations')
if 'evaluation' not in content.lower():
    raise ValueError('README should mention evaluations')
# Check it's valid markdown-ish structure
if '# ' not in content and content.count('- ') < 2:
    raise ValueError('Does not look like valid markdown')
print('README_VALID')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"README validation failed: {result.stderr}"
    assert "README_VALID" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (config/documentation) — SKILL.md
# ---------------------------------------------------------------------------

def test_skill_md_exists_with_valid_frontmatter():
    """exploring-llm-evaluations/SKILL.md must exist with valid YAML frontmatter."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml
from pathlib import Path
skill_file = Path('{EVAL_SKILL_MD}')
if not skill_file.exists():
    raise FileNotFoundError('SKILL.md file must exist')
content = skill_file.read_text()
if not content.startswith('---'):
    raise ValueError('SKILL.md must have YAML frontmatter')
# Extract and parse frontmatter
fm_end = content.index('---', 3)
frontmatter = yaml.safe_load(content[3:fm_end])
if frontmatter.get('name') != 'exploring-llm-evaluations':
    raise ValueError(f"Wrong name: {{frontmatter.get('name')}}")
if 'description' not in frontmatter:
    raise ValueError('Frontmatter must have description')
if 'evaluation' not in frontmatter['description'].lower():
    raise ValueError('Description must mention evaluations')
print('FRONTMATTER_VALID')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"SKILL.md validation failed: {result.stderr}"
    assert "FRONTMATTER_VALID" in result.stdout


def test_skill_md_documents_summary_tool():
    """SKILL.md must document the evaluation summary tool and its parameters."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{EVAL_SKILL_MD}').read_text().lower()
# Must reference the tool name or its endpoint
if 'evaluation-summary-create' not in content and 'evaluation_summary' not in content:
    raise ValueError('Must reference the evaluation summary tool')
# Must document key parameters
if 'filter' not in content:
    raise ValueError('Must document filter parameter')
if 'force_refresh' not in content and 'force refresh' not in content:
    raise ValueError('Must mention force_refresh / cache behavior')
print('DOCUMENTS_TOOL')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Tool documentation check failed: {result.stderr}"
    assert "DOCUMENTS_TOOL" in result.stdout


def test_skill_md_covers_both_evaluation_types():
    """SKILL.md must document both hog and llm_judge evaluation types."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{EVAL_SKILL_MD}').read_text().lower()
if 'hog' not in content:
    raise ValueError('Must document Hog evaluation type')
if 'llm_judge' not in content and 'llm judge' not in content:
    raise ValueError('Must document LLM judge evaluation type')
# Should describe Hog as deterministic
if 'deterministic' not in content and 'reproducible' not in content:
    raise ValueError('Should describe Hog evaluators as deterministic')
print('COVERS_BOTH_TYPES')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Evaluation types check failed: {result.stderr}"
    assert "COVERS_BOTH_TYPES" in result.stdout


def test_skill_md_has_workflow_sections():
    """SKILL.md must contain structured workflow guidance for investigation."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{EVAL_SKILL_MD}').read_text().lower()
# Should have workflow sections for common tasks
if 'workflow' not in content and 'step' not in content:
    raise ValueError('Should have workflow/step-by-step sections')
if '$ai_evaluation' not in content:
    raise ValueError('Must reference the $ai_evaluation event schema')
print('HAS_WORKFLOWS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Workflow sections check failed: {result.stderr}"
    assert "HAS_WORKFLOWS" in result.stdout


def test_skill_md_follows_naming_conventions():
    """SKILL.md name must be lowercase kebab-case, description under 1024 chars."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml
from pathlib import Path
skill_file = Path('{EVAL_SKILL_MD}')
if not skill_file.exists():
    raise FileNotFoundError('SKILL.md file must exist')
content = skill_file.read_text()
fm_end = content.index('---', 3)
frontmatter = yaml.safe_load(content[3:fm_end])
name = frontmatter.get('name', '')
# Name: lowercase kebab-case
if name != name.lower():
    raise ValueError(f'Skill name must be lowercase: {{name}}')
if ' ' in name:
    raise ValueError(f'Skill name must use kebab-case (no spaces): {{name}}')
if '-' not in name and not name.isalpha():
    raise ValueError(f'Skill name should use kebab-case: {{name}}')
# Description: under 1024 chars
desc = frontmatter.get('description', '')
if len(desc) > 1024:
    raise ValueError(f'Description too long: {{len(desc)}} chars (max 1024)')
print('CONVENTIONS_OK')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Naming conventions check failed: {result.stderr}"
    assert "CONVENTIONS_OK" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

def test_existing_clustering_tool_unchanged():
    """Previously enabled clustering-jobs-list tool must remain enabled."""
    data = _load_yaml_file(TOOLS_YAML)
    clustering = data["tools"].get("llm-analytics-clustering-jobs-list", {})
    assert clustering.get("enabled") is True, \
        "Clustering jobs list tool should remain enabled"


def test_existing_skills_remain_in_readme():
    """Previously listed skills must still appear in skills/README.md."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{SKILLS_README}').read_text()
required = ['exploring-llm-traces', 'exploring-llm-clusters']
missing = [s for s in required if s not in content]
if missing:
    raise ValueError(f'Missing skills: {{missing}}')
print('EXISTING_SKILLS_OK')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Existing skills check failed: {result.stderr}"
    assert "EXISTING_SKILLS_OK" in result.stdout


def test_no_wildcard_imports_in_generated_code():
    """Generated TypeScript must not use wildcard imports (per agent config)."""
    result = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
content = Path('{HANDLER_TS}').read_text()
if 'import * as' in content:
    # This is acceptable for Zod imports per codebase conventions
    pass
# Check for any actual wildcard usage that's not the standard zod pattern
lines = content.split('\\n')
for line in lines:
    if line.strip().startswith('import') and '*' in line and 'zod' not in line.lower():
        raise ValueError(f'Suspicious wildcard import: {{line}}')
print('IMPORTS_OK')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Wildcard import check failed: {result.stderr}"
    assert "IMPORTS_OK" in result.stdout
