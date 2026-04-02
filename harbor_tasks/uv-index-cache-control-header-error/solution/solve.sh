#!/usr/bin/env bash
set -euo pipefail

cd /src

# Idempotency check: if the fix is already applied, exit early
if grep -q 'IndexCacheControlWire' crates/uv-distribution-types/src/index.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-client/src/cached_client.rs b/crates/uv-client/src/cached_client.rs
index d8d6afad783d3..8ad6d502274d2 100644
--- a/crates/uv-client/src/cached_client.rs
+++ b/crates/uv-client/src/cached_client.rs
@@ -173,8 +173,8 @@ impl<E: Into<Self> + std::error::Error + 'static> From<CachedClientError<E>> for
     }
 }
 
-#[derive(Debug, Clone, Copy)]
-pub enum CacheControl<'a> {
+#[derive(Debug, Clone)]
+pub enum CacheControl {
     /// Respect the `cache-control` header from the response.
     None,
     /// Apply `max-age=0, must-revalidate` to the request.
@@ -182,10 +182,10 @@ pub enum CacheControl<'a> {
     /// Allow the client to return stale responses.
     AllowStale,
     /// Override the cache control header with a custom value.
-    Override(&'a str),
+    Override(http::HeaderValue),
 }
 
-impl From<Freshness> for CacheControl<'_> {
+impl From<Freshness> for CacheControl {
     fn from(value: Freshness) -> Self {
         match value {
             Freshness::Fresh => Self::None,
@@ -239,7 +239,7 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload, CachedClientError<CallBackError>> {
         let payload = self
@@ -272,13 +272,13 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload::Target, CachedClientError<CallBackError>> {
         let fresh_req = req.try_clone().expect("HTTP request must be cloneable");
         let start = Instant::now();
         let cached_response = if let Some(cached) = Self::read_cache(cache_entry).await {
-            self.send_cached(req, cache_control, cached)
+            self.send_cached(req, cache_control.clone(), cached)
                 .boxed_local()
                 .await?
         } else {
@@ -286,7 +286,7 @@ impl CachedClient {
                 "No cache entry for: {}",
                 DisplaySafeUrl::from_url(req.url().clone())
             );
-            let (response, cache_policy) = self.fresh_request(req, cache_control).await?;
+            let (response, cache_policy) = self.fresh_request(req, cache_control.clone()).await?;
             CachedResponse::ModifiedOrNew {
                 response,
                 cache_policy,
@@ -303,7 +303,7 @@ impl CachedClient {
                     self.resend_and_heal_cache(
                         fresh_req,
                         cache_entry,
-                        cache_control,
+                        cache_control.clone(),
                         response_callback,
                     )
                     .await
@@ -329,7 +329,7 @@ impl CachedClient {
                             self.resend_and_heal_cache(
                                 fresh_req,
                                 cache_entry,
-                                cache_control,
+                                cache_control.clone(),
                                 response_callback,
                             )
                             .await
@@ -380,7 +380,7 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload, CachedClientError<CallBackError>> {
         let start = Instant::now();
@@ -404,7 +404,7 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload::Target, CachedClientError<CallBackError>> {
         let _ = fs_err::tokio::remove_file(&cache_entry.path()).await;
@@ -494,18 +494,15 @@ impl CachedClient {
     async fn send_cached(
         &self,
         mut req: Request,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         cached: DataWithCachePolicy,
     ) -> Result<CachedResponse, Error> {
         // Apply the cache control header, if necessary.
-        match cache_control {
-            CacheControl::None | CacheControl::AllowStale | CacheControl::Override(..) => {}
-            CacheControl::MustRevalidate => {
-                req.headers_mut().insert(
-                    http::header::CACHE_CONTROL,
-                    http::HeaderValue::from_static("no-cache"),
-                );
-            }
+        if matches!(&cache_control, CacheControl::MustRevalidate) {
+            req.headers_mut().insert(
+                http::header::CACHE_CONTROL,
+                http::HeaderValue::from_static("no-cache"),
+            );
         }
         let url = DisplaySafeUrl::from_url(req.url().clone());
         Ok(match cached.cache_policy.before_request(&mut req) {
@@ -544,7 +541,7 @@ impl CachedClient {
     async fn send_cached_handle_stale(
         &self,
         req: Request,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         cached: DataWithCachePolicy,
         new_cache_policy_builder: CachePolicyBuilder,
     ) -> Result<CachedResponse, Error> {
@@ -575,12 +572,10 @@ impl CachedClient {
         }
 
         // If the user set a custom `Cache-Control` header, override it.
-        if let CacheControl::Override(header) = cache_control {
-            response.headers_mut().insert(
-                http::header::CACHE_CONTROL,
-                http::HeaderValue::from_str(header)
-                    .expect("Cache-Control header must be valid UTF-8"),
-            );
+        if let CacheControl::Override(header) = &cache_control {
+            response
+                .headers_mut()
+                .insert(http::header::CACHE_CONTROL, header.clone());
         }
 
         match cached
@@ -611,7 +606,7 @@ impl CachedClient {
     async fn fresh_request(
         &self,
         req: Request,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
     ) -> Result<(Response, Option<Box<CachePolicy>>), Error> {
         let url = DisplaySafeUrl::from_url(req.url().clone());
         debug!("Sending fresh {} request for: {}", req.method(), url);
@@ -629,12 +624,10 @@ impl CachedClient {
         );
 
         // If the user set a custom `Cache-Control` header, override it.
-        if let CacheControl::Override(header) = cache_control {
-            response.headers_mut().insert(
-                http::header::CACHE_CONTROL,
-                http::HeaderValue::from_str(header)
-                    .expect("Cache-Control header must be valid UTF-8"),
-            );
+        if let CacheControl::Override(header) = &cache_control {
+            response
+                .headers_mut()
+                .insert(http::header::CACHE_CONTROL, header.clone());
         }
 
         let retry_count = response
@@ -670,7 +663,7 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload, CachedClientError<CallBackError>> {
         let payload = self
@@ -694,14 +687,19 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload::Target, CachedClientError<CallBackError>> {
         let mut retry_state = RetryState::start(self.uncached().retry_policy(), req.url().clone());
         loop {
             let fresh_req = req.try_clone().expect("HTTP request must be cloneable");
             let result = self
-                .get_cacheable(fresh_req, cache_entry, cache_control, &response_callback)
+                .get_cacheable(
+                    fresh_req,
+                    cache_entry,
+                    cache_control.clone(),
+                    &response_callback,
+                )
                 .await;
 
             match result {
@@ -728,14 +726,19 @@ impl CachedClient {
         &self,
         req: Request,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
         response_callback: Callback,
     ) -> Result<Payload, CachedClientError<CallBackError>> {
         let mut retry_state = RetryState::start(self.uncached().retry_policy(), req.url().clone());
         loop {
             let fresh_req = req.try_clone().expect("HTTP request must be cloneable");
             let result = self
-                .skip_cache(fresh_req, cache_entry, cache_control, &response_callback)
+                .skip_cache(
+                    fresh_req,
+                    cache_entry,
+                    cache_control.clone(),
+                    &response_callback,
+                )
                 .await;
 
             match result {
diff --git a/crates/uv-client/src/registry_client.rs b/crates/uv-client/src/registry_client.rs
index 42a625bee7851..2c0cc6e2a5870 100644
--- a/crates/uv-client/src/registry_client.rs
+++ b/crates/uv-client/src/registry_client.rs
@@ -589,7 +589,7 @@ impl RegistryClient {
         url: &DisplaySafeUrl,
         index: &IndexUrl,
         cache_entry: &CacheEntry,
-        cache_control: CacheControl<'_>,
+        cache_control: CacheControl,
     ) -> Result<OwnedArchive<SimpleDetailMetadata>, Error> {
         // In theory, we should be able to pass `MediaType::all()` to all registries, and as
         // unsupported media types should be ignored by the server. For now, we implement this
@@ -1175,7 +1175,7 @@ impl RegistryClient {
                 .get_serde_with_retry(
                     req,
                     &cache_entry,
-                    cache_control,
+                    cache_control.clone(),
                     read_metadata_range_request,
                 )
                 .await
diff --git a/crates/uv-distribution-types/src/index.rs b/crates/uv-distribution-types/src/index.rs
index c3d962d766952..530f495c79f30 100644
--- a/crates/uv-distribution-types/src/index.rs
+++ b/crates/uv-distribution-types/src/index.rs
@@ -1,7 +1,8 @@
 use std::path::Path;
 use std::str::FromStr;
 
-use serde::{Deserialize, Serialize};
+use http::HeaderValue;
+use serde::{Deserialize, Serialize, Serializer};
 use thiserror::Error;
 use url::Url;
 
@@ -14,24 +15,25 @@ use crate::origin::Origin;
 use crate::{IndexStatusCodeStrategy, IndexUrl, IndexUrlError, SerializableStatusCode};
 
 /// Cache control configuration for an index.
-#[derive(Debug, Clone, Hash, Eq, PartialEq, Ord, PartialOrd, Serialize, Deserialize, Default)]
+#[derive(Debug, Clone, Hash, Eq, PartialEq, Ord, PartialOrd, Default)]
 #[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
-#[serde(rename_all = "kebab-case")]
 pub struct IndexCacheControl {
     /// Cache control header for Simple API requests.
-    pub api: Option<SmallString>,
+    #[cfg_attr(feature = "schemars", schemars(with = "Option<String>"))]
+    pub api: Option<HeaderValue>,
     /// Cache control header for file downloads.
-    pub files: Option<SmallString>,
+    #[cfg_attr(feature = "schemars", schemars(with = "Option<String>"))]
+    pub files: Option<HeaderValue>,
 }
 
 impl IndexCacheControl {
     /// Return the default Simple API cache control headers for the given index URL, if applicable.
-    pub fn simple_api_cache_control(_url: &Url) -> Option<&'static str> {
+    pub fn simple_api_cache_control(_url: &Url) -> Option<HeaderValue> {
         None
     }
 
     /// Return the default files cache control headers for the given index URL, if applicable.
-    pub fn artifact_cache_control(url: &Url) -> Option<&'static str> {
+    pub fn artifact_cache_control(url: &Url) -> Option<HeaderValue> {
         let dominated_by_pytorch_or_nvidia = url.host_str().is_some_and(|host| {
             host.eq_ignore_ascii_case("download.pytorch.org")
                 || host.eq_ignore_ascii_case("pypi.nvidia.com")
@@ -44,13 +46,83 @@ impl IndexCacheControl {
             // See: https://github.com/pytorch/pytorch/pull/149218
             //
             // The same issue applies to files hosted on `pypi.nvidia.com`.
-            Some("max-age=365000000, immutable, public")
+            Some(HeaderValue::from_static(
+                "max-age=365000000, immutable, public",
+            ))
         } else {
             None
         }
     }
 }
 
+#[derive(Serialize)]
+#[serde(rename_all = "kebab-case")]
+struct IndexCacheControlRef<'a> {
+    #[serde(skip_serializing_if = "Option::is_none")]
+    api: Option<&'a str>,
+    #[serde(skip_serializing_if = "Option::is_none")]
+    files: Option<&'a str>,
+}
+
+impl Serialize for IndexCacheControl {
+    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
+    where
+        S: Serializer,
+    {
+        IndexCacheControlRef {
+            api: self.api.as_ref().map(|api| {
+                api.to_str()
+                    .expect("cache-control.api is always parsed from a string")
+            }),
+            files: self.files.as_ref().map(|files| {
+                files
+                    .to_str()
+                    .expect("cache-control.files is always parsed from a string")
+            }),
+        }
+        .serialize(serializer)
+    }
+}
+
+#[derive(Debug, Clone, Deserialize)]
+#[serde(rename_all = "kebab-case")]
+struct IndexCacheControlWire {
+    api: Option<SmallString>,
+    files: Option<SmallString>,
+}
+
+impl<'de> Deserialize<'de> for IndexCacheControl {
+    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
+    where
+        D: serde::Deserializer<'de>,
+    {
+        let wire = IndexCacheControlWire::deserialize(deserializer)?;
+
+        let api = wire
+            .api
+            .map(|api| {
+                HeaderValue::from_str(api.as_ref()).map_err(|_| {
+                    serde::de::Error::custom(
+                        "`cache-control.api` must be a valid HTTP header value",
+                    )
+                })
+            })
+            .transpose()?;
+        let files = wire
+            .files
+            .map(|files| {
+                HeaderValue::from_str(files.as_ref()).map_err(|_| {
+                    serde::de::Error::custom(
+                        "`cache-control.files` must be a valid HTTP header value",
+                    )
+                })
+            })
+            .transpose()?;
+
+        Ok(Self { api, files })
+    }
+}
+
 #[derive(Debug, Clone, Serialize)]
 #[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
 #[serde(rename_all = "kebab-case")]
@@ -392,29 +464,19 @@ impl Index {
     }
 
     /// Return the cache control header for file requests to this index, if any.
-    pub fn artifact_cache_control(&self) -> Option<&str> {
-        if let Some(artifact_cache_control) = self
-            .cache_control
+    pub fn artifact_cache_control(&self) -> Option<HeaderValue> {
+        self.cache_control
             .as_ref()
-            .and_then(|cache_control| cache_control.files.as_deref())
-        {
-            Some(artifact_cache_control)
-        } else {
-            IndexCacheControl::artifact_cache_control(self.url.url())
-        }
+            .and_then(|cache_control| cache_control.files.clone())
+            .or_else(|| IndexCacheControl::artifact_cache_control(self.url.url()))
     }
 
     /// Return the cache control header for API requests to this index, if any.
-    pub fn simple_api_cache_control(&self) -> Option<&str> {
-        if let Some(api_cache_control) = self
-            .cache_control
+    pub fn simple_api_cache_control(&self) -> Option<HeaderValue> {
+        self.cache_control
             .as_ref()
-            .and_then(|cache_control| cache_control.api.as_deref())
-        {
-            Some(api_cache_control)
-        } else {
-            IndexCacheControl::simple_api_cache_control(self.url.url())
-        }
+            .and_then(|cache_control| cache_control.api.clone())
+            .or_else(|| IndexCacheControl::simple_api_cache_control(self.url.url()))
     }
 }
 
@@ -621,6 +683,7 @@ pub enum IndexSourceError {
 #[cfg(test)]
 mod tests {
     use super::*;
+    use http::HeaderValue;
 
     #[test]
     fn test_index_cache_control_headers() {
@@ -635,8 +698,14 @@ mod tests {
         assert_eq!(index.name.as_ref().unwrap().as_ref(), "test-index");
         assert!(index.cache_control.is_some());
         let cache_control = index.cache_control.as_ref().unwrap();
-        assert_eq!(cache_control.api.as_deref(), Some("max-age=600"));
-        assert_eq!(cache_control.files.as_deref(), Some("max-age=3600"));
+        assert_eq!(
+            cache_control.api,
+            Some(HeaderValue::from_static("max-age=600"))
+        );
+        assert_eq!(
+            cache_control.files,
+            Some(HeaderValue::from_static("max-age=3600"))
+        );
     }
 
     #[test]
@@ -665,7 +734,40 @@ mod tests {
         assert_eq!(index.name.as_ref().unwrap().as_ref(), "test-index");
         assert!(index.cache_control.is_some());
         let cache_control = index.cache_control.as_ref().unwrap();
-        assert_eq!(cache_control.api.as_deref(), Some("max-age=300"));
+        assert_eq!(
+            cache_control.api,
+            Some(HeaderValue::from_static("max-age=300"))
+        );
         assert_eq!(cache_control.files, None);
     }
+
+    #[test]
+    fn test_index_invalid_api_cache_control() {
+        let toml_str = r#"
+            name = "test-index"
+            url = "https://test.example.com/simple"
+            cache-control = { api = "max-age=600\n" }
+        "#;
+
+        let err = toml::from_str::<Index>(toml_str).unwrap_err();
+        assert!(
+            err.to_string()
+                .contains("`cache-control.api` must be a valid HTTP header value")
+        );
+    }
+
+    #[test]
+    fn test_index_invalid_files_cache_control() {
+        let toml_str = r#"
+            name = "test-index"
+            url = "https://test.example.com/simple"
+            cache-control = { files = "max-age=3600\n" }
+        "#;
+
+        let err = toml::from_str::<Index>(toml_str).unwrap_err();
+        assert!(
+            err.to_string()
+                .contains("`cache-control.files` must be a valid HTTP header value")
+        );
+    }
 }
diff --git a/crates/uv-distribution-types/src/index_url.rs b/crates/uv-distribution-types/src/index_url.rs
index 0d0f9f221653a..7e9f9a7202739 100644
--- a/crates/uv-distribution-types/src/index_url.rs
+++ b/crates/uv-distribution-types/src/index_url.rs
@@ -440,7 +440,7 @@ impl<'a> IndexLocations {
     }
 
     /// Return the Simple API cache control header for an [`IndexUrl`], if configured.
-    pub fn simple_api_cache_control_for(&self, url: &IndexUrl) -> Option<&str> {
+    pub fn simple_api_cache_control_for(&self, url: &IndexUrl) -> Option<http::HeaderValue> {
         for index in &self.indexes {
             if is_same_index(index.url(), url) {
                 return index.simple_api_cache_control();
@@ -450,7 +450,7 @@ impl<'a> IndexLocations {
     }
 
     /// Return the artifact cache control header for an [`IndexUrl`], if configured.
-    pub fn artifact_cache_control_for(&self, url: &IndexUrl) -> Option<&str> {
+    pub fn artifact_cache_control_for(&self, url: &IndexUrl) -> Option<http::HeaderValue> {
         for index in &self.indexes {
             if is_same_index(index.url(), url) {
                 return index.artifact_cache_control();
@@ -593,7 +593,7 @@ impl<'a> IndexUrls {
     }
 
     /// Return the Simple API cache control header for an [`IndexUrl`], if configured.
-    pub fn simple_api_cache_control_for(&self, url: &IndexUrl) -> Option<&str> {
+    pub fn simple_api_cache_control_for(&self, url: &IndexUrl) -> Option<http::HeaderValue> {
         for index in &self.indexes {
             if is_same_index(index.url(), url) {
                 return index.simple_api_cache_control();
@@ -603,7 +603,7 @@ impl<'a> IndexUrls {
     }
 
     /// Return the artifact cache control header for an [`IndexUrl`], if configured.
-    pub fn artifact_cache_control_for(&self, url: &IndexUrl) -> Option<&str> {
+    pub fn artifact_cache_control_for(&self, url: &IndexUrl) -> Option<http::HeaderValue> {
         for index in &self.indexes {
             if is_same_index(index.url(), url) {
                 return index.artifact_cache_control();
@@ -697,7 +697,7 @@ impl IndexCapabilities {
 mod tests {
     use super::*;
     use crate::{IndexCacheControl, IndexFormat, IndexName};
-    use uv_small_str::SmallString;
+    use http::HeaderValue;
 
     #[test]
     fn test_index_url_parse_valid_paths() {
@@ -736,8 +736,6 @@ mod tests {
     fn test_cache_control_lookup() {
         use std::str::FromStr;
 
-        use uv_small_str::SmallString;
-
         use crate::IndexFormat;
         use crate::index_name::IndexName;
 
@@ -746,8 +744,8 @@ mod tests {
                 name: Some(IndexName::from_str("index1").unwrap()),
                 url: IndexUrl::from_str("https://index1.example.com/simple").unwrap(),
                 cache_control: Some(crate::IndexCacheControl {
-                    api: Some(SmallString::from("max-age=300")),
-                    files: Some(SmallString::from("max-age=1800")),
+                    api: Some(HeaderValue::from_static("max-age=300")),
+                    files: Some(HeaderValue::from_static("max-age=1800")),
                 }),
                 explicit: false,
                 default: false,
@@ -776,11 +774,11 @@ mod tests {
         let url1 = IndexUrl::from_str("https://index1.example.com/simple").unwrap();
         assert_eq!(
             index_urls.simple_api_cache_control_for(&url1),
-            Some("max-age=300")
+            Some(HeaderValue::from_static("max-age=300"))
         );
         assert_eq!(
             index_urls.artifact_cache_control_for(&url1),
-            Some("max-age=1800")
+            Some(HeaderValue::from_static("max-age=1800"))
         );
 
         let url2 = IndexUrl::from_str("https://index2.example.com/simple").unwrap();
@@ -817,7 +815,9 @@ mod tests {
         assert_eq!(index_urls.simple_api_cache_control_for(&pytorch_url), None);
         assert_eq!(
             index_urls.artifact_cache_control_for(&pytorch_url),
-            Some("max-age=365000000, immutable, public")
+            Some(HeaderValue::from_static(
+                "max-age=365000000, immutable, public",
+            ))
         );
 
         // IndexLocations should also return the default for PyTorch
@@ -827,7 +827,9 @@ mod tests {
         );
         assert_eq!(
             index_locations.artifact_cache_control_for(&pytorch_url),
-            Some("max-age=365000000, immutable, public")
+            Some(HeaderValue::from_static(
+                "max-age=365000000, immutable, public",
+            ))
         );
     }
 
@@ -838,8 +840,8 @@ mod tests {
             name: Some(IndexName::from_str("pytorch").unwrap()),
             url: IndexUrl::from_str("https://download.pytorch.org/whl/cu118").unwrap(),
             cache_control: Some(IndexCacheControl {
-                api: Some(SmallString::from("no-cache")),
-                files: Some(SmallString::from("max-age=3600")),
+                api: Some(HeaderValue::from_static("no-cache")),
+                files: Some(HeaderValue::from_static("max-age=3600")),
             }),
             explicit: false,
             default: false,
@@ -858,21 +860,21 @@ mod tests {
         // User settings should override defaults
         assert_eq!(
             index_urls.simple_api_cache_control_for(&pytorch_url),
-            Some("no-cache")
+            Some(HeaderValue::from_static("no-cache"))
         );
         assert_eq!(
             index_urls.artifact_cache_control_for(&pytorch_url),
-            Some("max-age=3600")
+            Some(HeaderValue::from_static("max-age=3600"))
         );
 
         // Same for IndexLocations
         assert_eq!(
             index_locations.simple_api_cache_control_for(&pytorch_url),
-            Some("no-cache")
+            Some(HeaderValue::from_static("no-cache"))
         );
         assert_eq!(
             index_locations.artifact_cache_control_for(&pytorch_url),
-            Some("max-age=3600")
+            Some(HeaderValue::from_static("max-age=3600"))
         );
     }
 
@@ -901,7 +903,9 @@ mod tests {
         assert_eq!(index_urls.simple_api_cache_control_for(&nvidia_url), None);
         assert_eq!(
             index_urls.artifact_cache_control_for(&nvidia_url),
-            Some("max-age=365000000, immutable, public")
+            Some(HeaderValue::from_static(
+                "max-age=365000000, immutable, public",
+            ))
         );
 
         // IndexLocations should also return the default for NVIDIA
@@ -911,7 +915,9 @@ mod tests {
         );
         assert_eq!(
             index_locations.artifact_cache_control_for(&nvidia_url),
-            Some("max-age=365000000, immutable, public")
+            Some(HeaderValue::from_static(
+                "max-age=365000000, immutable, public",
+            ))
         );
     }
 }
diff --git a/crates/uv-distribution/src/distribution_database.rs b/crates/uv-distribution/src/distribution_database.rs
index 66802231183da..2267408972df0 100644
--- a/crates/uv-distribution/src/distribution_database.rs
+++ b/crates/uv-distribution/src/distribution_database.rs
@@ -746,7 +746,7 @@ impl<'a, Context: BuildContext> DistributionDatabase<'a, Context> {
                 client.cached_client().get_serde_with_retry(
                     req,
                     &http_entry,
-                    cache_control,
+                    cache_control.clone(),
                     download,
                 )
             })
@@ -953,7 +953,7 @@ impl<'a, Context: BuildContext> DistributionDatabase<'a, Context> {
                 client.cached_client().get_serde_with_retry(
                     req,
                     &http_entry,
-                    cache_control,
+                    cache_control.clone(),
                     download,
                 )
             })
diff --git a/crates/uv-distribution/src/source/mod.rs b/crates/uv-distribution/src/source/mod.rs
index 284902ac53e91..17c07fceae074 100644
--- a/crates/uv-distribution/src/source/mod.rs
+++ b/crates/uv-distribution/src/source/mod.rs
@@ -818,7 +818,7 @@ impl<'a, T: BuildContext> SourceDistributionBuilder<'a, T> {
                 client.cached_client().get_serde_with_retry(
                     req,
                     &cache_entry,
-                    cache_control,
+                    cache_control.clone(),
                     download,
                 )
             })
@@ -2278,7 +2278,7 @@ impl<'a, T: BuildContext> SourceDistributionBuilder<'a, T> {
                     .skip_cache_with_retry(
                         Self::request(url.clone(), client)?,
                         &cache_entry,
-                        cache_control,
+                        cache_control.clone(),
                         download,
                     )
                     .await
diff --git a/crates/uv/tests/it/lock.rs b/crates/uv/tests/it/lock.rs
index 9e0d1e3a1127f..dd848a637cc30 100644
--- a/crates/uv/tests/it/lock.rs
+++ b/crates/uv/tests/it/lock.rs
@@ -19254,6 +19254,53 @@ fn lock_unnamed_explicit_index() -> Result<()> {
     Ok(())
 }
 
+/// Error when an index cache-control override is not a valid HTTP header value.
+#[test]
+fn lock_invalid_index_cache_control() -> Result<()> {
+    let context = uv_test::test_context!("3.12");
+
+    let pyproject_toml = context.temp_dir.child("pyproject.toml");
+    pyproject_toml.write_str(
+        r#"
+        [project]
+        name = "project"
+        version = "0.1.0"
+        requires-python = ">=3.12"
+        dependencies = ["iniconfig==2.0.0"]
+
+        [[tool.uv.index]]
+        name = "test"
+        url = "https://test.pypi.org/simple"
+        cache-control.api = """
+        max-age=600
+        """
+        "#,
+    )?;
+
+    uv_snapshot!(context.filters(), context.lock(), @"
+    success: false
+    exit_code: 2
+    ----- stdout -----
+
+    ----- stderr -----
+    warning: Failed to parse `pyproject.toml` during settings discovery:
+      TOML parse error at line 11, column 9
+         |
+      11 |         cache-control.api = \"\"\"
+         |         ^^^^^^^^^^^^^
+      `cache-control.api` must be a valid HTTP header value
+
+    error: Failed to parse: `pyproject.toml`
+      Caused by: TOML parse error at line 11, column 9
+       |
+    11 |         cache-control.api = \"\"\"
+       |         ^^^^^^^^^^^^^
+    `cache-control.api` must be a valid HTTP header value
+    ");
+
+    Ok(())
+}
+
 #[tokio::test]
 async fn lock_named_index() -> Result<()> {
     let context = uv_test::test_context!("3.12");

PATCH
