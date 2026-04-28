#!/usr/bin/env bash
set -euo pipefail

cd /workspace/runtime

# Idempotency guard
if grep -qF "- **Check the manual**: EgorBot replies include a link to the [manual](https://g" ".github/skills/performance-benchmark/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/performance-benchmark/SKILL.md b/.github/skills/performance-benchmark/SKILL.md
@@ -3,9 +3,10 @@ name: performance-benchmark
 description: Generate and run ad hoc performance benchmarks to validate code changes. Use this when asked to benchmark, profile, or validate the performance impact of a code change in dotnet/runtime.
 ---
 
-# Ad Hoc Performance Benchmarking
+# Ad Hoc Performance Benchmarking with @EgorBot
 
-When you need to validate the performance impact of a code change, follow this process to write a BenchmarkDotNet benchmark and trigger EgorBot to run it.
+When you need to validate the performance impact of a code change, follow this process to write a BenchmarkDotNet benchmark and trigger @EgorBot to run it.
+The bot will notify you when results are ready, so don't wait for them.
 
 ## Step 1: Write the Benchmark
 
@@ -120,50 +121,37 @@ public class Bench
 }
 ```
 
-## Step 2: Post the EgorBot Comment
+## Step 2: Mention @EgorBot in a comment/PR description
 
 Post a comment on the PR to trigger EgorBot with your benchmark. The general format is:
 
-```
-@EgorBot [target flags] [options] [BenchmarkDotNet args]
+@EgorBot [targets] [options] [BenchmarkDotNet args]
 
 ```cs
 // Your benchmark code here
 ```
-```
-
-### Target Flags (Required - Choose at Least One)
+> **Note:** The @EgorBot command must not be inside the code block. Only the benchmark code should be inside the code block.
 
-| Flag | Architecture | Description |
-|------|--------------|-------------|
-| `-x64` or `-amd` | x64 | Linux Azure Genoa (AMD EPYC) - default x64 target |
-| `-arm` | ARM64 | Linux Azure Cobalt100 (Neoverse-N2) |
-| `-intel` | x64 | Azure Cascade Lake (more flaky due to JCC Erratum and loop alignment sensitivity) |
-| `-windows_x64` | x64 | Windows x64 (when Windows-specific testing is needed) |
+### Target Flags
 
-**Choosing targets:**
+- `-linux_amd`
+- `-linux_intel`
+- `-windows_amd`
+- `-windows_intel`
+- `-linux_arm64`
+- `-osx_arm64` (baremetal, feel free to always include it)
 
-- **Default for most changes**: Use `-x64` for quick verification of non-architecture/non-OS specific changes
-- **Default when ARM might differ**: Use `-x64 -arm` if there's any suspicion the change might behave differently on ARM
-- **Windows-specific changes**: Use `-windows_x64` when Windows behavior needs testing
-- **Noisy results suspected**: Use `-arm -intel -amd` to get results from multiple x64 CPUs (note: `-intel` targets are more flaky)
+The most common combination is `-linux_amd -osx_arm64`. Do not include more than 4 targets.
 
 ### Common Options
 
-| Option | Description |
-|--------|-------------|
-| `-profiler` | Collect flamegraph/hot assembly using perf record |
-| `--envvars KEY:VALUE` | Set environment variables (e.g., `DOTNET_JitDisasm:MethodName`) |
-| `-commit <hash>` | Run against a specific commit |
-| `-commit <hash1> vs <hash2>` | Compare two commits |
-| `-commit <hash> vs previous` | Compare commit with its parent |
+Use `-profiler` when absolutely necessary along with `-linux_arm64` and/or `-linux_amd` to include `perf` profiling and disassembly in the results.
 
 ### Example: Basic PR Benchmark
 
 To benchmark the current PR changes against the base branch:
 
-```
-@EgorBot -x64 -arm
+@EgorBot -linux_amd -osx_arm64
 
 ```cs
 using BenchmarkDotNet.Attributes;
@@ -182,73 +170,17 @@ public class Bench
     }
 }
 ```
-```
-
-### Example: Benchmark with Profiling and Disassembly
-
-```
-@EgorBot -x64 -profiler --envvars DOTNET_JitDisasm:SumArray
-
-```cs
-using System.Linq;
-using BenchmarkDotNet.Attributes;
-using BenchmarkDotNet.Running;
-
-BenchmarkSwitcher.FromAssembly(typeof(Bench).Assembly).Run(args);
-
-public class Bench
-{
-    private int[] _data = Enumerable.Range(0, 1000).ToArray();
-
-    [Benchmark]
-    public int SumArray() => _data.Sum();
-}
-```
-```
-
-### Example: Compare Two Commits
-
-```
-@EgorBot -amd -commit abc1234 vs def5678
-
-```cs
-using BenchmarkDotNet.Attributes;
-using BenchmarkDotNet.Running;
-
-BenchmarkSwitcher.FromAssembly(typeof(Bench).Assembly).Run(args);
-
-public class Bench
-{
-    [Benchmark]
-    public void TestMethod()
-    {
-        // Benchmark code
-    }
-}
-```
-```
-
-### Example: Run Existing dotnet/performance Benchmarks
-
-To run benchmarks from the dotnet/performance repository (no code snippet needed):
-
-```
-@EgorBot -arm -intel --filter `*TryGetValueFalse<String, String>*`
-```
-
-**Note**: Surround filter expressions with backticks to avoid issues with special characters.
 
 ## Important Notes
 
 - **Bot response time**: EgorBot uses polling and may take up to 30 seconds to respond
 - **Supported repositories**: EgorBot monitors `dotnet/runtime` and `EgorBot/runtime-utils`
 - **PR mode (default)**: When posting in a PR, EgorBot automatically compares the PR changes against the base branch
 - **Results variability**: Results may vary between runs due to VM differences. Do not compare results across different architectures or cloud providers
-- **Check the manual**: EgorBot replies include a link to the [manual](https://github.com/EgorBot/runtime-utils) for advanced options
+- **Check the manual**: EgorBot replies include a link to the [manual](https://github.com/EgorBo/EgorBot?tab=readme-ov-file#github-usage) for advanced options
 
 ## Additional Resources
 
 - [Microbenchmark Design Guidelines](https://github.com/dotnet/performance/blob/main/docs/microbenchmark-design-guidelines.md) - Essential reading for writing effective benchmarks
 - [BenchmarkDotNet CLI Arguments](https://github.com/dotnet/BenchmarkDotNet/blob/master/docs/articles/guides/console-args.md)
-- [EgorBot Manual](https://github.com/EgorBot/runtime-utils)
-- [BenchmarkDotNet Filter Simulator](http://egorbot.westus2.cloudapp.azure.com:5042/microbenchmarks)
+- [EgorBot Manual](https://github.com/EgorBo/EgorBot?tab=readme-ov-file#github-usage)
PATCH

echo "Gold patch applied."
