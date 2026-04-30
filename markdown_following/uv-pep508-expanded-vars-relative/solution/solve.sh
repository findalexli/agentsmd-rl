#!/usr/bin/env bash
# Oracle solution: applies the upstream gold patch from PR astral-sh/uv#18680.
# The full diff is inlined as a HEREDOC so this script is self-contained
# and does not fetch anything from the network.
set -euo pipefail

cd /workspace/uv

# Idempotency guard: if the gold patch is already present, do nothing.
if grep -q "expanded: bool," crates/uv-pep508/src/verbatim_url.rs 2>/dev/null \
   && grep -q "with_expanded" crates/uv-pep508/src/verbatim_url.rs 2>/dev/null; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

cat <<'PATCH' > /tmp/gold.patch
diff --git a/crates/uv-pep508/src/verbatim_url.rs b/crates/uv-pep508/src/verbatim_url.rs
index 9669d06691ee5..f085a6df43307 100644
--- a/crates/uv-pep508/src/verbatim_url.rs
+++ b/crates/uv-pep508/src/verbatim_url.rs
@@ -30,6 +30,9 @@ pub struct VerbatimUrl {
     /// Even if originally set, this will be [`None`] after
     /// serialization/deserialization.
     given: Option<ArcStr>,
+    /// Given value is a [`Pep508Url`] which contained variable references which were successfully
+    /// expanded.
+    expanded: bool,
 }

 impl Hash for VerbatimUrl {
@@ -53,7 +56,11 @@ impl PartialEq for VerbatimUrl {
 impl VerbatimUrl {
     /// Create a [`VerbatimUrl`] from a [`Url`].
     pub fn from_url(url: DisplaySafeUrl) -> Self {
-        Self { url, given: None }
+        Self {
+            url,
+            given: None,
+            expanded: false,
+        }
     }

     /// Parse a URL from a string.
@@ -61,7 +68,11 @@ impl VerbatimUrl {
         let given = given.as_ref();
         let url = DisplaySafeUrl::parse(given)?;

-        Ok(Self { url, given: None })
+        Ok(Self {
+            url,
+            given: None,
+            expanded: false,
+        })
     }

     /// Convert a [`VerbatimUrl`] from a path or a URL.
@@ -138,7 +149,11 @@ impl VerbatimUrl {
             url.set_fragment(Some(fragment));
         }

-        Ok(Self { url, given: None })
+        Ok(Self {
+            url,
+            given: None,
+            expanded: false,
+        })
     }

     /// Parse a URL from an absolute path.
@@ -168,7 +183,11 @@ impl VerbatimUrl {
             url.set_fragment(Some(fragment));
         }

-        Ok(Self { url, given: None })
+        Ok(Self {
+            url,
+            given: None,
+            expanded: false,
+        })
     }

     /// Parse a URL from a normalized path.
@@ -196,7 +215,11 @@ impl VerbatimUrl {
             url.set_fragment(Some(fragment));
         }

-        Ok(Self { url, given: None })
+        Ok(Self {
+            url,
+            given: None,
+            expanded: false,
+        })
     }

     /// Set the verbatim representation of the URL.
@@ -214,20 +237,35 @@ impl VerbatimUrl {
     }

     /// Returns `true` if the `given` input was an absolute path or file URL.
