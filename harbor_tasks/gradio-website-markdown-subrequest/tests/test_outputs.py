"""
Task: gradio-website-markdown-subrequest
Repo: gradio-app/gradio @ e900202946a615f8fea84253d7a4377fe8a504f0
PR:   13123

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
TARGET = "js/_website/functions/_shared.ts"


def _run_tsx(script: str, timeout: int = 30) -> str:
    """Write a .mjs script and execute it with tsx, returning stdout."""
    with tempfile.NamedTemporaryFile(suffix=".mjs", mode="w", delete=False) as f:
        f.write(script)
        f.flush()
        r = subprocess.run(
            ["npx", "tsx", f.name],
            capture_output=True, timeout=timeout, cwd=REPO,
        )
    return r.stdout.decode().strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target TypeScript file must parse without errors."""
    out = _run_tsx(f"""
const mod = await import('{REPO}/{TARGET}');
process.stdout.write('OK');
""")
    assert out == "OK", f"TypeScript parse failed: {out}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_doc_redirect():
    """serveDocMarkdown returns 3xx redirect to /api/markdown/<doc> for LLM UA."""
    out = _run_tsx("""
const mod = await import('/repo/js/_website/functions/_shared.ts');
for (const doc of ['textbox', 'slider', 'chatbot']) {
    const req = new Request('https://example.com/docs/' + doc, {
        headers: { 'user-agent': 'claudebot' }
    });
    let nextCalled = false;
    const ctx = {
        request: req,
        params: { doc },
        next: () => { nextCalled = true; return new Response('fallthrough'); }
    };
    const res = await mod.serveDocMarkdown(ctx);
    const loc = res.headers.get('location') || '';
    if (res.status < 300 || res.status >= 400 || !loc.includes('/api/markdown/' + doc) || nextCalled) {
        process.stdout.write('FAIL:' + doc);
        process.exit(0);
    }
}
process.stdout.write('PASS');
""")
    assert out == "PASS", f"serveDocMarkdown redirect check failed: {out}"


# [pr_diff] fail_to_pass
def test_guide_redirect():
    """serveGuideMarkdown returns 3xx redirect to /api/markdown/guide/<guide> for LLM UA."""
    out = _run_tsx("""
const mod = await import('/repo/js/_website/functions/_shared.ts');
for (const guide of ['quickstart', 'sharing-your-app', 'blocks-and-event-listeners']) {
    const req = new Request('https://example.com/guides/' + guide, {
        headers: { 'user-agent': 'GPTBot/1.0' }
    });
    let nextCalled = false;
    const ctx = {
        request: req,
        params: { guide },
        next: () => { nextCalled = true; return new Response('fallthrough'); }
    };
    const res = await mod.serveGuideMarkdown(ctx);
    const loc = res.headers.get('location') || '';
    if (res.status < 300 || res.status >= 400 || !loc.includes('/api/markdown/guide/' + guide) || nextCalled) {
        process.stdout.write('FAIL:' + guide);
        process.exit(0);
    }
}
process.stdout.write('PASS');
""")
    assert out == "PASS", f"serveGuideMarkdown redirect check failed: {out}"


# [pr_diff] fail_to_pass
def test_no_subrequest():
    """Handlers must not make fetch() subrequests for LLM requests."""
    out = _run_tsx("""
// Override fetch to detect subrequests
let fetchCalled = false;
globalThis.fetch = () => {
    fetchCalled = true;
    return Promise.resolve(new Response('{"markdown":"x"}', { status: 200 }));
};

const mod = await import('/repo/js/_website/functions/_shared.ts');
for (const [fn, params] of [
    ['serveDocMarkdown', { doc: 'textbox' }],
    ['serveDocMarkdown', { doc: 'chatbot' }],
    ['serveGuideMarkdown', { guide: 'quickstart' }],
]) {
    fetchCalled = false;
    const req = new Request('https://example.com/test', {
        headers: { 'user-agent': 'claudebot' }
    });
    const ctx = {
        request: req,
        params,
        next: () => new Response('fallthrough')
    };
    await mod[fn](ctx);
    if (fetchCalled) {
        process.stdout.write('FAIL:' + fn + ':' + JSON.stringify(params));
        process.exit(0);
    }
}
process.stdout.write('PASS');
""")
    assert out == "PASS", f"Subrequest detection failed: {out}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_llm_fallthrough():
    """Non-LLM user-agents fall through to next() for both handlers."""
    out = _run_tsx("""
const mod = await import('/repo/js/_website/functions/_shared.ts');
for (const [fn, params] of [
    ['serveDocMarkdown', { doc: 'textbox' }],
    ['serveDocMarkdown', { doc: 'slider' }],
    ['serveGuideMarkdown', { guide: 'quickstart' }],
    ['serveGuideMarkdown', { guide: 'sharing-your-app' }],
]) {
    const req = new Request('https://example.com/test', {
        headers: { 'user-agent': 'Mozilla/5.0 Chrome/120' }
    });
    let nextCalled = false;
    const ctx = {
        request: req,
        params,
        next: () => { nextCalled = true; return new Response('normal page', { status: 200 }); }
    };
    const res = await mod[fn](ctx);
    if (!nextCalled || res.status !== 200) {
        process.stdout.write('FAIL:' + fn);
        process.exit(0);
    }
}
process.stdout.write('PASS');
""")
    assert out == "PASS", f"Non-LLM fallthrough check failed: {out}"


# [agent_config] pass_to_pass
def test_prettier_formatting():
    """Changed TypeScript file must be formatted with prettier (AGENTS.md line 44)."""
    # Check only the target file (not the whole repo which has pre-existing issues)
    result = subprocess.run(
        ["bash", "-c", f"cd /repo && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && npx prettier --ignore-path .config/.prettierignore --check --config .config/.prettierrc.json --plugin prettier-plugin-svelte {TARGET}"],
        capture_output=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"prettier check failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )


# [static] pass_to_pass
def test_exports_callable():
    """serveDocMarkdown and serveGuideMarkdown are exported async functions."""
    out = _run_tsx("""
const mod = await import('/repo/js/_website/functions/_shared.ts');
if (typeof mod.serveDocMarkdown === 'function' && typeof mod.serveGuideMarkdown === 'function') {
    process.stdout.write('PASS');
} else {
    process.stdout.write('FAIL:doc=' + typeof mod.serveDocMarkdown + ',guide=' + typeof mod.serveGuideMarkdown);
}
""")
    assert out == "PASS", f"Exports check failed: {out}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests — verify repo's own checks pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """Target TypeScript file must compile without errors (pass_to_pass)."""
    script = f"""
const mod = await import('{REPO}/{TARGET}');
if (typeof mod.serveDocMarkdown === 'function' && typeof mod.serveGuideMarkdown === 'function') {{
    process.stdout.write('PASS');
}} else {{
    process.stdout.write('FAIL: exports not found');
    process.exit(1);
}}
"""
    out = _run_tsx(script)
    assert out == "PASS", f"TypeScript syntax check failed: {out}"
