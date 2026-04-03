#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'python36-support.patch' crates/uv-python/python/packaging/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Lower version floor in get_interpreter_info.py from (3, 7) to (3, 6)
sed -i 's/if sys\.version_info < (3, 7):/if sys.version_info < (3, 6):/' \
    crates/uv-python/python/get_interpreter_info.py

# 2. Patch _elffile.py for Python 3.6 compat
sed -i '/^from __future__ import annotations$/d' \
    crates/uv-python/python/packaging/_elffile.py
sed -i 's/) -> tuple\[int, \.\.\.]:/) -> "tuple[int, ...]":/' \
    crates/uv-python/python/packaging/_elffile.py
sed -i 's/) -> str | None:/) -> "str | None":/' \
    crates/uv-python/python/packaging/_elffile.py

# 3. Patch _manylinux.py for Python 3.6 compat
sed -i '/^from __future__ import annotations$/d' \
    crates/uv-python/python/packaging/_manylinux.py
sed -i 's/) -> Generator\[ELFFile | None, None, None]:/) -> "Generator[ELFFile | None, None, None]":/' \
    crates/uv-python/python/packaging/_manylinux.py
sed -i "s/_LAST_GLIBC_MINOR: dict\[int, int\]/_LAST_GLIBC_MINOR: \"dict[int, int]\"/" \
    crates/uv-python/python/packaging/_manylinux.py
sed -i 's/) -> str | None:/) -> "str | None":/' \
    crates/uv-python/python/packaging/_manylinux.py
sed -i 's/version_string: str | None/version_string: "str | None"/' \
    crates/uv-python/python/packaging/_manylinux.py
sed -i "s/_LEGACY_MANYLINUX_MAP: dict\[_GLibCVersion, str\]/_LEGACY_MANYLINUX_MAP: \"dict[_GLibCVersion, str]\"/" \
    crates/uv-python/python/packaging/_manylinux.py

# 4. Patch _musllinux.py for Python 3.6 compat
sed -i '/^from __future__ import annotations$/d' \
    crates/uv-python/python/packaging/_musllinux.py
sed -i 's/) -> _MuslVersion | None:/) -> "_MuslVersion | None":/' \
    crates/uv-python/python/packaging/_musllinux.py

# 5. Create python36-support.patch documenting the changes
cat > crates/uv-python/python/packaging/python36-support.patch << 'PATCHEOF'
From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001
Subject: [PATCH] python36-support

Remove `from __future__ import annotations` and quote PEP 604 (`X | Y`) union
annotations and PEP 585 (`dict[K, V]`) lowercase generics so these vendored
modules remain compatible with Python 3.6.