+    ///
+    /// If the URL was a PEP 508 URL which contained environment variable references which were
+    /// expanded. This function returns false to preserve existing usecases which may rely on
+    /// things like `${PWD}` or `${PROJECT_ROOT}`.
     pub fn was_given_absolute(&self) -> bool {
         let Some(given) = &self.given else {
             return false;
         };
+        if self.expanded {
+            return false;
+        }

-        if let Some((scheme, _)) = split_scheme(given) {
-            if let Some(parsed_scheme) = Scheme::parse(scheme) {
-                return parsed_scheme.is_file();
-            }
+        if let Some((scheme, _)) = split_scheme(given)
+            && let Some(parsed_scheme) = Scheme::parse(scheme)
+        {
+            return parsed_scheme.is_file();
         }

         Path::new(given.as_str()).is_absolute()
     }

+    /// Set the "given value contained variables which were expanded" flag.
+    ///
+    /// Intended to only be used by the [`Pep508Url`] impl.
+    #[must_use]
+    fn with_expanded(self, expanded: bool) -> Self {
+        Self { expanded, ..self }
+    }
+
     /// Return the underlying [`DisplaySafeUrl`].
     pub fn raw(&self) -> &DisplaySafeUrl {
         &self.url
@@ -336,6 +374,16 @@ impl Pep508Url for VerbatimUrl {
         // Expand environment variables in the URL.
         let expanded = expand_env_vars(url);

+        // Since `expand_env_vars` can return `Cow::Owned` even when variables were not expanded,
+        // the check needs to fall back to comparison for that case.
+        //
+        // Note: If a variable named `FOO` expands to `${FOO}` then this will produce a false
+        // negative. This seems like too much of a corner case to justify trying to fix it.
+        let vars_expanded = match &expanded {
+            Cow::Owned(owned) => owned != url,
+            Cow::Borrowed(_) => false,
+        };
+
         if let Some((scheme, path)) = split_scheme(&expanded) {
             match Scheme::parse(scheme) {
                 // Ex) `file:///home/ferris/project/scripts/...`, `file://localhost/home/ferris/project/scripts/...`, or `file:../ferris/`
@@ -350,13 +398,19 @@ impl Pep508Url for VerbatimUrl {
                         let path = normalize_url_path(path);

                         if let Some(working_dir) = working_dir {
-                            return Ok(Self::from_path(path.as_ref(), working_dir)?.with_given(url));
+                            return Ok(Self::from_path(path.as_ref(), working_dir)?
+                                .with_given(url)
+                                .with_expanded(vars_expanded));
                         }

-                        Ok(Self::from_absolute_path(path.as_ref())?.with_given(url))
+                        Ok(Self::from_absolute_path(path.as_ref())?
+                            .with_given(url)
+                            .with_expanded(vars_expanded))
                     }
                     #[cfg(not(feature = "non-pep508-extensions"))]
-                    Ok(Self::parse_url(expanded)?.with_given(url))
+                    Ok(Self::parse_url(expanded)?
+                        .with_given(url)
+                        .with_expanded(vars_expanded))
                 }

                 // Ex) `https://download.pytorch.org/whl/torch_stable.html`
@@ -370,12 +424,14 @@ impl Pep508Url for VerbatimUrl {
                     #[cfg(feature = "non-pep508-extensions")]
                     {
                         if let Some(working_dir) = working_dir {
-                            return Ok(
-                                Self::from_path(expanded.as_ref(), working_dir)?.with_given(url)
-                            );
+                            return Ok(Self::from_path(expanded.as_ref(), working_dir)?
+                                .with_given(url)
+                                .with_expanded(vars_expanded));
                         }

-                        Ok(Self::from_absolute_path(expanded.as_ref())?.with_given(url))
+                        Ok(Self::from_absolute_path(expanded.as_ref())?
+                            .with_given(url)
+                            .with_expanded(vars_expanded))
                     }
                     #[cfg(not(feature = "non-pep508-extensions"))]
                     Err(Self::Err::NotAUrl(expanded.to_string()))
@@ -386,10 +442,14 @@ impl Pep508Url for VerbatimUrl {
             #[cfg(feature = "non-pep508-extensions")]
             {
                 if let Some(working_dir) = working_dir {
-                    return Ok(Self::from_path(expanded.as_ref(), working_dir)?.with_given(url));
+                    return Ok(Self::from_path(expanded.as_ref(), working_dir)?
+                        .with_given(url)
+                        .with_expanded(vars_expanded));
                 }

-                Ok(Self::from_absolute_path(expanded.as_ref())?.with_given(url))
+                Ok(Self::from_absolute_path(expanded.as_ref())?
+                    .with_given(url)
+                    .with_expanded(vars_expanded))
             }

             #[cfg(not(feature = "non-pep508-extensions"))]
PATCH

git apply --whitespace=nowarn /tmp/gold.patch
echo "Gold patch applied successfully."
