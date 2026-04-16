#!/bin/bash
set -e

cd /workspace/lancedb

# Check if already applied (idempotency check)
if grep -q "3.1.0-beta.2" Cargo.toml; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
patch -p1 <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 75066a78bb..53c65d93da 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -128,15 +128,6 @@ version = "1.0.100"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a23eb6b1614318a8071c9b2521f36b424b2c83db5eb3a0fead4a6c0809af6e61"

-[[package]]
-name = "approx"
-version = "0.5.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cab112f0a86d568ea0e627cc1d6be74a1e9cd55214684db5561995f6dad897c6"
-dependencies = [
- "num-traits",
-]
-
 [[package]]
 name = "arbitrary"
 version = "1.4.2"
@@ -2796,16 +2787,6 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "05dbec7076f432bb132db738df90d87a4f5789e99f59e7b1219a6b8ef61eaa68"

-[[package]]
-name = "earcutr"
-version = "0.4.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "79127ed59a85d7687c409e9978547cffb7dc79675355ed22da6b66fd5f6ead01"
-dependencies = [
- "itertools 0.11.0",
- "num-traits",
-]
-
 [[package]]
 name = "ecdsa"
 version = "0.14.8"
@@ -3052,12 +3033,6 @@ dependencies = [
  "miniz_oxide",
 ]

-[[package]]
-name = "float_next_after"
-version = "1.0.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8bf7cc16383c4b8d58b9905a8509f02926ce3058053c056376248d958c9df1e8"
-
 [[package]]
 name = "fnv"
 version = "1.0.7"
@@ -3103,8 +3078,8 @@ checksum = "42703706b716c37f96a77aea830392ad231f44c9e9a67872fa5548707e11b11c"

 [[package]]
 name = "fsst"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-array",
  "rand 0.9.2",
@@ -3481,128 +3456,6 @@ dependencies = [
  "version_check",
 ]

-[[package]]
-name = "geo"
-version = "0.31.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2fc1a1678e54befc9b4bcab6cd43b8e7f834ae8ea121118b0fd8c42747675b4a"
-dependencies = [
- "earcutr",
- "float_next_after",
- "geo-types",
- "geographiclib-rs",
- "i_overlay",
- "log",
- "num-traits",
- "robust",
- "rstar",
- "spade",
-]
-
-[[package]]
-name = "geo-traits"
-version = "0.3.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2e7c353d12a704ccfab1ba8bfb1a7fe6cb18b665bf89d37f4f7890edcd260206"
-dependencies = [
- "geo-types",
-]
-
-[[package]]
-name = "geo-types"
-version = "0.7.17"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "75a4dcd69d35b2c87a7c83bce9af69fd65c9d68d3833a0ded568983928f3fc99"
-dependencies = [
- "approx",
- "num-traits",
- "rayon",
- "rstar",
- "serde",
-]
-
-[[package]]
-name = "geoarrow-array"
-version = "0.7.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dc1cc4106ac0a0a512c398961ce95d8150475c84a84e17c4511c3643fa120a17"
-dependencies = [
- "arrow-array",
- "arrow-buffer",
- "arrow-schema",
- "geo-traits",
- "geoarrow-schema",
- "num-traits",
- "wkb",
- "wkt",
-]
-
-[[package]]
-name = "geoarrow-expr-geo"
-version = "0.7.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fa84300361ce57fb875bcaa6e32b95b0aff5c6b1af692b936bdd58ff343f4394"
-dependencies = [
- "arrow-array",
- "arrow-buffer",
- "geo",
- "geo-traits",
- "geoarrow-array",
- "geoarrow-schema",
-]
-
-[[package]]
-name = "geoarrow-schema"
-version = "0.7.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e97be4e9f523f92bd6a0e0458323f4b783d073d011664decd8dbf05651704f34"
-dependencies = [
- "arrow-schema",
- "geo-traits",
- "serde",
- "serde_json",
- "thiserror 1.0.69",
-]
-
-[[package]]
-name = "geodatafusion"
-version = "0.2.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "773cfa1fb0d7f7661b76b3fde00f3ffd8e0ff7b3635096f0ff6294fe5ca62a2b"
-dependencies = [
- "arrow-arith",
- "arrow-array",
- "arrow-schema",
- "datafusion",
- "geo",
- "geo-traits",
- "geoarrow-array",
- "geoarrow-expr-geo",
- "geoarrow-schema",
- "geohash",
- "thiserror 1.0.69",
- "wkt",
-]
-
-[[package]]
-name = "geographiclib-rs"
-version = "0.2.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f611040a2bb37eaa29a78a128d1e92a378a03e0b6e66ae27398d42b1ba9a7841"
-dependencies = [
- "libm",
-]
-
-[[package]]
-name = "geohash"
-version = "0.13.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fb94b1a65401d6cbf22958a9040aa364812c26674f841bee538b12c135db1e6"
-dependencies = [
- "geo-types",
- "libm",
-]
-
 [[package]]
 name = "getrandom"
 version = "0.2.16"
