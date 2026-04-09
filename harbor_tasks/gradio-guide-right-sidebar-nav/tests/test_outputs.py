"""
Task: gradio-guide-right-sidebar-nav
Repo: gradio-app/gradio @ 41e98f9468bcf322ed55d1470e31e7b4021d0480
PR:   12976

Behavioral tests for a Svelte component that adds a right-side TOC sidebar
to guide pages. Uses Node.js subprocess calls to parse and validate the
Svelte file's TypeScript script block and HTML template structure.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte"


def _read():
    """Read and parse the Svelte file into script + template sections."""
    content = TARGET.read_text()

    script_match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    script = script_match.group(1) if script_match else ""
    script = re.sub(r"//.*$", "", script, flags=re.MULTILINE)
    script = re.sub(r"/\*.*?\*/", "", script, flags=re.DOTALL)

    template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
    template = re.sub(r"<style[^>]*>.*?</style>", "", template, flags=re.DOTALL)
    template = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)

    return content, script, template


def _find_slug_each_blocks(template: str) -> list[str]:
    """Find {#each} blocks iterating guide_slug/slug data."""
    return re.findall(
        r"\{#each\s+[\w.$]*(?:guide_slug|slug)[\w.]*\s+as\s+\w+.*?\{/each\}",
        template,
        re.DOTALL,
    )


def _run_node_script(js_code: str, file_path: str = "", timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute JavaScript via Node.js. If file_path given, passed as argv[1]."""
    cmd = ["node", "-e", js_code]
    if file_path:
        cmd.append(file_path)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def _run_node_stdin(js_code: str, stdin_data: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute JavaScript via Node.js with data piped via stdin."""
    return subprocess.run(
        ["node", "-e", js_code],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_repo_svelte_file_structure():
    """Target Svelte file has valid structure: script block, template, proper syntax.

    Pass-to-pass check that verifies the file is syntactically valid Svelte
    with both script and template sections present. This ensures the base
    commit has a working foundation before any modifications.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"
    content = TARGET.read_text()

    # Must have script block with TypeScript
    script_match = re.search(r"<script[^>]*lang=[\"']ts[\"'][^>]*>", content)
    assert script_match, "Missing TypeScript script block"

    # Must have closing script tag
    assert "</script>" in content, "Missing closing script tag"

    # Must have template content after script
    template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
    assert len(template.strip()) > 200, "Template section too short or missing"

    # Basic Svelte syntax validation - check for common structural issues
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces > 0 and close_braces > 0, "No template expressions found"

    # Check for unmatched braces in script section (basic check)
    script_content = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    if script_content:
        script = script_content.group(1)
        # Remove comments and strings for brace counting
        script_clean = re.sub(r"//.*?$", "", script, flags=re.MULTILINE)
        script_clean = re.sub(r"\"[^\"]*\"", '""', script_clean)
        script_clean = re.sub(r"'[^']*'", "''", script_clean)
        script_clean = re.sub(r"`[^`]*`", "``", script_clean)
        # Basic brace balance check for script
        open_script = script_clean.count("{")
        close_script = script_clean.count("}")
        # Allow for object shorthand and other JS features - just ensure reasonable
        assert abs(open_script - close_script) <= 5, "Script braces severely unbalanced"


# [static] pass_to_pass
def test_repo_svelte_types_valid():
    """TypeScript type declarations in Svelte file are syntactically valid.

    Verifies that guide_slug and guide_names type declarations exist and have
    reasonable structure. Ensures base commit has valid types before changes.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"
    _, script, _ = _read()

    # Check for guide_slug type declaration
    slug_type_match = re.search(r"guide_slug\s*:\s*\{([^}]+)\}\[\]", script)
    assert slug_type_match, "guide_slug type declaration not found"

    # Check type has expected fields
    slug_type_body = slug_type_match.group(1)
    assert "text:" in slug_type_body, "guide_slug type missing 'text' field"
    assert "href:" in slug_type_body, "guide_slug type missing 'href' field"

    # Check for guide_names type
    names_type_match = re.search(r"guide_names\s*:\s*\{([^}]+)\}\[\]", script)
    assert names_type_match, "guide_names type declaration not found"

    # Check guide_names has category field
    names_type_body = names_type_match.group(1)
    assert "category:" in names_type_body, "guide_names type missing 'category' field"


# [static] pass_to_pass
def test_repo_svelte_template_valid():
    """Svelte template section has valid syntax and required elements.

    Verifies the template contains expected Svelte constructs like {#each} blocks,
    proper HTML structure, and reactive statements in script. Ensures base 
    template is valid before any modifications.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"
    _, script, template = _read()

    # Must have {#each} blocks for iteration in template
    each_blocks = re.findall(r"\{#each\s+\w+", template)
    assert len(each_blocks) >= 1, "No Svelte {#each} blocks found in template"

    # Reactive statements ($:) are in script section
    reactive_stmts = re.findall(r"\$:\s*if", script) or re.findall(r"\$:\s*\w+", script)
    assert len(reactive_stmts) >= 1, "No Svelte reactive statements ($:) found in script"

    # Check for event bindings in template
    bindings = re.findall(r"bind:\w+", template)
    assert len(bindings) >= 1, "No Svelte bind directives found in template"

    # Must have proper HTML element structure (balanced common tags)
    div_open = len(re.findall(r"<div[>\s]", template))
    div_close = len(re.findall(r"</div>", template))
    assert div_open > 0 and div_close > 0, "No div elements found"
    assert abs(div_open - div_close) <= 2, "Div elements severely unbalanced"


# [static] pass_to_pass
def test_file_exists_and_parses():
    """Target file exists with substantial script + template sections.

    Uses Node.js to parse the file and verify structural completeness.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const lines = content.split('\\n').length;
const scriptMatch = content.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/);
const scriptLen = scriptMatch ? scriptMatch[1].trim().length : 0;
const template = content
    .replace(/<script[^>]*>[\\s\\S]*?<\\/script>/g, '')
    .replace(/<style[^>]*>[\\s\\S]*?<\\/style>/g, '')
    .trim();
console.log(JSON.stringify({lines, scriptLen, templateLen: template.length}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node file analysis failed: {r.stderr}"
    info = json.loads(r.stdout.strip())
    assert info["lines"] >= 50, f"File only {info['lines']} lines — likely stubbed"
    assert info["scriptLen"] >= 50, "Script section too short"
    assert info["templateLen"] >= 100, "Template section too short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_right_sidebar_with_slug_links():
    """Right-side TOC iterates guide_slug with clickable links in a sidebar container.

    Uses Node.js to parse the Svelte template, extract {#each} blocks that
    iterate guide_slug, verify they contain anchor elements, and confirm
    the surrounding context is a sidebar/sticky container.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

const eachBlocks = [];
const regex = /\{#each\s+[\w.$]*(?:guide_slug|slug)[\w.]*\s+as\s+\w+[\s\S]*?\{\/each\}/g;
let match;
while ((match = regex.exec(template)) !== null) {
    eachBlocks.push(match[0]);
}

const results = eachBlocks.map(b => {
    const blockStart = template.indexOf(b);
    const region = template.substring(Math.max(0, blockStart - 800), blockStart + b.length + 100);
    const sidebarPatterns = ['sticky', 'float-right', 'sidebar', 'toc', 'aside', 'lg:block', 'overflow'];
    const inSidebar = sidebarPatterns.some(p => new RegExp(p, 'i').test(region));
    const hasAnchor = /<a\b[^>]*href/.test(b);
    const realLines = b.split('\n').filter(l => {
        const t = l.trim();
        return t && !t.startsWith('{#') && !t.startsWith('{/');
    }).length;
    return {hasAnchor, realLines, inSidebar};
});

console.log(JSON.stringify({total: eachBlocks.length, results}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node template analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["total"] > 0, "No {#each} block iterating guide_slug/slug data"

    # At least one block must have anchors, meaningful content, and be in a sidebar
    found = any(
        blk["hasAnchor"] and blk["realLines"] >= 3 and blk["inSidebar"]
        for blk in data["results"]
    )
    assert found, (
        "No slug iteration block with anchor elements, meaningful content (>=3 lines), "
        "and sidebar/sticky container context found"
    )


# [pr_diff] fail_to_pass
def test_scroll_tracking():
    """Reactive scroll tracking highlights the current section in TOC.

    Uses Node.js to parse the script section and verify:
    1. A tracking variable is declared (e.g., current_header_id)
    2. A reactive statement ($:) references scroll position
    3. The reactive block iterates guide_slug entries
    4. DOM elements are looked up via getElementById or similar
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
const script = scriptMatch ? scriptMatch[1] : '';

// Strip comments
const cleanScript = script.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

const result = {
    // Tracking variable: let current_xxx or let xxx_id etc.
    hasTrackingVar: /(?:let|const|var)\s+\w*(?:current|active|selected|highlight)\w*/.test(cleanScript)
        || /(?:let|const|var)\s+\w*(?:header|heading|section|slug|toc)\w*(?:_id|Id|_index)/.test(cleanScript),

    // Scroll logic
    hasScrollLogic: /scrollY|scroll_y|pageYOffset|offsetTop|getBoundingClientRect|IntersectionObserver/.test(cleanScript)
        || /addEventListener.*scroll|onscroll/.test(cleanScript),

    // Svelte bind:scrollY in the full content
    hasBindScroll: /bind:scrollY|bind:scroll/.test(content),

    // Reactive statement that references scroll
    hasReactive: /\$:\s*if\s*\(/.test(cleanScript),

    // Reactive block references both y and slug
    reactiveRefY: false,
    reactiveRefSlug: false,
};

// Check reactive block content
const reactiveMatch = cleanScript.match(/\$:\s*if\s*\([\s\S]{0,300}/);
if (reactiveMatch) {
    const block = reactiveMatch[0];
    result.reactiveRefY = /\by\b/.test(block);
    result.reactiveRefSlug = /\bslug\b/.test(block);
}

console.log(JSON.stringify(result));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node script analysis failed: {r.stderr}"
    info = json.loads(r.stdout.strip())

    assert info["hasTrackingVar"], "No tracking variable for current section in script"
    assert info["hasScrollLogic"] or info["hasBindScroll"], (
        "No scroll-to-state logic (scrollY, offsetTop, IntersectionObserver, etc.)"
    )
    assert info["hasReactive"], "No reactive statement ($:) for scroll tracking"
    assert info["reactiveRefY"], "Reactive block doesn't reference scroll variable 'y'"
    assert info["reactiveRefSlug"], "Reactive block doesn't iterate 'slug' entries"


# [pr_diff] fail_to_pass
def test_level_field_in_slug_type():
    """guide_slug type declaration includes a numeric level/depth field.

    Uses Node.js to parse the TypeScript type declaration from the script
    block and verify it contains a `level: number` or `depth: number` field.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
const script = scriptMatch ? scriptMatch[1] : '';

// Find guide_slug type declaration: guide_slug: { ... }[]
const match = script.match(/guide_slug\s*:\s*\{([\s\S]*?)\}\s*\[\]/);
if (!match) {
    console.log(JSON.stringify({found: false, reason: "guide_slug type not found"}));
    process.exit(0);
}

const typeBody = match[1];
const hasLevel = /(?:level|depth)\s*:\s*number/.test(typeBody);
const fields = typeBody.match(/(\w+)\s*:\s*(\w+)/g) || [];

console.log(JSON.stringify({found: true, hasLevel, fields}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node type analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("found"), f"guide_slug type declaration not found: {data.get('reason', '')}"
    assert data.get("hasLevel"), (
        f"guide_slug type missing numeric level/depth field. Fields found: {data.get('fields', [])}"
    )


# [pr_diff] fail_to_pass
def test_layout_no_mx_auto():
    """Content area no longer uses 'lg:w-8/12 mx-auto' — room for right sidebar.

    Uses Node.js to verify the specific Tailwind class combination is removed.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const hasMxAuto = /lg:w-8\/12\s+mx-auto/.test(content);
console.log(JSON.stringify({hasMxAuto}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node layout analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert not data["hasMxAuto"], (
        "lg:w-8/12 mx-auto still present — content still centered, no room for sidebar"
    )


# [pr_diff] fail_to_pass
def test_heading_level_indentation():
    """TOC entries indented based on heading level/depth.

    Uses Node.js to verify the slug iteration block references the level field
    to compute indentation (padding-left, margin-left, etc.).
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

const eachBlocks = [];
const regex = /\{#each\s+[\w.$]*(?:guide_slug|slug)[\w.]*\s+as\s+\w+[\s\S]*?\{\/each\}/g;
let match;
while ((match = regex.exec(template)) !== null) {
    eachBlocks.push(match[0]);
}

const results = eachBlocks.map(b => {
    const hasLevel = /\.?(?:level|depth|heading_level)/.test(b);
    const hasStyleIndent = /style=.*\{.*(?:level|depth)/.test(b);
    const hasClassIndent = /class.*(?:level|depth)/.test(b);
    const hasPaddingLevel = /(?:padding-left|margin-left|pl-|ml-|indent).*(?:level|depth)/.test(b)
        || /(?:level|depth).*(?:padding-left|margin-left|pl-|ml-|indent)/.test(b);
    const hasConditionalIndent = /\{#if.*(?:level|depth)/.test(b);
    const hasHeadingIndent = /h[2-6].*(?:pl-|ml-|padding|margin|indent)/.test(b);
    return {
        hasLevel,
        hasIndentation: hasStyleIndent || hasClassIndent || hasPaddingLevel || hasConditionalIndent,
        hasHeadingIndent
    };
});

console.log(JSON.stringify({total: eachBlocks.length, results}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node indentation analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["total"] > 0, "No slug iteration block found"

    found = any(
        (blk["hasLevel"] and blk["hasIndentation"]) or blk["hasHeadingIndent"]
        for blk in data["results"]
    )
    assert found, "No level-based indentation found in any slug iteration block"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_left_sidebar_preserved():
    """Left sidebar iterating guide_names with categories still exists."""
    _, _, template = _read()
    assert re.search(
        r"\{#each\s+[\w.$]*guide_names", template
    ), "Left sidebar guide_names iteration missing"
    assert re.search(r"category", template), "Category references missing from template"


# [pr_diff] pass_to_pass
def test_prev_next_navigation_preserved():
    """Previous/next guide navigation links still exist."""
    _, _, template = _read()
    has_prev = bool(re.search(r"prev_guide|previous_guide|prev\.href|prev\.url", template))
    has_next = bool(re.search(r"next_guide|next\.href|next\.url", template))
    assert has_prev and has_next, "Previous/next navigation links missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:45 @ 41e98f9468bcf322ed55d1470e31e7b4021d0480
def test_sidebar_uses_tailwind():
    """New sidebar region uses Tailwind CSS utilities (consistent with rest of file)."""
    _, _, template = _read()
    blocks = _find_slug_each_blocks(template)
    assert blocks, "No slug iteration block found — sidebar missing"

    block = blocks[0]
    block_start = template.find(block)
    region = template[max(0, block_start - 300) : block_start + len(block)]
    tw_hits = len(
        re.findall(
            r"(?:text-|dark:|lg:|hover:|space-|font-|py-|px-|mx-|my-|pl-|pr-|ml-|mr-|block|hidden|flex|grid|overflow)",
            region,
        )
    )
    assert tw_hits >= 3, f"Sidebar region has only {tw_hits} Tailwind utilities (need >= 3)"
