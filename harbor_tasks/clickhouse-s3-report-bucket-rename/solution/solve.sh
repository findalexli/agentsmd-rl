#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already patched (idempotency check)
# Using a distinctive line from the patch: S3_UPSTREAM_REPORT_BUCKET setting
if grep -q "S3_UPSTREAM_REPORT_BUCKET" ci/praktika/settings.py 2>/dev/null; then
    echo "Already patched, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/ci/jobs/collect_statistics.py b/ci/jobs/collect_statistics.py
index 4f4aae99b946..e99c0a12a18c 100644
--- a/ci/jobs/collect_statistics.py
+++ b/ci/jobs/collect_statistics.py
@@ -7,7 +7,7 @@
 from ci.praktika.result import Result
 from ci.praktika.s3 import S3
 from ci.praktika.utils import Shell
-from ci.settings.settings import S3_REPORT_BUCKET_NAME
+from ci.praktika.settings import Settings

 # Job collects overall CI statistics per each job

@@ -196,13 +196,13 @@ def do():
             )
             _ = S3.copy_file_to_s3(
                 local_path=archive_name,
-                s3_path=f"{S3_REPORT_BUCKET_NAME}/statistics",
+                s3_path=f"{Settings.S3_REPORT_BUCKET}/statistics",
                 content_type="application/json",
                 content_encoding="gzip",
             )
             statistics_link = S3.copy_file_to_s3(
                 local_path=archive_name_with_date,
-                s3_path=f"{S3_REPORT_BUCKET_NAME}/statistics",
+                s3_path=f"{Settings.S3_REPORT_BUCKET}/statistics",
                 content_type="application/json",
                 content_encoding="gzip",
             )
diff --git a/ci/praktika/hook_html.py b/ci/praktika/hook_html.py
index af1f87aaa40b..58c257867c34 100644
--- a/ci/praktika/hook_html.py
+++ b/ci/praktika/hook_html.py
@@ -79,7 +79,7 @@ def get_s3_path(cls):
         else:
             assert env.BRANCH
             s3suffix = f"REFs/{env.BRANCH}"
-        return f"{Settings.HTML_S3_PATH}/{s3suffix}"
+        return f"{Settings.S3_REPORT_BUCKET}/{s3suffix}"

     @classmethod
     def pull_from_s3(cls):
