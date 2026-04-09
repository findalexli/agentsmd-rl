#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'const runtime = target.os === "windows" && target.arch === "aarch64"' .buildkite/ci.mjs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full PR patch
git apply - <<'PATCH'
diff --git a/.buildkite/ci.mjs b/.buildkite/ci.mjs
index d9a04bd7957..312f644a7a0 100755
--- a/.buildkite/ci.mjs
+++ b/.buildkite/ci.mjs
@@ -497,7 +497,11 @@ function getBuildCommand(target, options, mode) {
   // is wrong. PATH on the agent has node via bootstrap.sh.
   // --experimental-strip-types for Node 24's .ts support (unflagged in
   // 25+; drop once CI bumps past the ABI-141 blocker).
-  return `node --experimental-strip-types scripts/build.ts ${getBuildArgs(target, options, mode)}`;
+  //
+  // Windows ARM64 node v24 intermittently fastfails (0xC0000409) in
+  // fetch-cli.ts; run build.ts under bun there instead.
+  const runtime = target.os === "windows" && target.arch === "aarch64" ? "bun" : "node --experimental-strip-types";
+  return `${runtime} scripts/build.ts ${getBuildArgs(target, options, mode)}`;
 }

 /**
@@ -808,6 +812,37 @@ function getWindowsSignStep(windowsPlatforms, options) {
   };
 }

+/**
+ * Aggregates stripped-binary sizes from every release build, compares them
+ * against the latest main build's binary-sizes.json, and fails if any grew
+ * past the threshold. Runs on PR builds (comparison) and main (record-only,
+ * to produce the baseline artifact).
+ *
+ * @param {Platform[]} releasePlatforms
+ * @param {PipelineOptions} options
+ * @param {{ recordOnly: boolean }} [extra]
+ * @returns {Step}
+ */
+function getBinarySizeStep(releasePlatforms, options, { recordOnly = false } = {}) {
+  const targets = releasePlatforms.map(p => ({ triplet: getTargetTriplet(p) }));
+  const args = [`--targets '${JSON.stringify(targets)}'`, `--threshold-mb ${BINARY_SIZE_THRESHOLD_MB}`];
+  if (recordOnly) args.push("--no-fail");
+
+  return {
+    key: "binary-size",
+    label: `${getBuildkiteEmoji("package")} binary-size`,
+    agents: { queue: "test-darwin" },
+    depends_on: releasePlatforms.map(p => `${getTargetKey(p)}-build-bun`),
+    allow_dependency_failure: true,
+    soft_fail: !!options.skipSizeCheck,
+    retry: getRetry(),
+    cancel_on_build_failing: isMergeQueue(),
+    command: `bun scripts/binary-size.ts ${args.join(" ")}`,
+  };
+}
+
+const BINARY_SIZE_THRESHOLD_MB = 0.5;
+
 /**
  * @param {Platform[]} buildPlatforms
  * @param {PipelineOptions} options
@@ -922,6 +957,7 @@ function getReleaseStep(buildPlatforms, options, { signed = false } = {}) {
  * @property {string | boolean} [skipEverything]
  * @property {string | boolean} [skipBuilds]
  * @property {string | boolean} [skipTests]
+ * @property {string | boolean} [skipSizeCheck]
  * @property {string | boolean} [forceBuilds]
  * @property {string | boolean} [forceTests]
  * @property {string | boolean} [buildImages]
@@ -1201,6 +1237,7 @@ async function getPipelineOptions() {
     skipBuilds: parseOption(/\[(skip builds?|no builds?|only tests?)\]/i),
     forceBuilds: parseOption(/\[(force builds?)\]/i),
     skipTests: parseOption(/\[(skip tests?|no tests?|only builds?)\]/i),
+    skipSizeCheck: parseOption(/\[(skip size( check)?|allow size)\]/i),
     signWindows: parseOption(/\[(sign windows)\]/i),
     buildImages: parseOption(/\[(build (?:(?:windows|linux) )?images?)\]/i),
     dryRun: parseOption(/\[(dry run)\]/i),
@@ -1316,6 +1353,11 @@ async function getPipeline(options = {}) {
     }
   }

+  const strippedPlatforms = buildPlatforms.filter(p => (p.profile ?? "release") === "release");
+  if (!buildId && strippedPlatforms.length) {
+    steps.push(getBinarySizeStep(strippedPlatforms, options, { recordOnly: isMainBranch() }));
+  }
+
   // Sign Windows builds on release (non-canary main) or when [sign windows]
   // is in the commit message (for testing the sign step on a branch).
   // DigiCert charges per signature, so canary builds are never signed.
diff --git a/scripts/binary-size.ts b/scripts/binary-size.ts
new file mode 100644
index 00000000000..735c51c87d1
--- /dev/null
+++ b/scripts/binary-size.ts
@@ -0,0 +1,271 @@
+// Measure stripped binary sizes for every release platform and compare them
+// against (a) the latest finished `main` build ("canary") and (b) a pinned
+// release baseline hardcoded below.
+//
+// Run by the `binary-size` step in .buildkite/ci.mjs after all *-build-bun
+// jobs finish. Always posts an annotation with sizes and deltas. On PR builds
+// it fails if any binary grew by more than --threshold-mb vs canary; on main
+// it never fails (--no-fail) but still shows the comparison against the
+// previous main build and the last release.
+//
+// Escape hatch: put `[skip size check]` in the commit message, which makes
+// ci.mjs set soft_fail on this step (it still runs and annotates).
+//
+// Usage (invoked from ci.mjs — not meant to be run by hand):
+//   bun scripts/binary-size.ts \\
+//     --targets '[{"triplet":"bun-darwin-aarch64"},...]' \\
+//     --threshold-mb 0.5 \\
+//     [--no-fail]
+
+import { mkdirSync, rmSync } from "node:fs";
+import { parseArgs } from "node:util";
+
+type Target = { triplet: string };
+type Sizes = Record<string, number>;
+
+const { values } = parseArgs({
+  options: {
+    targets: { type: "string" },
+    "threshold-mb": { type: "string", default: "0.5" },
+    "no-fail": { type: "boolean", default: false },
+  },
+});
+
+const targets: Target[] = JSON.parse(values.targets!);
+const thresholdBytes = parseFloat(values["threshold-mb"]!) * 1024 * 1024;
+const noFail = values["no-fail"];
+
+const org = process.env.BUILDKITE_ORGANIZATION_SLUG || "bun";
+const pipeline = process.env.BUILDKITE_PIPELINE_SLUG || "bun";
+const buildNumber = process.env.BUILDKITE_BUILD_NUMBER;
+const branch = process.env.BUILDKITE_BRANCH;
+
+function agent(args: string[], opts: { quiet?: boolean } = {}): string | undefined {
+  const { exitCode, stdout } = Bun.spawnSync(["buildkite-agent", ...args], {
+    stderr: opts.quiet ? "ignore" : "inherit",
+  });
+  return exitCode === 0 ? stdout.toString().trim() : undefined;
+}
+
+async function getSecret(name: string): Promise<string | undefined> {
+  const { exitCode, stdout } = Bun.spawnSync(["buildkite-agent", "secret", "get", name], { stderr: "ignore" });
+  if (exitCode !== 0) return undefined;
+  return stdout.toString().trim() || undefined;
+}
+
+// ─── Collect current build's sizes from meta-data ───
+// Each *-build-bun job sets `binary-size:<triplet>` after stripping
+// (scripts/build/ci.ts).
+
+console.log("--- Reading sizes from build meta-data");
+const sizes: Sizes = {};
+for (const { triplet } of targets) {
+  const v = agent(["meta-data", "get", `binary-size:${triplet}`], { quiet: true });
+  if (!v) {
+    console.log(`  ${triplet}: not set (build may have failed), skipping`);
+    continue;
+  }
+  sizes[triplet] = parseInt(v, 10);
+  console.log(`  ${triplet.padEnd(30)} ${fmtBytes(sizes[triplet]).padStart(10)}`);
+}
+
+await Bun.write("binary-sizes.json", JSON.stringify({ build: buildNumber, branch, sizes }, null, 2));
+agent(["artifact", "upload", "binary-sizes.json"]);
+
+// ─── Baselines ───
+
+type Baseline = { label: string; href?: string; sizes: Sizes };
+
+const ghToken = (await getSecret("GITHUB_TOKEN")) ?? process.env.GITHUB_TOKEN;
+const ghHeaders: Record<string, string> = ghToken ? { Authorization: `Bearer ${ghToken}` } : {};
+
+async function githubJson<T>(path: string): Promise<T> {
+  const res = await fetch(`https://api.github.com/repos/oven-sh/bun/${path}`, { headers: ghHeaders });
+  if (!res.ok) throw new Error(`github ${path}: ${res.status}`);
+  return res.json() as Promise<T>;
+}
+
+async function buildNumberForCommit(sha: string): Promise<number | undefined> {
+  const { statuses } = await githubJson<{ statuses: { context: string; target_url: string }[] }>(
+    `commits/${sha}/status`,
+  );
+  const bk = statuses.find(s => s.context.startsWith("buildkite/"));
+  const m = bk?.target_url.match(/\\/builds\\/(\\d+)/);
+  return m ? parseInt(m[1], 10) : undefined;
+}
+
+async function sizesFromBuild(n: number): Promise<Sizes | undefined> {
+  const res = await fetch(`https://buildkite.com/${org}/${pipeline}/builds/${n}.json`);
+  if (!res.ok) return;
+  const { id } = (await res.json()) as { id: string };
+  const dir = "binary-size-tmp";
+  rmSync(dir, { recursive: true, force: true });
+  mkdirSync(dir, { recursive: true });
+  const ok = agent(["artifact", "download", "binary-sizes.json", dir, "--build", id], { quiet: true });
+  if (ok === undefined) return;
+  return ((await Bun.file(`${dir}/binary-sizes.json`).json()) as { sizes: Sizes }).sizes;
+}
+
+async function baselineFromCommit(sha: string, label: (n: number) => string): Promise<Baseline | undefined> {
+  const n = await buildNumberForCommit(sha);
+  if (!n || String(n) === String(buildNumber)) return;
+  const sizes = await sizesFromBuild(n);
+  if (!sizes) return;
+  return { label: label(n), href: `https://buildkite.com/${org}/${pipeline}/builds/${n}`, sizes };
+}
+
+// Canary: walk recent main commits until one whose build has binary-sizes.json.
+console.log("--- Fetching canary baseline");
+let canaryNote = "";
+const canary: Baseline | undefined = await (async () => {
+  const commits = await githubJson<{ sha: string }[]>("commits?sha=main&per_page=15");
+  for (const { sha } of commits) {
+    const b = await baselineFromCommit(sha, n => `main #${n}`);
+    if (b) return b;
+  }
+  canaryNote = "no recent main build has binary-sizes.json yet";
+})().catch(e => ((canaryNote = String(e?.message || e)), undefined));
+console.log(canary ? `  ${canary.label}` : `  unavailable: ${canaryNote}`);
+
+// Release: latest bun-v* tag's commit. Falls back to the hardcoded table
+// until a tagged commit's build carries binary-sizes.json.
+const releaseFallback: Baseline = {
+  label: "bun-v1.3.11",
+  href: "https://github.com/oven-sh/bun/releases/tag/bun-v1.3.11",
+  sizes: {
+    "bun-darwin-aarch64": 61069216,
+    "bun-darwin-x64": 66128448,
+    "bun-linux-aarch64": 98736456,
+    "bun-linux-x64": 99295408,
+    "bun-linux-x64-baseline": 98451632,
+    "bun-linux-aarch64-musl": 93164848,
+    "bun-linux-x64-musl": 94162760,
+    "bun-linux-x64-musl-baseline": 93626184,
+    "bun-windows-x64": 115416576,
+    "bun-windows-x64-baseline": 114743296,
+    "bun-windows-aarch64": 112043008,
+  },
+};
+
+async function fetchReleaseBaseline(): Promise<Baseline | undefined> {
+  const out = Bun.spawnSync(["git", "ls-remote", "--tags", "--sort=-version:refname", "origin", "refs/tags/bun-v*"], {
+    stderr: "inherit",
+  })
+    .stdout.toString()
+    .split("\\n")
+    .find(l => l && !l.includes("^{}"));
+  if (!out) return;
+  const [sha, ref] = out.split("\\t");
+  const tag = ref.replace("refs/tags/", "");
+  return baselineFromCommit(sha, n => `${tag} (#${n})`);
+}
+
+console.log("--- Fetching release baseline");
+const release: Baseline = (await fetchReleaseBaseline().catch(() => undefined)) ?? releaseFallback;
+console.log(`  ${release.label}`);
+
+// ─── Compare & annotate ───
+
+console.log("--- Results");
+
+type Delta = { base: number; bytes: number };
+type Row = { triplet: string; now: number; canary?: Delta; release?: Delta };
+
+function delta(now: number, base: number | undefined): Delta | undefined {
+  if (!base) return undefined;
+  return { base, bytes: now - base };
+}
+
+// Preserve --targets order (buildPlatforms in ci.mjs) so OS families stay grouped.
+const rows: Row[] = targets
+  .filter(t => sizes[t.triplet] !== undefined)
+  .map(({ triplet }) => ({
+    triplet,
+    now: sizes[triplet],
+    canary: delta(sizes[triplet], canary?.sizes[triplet]),
+    release: delta(sizes[triplet], release.sizes[triplet]),
+  }));
+
+const overThreshold = rows.filter(r => r.canary && r.canary.bytes > thresholdBytes);
+const failed = !noFail && overThreshold.length > 0;
+
+const link = (b: Baseline | undefined, fallback: string) =>
+  b?.href ? `<a href="${b.href}">${b.label}</a>` : (b?.label ?? `${fallback} (n/a)`);
+
+const deltaCells = (d: Delta | undefined, over: boolean) => {
+  if (!d) return `<td align="right">—</td><td align="right">—</td>`;
+  return (
+    `<td align="right">${fmtBytes(d.base)}</td>` +
+    `<td align="right">${over ? "<b>" : ""}${fmtDelta(d.bytes)}${over ? "</b>" : ""}</td>`
+  );
+};
+
+const tableRows = rows
+  .map(r => {
+    const over = !!r.canary && r.canary.bytes > thresholdBytes;
+    return (
+      `<tr><td>${over ? "❌ " : ""}<code>${r.triplet}</code></td>` +
+      `<td align="right">${fmtBytes(r.now)}</td>` +
+      deltaCells(r.canary, over) +
+      deltaCells(r.release, false) +
+      `</tr>`
+    );
+  })
+  .join("\\n");
+
+const limit = fmtBytes(thresholdBytes);
+const header =
+  overThreshold.length > 0
+    ? `<b>${overThreshold.length}</b> over ${limit}`
+    : canary
+      ? `all within ${limit}`
+      : `no canary comparison (${canaryNote})`;
+
+const annotation = `
+<details${failed ? " open" : ""}>
+<summary>📦 Binary size — ${header}</summary>
+<table>
+<tr>
+  <th rowspan="2">target</th><th rowspan="2">this build</th>
+  <th colspan="2">canary: ${link(canary, "main")}</th>
+  <th colspan="2">release: ${link(release, "latest")}</th>
+</tr>
+<tr><th>size</th><th>Δ</th><th>size</th><th>Δ</th></tr>
+${tableRows}
+</table>
+${failed ? `<p>Add <code>[skip size check]</code> to the commit message if this increase is intentional.</p>` : ""}
+</details>`;
+
+Bun.spawnSync(
+  [
+    "buildkite-agent",
+    "annotate",
+    "--style",
+    failed ? "error" : "info",
+    "--context",
+    "binary-size",
+    "--priority",
+    failed ? "5" : "2",
+  ],
+  { stdin: new Blob([annotation]), stderr: "inherit" },
+);
+
+for (const r of rows) {
+  const c = r.canary ? `  canary ${fmtDelta(r.canary.bytes).padStart(10)}` : "";
+  const rel = r.release ? `  release ${fmtDelta(r.release.bytes).padStart(10)}` : "";
+  console.log(`  ${r.triplet.padEnd(30)} ${fmtBytes(r.now).padStart(10)}${c}${rel}`);
+}
+
+if (failed) {
+  console.error(`\\nerror: ${overThreshold.length} target(s) exceeded ${limit} vs canary`);
+  process.exit(1);
+}
+
+// ─── helpers ───
+
+function fmtBytes(n: number): string {
+  return `${(n / 1024 / 1024).toFixed(2)} MB`;
+}
+function fmtDelta(n: number): string {
+  return `${n >= 0 ? "+" : "-"}${(Math.abs(n) / 1024 / 1024).toFixed(2)} MB`;
+}
diff --git a/scripts/build/ci.ts b/scripts/build/ci.ts
index ddbd686b715..e8c2dede5c0 100644
--- a/scripts/build/ci.ts
+++ b/scripts/build/ci.ts
@@ -387,6 +387,8 @@ export function packageAndUpload(cfg: Config, output: BunOutput): void {
   // cmake: bunStripPath = string(REPLACE bun ${bunTriplet} bunStripPath bun) = bunTriplet.
   if (shouldStrip(cfg) && output.strippedExe !== undefined) {
     zipPaths.push(makeZip(cfg, bunTriplet, [basename(output.strippedExe)]));
+    const bytes = statSync(output.strippedExe).size;
+    run(["buildkite-agent", "meta-data", "set", `binary-size:${bunTriplet}`, String(bytes)], buildDir);
   }

   // ─── Upload ───
diff --git a/scripts/utils.mjs b/scripts/utils.mjs
index 9ca4a597d15..dc4b886b20d 100755
--- a/scripts/utils.mjs
+++ b/scripts/utils.mjs
@@ -3056,6 +3056,7 @@ const emojiMap = {
   release: ["🏆", "trophy"],
   gear: ["⚙️", "gear"],
   clipboard: ["📋", "clipboard"],
+  package: ["📦", "package"],
   rocket: ["🚀", "rocket"],
   openbsd: ["🐡", "openbsd"],
   netbsd: ["🚩", "netbsd"],

PATCH

echo "Patch applied successfully."
