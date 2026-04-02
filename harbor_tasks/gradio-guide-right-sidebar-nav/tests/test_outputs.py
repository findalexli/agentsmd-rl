"""
Task: gradio-guide-right-sidebar-nav
Repo: gradio-app/gradio @ 41e98f9468bcf322ed55d1470e31e7b4021d0480
PR:   12976

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a Svelte frontend component with no CPU-testable runtime.
All checks are structural (regex on file content). This is justified because
SvelteKit requires a full browser/build pipeline — there is no way to import
or render the component in a Python test.
"""

import re
from pathlib import Path

TARGET = Path("/repo/js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte")


def _read():
    """Read and parse the Svelte file into script + template sections."""
    content = TARGET.read_text()

    script_match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    script = script_match.group(1) if script_match else ""
    # Strip JS comments
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_exists_and_parses():
    """Target file exists, has script + template sections of substantial length."""
    assert TARGET.exists(), f"{TARGET} does not exist"
    content, script, template = _read()
    lines = content.splitlines()
    assert len(lines) >= 50, f"File only {len(lines)} lines — likely stubbed"
    assert len(script.strip()) >= 50, "Script section too short"
    assert len(template.strip()) >= 100, "Template section too short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_right_sidebar_with_slug_links():
    """A right-side TOC iterates guide_slug with clickable <a> links."""
    content, script, template = _read()
    blocks = _find_slug_each_blocks(template)
    assert blocks, "No {#each} block iterating guide_slug/slug data"

    # At least one block must have <a href=...> and real content (>=3 non-control lines)
    found = False
    for block in blocks:
        has_anchor = bool(re.search(r"<a\b[^>]*href", block))
        real_lines = [
            l.strip()
            for l in block.splitlines()
            if l.strip()
            and not l.strip().startswith("{#")
            and not l.strip().startswith("{/")
        ]
        if has_anchor and len(real_lines) >= 3:
            found = True
            break
    assert found, "Slug iteration block lacks anchor elements or meaningful content"

    # Block must be in a sidebar/right/sticky context
    block_start = template.find(blocks[0])
    region = template[max(0, block_start - 800) : block_start + len(blocks[0]) + 100]
    sidebar_pats = [
        r"sticky", r"float-right", r"right", r"sidebar", r"toc",
        r"table.of.contents", r"aside", r"order-(?:last|2|3)",
        r"col-(?:span|start)", r"lg:block",
    ]
    assert any(
        re.search(p, region, re.IGNORECASE) for p in sidebar_pats
    ), "Slug iteration block not inside a sidebar/sticky/right container"


# [pr_diff] fail_to_pass
def test_scroll_tracking():
    """Reactive scroll tracking highlights the current section in TOC."""
    content, script, template = _read()

    # Script must declare a tracking variable
    tracking_pats = [
        r"(?:let|const|var)\s+\w*(?:current|active|selected|highlight)\w*",
        r"(?:let|const|var)\s+\w*(?:header|heading|section|slug|toc)\w*(?:_id|Id|_index)",
    ]
    has_tracking = any(re.search(p, script) for p in tracking_pats)

    # Scroll-related logic
    scroll_pats = [
        r"scrollY|scroll_y|pageYOffset",
        r"offsetTop|getBoundingClientRect",
        r"IntersectionObserver",
        r"addEventListener.*scroll",
        r"onscroll",
        r"\$:.*(?:y\b|scroll|offset)",
    ]
    has_scroll = any(re.search(p, script) for p in scroll_pats)
    if not has_scroll:
        has_scroll = bool(re.search(r"bind:scrollY|bind:scroll", content))

    assert has_tracking, "No tracking variable for current section in script"
    assert has_scroll, "No scroll-to-state logic (scrollY, offsetTop, IntersectionObserver, etc.)"


# [pr_diff] fail_to_pass
def test_level_field_in_slug_type():
    """guide_slug type declaration includes a numeric level/depth field."""
    _, script, _ = _read()
    # The PR adds `level: number` to the guide_slug type.
    # Check the type block near guide_slug for a numeric level/depth field.
    slug_type = re.search(
        r"guide_slug\s*:\s*\{(.*?)\}\s*\[\]", script, re.DOTALL
    )
    assert slug_type, "guide_slug type declaration not found in script"
    type_body = slug_type.group(1)
    assert re.search(
        r"(?:level|depth)\s*:\s*number", type_body
    ), "guide_slug type missing a numeric level/depth field"


# [pr_diff] fail_to_pass
def test_layout_no_mx_auto():
    """Content area no longer uses 'lg:w-8/12 mx-auto' — room for right sidebar."""
    content, _, _ = _read()
    assert not re.search(
        r"lg:w-8/12\s+mx-auto", content
    ), "lg:w-8/12 mx-auto still present — content still centered, no room for sidebar"


# [pr_diff] fail_to_pass
def test_heading_level_indentation():
    """TOC entries indented based on heading level/depth."""
    _, _, template = _read()
    blocks = _find_slug_each_blocks(template)
    assert blocks, "No slug iteration block found"

    found = False
    for block in blocks:
        has_level = bool(re.search(r"\.(?:level|depth|heading_level)", block))
        has_indent = bool(
            re.search(r"style=.*\{.*(?:level|depth)", block, re.DOTALL)
            or re.search(r"(?:padding-left|margin-left|pl-|ml-|indent).*(?:level|depth)", block, re.DOTALL)
            or re.search(r"(?:level|depth).*(?:padding-left|margin-left|pl-|ml-|indent)", block, re.DOTALL)
            or re.search(r"class.*(?:level|depth)", block)
            or re.search(r"\{#if.*(?:level|depth)", block)
        )
        if has_level and has_indent:
            found = True
            break
        # Alternative: heading tags with indentation
        if re.search(r"h[2-6].*(?:pl-|ml-|padding|margin|indent)", block, re.DOTALL):
            found = True
            break
    assert found, "No level-based indentation in slug iteration block"


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