---
diff --git a/crates/uv-python/python/packaging/_elffile.py b/crates/uv-python/python/packaging/_elffile.py
index 8dc7fb32a..f1907a595 100644
--- a/crates/uv-python/python/packaging/_elffile.py
+++ b/crates/uv-python/python/packaging/_elffile.py
@@ -8,8 +8,6 @@ Based on: https://gist.github.com/lyssdod/f51579ae8d93c8657a5564aefc2ffbca
 ELF header: https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.eheader.html
 """

-from __future__ import annotations
-
 import enum
 import os
 import struct
@@ -88,11 +86,11 @@ class ELFFile:
         except struct.error as e:
             raise ELFInvalid("unable to parse machine and section information") from e

-    def _read(self, fmt: str) -> tuple[int, ...]:
+    def _read(self, fmt: str) -> "tuple[int, ...]":
         return struct.unpack(fmt, self._f.read(struct.calcsize(fmt)))

     @property
-    def interpreter(self) -> str | None:
+    def interpreter(self) -> "str | None":
         """
         The path recorded in the ``PT_INTERP`` section header.
         """
diff --git a/crates/uv-python/python/packaging/_manylinux.py b/crates/uv-python/python/packaging/_manylinux.py
index 7b52a5581..d3c871aab 100644
--- a/crates/uv-python/python/packaging/_manylinux.py
+++ b/crates/uv-python/python/packaging/_manylinux.py
@@ -1,5 +1,3 @@
-from __future__ import annotations
-
 import collections
 import contextlib
 import functools
@@ -19,7 +17,7 @@ EF_ARM_ABI_FLOAT_HARD = 0x00000400
 # `os.PathLike` not a generic type until Python 3.9, so sticking with `str`
 # as the type for `path` until then.
 @contextlib.contextmanager
-def _parse_elf(path: str) -> Generator[ELFFile | None, None, None]:
+def _parse_elf(path: str) -> "Generator[ELFFile | None, None, None]":
     try:
         with open(path, "rb") as f:
             yield ELFFile(f)
@@ -74,7 +72,7 @@ def _have_compatible_abi(executable: str, archs: Sequence[str]) -> bool:
 # For now, guess what the highest minor version might be, assume it will
 # be 50 for testing. Once this actually happens, update the dictionary
 # with the actual value.
-_LAST_GLIBC_MINOR: dict[int, int] = collections.defaultdict(lambda: 50)
+_LAST_GLIBC_MINOR: "dict[int, int]" = collections.defaultdict(lambda: 50)


 class _GLibCVersion(NamedTuple):
@@ -82,7 +80,7 @@ class _GLibCVersion(NamedTuple):
     minor: int


-def _glibc_version_string_confstr() -> str | None:
+def _glibc_version_string_confstr() -> "str | None":
     """
     Primary implementation of glibc_version_string using os.confstr.
     """
@@ -92,7 +90,7 @@ def _glibc_version_string_confstr() -> str | None:
     # https://github.com/python/cpython/blob/fcf1d003bf4f0100c/Lib/platform.py#L175-L183
     try:
         # Should be a string like "glibc 2.17".
-        version_string: str | None = os.confstr("CS_GNU_LIBC_VERSION")
+        version_string: "str | None" = os.confstr("CS_GNU_LIBC_VERSION")
         assert version_string is not None
         _, version = version_string.rsplit()
     except (AssertionError, AttributeError, OSError, ValueError):
@@ -101,7 +99,7 @@ def _glibc_version_string_confstr() -> str | None:
     return version


-def _glibc_version_string_ctypes() -> str | None:
+def _glibc_version_string_ctypes() -> "str | None":
     """
     Fallback implementation of glibc_version_string using ctypes.
     """
@@ -145,7 +143,7 @@ def _glibc_version_string_ctypes() -> str | None:
     return version_str


-def _glibc_version_string() -> str | None:
+def _glibc_version_string() -> "str | None":
     """Returns glibc version string, or None if not using glibc."""
     return _glibc_version_string_confstr() or _glibc_version_string_ctypes()

@@ -203,7 +201,7 @@ def _is_compatible(arch: str, version: _GLibCVersion) -> bool:
     return True


-_LEGACY_MANYLINUX_MAP: dict[_GLibCVersion, str] = {
+_LEGACY_MANYLINUX_MAP: "dict[_GLibCVersion, str]" = {
     # CentOS 7 w/ glibc 2.17 (PEP 599)
     _GLibCVersion(2, 17): "manylinux2014",
     # CentOS 6 w/ glibc 2.12 (PEP 571)
diff --git a/crates/uv-python/python/packaging/_musllinux.py b/crates/uv-python/python/packaging/_musllinux.py
index b4ca23804..40a72f05b 100644
--- a/crates/uv-python/python/packaging/_musllinux.py
+++ b/crates/uv-python/python/packaging/_musllinux.py
@@ -4,8 +4,6 @@ This module implements logic to detect if the currently running Python is
 linked against musl, and what musl version is used.
 """

-from __future__ import annotations
-
 import functools
 import re
 import subprocess
@@ -20,7 +18,7 @@ class _MuslVersion(NamedTuple):
     minor: int


-def _parse_musl_version(output: str) -> _MuslVersion | None:
+def _parse_musl_version(output: str) -> "_MuslVersion | None":
     lines = [n for n in (n.strip() for n in output.splitlines()) if n]
     if len(lines) < 2 or lines[0][:4] != "musl":
         return None
@@ -31,7 +29,7 @@ def _parse_musl_version(output: str) -> _MuslVersion | None:


 @functools.lru_cache()
-def _get_musl_version(executable: str) -> _MuslVersion | None:
+def _get_musl_version(executable: str) -> "_MuslVersion | None":
     """Detect currently-running musl runtime version.

     This is done by checking the specified executable's dynamic linking
PATCHEOF

# 6. Update packaging/README.md to document applied patches
cat >> crates/uv-python/python/packaging/README.md << 'READMEEOF'

## Patches

The following patches have been applied:

- [python36-support.patch](./python36-support.patch)
READMEEOF

echo "Patch applied successfully."
