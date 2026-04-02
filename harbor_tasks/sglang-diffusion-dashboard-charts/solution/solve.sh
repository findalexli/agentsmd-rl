#!/usr/bin/env bash
set -euo pipefail

FILE="scripts/ci/utils/diffusion/generate_diffusion_dashboard.py"

# Idempotency check: if y_range calculation already present, patch was applied
if grep -q 'y_range = y_max - y_min' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/ci/utils/diffusion/generate_diffusion_dashboard.py b/scripts/ci/utils/diffusion/generate_diffusion_dashboard.py
index 183611ef044d..bb223fbe6dde 100644
--- a/scripts/ci/utils/diffusion/generate_diffusion_dashboard.py
+++ b/scripts/ci/utils/diffusion/generate_diffusion_dashboard.py
@@ -26,7 +26,7 @@
 CI_DATA_REPO_NAME = "sglang-ci-data"
 CI_DATA_BRANCH = "main"
 HISTORY_PREFIX = "diffusion-comparisons"
-MAX_HISTORY_RUNS = 7
+MAX_HISTORY_RUNS = 14

 # Base URL for chart images pushed to sglang-ci-data
 CHARTS_RAW_BASE_URL = (
@@ -344,7 +344,7 @@ def generate_dashboard(

     # ---- Section 2: SGLang Performance Trend ----
     if history:
-        lines.append("\n## SGLang Performance Trend (Last 7 Runs)\n")
+        lines.append(f"\n## SGLang Performance Trend (Last {len(history) + 1} Runs)\n")

         # Build header
         header = "| Date | Commit |"
@@ -491,9 +491,16 @@ def _chart_label(run: dict) -> str:
                 ax.set_xticklabels(labels, fontsize=7)
                 ax.set_ylabel("Latency (s)")
                 ax.set_title(f"Latency Trend -- {cid}", fontsize=11, fontweight="bold")
-                ax.legend(loc="upper right", fontsize=8)
+                ax.legend(loc="lower right", fontsize=8, framealpha=0.8)
                 ax.grid(True, alpha=0.3)
-                ax.set_ylim(bottom=0)
+                all_vals = sg_vals + [v for v in vl_vals if v is not None]
+                y_min = min(all_vals)
+                y_max = max(all_vals)
+                y_range = y_max - y_min if y_max > y_min else max(y_max * 0.1, 0.1)
+                ax.set_ylim(
+                    bottom=max(0, y_min - y_range * 0.3),
+                    top=y_max + y_range * 0.3,
+                )

                 filename = f"latency_{_sanitize_filename(cid)}.png"
                 chart_path = os.path.join(charts_dir, filename)

PATCH

echo "Patch applied successfully."
