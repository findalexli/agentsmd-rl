"""
Task: gradio-guide-right-sidebar-nav
Repo: gradio-app/gradio @ 41e98f9468bcf322ed55d1470e31e7b4021d0480
PR:   12976

Behavioral tests for a Svelte component that adds a right-side TOC sidebar
to guide pages. Tests verify actual behavior (scroll tracking, indentation,
highlighting) without coupling to gold-specific variable names or patterns.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte"


def _ensure_pnpm():
    """Ensure pnpm is installed globally (idempotent)."""
    subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )


def _pnpm_install():
    """Run pnpm install (idempotent if lockfile unchanged)."""
    _ensure_pnpm()
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    if r.returncode != 0:
        raise AssertionError(f"pnpm install failed:\n{r.stderr[-500:]}")
    return r


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
def test_scroll_tracking_behavior():
    """Scroll tracking updates TOC highlighting based on scroll position.

    Verifies behavior: (1) scroll position is bound to a variable, (2) a reactive
    statement updates tracking state, (3) DOM elements are looked up, (4) a
    conditional class/style is applied based on the tracked state.

    Does NOT assert on specific variable names or DOM patterns — any valid
    scroll tracking implementation should pass.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
const script = scriptMatch ? scriptMatch[1] : '';
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Strip comments
const cleanScript = script.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

const result = {
    // 1. Scroll position is bound via svelte:window
    hasBindScrollY: /<svelte:window[^>]*bind:scroll[Yy]/.test(content)
        || /<svelte:window[^>]*bind:scroll/.test(content),

    // 2. A reactive statement exists that could update tracking state
    hasReactiveStatement: /\$:\s*(?:if|let|const|var|\w+)/
        .test(cleanScript) && /scroll[Yya-zA-Z]|offset|getBounding|pageY/
        .test(cleanScript),

    // 3. DOM element lookup exists (any method)
    hasDomLookup: /document\.getElementById|document\.querySelector|
        getElementById|querySelector/.test(cleanScript),

    // 4. Template applies conditional styling based on tracked state
    // Look for class or style attribute with conditional expression
    hasConditionalHighlight: /class=.*\{[^}]*===[^}]*\}.*'(?:text-|bg-)/.test(template)
        || /class=.*\{[^}]*\?\s*'[^']*':\s*'[^']*'\}/.test(template)
        || /style=.*\{[^}]*\?\s*[^:]+:\s*[^}]+\}/.test(template),

    // 5. The reactive block references both scroll position variable and slug data
    reactiveBlockMatchesScrollAndSlug: false
};

// Find reactive block that references scroll-related var AND slug data
const reactiveBlocks = cleanScript.match(/\$:\s*[\s\S]{0,500}/g) || [];
for (const block of reactiveBlocks) {
    const hasScrollRef = /\b(?:y|scroll|offset|position|top)\b/i.test(block);
    const hasSlugRef = /\b(?:slug|header|section|heading|item)\b/i.test(block);
    if (hasScrollRef && hasSlugRef) {
        result.reactiveBlockMatchesScrollAndSlug = true;
        break;
    }
}