diff --git a/ci/praktika/html_prepare.py b/ci/praktika/html_prepare.py
index 193edc1b1405..d42edc7a2bc0 100644
--- a/ci/praktika/html_prepare.py
+++ b/ci/praktika/html_prepare.py
@@ -25,7 +25,7 @@ def prepare(cls, is_test):
         compressed_file = Utils.compress_gz(page_file)

         S3.copy_file_to_s3(
-            s3_path=str(Path(Settings.HTML_S3_PATH) / Path(page_file).name),
+            s3_path=str(Path(Settings.S3_REPORT_BUCKET) / Path(page_file).name),
             local_path=compressed_file,
             content_type="text/html",
             content_encoding="gzip",
diff --git a/ci/praktika/info.py b/ci/praktika/info.py
index c887c1071cf6..792bffc10622 100644
--- a/ci/praktika/info.py
+++ b/ci/praktika/info.py
@@ -190,7 +190,7 @@ def get_specific_report_url(
         else:
             assert branch
             ref_param = f"REF={branch}"
-        path = Settings.HTML_S3_PATH
+        path = Settings.S3_REPORT_BUCKET
         for bucket, endpoint in Settings.S3_BUCKET_TO_HTTP_ENDPOINT.items():
             if bucket in path:
                 path = path.replace(bucket, endpoint)
@@ -210,7 +210,7 @@ def get_specific_report_url_static(pr_number, branch, sha, job_name, workflow_na
         else:
             assert branch
             ref_param = f"REF={branch}"
-        path = Settings.HTML_S3_PATH
+        path = Settings.S3_REPORT_BUCKET
         for bucket, endpoint in Settings.S3_BUCKET_TO_HTTP_ENDPOINT.items():
             if bucket in path:
                 path = path.replace(bucket, endpoint)
diff --git a/ci/praktika/issue.py b/ci/praktika/issue.py
index d752fc02cba7..58dfe895c1ce 100644
--- a/ci/praktika/issue.py
+++ b/ci/praktika/issue.py
@@ -12,6 +12,7 @@
 from praktika.gh import GH
 from praktika.result import Result
 from praktika.s3 import S3
+from praktika.settings import Settings
 from praktika.utils import MetaClasses, Shell, Utils

 if TYPE_CHECKING:
@@ -492,24 +493,18 @@ def to_s3(self):
         compressed_name = Utils.compress_gz(local_name)
         link = S3.copy_file_to_s3(
             local_path=compressed_name,
-            s3_path=f"clickhouse-test-reports/statistics",
+            s3_path=f"{Settings.S3_REPORT_BUCKET}/statistics",
             content_type="application/json",
             content_encoding="gzip",
         )
         return link

     @classmethod
-    def from_s3(cls):
-        """
-        Download catalog from S3.
-
-
-        Returns:
-            TestCaseIssueCatalog instance or None if download failed
-        """
-        local_catalog_gz = cls.file_name_static(cls.name) + ".gz"
-        local_catalog_json = cls.file_name_static(cls.name)
-        s3_catalog_path = f"clickhouse-test-reports/statistics/{Utils.normalize_string(cls.name)}.json.gz"
+    def _download_catalog(cls, bucket, suffix=""):
+        """Download and decompress a single catalog from an S3 bucket."""
+        local_catalog_gz = cls.file_name_static(cls.name + suffix) + ".gz"
+        local_catalog_json = cls.file_name_static(cls.name + suffix)
+        s3_catalog_path = f"{bucket}/statistics/{Utils.normalize_string(cls.name)}.json.gz"

         if not S3.copy_file_from_s3(
             s3_catalog_path, local_catalog_gz, _skip_download_counter=True
@@ -517,10 +512,8 @@ def from_s3(cls):
             print(f"  WARNING: Could not download catalog from S3: {s3_catalog_path}")
             return None

-        # Decompress the file
         Shell.check(f"gunzip -f {local_catalog_gz}", verbose=True)

-        # Load from decompressed file
         if not Path(local_catalog_json).exists():
             print(
                 f"  WARNING: Decompressed catalog file not found: {local_catalog_json}"
@@ -529,6 +522,40 @@ def from_s3(cls):

         return cls.from_file(local_catalog_json)

+    @classmethod
+    def from_s3(cls):
+        """
+        Download catalog from S3. If S3_UPSTREAM_REPORT_BUCKET is set,
+        also downloads the upstream catalog and merges issues from both.
+
+        Returns:
+            TestCaseIssueCatalog instance or None if download failed
+        """
+        catalog = cls._download_catalog(Settings.S3_REPORT_BUCKET)
+
+        if Settings.S3_UPSTREAM_REPORT_BUCKET:
+            upstream = cls._download_catalog(
+                Settings.S3_UPSTREAM_REPORT_BUCKET, suffix="_upstream"
+            )
+            if upstream:
+                if catalog is None:
+                    catalog = upstream
+                else:
+                    existing = {
+                        issue.number for issue in catalog.active_test_issues
+                    }
+                    added = 0
+                    for issue in upstream.active_test_issues:
+                        if issue.number not in existing:
+                            catalog.active_test_issues.append(issue)
+                            added += 1
+                    print(
+                        f"  Merged {added} issues from upstream catalog "
+                        f"(total: {len(catalog.active_test_issues)})"
+                    )
+
+        return catalog
+

 if __name__ == "__main__":
     temp_path = f"{Utils.cwd()}/ci/tmp"
diff --git a/ci/praktika/result.py b/ci/praktika/result.py
index 9ee5dd7b8849..a76f48aecb73 100644
--- a/ci/praktika/result.py
+++ b/ci/praktika/result.py
@@ -1057,7 +1057,7 @@ def copy_result_to_s3(cls, result, clean=False):
         result.dump()
         env = _Environment.get()
         result_file_path = result.file_name()
-        s3_path = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}/{Path(result_file_path).name}"
+        s3_path = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}/{Path(result_file_path).name}"
         if clean:
             S3.delete(s3_path)
         # gzip is supported by most browsers
@@ -1082,14 +1082,14 @@ def copy_result_to_s3(cls, result, clean=False):
     def copy_result_from_s3(cls, local_path):
         env = _Environment.get()
         file_name = Path(local_path).name
-        s3_path = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}/{file_name}"
+        s3_path = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}/{file_name}"
         S3.copy_file_from_s3(s3_path=s3_path, local_path=local_path)

     @classmethod
     def copy_result_from_s3_with_version(cls, local_path):
         env = _Environment.get()
         file_name = Path(local_path).name
-        s3_path = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}"
+        s3_path = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}"
         s3_file = f"{s3_path}/{file_name}"

         return S3.copy_file_from_s3_with_version(s3_path=s3_file, local_path=local_path)
@@ -1099,7 +1099,7 @@ def copy_result_to_s3_with_version(cls, result, version, no_strict=False):
         result.dump()
         filename = Path(result.file_name()).name
         env = _Environment.get()
-        s3_path = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}/"
+        s3_path = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}/"
         s3_file = f"{s3_path}{filename}"

         return S3.copy_file_to_s3_with_version(
@@ -1176,7 +1176,7 @@ def upload_result_files_to_s3(
             if asset_paths:
                 common_root = os.path.commonpath([p.parent for p in asset_paths])
                 env = _Environment.get()
-                base_s3_prefix = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}/{s3_subprefix}".replace(
+                base_s3_prefix = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}/{s3_subprefix}".replace(
                     "//", "/"
                 )

