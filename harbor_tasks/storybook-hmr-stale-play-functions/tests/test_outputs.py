"""Behavior checks for storybookjs/storybook PR #33930.

The PR fixes HMR race conditions where stale play functions fired on
re-rendered stories. The fix:
  - index-json.ts: trailing-only debounce (was leading+trailing)
  - codegen-modern-iframe-script.ts: emit STORY_HOT_UPDATED at top of accept
  - codegen-project-annotations.ts: emit STORY_HOT_UPDATED at top of accept
  - virtualModuleModernEntry.js (webpack5): emit STORY_HOT_UPDATED at top of accept

Two tests subprocess into vitest using helper TypeScript files that we
materialise at runtime (not committed alongside test_outputs.py because
only test.sh / test_outputs.py / eval_manifest.yaml / standalone_judge.py
are allowed in tests/).
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/storybook")
CODE = REPO / "code"

VITE_BUILDER = CODE / "builders" / "builder-vite"
WEBPACK5_BUILDER = CODE / "builders" / "builder-webpack5"
CORE_SERVER_UTILS = CODE / "core" / "src" / "core-server" / "utils"

VITEST_ENV = {
    **os.environ,
    "NODE_OPTIONS": "--max_old_space_size=4096",
    "CI": "1",
}


def _run_vitest(spec: str, name_filter: str | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a single vitest file (or file + -t pattern), surfacing output on failure."""
    args = ["yarn", "vitest", "run", "--no-coverage", "--reporter=default", spec]
    if name_filter:
        args.extend(["-t", name_filter])
    return subprocess.run(
        args,
        cwd=str(CODE),
        env=VITEST_ENV,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# Helper TS test bodies materialised at runtime — we keep them as strings
# rather than separate .ts files because tests/ is restricted to
# test.sh / test_outputs.py / eval_manifest.yaml / standalone_judge.py.
_PROJECT_ANNOTATIONS_TS = r"""
import { describe, expect, it } from 'vitest';

import { generateProjectAnnotationsCodeFromPreviews } from './codegen-project-annotations';

function checkEmitOrdering(code: string) {
  const acceptCbIdx = code.indexOf('(previewAnnotationModules) =>');
  const emitIdx = code.indexOf("emit('storyHotUpdated')");
  const onChangedIdx = code.indexOf('onGetProjectAnnotationsChanged');

  expect(acceptCbIdx, `(previewAnnotationModules) => not found in:\n${code}`).toBeGreaterThanOrEqual(0);
  expect(emitIdx, `emit('storyHotUpdated') not found in:\n${code}`).toBeGreaterThanOrEqual(0);
  expect(onChangedIdx, `onGetProjectAnnotationsChanged not found in:\n${code}`).toBeGreaterThanOrEqual(0);

  expect(emitIdx).toBeGreaterThan(acceptCbIdx);
  expect(emitIdx).toBeLessThan(onChangedIdx);
}

describe('codegen-project-annotations: STORY_HOT_UPDATED emit ordering', () => {
  it('non-CSF4: emits storyHotUpdated inside accept callback before onGetProjectAnnotationsChanged', () => {
    const result = generateProjectAnnotationsCodeFromPreviews({
      previewAnnotations: ['/proj/preview.ts'],
      projectRoot: '/proj',
      frameworkName: '@storybook/react-vite',
      isCsf4: false,
    });
    expect(typeof result).toBe('string');
    checkEmitOrdering(result);
  });

  it('CSF4: emits storyHotUpdated inside accept callback before onGetProjectAnnotationsChanged', () => {
    const result = generateProjectAnnotationsCodeFromPreviews({
      previewAnnotations: ['/proj/preview.ts'],
      projectRoot: '/proj',
      frameworkName: '@storybook/react-vite',
      isCsf4: true,
    });
    expect(typeof result).toBe('string');
    checkEmitOrdering(result);
  });
});
"""


_INDEX_JSON_TS = r"""
import { join } from 'node:path';

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { normalizeStoriesEntry } from 'storybook/internal/common';
import { STORY_INDEX_INVALIDATED } from 'storybook/internal/core-events';

import { debounce } from 'es-toolkit/function';
import type { Polka } from 'polka';
import Watchpack from 'watchpack';

import { csfIndexer } from '../presets/common-preset';
import type { StoryIndexGeneratorOptions } from './StoryIndexGenerator';
import { StoryIndexGenerator } from './StoryIndexGenerator';
import type { ServerChannel } from './get-server-channel';
import { registerIndexJsonRoute } from './index-json';

vi.mock('watchpack');
vi.mock('es-toolkit/function', { spy: true });
vi.mock('storybook/internal/node-logger');

vi.mock('../utils/constants', () => {
  return {
    defaultStaticDirs: [{ from: './from', to: './to' }],
    defaultFavicon: './favicon.svg',
  };
});

const workingDir = join(__dirname, '__mockdata__');
const normalizedStories = [
  normalizeStoriesEntry(
    {
      titlePrefix: '',
      directory: './src',
      files: '**/*.stories.@(ts|js|mjs|jsx)',
    },
    { workingDir, configDir: workingDir }
  ),
];

const getStoryIndexGeneratorPromise = async () => {
  const options: StoryIndexGeneratorOptions = {
    indexers: [csfIndexer],
    configDir: workingDir,
    workingDir,
    docs: { defaultName: 'docs' },
  };
  const generator = new StoryIndexGenerator(normalizedStories, options);
  await generator.initialize();
  return generator;
};

describe('registerIndexJsonRoute (scaffold f2p)', () => {
  const use = vi.fn();
  const app: Polka = { use } as any;

  beforeEach(async () => {
    use.mockClear();
    vi.mocked(debounce).mockImplementation(
      (await vi.importActual<typeof import('es-toolkit/function')>('es-toolkit/function'))
        .debounce
    );
    Watchpack.mockClear();
  });

  it('emits STORY_INDEX_INVALIDATED only once when two distinct paths are queued in a single watch batch', async () => {
    const mockServerChannel = { emit: vi.fn() } as any as ServerChannel;
    registerIndexJsonRoute({
      app,
      channel: mockServerChannel,
      workingDir,
      normalizedStories,
      storyIndexGeneratorPromise: getStoryIndexGeneratorPromise(),
    });

    const watcher = Watchpack.mock.instances[0];
    const onChange = watcher.on.mock.calls[0][1];

    onChange(`${workingDir}/src/nested/Foo.stories.ts`);
    onChange(`${workingDir}/src/nested/Bar.stories.ts`);

    await new Promise((resolve) => setTimeout(resolve, 600));

    expect(mockServerChannel.emit).toHaveBeenCalledTimes(1);
    expect(mockServerChannel.emit).toHaveBeenCalledWith(STORY_INDEX_INVALIDATED);
  });
});
"""


def _run_with_helper(target_path: Path, helper_text: str, spec: str) -> subprocess.CompletedProcess:
    """Materialise a helper .ts file inside the repo, run vitest on it, then clean up."""
    target_path.write_text(helper_text)
    try:
        return _run_vitest(spec, timeout=600)
    finally:
        try:
            target_path.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# F2P 1: snapshot tests in codegen-modern-iframe-script.test.ts
# ---------------------------------------------------------------------------
def test_iframe_codegen_snapshots_match():
    """generateModernIframeScriptCodeFromPreviews must produce code that
    emits STORY_HOT_UPDATED inside accept callback (no vite:afterUpdate).
    The upstream snapshot tests encode the new expected output."""
    spec = "builders/builder-vite/src/codegen-modern-iframe-script.test.ts"
    r = _run_vitest(spec)
    assert r.returncode == 0, (
        "Iframe codegen snapshot tests failed.\n"
        f"STDOUT (last 3KB):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 2KB):\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# F2P 2: real-debounce behavior — two paths in one batch should emit once
# ---------------------------------------------------------------------------
def test_index_json_emits_once_for_two_paths_in_batch():
    """Fires two distinct paths in a single watch batch (so two
    maybeInvalidate calls happen in succession). With a leading+trailing
    debounce that produces TWO emits (leading from call-1 + trailing from
    call-2). With trailing-only it produces ONE emit. We assert ONE."""
    target = CORE_SERVER_UTILS / "index_json_scaffold.test.ts"
    spec = f"core/src/core-server/utils/{target.name}"
    r = _run_with_helper(target, _INDEX_JSON_TS, spec)
    assert r.returncode == 0, (
        "index-json real-debounce test failed.\n"
        f"STDOUT (last 3KB):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 2KB):\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# F2P 3: project-annotations codegen — emit BEFORE handler in accept callback
# ---------------------------------------------------------------------------
def test_project_annotations_codegen_structure():
    """generateProjectAnnotationsCodeFromPreviews's output must emit
    STORY_HOT_UPDATED inside the accept callback BEFORE
    onGetProjectAnnotationsChanged is invoked."""
    target = VITE_BUILDER / "src" / "codegen_project_annotations_scaffold.test.ts"
    spec = f"builders/builder-vite/src/{target.name}"
    r = _run_with_helper(target, _PROJECT_ANNOTATIONS_TS, spec)
    assert r.returncode == 0, (
        "project-annotations codegen structure test failed.\n"
        f"STDOUT (last 3KB):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 2KB):\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# F2P 4: webpack5 template emits HOT_UPDATED inside accept callback
# ---------------------------------------------------------------------------
def test_webpack5_template_emits_in_accept():
    """The webpack5 modern entry template must emit STORY_HOT_UPDATED at the
    top of each accept callback, not via a separate addStatusHandler.
    This is a static template file consumed verbatim by webpack5; checking
    its structure is the natural verification."""

    template = WEBPACK5_BUILDER / "templates" / "virtualModuleModernEntry.js"
    src = template.read_text()

    assert "addStatusHandler" not in src, (
        "virtualModuleModernEntry.js still uses addStatusHandler for STORY_HOT_UPDATED.\n"
        "Expected: emit STORY_HOT_UPDATED at the top of each webpackHot.accept callback."
    )

    stories_accept = re.search(
        r"import\.meta\.webpackHot\.accept\(\s*'\{\{storiesFilename\}\}'\s*,\s*\(\)\s*=>\s*\{(.*?)\}\s*\)\s*;",
        src,
        re.DOTALL,
    )
    assert stories_accept, "could not locate the {{storiesFilename}} accept block"
    body = stories_accept.group(1)
    emit_pos = body.find("emit(STORY_HOT_UPDATED)")
    on_changed_pos = body.find("preview.onStoriesChanged")
    assert emit_pos >= 0, (
        f"missing emit(STORY_HOT_UPDATED) inside {{{{storiesFilename}}}} accept callback. Body:\n{body}"
    )
    assert on_changed_pos >= 0, "missing preview.onStoriesChanged inside accept body"
    assert emit_pos < on_changed_pos, (
        "emit(STORY_HOT_UPDATED) must occur BEFORE preview.onStoriesChanged "
        "inside the {{storiesFilename}} accept callback."
    )

    pa_accept = re.search(
        r"import\.meta\.webpackHot\.accept\(\s*\[\s*'\{\{previewAnnotations\}\}'\s*\]\s*,\s*\(\)\s*=>\s*\{(.*?)\}\s*\)\s*;",
        src,
        re.DOTALL,
    )
    assert pa_accept, "could not locate the {{previewAnnotations}} accept block"
    body2 = pa_accept.group(1)
    emit_pos2 = body2.find("emit(STORY_HOT_UPDATED)")
    on_changed_pos2 = body2.find("preview.onGetProjectAnnotationsChanged")
    assert emit_pos2 >= 0, (
        f"missing emit(STORY_HOT_UPDATED) inside {{{{previewAnnotations}}}} accept callback. Body:\n{body2}"
    )
    assert on_changed_pos2 >= 0, "missing preview.onGetProjectAnnotationsChanged inside accept body"
    assert emit_pos2 < on_changed_pos2, (
        "emit(STORY_HOT_UPDATED) must occur BEFORE preview.onGetProjectAnnotationsChanged "
        "inside the {{previewAnnotations}} accept callback."
    )


# ---------------------------------------------------------------------------
# P2P: existing 'debounces invalidation events' test still passes
# ---------------------------------------------------------------------------
def test_index_json_debounces_invalidation_events():
    """Existing upstream test 'debounces invalidation events' — passes on
    both base and gold (the assertion logic is compatible with both edge
    configs)."""
    spec = "core/src/core-server/utils/index-json.test.ts"
    r = _run_vitest(spec, name_filter="debounces invalidation events")
    assert r.returncode == 0, (
        "index-json debounces test failed.\n"
        f"STDOUT (last 3KB):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 2KB):\n{r.stderr[-2000:]}"
    )