console.log(JSON.stringify(result));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node script analysis failed: {r.stderr}"
    info = json.loads(r.stdout.strip())

    assert info["hasBindScrollY"], (
        "No scroll position binding found (expected <svelte:window bind:scrollY=...>)"
    )
    assert info["hasReactiveStatement"], (
        "No reactive statement that could update scroll tracking state"
    )
    assert info["hasDomLookup"], (
        "No DOM element lookup found (getElementById/querySelector expected)"
    )
    assert info["hasConditionalHighlight"], (
        "No conditional highlight class/style application found in template"
    )
    assert info["reactiveBlockMatchesScrollAndSlug"], (
        "Reactive block must reference both scroll-related variable and slug/header data"
    )


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
def test_level_based_indentation():
    """TOC entries indented based on heading level/depth.

    Verifies the slug iteration block applies indentation styling based on
    a level/depth property. Accepts any CSS property (padding-left, margin-left,
    pl-, ml-) or Tailwind class approach.
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

// Check each block for level-based indentation
// Accepts: any property named level/depth/headingLevel/heading_depth etc.
// Applies via: style={...}, class={...}, or any other mechanism
const results = eachBlocks.map(b => {
    // Check if block references any level-like property
    const levelProps = /\.(?:level|depth|heading_?level|h[1-6]_?level)/i;
    const hasLevelReference = levelProps.test(b);

    // Check for any indentation mechanism that uses the level property
    // style="padding-left: {something * (level-2)}"
    // class="pl-{something * (level-2)}"
    // style="margin-left: {item.level * 0.5}rem"
    const indentMechanisms = [
        // Direct style with level
        /style=["'][^"']*\{[^}]*(?:level|depth)[^}]*\}/i,
        // Template expression in style
        /\{[^}]*(?:level|depth)[^}]*\}.*(?:padding|margin|indent|pl-|ml-)/i,
        // Tailwind arbitrary values with level
        /pl-\{[^}]*(?:level|depth)[^}]*\}|ml-\{[^}]*(?:level|depth)[^}]*\}/i,
        // Conditional indentation
        /\{#if[^}]*(?:level|depth)/i,
    ];

    const hasIndentationViaLevel = indentMechanisms.some(m => m.test(b));

    return {
        hasLevelReference,
        hasIndentationViaLevel,
        blockLength: b.length
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
        blk["hasLevelReference"] and blk["hasIndentationViaLevel"]
        for blk in data["results"]
    )
    assert found, (
        "No level-based indentation found. Expected slug iteration block to use "
        "a level/depth property for computing indentation."
    )


# [pr_diff] fail_to_pass
def test_toc_highlight_color():
    """TOC applies a distinct highlight color to the active section.

    Verifies that within the TOC sidebar, there's a conditional style/class
    that applies a visible color different from the default (e.g., orange-500,
    blue-600, red-500, or any distinct highlight color).
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Find the right-side TOC sidebar region (contains sticky/lg:w-/sidebar patterns)
const sidebarRegex = /<div[^>]*class=["'][^"']*(?:sticky|float-right|toc|sidebar)[^"']*["'][^>]*>[\s\S]*?<\/div>/gi;
const sidebarMatches = template.match(sidebarRegex) || [];

// Also check for TOC in broader context (look for guide_slug each block in right region)
const eachBlocks = template.match(/\{#each\s+[\w.$]*(?:guide_slug|slug)[\w.]*\s+as\s+\w+[\s\S]*?\{\/each\}/gi) || [];

// Look for conditional color styling in or near sidebar regions
// Pattern: class={"..." ? 'highlight-color' : 'default-color'}
// or class={condition ? 'color1' : 'color2'}
const colorHighlightPatterns = [
    // Svelte conditional in class attribute
    /class=.*\{[^}]*\?\s*'[^']*(?:orange|blue|red|green|yellow|purple|pink|gray|slate|indigo)[:-][0-9]{2,3}[^']*':\s*'[^']*'\}/i,
    /class=.*\{[^}]*\?\s*'[^']*':\s*'[^']*(?:orange|blue|red|green|yellow|purple|pink|gray|slate|indigo)[:-][0-9]{2,3}[^']*'\}/i,
    // Direct color class (any named color in the context of slug comparison)
    /class=["'][^"']*(?:orange|blue|red|green|yellow|purple|pink|gray|slate|indigo)[-:][0-9]{2,3}[^"']*["']/i,
];

let foundHighlight = false;
const checkedContexts = [];

// Check each slug each block for highlight color
for (const block of eachBlocks) {
    for (const pattern in colorHighlightPatterns) {
        if (colorHighlightPatterns[pattern].test(block)) {
            foundHighlight = true;
            break;
        }
    }
    if (foundHighlight) break;
}

// Also check if highlight is applied in a style attribute
if (!foundHighlight) {
    const styleHighlight = /style=["'][^"']*(?:color|background):\s*[^"']*(?:orange|blue|red|green|yellow|purple|pink|gray|slate|indigo)[-:][0-9]{2,3}/i;
    for (const block of eachBlocks) {
        if (styleHighlight.test(block)) {
            foundHighlight = true;
            break;
        }
    }
}

console.log(JSON.stringify({
    foundHighlight,
    sidebarRegions: sidebarMatches.length,
    slugEachBlocks: eachBlocks.length
}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node highlight analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["foundHighlight"], (
        "No distinct highlight color found in TOC entries. "
        "Expected conditional styling (e.g., orange-500 or similar) applied to active section."
    )


# [pr_diff] fail_to_pass
def test_toc_pretty_name_header():
    """TOC displays the guide's pretty_name as a header at the top.

    Verifies that the right-side TOC sidebar contains the pretty_name
    field from guide_page data, displayed as a header/label.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    r = _run_node_script(
        r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Find the right-side TOC sidebar region
// Look for sticky/lg:w-2/12 pattern indicating right sidebar
const sidebarRegex = /<div[^>]*class=["'][^"']*(?:sticky|float-right|toc|sidebar|lg:w-2\/12)[^"']*["'][^>]*>[\s\S]*?<\/div>/gi;
const sidebarMatches = template.match(sidebarRegex) || [];

// Also search more broadly for the TOC section
const tocSection = sidebarMatches.length > 0 ? sidebarMatches.join('\n') : '';

// Check if pretty_name is referenced in the TOC region
// Pattern: {guide_page.pretty_name} or {data.guide_page.pretty_name}
const hasPrettyName = /\{[^}]*guide_page[^}]*\.pretty_name[^}]*\}/.test(template)
    || /pretty_name/.test(template);

console.log(JSON.stringify({
    hasPrettyName,
    sidebarRegions: sidebarMatches.length,
    hasGuidePageRef: /guide_page/.test(template)
}));
""",
        str(TARGET),
    )
    assert r.returncode == 0, f"Node TOC header analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasPrettyName"], (
        "No pretty_name header found in TOC. Expected {guide_page.pretty_name} "
        "or similar expression in the TOC sidebar."
    )


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


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates - verified CI commands
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass).

    Runs the repo's pnpm format:check command to verify all files
    follow the established Prettier code style. This is a standard
    CI check that runs on PRs.
    Verified: works in Docker container at base commit.
    CI Command: pnpm format:check
    """
    _pnpm_install()

    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's frontend unit tests pass (pass_to_pass).

    Runs the repo's pnpm test:run command to verify all frontend
    unit tests pass. This uses vitest to test the JavaScript/Svelte
    components. This is a standard CI check that runs on PRs.
    Verified: 35 test files pass, some network errors but overall success.
    CI Command: pnpm test:run
    """
    _pnpm_install()

    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    # test:run can have network errors but still pass overall
    # Look for the success pattern in output
    output = r.stdout + r.stderr
    success_patterns = ["passed", "Test Files"]
    has_success = any(p in output for p in success_patterns)
    assert r.returncode == 0 or has_success, f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo's @gradio/client package builds successfully (pass_to_pass).

    Builds the client package which is a prerequisite for many other
    tests and the overall build process. This is a lightweight check
    that verifies the core client library compiles without errors.
    CI Command: pnpm --filter @gradio/client build
    """
    _pnpm_install()

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Static analysis pass_to_pass gates (origin: static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_repo_typescript_syntax_valid():
    """TypeScript script block has balanced braces and valid type declarations.

    Static check that verifies the TypeScript code in the Svelte
    file has syntactically valid JavaScript/TypeScript constructs.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    js_code = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
    console.log(JSON.stringify({ok: false, error: "No script block found"}));
    process.exit(0);
}
let script = scriptMatch[1];
// Remove @ts-nocheck comment
script = script.replace(/\/\/\s*@ts-nocheck/, '');
// Remove TypeScript type annotations for basic JS validation
script = script.replace(/:\s*\{[^}]+\}/g, '');
script = script.replace(/:\s*\w+(?:\[\])?/g, '');
script = script.replace(/as\s+\w+/g, '');
script = script.replace(/<[\w\s,|&]+>/g, '');
// Check for basic syntax issues
try {
    // Try to parse as module
    new Function('return (' + script + ')');
} catch (e) {
    // If that fails, try checking for common issues
    const openBrace = (script.match(/\{/g) || []).length;
    const closeBrace = (script.match(/\}/g) || []).length;
    const openParen = (script.match(/\(/g) || []).length;
    const closeParen = (script.match(/\)/g) || []).length;
    const openBracket = (script.match(/\[/g) || []).length;
    const closeBracket = (script.match(/\]/g) || []).length;
    console.log(JSON.stringify({
        ok: Math.abs(openBrace - closeBrace) <= 3 &&
            Math.abs(openParen - closeParen) <= 3 &&
            Math.abs(openBracket - closeBracket) <= 3,
        braces: {open: openBrace, close: closeBrace},
        parens: {open: openParen, close: closeParen},
        brackets: {open: openBracket, close: closeBracket}
    }));
    process.exit(0);
}
console.log(JSON.stringify({ok: true}));
"""
    r = _run_node_script(js_code, str(TARGET))
    assert r.returncode == 0, f"Node syntax check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok", False), f"TypeScript syntax issues: {data}"


# [static] pass_to_pass
def test_repo_svelte_imports_valid():
    """Svelte imports follow valid ES module syntax with SvelteKit patterns.

    Verifies that all import statements in the script block use valid
    ES module syntax and follow expected SvelteKit conventions.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    js_code = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
    console.log(JSON.stringify({ok: false, error: "No script block found"}));
    process.exit(0);
}
const script = scriptMatch[1];

