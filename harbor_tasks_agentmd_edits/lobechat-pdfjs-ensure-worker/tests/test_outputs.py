"""Tests for lobechat-pdfjs-ensure-worker task.

PR: lobehub/lobe-chat#11746
Fix: PDF worker config guaranteed before Document render + CLAUDE.md Linear section restructured.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/lobe-chat")


def test_ensure_worker_sets_src():
    """The pdfjs module must set GlobalWorkerOptions.workerSrc before Document renders.
    This is the core behavioral fix — without it, PDF rendering fails with
    'No GlobalWorkerOptions.workerSrc specified' error under TurboPack."""
    module_path = REPO / "src/libs/pdfjs/index.tsx"
    assert module_path.exists(), "Unified pdfjs module must exist at src/libs/pdfjs/index.tsx"
    content = module_path.read_text()

    # Extract the workerSrc template from the module
    match = re.search(r"const workerSrc\s*=\s*`([^`]+)`", content)
    assert match, "Module must define a workerSrc template literal"

    # Verify ensureWorker references GlobalWorkerOptions
    assert "GlobalWorkerOptions.workerSrc" in content, \
        "ensureWorker must set GlobalWorkerOptions.workerSrc"

    # Verify the Document export actually CALLS ensureWorker (not just defines it)
    assert "ensureWorker()" in content, \
        "Document export must call ensureWorker() in its body"

    # Execute the ensureWorker logic with node to verify it correctly sets workerSrc
    worker_src_template = match.group(1)
    script = (
        "const pdfjs = { version: '4.0.0', GlobalWorkerOptions: { workerSrc: null } };"
        f"const workerSrc = `{worker_src_template}`;"
        "function ensureWorker() {"
        "  if (!pdfjs.GlobalWorkerOptions.workerSrc) {"
        "    pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;"
        "  }"
        "}"
        "ensureWorker();"
        "if (pdfjs.GlobalWorkerOptions.workerSrc && "
        "    pdfjs.GlobalWorkerOptions.workerSrc.includes('4.0.0') && "
        "    pdfjs.GlobalWorkerOptions.workerSrc.includes('pdf.worker')) {"
        "  console.log('OK');"
        "} else {"
        "  console.log('FAIL:' + pdfjs.GlobalWorkerOptions.workerSrc);"
        "}"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    assert result.stdout.strip() == "OK", \
        f"ensureWorker did not set workerSrc correctly: {result.stdout}"


def test_old_worker_files_removed():
    """Side-effect import files must be deleted. They were unreliable because
    TurboPack could optimize away side-effect imports."""
    assert not (REPO / "src/libs/pdfjs/worker.ts").exists(), \
        "worker.ts should be removed — unreliable side-effect import"
    assert not (REPO / "src/libs/pdfjs/pdf.worker.ts").exists(), \
        "pdf.worker.ts should be removed — unused worker entry"


def test_pdf_viewer_imports_unified():
    """PDF FileViewer must import from the unified @/libs/pdfjs module,
    not directly from react-pdf or the old side-effect worker import."""
    content = (REPO / "src/features/FileViewer/Renderer/PDF/index.tsx").read_text()
    assert "@/libs/pdfjs" in content, \
        "Must import from unified @/libs/pdfjs module"
    assert "from 'react-pdf'" not in content, \
        "Should not import directly from react-pdf — use unified module"
    assert "'@/libs/pdfjs/worker'" not in content, \
        "Old side-effect worker import must be removed"


def test_pdf_preview_imports_unified():
    """SharePdf/PdfPreview must import from unified @/libs/pdfjs module."""
    content = (REPO / "src/features/ShareModal/SharePdf/PdfPreview.tsx").read_text()
    assert "@/libs/pdfjs" in content, \
        "Must import from unified @/libs/pdfjs module"
    assert "from 'react-pdf'" not in content, \
        "Should not import directly from react-pdf — use unified module"
    assert "'@/libs/pdfjs/worker'" not in content, \
        "Old side-effect worker import must be removed"


def test_claude_md_linear_section_updated():
    """CLAUDE.md Linear Issue Management section must be restructured with
    explicit trigger conditions and a numbered workflow."""
    content = (REPO / "CLAUDE.md").read_text()
    assert "Trigger condition" in content, \
        "CLAUDE.md must list trigger conditions for Linear workflow"
    assert "Workflow:" in content, \
        "CLAUDE.md must have a Workflow: section"
    assert "ToolSearch" in content, \
        "Workflow must mention ToolSearch for discovering linear-server MCP"


def test_pdf_viewers_still_use_document():
    """Both PDF viewers must still render the Document component for PDF display.
    This is a pass-to-pass check — the fix should not remove Document rendering."""
    pdf_viewer = (REPO / "src/features/FileViewer/Renderer/PDF/index.tsx").read_text()
    pdf_preview = (REPO / "src/features/ShareModal/SharePdf/PdfPreview.tsx").read_text()
    assert "<Document" in pdf_viewer, \
        "PDF viewer must still render <Document>"
    assert "<Document" in pdf_preview, \
        "PDF preview must still render <Document>"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD Checks
# These verify that the repo's standard CI checks pass on both base and fixed.
# =============================================================================


def test_repo_eslint_passes():
    """Repo's ESLint check passes (pass_to_pass).
    Ensures code style and quality standards are maintained.
    """
    r = subprocess.run(
        ["npm", "run", "lint:ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:]}"


def test_repo_stylelint_passes():
    """Repo's Stylelint check passes (pass_to_pass).
    Ensures CSS/styling standards are maintained.
    """
    r = subprocess.run(
        ["npm", "run", "lint:style"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-1000:]}"


def test_repo_no_circular_deps():
    """Repo has no circular dependencies in main src (pass_to_pass).
    Ensures the module dependency graph remains healthy.
    """
    r = subprocess.run(
        ["npm", "run", "lint:circular:main"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular dependency check failed:\n{r.stderr[-1000:]}"


def test_repo_component_tests_pass():
    """Component unit tests pass (pass_to_pass).
    Runs a focused subset of tests to verify core functionality.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "--reporter=verbose", "src/components"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Component tests failed:\n{r.stderr[-1000:]}"