@@ -3712,15 +3565,6 @@ dependencies = [
  "zerocopy",
 ]

-[[package]]
-name = "hash32"
-version = "0.3.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "47d60b12902ba28e2730cd37e95b8c9223af2808df9e902d4df49588d1470606"
-dependencies = [
- "byteorder",
-]
-
 [[package]]
 name = "hashbrown"
 version = "0.12.3"
@@ -3755,16 +3599,6 @@ version = "0.16.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5419bdc4f6a9207fbeba6d11b604d481addf78ecd10c11ad51e76c2f6482748d"

-[[package]]
-name = "heapless"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0bfb9eb618601c89945a70e254898da93b13be0388091d42117462b265bb3fad"
-dependencies = [
- "hash32",
- "stable_deref_trait",
-]
-
 [[package]]
 name = "heck"
 version = "0.4.1"
@@ -4026,49 +3860,6 @@ dependencies = [
  "serde",
 ]

-[[package]]
-name = "i_float"
-version = "1.15.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "010025c2c532c8d82e42d0b8bb5184afa449fa6f06c709ea9adcb16c49ae405b"
-dependencies = [
- "libm",
-]
-
-[[package]]
-name = "i_key_sort"
-version = "0.6.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9190f86706ca38ac8add223b2aed8b1330002b5cdbbce28fb58b10914d38fc27"
-
-[[package]]
-name = "i_overlay"
-version = "4.0.6"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fcccbd4e4274e0f80697f5fbc6540fdac533cce02f2081b328e68629cce24f9"
-dependencies = [
- "i_float",
- "i_key_sort",
- "i_shape",
- "i_tree",
- "rayon",
-]
-
-[[package]]
-name = "i_shape"
-version = "1.14.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1ea154b742f7d43dae2897fcd5ead86bc7b5eefcedd305a7ebf9f69d44d61082"
-dependencies = [
- "i_float",
-]
-
-[[package]]
-name = "i_tree"
-version = "0.16.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "35e6d558e6d4c7b82bc51d9c771e7a927862a161a7d87bf2b0541450e0e20915"
-
 [[package]]
 name = "iana-time-zone"
 version = "0.1.64"
