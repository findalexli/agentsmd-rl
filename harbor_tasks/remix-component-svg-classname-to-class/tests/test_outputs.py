"""Behavioral tests for the SVG className -> class normalization fix.

The PR fixes two prop-name normalization paths in @remix-run/component:
 - SSR (renderToStream)  → packages/component/src/lib/stream.ts
 - VDOM diff             → packages/component/src/lib/diff-props.ts

At base, both paths only handled `className -> class` for non-SVG
elements. For SVG, `className` fell through to camelToKebab() and
rendered as `class-name="..."`, which is wrong. The fix moves the rule
above the `!isSvg` guard so SVG also gets the standard mapping.

These tests construct elements via the package's `jsx()` factory rather
than JSX syntax so they run under plain `tsx` without needing the
project's JSX runtime to be wired into a transform.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")
COMPONENT = REPO / "packages" / "component"


def _run_tsx(name: str, body: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Write a one-off TypeScript script into the component package and run
    it under `tsx`."""
    script = COMPONENT / f".__taskforge_{name}.ts"
    script.write_text(body)
    try:
        env = os.environ.copy()
        env.setdefault("NODE_NO_WARNINGS", "1")
        return subprocess.run(
            ["pnpm", "exec", "tsx", script.name],
            cwd=str(COMPONENT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    finally:
        try:
            script.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# fail-to-pass: SSR (renderToStream) renders className as class for SVG
# ---------------------------------------------------------------------------

def test_ssr_svg_classname_renders_as_class():
    """`<svg className="icon">` rendered via renderToStream should yield
    `class="icon"` in the output HTML, never `class-name="icon"` and never
    a `classname="..."` attribute."""
    r = _run_tsx(
        "ssr_classname",
        """
import { renderToStream } from './src/lib/stream.ts'
import { drain } from './src/test/utils.ts'
import { jsx } from './src/lib/jsx.ts'

;(async () => {
  let svgEl = jsx('svg', {
    viewBox: '0 0 24 24',
    fill: 'none',
    className: 'icon',
    children: jsx('path', { d: 'm0 0' }),
  })
  let stream = renderToStream(svgEl)
  let html = await drain(stream)
  process.stdout.write(html)
})()
""",
    )
    assert r.returncode == 0, f"tsx failed: {r.stderr}\nstdout: {r.stdout}"
    html = r.stdout

    assert 'class="icon"' in html, (
        f"Expected SVG to render with class=\"icon\"; got: {html!r}"
    )
    # Bug at base: camelToKebab('className') => 'class-name'
    assert "class-name" not in html, (
        f"SVG should not contain kebab-cased 'class-name' attribute; got: {html!r}"
    )
    # And a literal lowercase 'classname=' attribute is also wrong.
    assert "classname=" not in html.lower().replace('class="', '').replace("class='", ""), (
        f"SVG should not contain a 'classname=' attribute; got: {html!r}"
    )


def test_ssr_svg_classname_full_expected_output():
    """End-to-end SSR output for the canonical SVG icon snippet matches the
    expected string exactly."""
    r = _run_tsx(
        "ssr_full",
        """
import { renderToStream } from './src/lib/stream.ts'
import { drain } from './src/test/utils.ts'
import { jsx } from './src/lib/jsx.ts'

;(async () => {
  let svgEl = jsx('svg', {
    viewBox: '0 0 24 24',
    fill: 'none',
    className: 'icon',
    children: jsx('path', {
      strokeLinecap: 'round',
      strokeLinejoin: 'round',
      d: 'm4.5 12.75 6 6 9-13.5',
    }),
  })
  let stream = renderToStream(svgEl)
  let html = await drain(stream)
  process.stdout.write(html)
})()
""",
    )
    assert r.returncode == 0, f"tsx failed: {r.stderr}\nstdout: {r.stdout}"
    expected = (
        '<svg viewBox="0 0 24 24" fill="none" class="icon">'
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m4.5 12.75 6 6 9-13.5"></path></svg>'
    )
    assert r.stdout == expected, (
        f"SSR output mismatch.\nExpected: {expected!r}\nActual:   {r.stdout!r}"
    )


def test_ssr_html_classname_still_renders_as_class():
    """Regression: non-SVG elements continue to map className -> class.
    Guards against an agent breaking the existing HTML mapping while
    fixing SVG."""
    r = _run_tsx(
        "ssr_html_classname",
        """
import { renderToStream } from './src/lib/stream.ts'
import { drain } from './src/test/utils.ts'
import { jsx } from './src/lib/jsx.ts'

;(async () => {
  let div = jsx('div', { className: 'card', children: 'hi' })
  let stream = renderToStream(div)
  let html = await drain(stream)
  process.stdout.write(html)
})()
""",
    )
    assert r.returncode == 0, f"tsx failed: {r.stderr}\nstdout: {r.stdout}"
    assert 'class="card"' in r.stdout, r.stdout
    assert "class-name" not in r.stdout, r.stdout
    assert "classname=" not in r.stdout.lower().replace('class=', ''), r.stdout


# ---------------------------------------------------------------------------
# fail-to-pass: VDOM (createRoot) sets `class` attribute for SVG className
# ---------------------------------------------------------------------------

def test_vdom_svg_classname_sets_class_attribute():
    """createRoot/render for an SVG element with `className` should call
    setAttribute('class', value) on the SVGElement, never 'class-name'.

    Uses happy-dom to provide DOM globals so the VDOM runtime can run
    without a real browser."""
    r = _run_tsx(
        "vdom_classname",
        """
import { Window } from 'happy-dom'

let window = new Window()
let g = globalThis as any
g.window = window
g.document = window.document
g.Element = window.Element
g.Node = window.Node
g.Text = window.Text
g.DocumentFragment = window.DocumentFragment
g.HTMLElement = window.HTMLElement
g.SVGElement = window.SVGElement
g.Comment = window.Comment
g.Range = window.Range
g.MutationObserver = window.MutationObserver
g.requestAnimationFrame = (cb: any) => setTimeout(() => cb(performance.now()), 0)
g.cancelAnimationFrame = (id: any) => clearTimeout(id)

import { createRoot } from './src/index.ts'
import { jsx } from './src/lib/jsx.ts'

;(async () => {
  let container = window.document.createElement('div')
  let root = createRoot(container as any)

  let svgEl = jsx('svg', {
    viewBox: '0 0 24 24',
    fill: 'none',
    className: 'icon',
    children: jsx('path', {
      strokeLinecap: 'round',
      strokeLinejoin: 'round',
      d: 'm4.5 12.75 6 6 9-13.5',
    }),
  })
  root.render(svgEl)
  root.flush()

  let svg = container.querySelector('svg')!
  let path = svg.querySelector('path')!

  let payload = {
    class: svg.getAttribute('class'),
    classDash: svg.getAttribute('class-name'),
    classname: svg.getAttribute('classname'),
    viewBox: svg.getAttribute('viewBox'),
    pathStrokeLinecap: path.getAttribute('stroke-linecap'),
  }
  console.log(JSON.stringify(payload))
})()
""",
        timeout=180,
    )
    assert r.returncode == 0, f"tsx failed: {r.stderr}\nstdout: {r.stdout}"
    last_line = r.stdout.strip().splitlines()[-1]
    payload = json.loads(last_line)

    assert payload["class"] == "icon", (
        f"SVG should have class='icon'; got payload={payload}"
    )
    assert payload["classDash"] is None, (
        f"SVG should NOT have a 'class-name' attribute; got payload={payload}"
    )
    assert payload["classname"] is None, (
        f"SVG should NOT have a lowercase 'classname' attribute; got payload={payload}"
    )
    assert payload["viewBox"] == "0 0 24 24", (
        f"viewBox should be preserved as camelCase; got payload={payload}"
    )
    assert payload["pathStrokeLinecap"] == "round", (
        f"path stroke-linecap should still be kebab-cased; got payload={payload}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: typecheck of the component package still succeeds
# ---------------------------------------------------------------------------

def test_component_package_typecheck():
    """`pnpm --filter @remix-run/component run typecheck` must succeed
    on both base and patched code."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/component", "run", "typecheck"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"typecheck failed (rc={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: changes:validate still passes
# ---------------------------------------------------------------------------

def test_changes_validate():
    """Repo's change-file validator must keep passing. After the patch a
    new `patch.fix-svg-classname-mapping.md` file exists; the validator
    must accept it."""
    r = subprocess.run(
        ["pnpm", "run", "changes:validate"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"changes:validate failed:\nstdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")