diff --git a/ci/praktika/s3.py b/ci/praktika/s3.py
index 1a018a6d2cef..7603f33ada5a 100644
--- a/ci/praktika/s3.py
+++ b/ci/praktika/s3.py
@@ -414,7 +414,7 @@ def _upload_file_to_s3(
     ) -> str:
         if upload_to_s3:
             env = _Environment.get()
-            s3_path = f"{Settings.HTML_S3_PATH}/{env.get_s3_prefix()}"
+            s3_path = f"{Settings.S3_REPORT_BUCKET}/{env.get_s3_prefix()}"
             if s3_subprefix:
                 s3_subprefix = s3_subprefix.removeprefix("/").removesuffix("/")
                 s3_path += f"/{s3_subprefix}"
diff --git a/ci/praktika/settings.py b/ci/praktika/settings.py
index cd453af8b210..b09fef93f241 100644
--- a/ci/praktika/settings.py
+++ b/ci/praktika/settings.py
@@ -84,7 +84,9 @@ class _Settings:
     ######################################
     #        Report settings             #
     ######################################
-    HTML_S3_PATH: str = ""
+    S3_REPORT_BUCKET: str = ""
+    # Optional: upstream report bucket to merge issue catalogs from (e.g. "clickhouse-test-reports")
+    S3_UPSTREAM_REPORT_BUCKET: str = ""
     HTML_PAGE_FILE: str = "./ci/praktika/json.html"
     S3_BUCKET_TO_HTTP_ENDPOINT: Optional[Dict[str, str]] = None
     TEXT_CONTENT_EXTENSIONS: Iterable[str] = frozenset([".txt", ".log"])
@@ -129,7 +131,8 @@ class _Settings:
 _USER_DEFINED_SETTINGS = [
     "S3_ARTIFACT_PATH",
     "CACHE_S3_PATH",
-    "HTML_S3_PATH",
+    "S3_REPORT_BUCKET",
+    "S3_UPSTREAM_REPORT_BUCKET",
     "CLOUD_INFRASTRUCTURE_CONFIG_PATH",
     "EVENT_FEED_S3_PATH",
     "AWS_REGION",
diff --git a/ci/praktika/validator.py b/ci/praktika/validator.py
index 3f937ae2b967..7b7fccf7d776 100644
--- a/ci/praktika/validator.py
+++ b/ci/praktika/validator.py
@@ -199,15 +199,15 @@ def is_valid_cron_field(field: str) -> bool:

             if workflow.enable_report:
                 assert (
-                    Settings.HTML_S3_PATH
-                ), f"HTML_S3_PATH Setting must be defined if enable_html=True, workflow [{workflow.name}]"
+                    Settings.S3_REPORT_BUCKET
+                ), f"S3_REPORT_BUCKET Setting must be defined if enable_html=True, workflow [{workflow.name}]"
                 assert (
                     Settings.S3_BUCKET_TO_HTTP_ENDPOINT
                 ), f"S3_BUCKET_TO_HTTP_ENDPOINT Setting must be defined if enable_html=True, workflow [{workflow.name}]"
                 assert (
-                    Settings.HTML_S3_PATH.split("/")[0]
+                    Settings.S3_REPORT_BUCKET.split("/")[0]
                     in Settings.S3_BUCKET_TO_HTTP_ENDPOINT
-                ), f"S3_BUCKET_TO_HTTP_ENDPOINT Setting must include bucket name [{Settings.HTML_S3_PATH}] from HTML_S3_PATH, workflow [{workflow.name}]"
+                ), f"S3_BUCKET_TO_HTTP_ENDPOINT Setting must include bucket name [{Settings.S3_REPORT_BUCKET}] from S3_REPORT_BUCKET, workflow [{workflow.name}]"

             if workflow.enable_cache:
                 for artifact in workflow.artifacts or []:
diff --git a/ci/settings/settings.py b/ci/settings/settings.py
index 474fc1e14f0a..900a384376e6 100644
--- a/ci/settings/settings.py
+++ b/ci/settings/settings.py
@@ -19,7 +19,7 @@ class RunnerLabels:
 DOCKER_BUILD_AMD_RUNS_ON = RunnerLabels.STYLE_CHECK_AMD

 CACHE_S3_PATH = f"{S3_BUCKET_NAME}/ci_ch_cache"
-HTML_S3_PATH = S3_REPORT_BUCKET_NAME
+S3_REPORT_BUCKET = S3_REPORT_BUCKET_NAME
 S3_BUCKET_TO_HTTP_ENDPOINT = {
     S3_BUCKET_NAME: S3_BUCKET_HTTP_ENDPOINT,
     S3_REPORT_BUCKET_NAME: S3_REPORT_BUCKET_HTTP_ENDPOINT,
PATCH

echo "Patch applied successfully."