@@ -4435,8 +4226,8 @@ dependencies = [

 [[package]]
 name = "lance"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4473,7 +4264,6 @@ dependencies = [
  "lance-datafusion",
  "lance-encoding",
  "lance-file",
- "lance-geo",
  "lance-index",
  "lance-io",
  "lance-linalg",
@@ -4503,8 +4293,8 @@ dependencies = [

 [[package]]
 name = "lance-arrow"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4523,8 +4313,8 @@ dependencies = [

 [[package]]
 name = "lance-bitpacking"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrayref",
  "paste",
@@ -4533,8 +4323,8 @@ dependencies = [

 [[package]]
 name = "lance-core"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4571,8 +4361,8 @@ dependencies = [

 [[package]]
 name = "lance-datafusion"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4591,7 +4381,6 @@ dependencies = [
  "lance-arrow",
  "lance-core",
  "lance-datagen",
- "lance-geo",
  "log",
  "pin-project",
  "prost",
@@ -4603,8 +4392,8 @@ dependencies = [

 [[package]]
 name = "lance-datagen"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4622,8 +4411,8 @@ dependencies = [

 [[package]]
 name = "lance-encoding"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-arith",
  "arrow-array",
@@ -4660,8 +4449,8 @@ dependencies = [

 [[package]]
 name = "lance-file"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-arith",
  "arrow-array",
@@ -4691,25 +4480,10 @@ dependencies = [
  "tracing",
 ]

-[[package]]
-name = "lance-geo"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
-dependencies = [
- "datafusion",
- "geo-traits",
- "geo-types",
- "geoarrow-array",
- "geoarrow-schema",
- "geodatafusion",
- "lance-core",
- "serde",
-]
-
 [[package]]
 name = "lance-index"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4733,9 +4507,6 @@ dependencies = [
  "dirs",
  "fst",
  "futures",
- "geo-types",
- "geoarrow-array",
- "geoarrow-schema",
  "half",
  "itertools 0.13.0",
  "jsonb",
@@ -4745,7 +4516,6 @@ dependencies = [
  "lance-datagen",
  "lance-encoding",
  "lance-file",
- "lance-geo",
  "lance-io",
  "lance-linalg",
  "lance-table",
@@ -4776,8 +4546,8 @@ dependencies = [

 [[package]]
 name = "lance-io"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4808,7 +4578,6 @@ dependencies = [
  "prost",
  "rand 0.9.2",
  "serde",
- "shellexpand",
  "snafu",
  "tempfile",
  "tokio",
@@ -4818,8 +4587,8 @@ dependencies = [

 [[package]]
 name = "lance-linalg"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4835,8 +4604,8 @@ dependencies = [

 [[package]]
 name = "lance-namespace"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "async-trait",
@@ -4848,8 +4617,8 @@ dependencies = [

 [[package]]
 name = "lance-namespace-impls"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-ipc",
@@ -4893,8 +4662,8 @@ dependencies = [

 [[package]]
 name = "lance-table"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4933,8 +4702,8 @@ dependencies = [

 [[package]]
 name = "lance-testing"
-version = "3.0.0-beta.5"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-beta.5#c69274bd83da9930157d5e2ceeb101af13a916a3"
+version = "3.1.0-beta.2"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.1.0-beta.2#ae3b1f413cc49d783f51abe62c8261c106c9b6cd"
 dependencies = [
  "arrow-array",
  "arrow-schema",
@@ -7318,12 +7087,6 @@ dependencies = [
  "byteorder",
 ]

-[[package]]
-name = "robust"
-version = "1.2.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4e27ee8bb91ca0adcf0ecb116293afa12d393f9c2b9b9cd54d33e8078fe19839"
-
 [[package]]
 name = "rsa"
 version = "0.9.8"
@@ -7345,17 +7108,6 @@ dependencies = [
  "zeroize",
 ]

-[[package]]
-name = "rstar"
-version = "0.12.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "421400d13ccfd26dfa5858199c30a5d76f9c54e0dba7575273025b43c5175dbb"
-dependencies = [
- "heapless",
- "num-traits",
- "smallvec",
-]
-
 [[package]]
 name = "rstest"
 version = "0.23.0"
@@ -7910,15 +7662,6 @@ dependencies = [
  "lazy_static",
 ]

-[[package]]
-name = "shellexpand"
-version = "3.1.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8b1fdf65dd6331831494dd616b30351c38e96e45921a27745cf98490458b90bb"
-dependencies = [
- "dirs",
-]
-
 [[package]]
 name = "shlex"
 version = "1.3.0"
@@ -8068,18 +7811,6 @@ dependencies = [
  "winapi",
 ]

-[[package]]
-name = "spade"
-version = "2.15.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fb313e1c8afee5b5647e00ee0fe6855e3d529eb863a0fdae1d60006c4d1e9990"
-dependencies = [
- "hashbrown 0.15.5",
- "num-traits",
- "robust",
- "smallvec",
-]
-
 [[package]]
 name = "spin"
 version = "0.9.8"
@@ -9674,31 +9405,6 @@ version = "0.46.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f17a85883d4e6d00e8a97c586de764dabcc06133f7f1d55dce5cdc070ad7fe59"

-[[package]]
-name = "wkb"
-version = "0.9.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a120b336c7ad17749026d50427c23d838ecb50cd64aaea6254b5030152f890a9"
-dependencies = [
- "byteorder",
- "geo-traits",
- "num_enum",
- "thiserror 1.0.69",
-]
-
-[[package]]
-name = "wkt"
-version = "0.14.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efb2b923ccc882312e559ffaa832a055ba9d1ac0cc8e86b3e25453247e4b81d7"
-dependencies = [
- "geo-traits",
- "geo-types",
- "log",
- "num-traits",
- "thiserror 1.0.69",
-]
-
 [[package]]
 name = "writeable"
 version = "0.6.1"
diff --git a/Cargo.toml b/Cargo.toml
index 3c7f2c4ab7..c83dfd4465 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -15,20 +15,20 @@ categories = ["database-implementations"]
 rust-version = "1.91.0"

 [workspace.dependencies]
-lance = { "version" = "=3.0.0-beta.5", default-features = false, "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-core = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-datagen = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-file = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-io = { "version" = "=3.0.0-beta.5", default-features = false, "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-index = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-linalg = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-namespace = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-namespace-impls = { "version" = "=3.0.0-beta.5", default-features = false, "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-table = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-testing = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-datafusion = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-encoding = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
-lance-arrow = { "version" = "=3.0.0-beta.5", "tag" = "v3.0.0-beta.5", "git" = "https://github.com/lance-format/lance.git" }
+lance = { "version" = "=3.1.0-beta.2", default-features = false, "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-core = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-datagen = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-file = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-io = { "version" = "=3.1.0-beta.2", default-features = false, "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-index = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-linalg = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-namespace = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-namespace-impls = { "version" = "=3.1.0-beta.2", default-features = false, "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-table = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-testing = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-datafusion = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-encoding = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
+lance-arrow = { "version" = "=3.1.0-beta.2", "tag" = "v3.1.0-beta.2", "git" = "https://github.com/lance-format/lance.git" }
 ahash = "0.8"
 # Note that this one does not include pyarrow
 arrow = { version = "57.2", optional = false }
diff --git a/java/pom.xml b/java/pom.xml
index 9ba445d35a..f3a898822a 100644
--- a/java/pom.xml
+++ b/java/pom.xml
@@ -28,7 +28,7 @@
     <properties>
         <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
         <arrow.version>15.0.0</arrow.version>
-        <lance-core.version>3.0.0-beta.5</lance-core.version>
+        <lance-core.version>3.1.0-beta.2</lance-core.version>
         <spotless.skip>false</spotless.skip>
         <spotless.version>2.30.0</spotless.version>
         <spotless.java.googlejavaformat.version>1.7</spotless.java.googlejavaformat.version>
PATCH

echo "Patch applied successfully"
