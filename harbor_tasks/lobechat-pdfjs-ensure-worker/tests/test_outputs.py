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

    # Core requirement: module must configure GlobalWorkerOptions.workerSrc
    assert "GlobalWorkerOptions.workerSrc" in content, \
        "Module must configure GlobalWorkerOptions.workerSrc"

    # Must use the npmmirror CDN for the pdfjs-dist worker URL
    assert "registry.npmmirror.com/pdfjs-dist" in content, \
        "Module must use the npmmirror CDN for the pdfjs-dist worker"

    # Must export Document, Page, and pdfjs for consuming components
    assert re.search(r'export\b.*\bDocument\b', content), \
        "Module must export a Document component"
    assert re.search(r'export\b.*\bPage\b', content), \
        "Module must export Page"
    assert re.search(r'export\b.*\bpdfjs\b', content), \
        "Module must export pdfjs"

    # Behavioral subprocess check: extract the CDN URL template literal and verify
    # it correctly interpolates the pdfjs version number using Node
    url_match = re.search(r'`([^`]*registry\.npmmirror\.com/pdfjs-dist/[^`]*)`', content)
    assert url_match, \
        "Worker URL must be a template literal using the npmmirror CDN"
    url_template = url_match.group(1)

    result = subprocess.run(
        ["node", "-e",
         "const pdfjs = { version: '4.8.69' };"
         f"const url = `{url_template}`;"
         "if (url.includes('4.8.69') && url.includes('pdf.worker')) {"
         "  console.log('OK');"
         "} else {"
         "  console.log('FAIL:' + url);"
         "}"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    assert result.stdout.strip() == "OK", \
        f"Worker URL did not interpolate correctly: {result.stdout}"


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
    """SharePdf/PdfPreview must import from the unified @/libs/pdfjs module."""
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
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:]}"


def test_repo_stylelint_passes():
    """Repo's Stylelint check passes (pass_to_pass).
    Ensures CSS/styling standards are maintained.
    """
    r = subprocess.run(
        ["npm", "run", "lint:style"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-1000:]}"


def test_repo_no_circular_deps():
    """Repo has no circular dependencies in main src (pass_to_pass).
    Ensures the module dependency graph remains healthy.
    """
    r = subprocess.run(
        ["npm", "run", "lint:circular:main"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular dependency check failed:\n{r.stderr[-1000:]}"


def test_repo_component_tests_pass():
    """Component unit tests pass (pass_to_pass).
    Runs a focused subset of tests to verify core functionality.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "--reporter=verbose", "src/components"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Component tests failed:\n{r.stderr[-1000:]}"


def test_repo_hooks_tests_pass():
    """Hook unit tests pass (pass_to_pass).
    Verifies React hooks functionality is intact.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "src/hooks"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Hooks tests failed:\n{r.stderr[-1000:]}"


def test_repo_sharemodal_tests_pass():
    """ShareModal tests pass (pass_to_pass).
    Verifies ShareModal functionality including SharePdf components.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "src/features/ShareModal"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ShareModal tests failed:\n{r.stderr[-1000:]}"


def test_repo_features_tests_pass():
    """Feature tests pass (pass_to_pass).
    Verifies feature-level functionality across the app.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "src/features"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Features tests failed:\n{r.stderr[-1000:]}"


def test_repo_services_tests_pass():
    """Service layer tests pass (pass_to_pass).
    Verifies service layer functionality including file services.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "src/services"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Services tests failed:\n{r.stderr[-1000:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_packages_test_packages_with_coverage():
    """pass_to_pass | CI job 'Test Packages' → step 'Test packages with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run --filter $package test:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test packages with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_desktop_app_typecheck_desktop():
    """pass_to_pass | CI job 'Test Desktop App' → step 'Typecheck Desktop'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm type-check'], cwd=os.path.join(REPO, 'apps/desktop'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck Desktop' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_desktop_app_test_desktop_client():
    """pass_to_pass | CI job 'Test Desktop App' → step 'Test Desktop Client'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=os.path.join(REPO, 'apps/desktop'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Desktop Client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_lint():
    """pass_to_pass | CI job 'Test Database' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_test_client_db():
    """pass_to_pass | CI job 'Test Database' → step 'Test Client DB'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:client-db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Client DB' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_test_coverage():
    """pass_to_pass | CI job 'Test Database' → step 'Test Coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_desktop_next_bundle_build_desktop_next_js_bundle():
    """pass_to_pass | CI job 'Build desktop Next bundle' → step 'Build desktop Next.js bundle'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run desktop:build-electron'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build desktop Next.js bundle' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")