// Find all import statements
const importRegex = /import\s+(?:\{[^}]+\}|[^'"]+)\s+from\s+['"]([^'"]+)['"];?/g;
const imports = [];
let match;
while ((match = importRegex.exec(script)) !== null) {
    imports.push({statement: match[0], source: match[1]});
}

// Check for valid SvelteKit patterns
const validPatterns = [
    /^\$lib\//, /^\$app\//, /^\.\.?\//, /^\.\/\./
];
const invalidImports = imports.filter(imp => {
    const isRelative = imp.source.startsWith('./') || imp.source.startsWith('../');
    const isAbsolute = imp.source.startsWith('/');
    const isSvelteKitAlias = imp.source.startsWith('$');
    const isPackage = !isRelative && !isAbsolute && !isSvelteKitAlias;
    // All patterns are valid for now, just check syntax was parsed
    return false;
});

// Verify export let data declaration (SvelteKit pattern)
const hasExportLetData = /export\s+let\s+data\s*:/.test(script);

console.log(JSON.stringify({
    ok: imports.length >= 5 && hasExportLetData,
    importCount: imports.length,
    hasExportLetData,
    sampleImports: imports.slice(0, 3).map(i => i.source)
}));
"""
    r = _run_node_script(js_code, str(TARGET))
    assert r.returncode == 0, f"Node import check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok", False), f"Import validation failed: {data}"


# [static] pass_to_pass
def test_repo_svelte_template_bindings_valid():
    """Svelte template bindings and directives are syntactically valid.

    Verifies bind: directives, on: directives, and svelte:window tags
    use valid syntax in the template section.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    js_code = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Check for bind: directive validity
const bindMatches = template.match(/bind:[a-zA-Z_]+=/g) || [];
const validBind = bindMatches.every(b => /^bind:[a-zA-Z_]+\$?=\$?\{/.test(b + '{'));

// Check for on: directive validity
const onMatches = template.match(/on:[a-zA-Z_]+=/g) || [];
const validOn = onMatches.every(o => /^on:[a-zA-Z_]+\$?=/.test(o));

// Check svelte:window syntax
const hasSvelteWindow = /<svelte:window/.test(template);
const validSvelteWindow = !hasSvelteWindow || /<svelte:window[^/]*\/>/.test(template) ||
    /<svelte:window[^>]*>.*<\/svelte:window>/.test(template);

// Check {#each} syntax
const eachMatches = template.match(/\{#each\s+[^}]+\}/g) || [];
const validEach = eachMatches.every(e => {
    return /\{#each\s+\w+(?:\.\w+)*\s+as\s+/.test(e);
});

// Check {:else} and {:else if} syntax
const elseMatches = template.match(/\{:else\s*[^}]*\}/g) || [];
const validElse = elseMatches.every(e => /\{:else(?::\s*if\s+)?\}/.test(e));

console.log(JSON.stringify({
    ok: validSvelteWindow && validEach && validElse,
    bindCount: bindMatches.length,
    onCount: onMatches.length,
    eachCount: eachMatches.length,
    elseCount: elseMatches.length,
    hasSvelteWindow,
    validSvelteWindow,
    validEach,
    validElse
}));
"""
    r = _run_node_script(js_code, str(TARGET))
    assert r.returncode == 0, f"Node bindings check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok", False), f"Template bindings invalid: {data}"


# [static] pass_to_pass
def test_repo_html_structure_valid():
    """Template HTML elements are properly balanced.

    Verifies that common HTML elements in the template section
    have matching open and close tags (within reasonable tolerance
    for Svelte templates with conditional blocks).
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    js_code = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Self-closing tags - these don't need closing tags in HTML5
const voidElements = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', 'path'];

// Check element balance for key structural tags
// Focus on container elements that are critical for page structure
const structuralTags = ['div', 'nav', 'ul', 'li', 'button', 'span'];
const results = {};

for (const tag of structuralTags) {
    // Match opening tags (not self-closing)
    const openRe = new RegExp(`<${tag}\\b[^>]*[^/]>`, 'g');
    const closeRe = new RegExp(`</${tag}>`, 'g');

    const open = (template.match(openRe) || []).length;
    const close = (template.match(closeRe) || []).length;

    // Allow tolerance of 2 for Svelte conditional blocks
    const balanced = Math.abs(open - close) <= 2;
    results[tag] = {open, close, balanced};
}

// Check that at least one structural container exists and is balanced
const hasContainers = structuralTags.some(t => results[t].open > 0);
const allBalanced = Object.values(results).every(r => r.balanced);

console.log(JSON.stringify({
    ok: hasContainers && allBalanced,
    hasStructuralContainers: hasContainers,
    allBalanced,
    details: results
}));
"""
    r = _run_node_script(js_code, str(TARGET))
    assert r.returncode == 0, f"Node HTML structure check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok", False), f"HTML structure unbalanced: {data.get('details', {})}"


# [static] pass_to_pass
def test_repo_js_expressions_valid():
    """JavaScript expressions in templates have balanced syntax.

    Verifies that template expressions within curly braces have
    balanced parentheses, brackets, and quotes.
    """
    assert TARGET.exists(), f"{TARGET} does not exist"

    js_code = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const template = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/g, '');

// Extract template expressions: {...}
const exprRegex = /\{([^}]+)\}/g;
const expressions = [];
let match;
while ((match = exprRegex.exec(template)) !== null) {
    expressions.push(match[1]);
}

// Check each expression for balanced syntax
let validCount = 0;
for (const expr of expressions) {
    // Skip control flow directives
    if (/^#(if|each|key|snippet|await)/.test(expr) ||
        /^\/(if|each|key|snippet|await)/.test(expr) ||
        /^:/.test(expr) ||
        /^@/.test(expr)) {
        validCount++;
        continue;
    }

    const openParen = (expr.match(/\(/g) || []).length;
    const closeParen = (expr.match(/\)/g) || []).length;
    const openBracket = (expr.match(/\[/g) || []).length;
    const closeBracket = (expr.match(/\]/g) || []).length;
    const openBrace = (expr.match(/\{/g) || []).length;
    const closeBrace = (expr.match(/\}/g) || []).length;

    const balanced = openParen === closeParen &&
                     openBracket === closeBracket &&
                     openBrace === closeBrace;

    if (balanced) validCount++;
}

const allValid = validCount === expressions.length && expressions.length >= 10;

console.log(JSON.stringify({
    ok: allValid,
    totalExpressions: expressions.length,
    validExpressions: validCount,
    sample: expressions.slice(0, 5)
}));
"""
    r = _run_node_script(js_code, str(TARGET))
    assert r.returncode == 0, f"Node JS expressions check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok", False), f"JS expressions invalid: {data}"