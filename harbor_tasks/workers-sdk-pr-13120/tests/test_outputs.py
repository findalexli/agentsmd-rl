import subprocess
import os
import json
import re

REPO = "/workspace/workers-sdk"
FIXTURE = os.path.join(REPO, "fixtures", "worker-with-resources")
INDEX_TS = os.path.join(FIXTURE, "src", "index.ts")
WRANGLER_JSONC = os.path.join(FIXTURE, "wrangler.jsonc")
WORKER_DTS = os.path.join(FIXTURE, "worker-configuration.d.ts")


def parse_jsonc(path):
    with open(path) as f:
        content = f.read()
    content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    content = re.sub(r",\s*([}\]])", r"\1", content)
    return json.loads(content)


def _run_ts_ast(script, *args):
    """Run a TypeScript AST check via Node.js (CommonJS).
    Runs from /workspace/workers-sdk so Node.js resolves typescript from the monorepo's node_modules.
    """
    r = subprocess.run(
        ["node", "-e", script, *args],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    return r


# -- pass_to_pass ---------------------------------------------------------------


def test_wrangler_jsonc_is_valid():
    """p2p: wrangler.jsonc is valid JSONC and parses successfully."""
    config = parse_jsonc(WRANGLER_JSONC)
    assert "name" in config, "Missing 'name' field"
    assert "main" in config, "Missing 'main' field"


def test_existing_durable_object_intact():
    """p2p: MyDurableObject class is still present."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let found = false;"
        "function walk(node) {"
        "  if (ts.isClassDeclaration(node) && node.name && node.name.text === 'MyDurableObject') found = true;"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(found ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"MyDurableObject class not found:\n{r.stderr}"


def test_existing_fetch_handler_intact():
    """p2p: Default export is present (fetch handler)."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let found = false;"
        "function walk(node) {"
        "  if (ts.isExportAssignment(node) && !node.isExportEquals) found = true;"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(found ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"Default export not found:\n{r.stderr}"


def test_typescript_typecheck():
    """p2p: TypeScript type-checking passes on fixture source (check:type CI equivalent)."""
    tsconfig_path = os.path.join(FIXTURE, "tsconfig_src.json")
    tsconfig = {
        "compilerOptions": {
            "types": ["./worker-configuration.d.ts", "@cloudflare/workers-types", "node"],
            "target": "ES2020",
            "esModuleInterop": True,
            "module": "preserve",
            "lib": ["ES2020"],
            "skipLibCheck": True,
            "moduleResolution": "node",
            "noEmit": True,
        },
        "include": ["src"],
    }
    with open(tsconfig_path, "w") as f:
        json.dump(tsconfig, f)
    try:
        r = subprocess.run(
            ["bash", "-lc", f"cd {FIXTURE} && npx tsc --noEmit --project tsconfig_src.json"],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"TypeScript type errors:\n{r.stdout}\n{r.stderr}"
    finally:
        if os.path.exists(tsconfig_path):
            os.remove(tsconfig_path)


# -- fail_to_pass ----------------------------------------------------------------


def test_workflows_section_exists():
    """f2p: wrangler.jsonc has a workflows array with MY_WORKFLOW binding."""
    config = parse_jsonc(WRANGLER_JSONC)
    assert "workflows" in config, "No 'workflows' key in wrangler.jsonc"
    workflows = config["workflows"]
    bindings = [w.get("binding") for w in workflows]
    assert "MY_WORKFLOW" in bindings, f"MY_WORKFLOW binding not in workflows: {bindings}"
    class_names = [w.get("class_name") for w in workflows]
    assert "MyWorkflow" in class_names, f"MyWorkflow class_name not in workflows: {class_names}"


def test_my_workflow_class_exists():
    """f2p: MyWorkflow class extends WorkflowEntrypoint."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let found = false;"
        "function walk(node) {"
        "  if (ts.isClassDeclaration(node) && node.name && node.name.text === 'MyWorkflow') {"
        "    const clauses = node.heritageClauses;"
        "    if (clauses) {"
        "      for (const c of clauses) {"
        "        for (const t of c.types) {"
        "          if (t.expression.getText(sf) === 'WorkflowEntrypoint') found = true;"
        "        }"
        "      }"
        "    }"
        "  }"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(found ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"MyWorkflow class not extending WorkflowEntrypoint:\n{r.stderr}"


def test_workflow_entrypoint_imported():
    """f2p: WorkflowEntrypoint is imported from cloudflare:workers."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let found = false;"
        "function walk(node) {"
        "  if (ts.isImportDeclaration(node) && node.moduleSpecifier.text === 'cloudflare:workers') {"
        "    const clause = node.importClause;"
        "    if (clause && clause.namedBindings) {"
        "      for (const el of clause.namedBindings.elements || []) {"
        "        if (el.name.text === 'WorkflowEntrypoint') found = true;"
        "      }"
        "    }"
        "  }"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(found ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"WorkflowEntrypoint import not found:\n{r.stderr}"


def test_workflow_type_imports_present():
    """f2p: type-only imports for WorkflowEvent and WorkflowStep are present."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let foundEvent = false, foundStep = false;"
        "function walk(node) {"
        "  if (ts.isImportDeclaration(node) && node.moduleSpecifier.text === 'cloudflare:workers') {"
        "    const clause = node.importClause;"
        "    if (clause && clause.isTypeOnly) {"
        "      const elements = clause.namedBindings ? clause.namedBindings.elements : [];"
        "      for (const el of elements) {"
        "        if (el.name.text === 'WorkflowEvent') foundEvent = true;"
        "        if (el.name.text === 'WorkflowStep') foundStep = true;"
        "      }"
        "    }"
        "  }"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(foundEvent && foundStep ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"Type-only imports for WorkflowEvent/WorkflowStep not found:\n{r.stderr}"


def test_my_workflow_type_in_dts():
    """f2p: worker-configuration.d.ts declares MY_WORKFLOW Workflow type."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('dts.ts', src, ts.ScriptTarget.Latest, true);"
        "let found = false;"
        "function walk(node) {"
        "  if (ts.isInterfaceDeclaration(node) && node.name.text === 'Env') {"
        "    for (const member of node.members) {"
        "      if (ts.isPropertySignature(member) && member.name.getText(sf) === 'MY_WORKFLOW') {"
        "        if (member.type && ts.isTypeReferenceNode(member.type)) {"
        "          if (member.type.typeName.getText(sf) === 'Workflow') found = true;"
        "        }"
        "      }"
        "    }"
        "  }"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(found ? 0 : 1);",
        WORKER_DTS,
    )
    assert r.returncode == 0, f"MY_WORKFLOW: Workflow<...> type not found in Env interface:\n{r.stderr}"


def test_workflow_run_method_exists():
    """f2p: MyWorkflow class has a run method with step.do and step.sleep calls."""
    r = _run_ts_ast(
        "const ts = require('typescript');"
        "const fs = require('fs');"
        "const src = fs.readFileSync(process.argv[1], 'utf8');"
        "const sf = ts.createSourceFile('index.ts', src, ts.ScriptTarget.Latest, true);"
        "let hasRun = false, hasDo = false, hasSleep = false;"
        "function walk(node) {"
        "  if (ts.isClassDeclaration(node) && node.name && node.name.text === 'MyWorkflow') {"
        "    for (const member of node.members) {"
        "      if (ts.isMethodDeclaration(member) && member.name.getText(sf) === 'run') {"
        "        hasRun = true;"
        "        const body = member.body ? member.body.getText(sf) : '';"
        "        if (body.includes('step.do')) hasDo = true;"
        "        if (body.includes('step.sleep')) hasSleep = true;"
        "      }"
        "    }"
        "  }"
        "  ts.forEachChild(node, walk);"
        "}"
        "walk(sf);"
        "process.exit(hasRun && hasDo && hasSleep ? 0 : 1);",
        INDEX_TS,
    )
    assert r.returncode == 0, f"MyWorkflow.run() with step.do/step.sleep not found:\n{r.stderr}"
