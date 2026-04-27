"""Behavioral verification for selenium PR #17340.

Strategy: stub out the small set of selenium types referenced by
``HttpClient.java`` so we can compile that single source file with javac in
isolation. Then run ``javap -v`` against the resulting class file and parse
its annotation table — a real binary-level check, not source grepping.
``JdkHttpClient.java`` pulls in heavy third-party deps (AutoService, Guava,
jspecify, …) that we cannot reasonably bring in without Bazel, so its new
public method is verified by AST-style source parsing.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/selenium")
HTTP_CLIENT_JAVA = REPO / "java/src/org/openqa/selenium/remote/http/HttpClient.java"
JDK_HTTP_CLIENT_JAVA = REPO / "java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java"
AGENTS_MD = REPO / "java/AGENTS.md"

STUB_DIR = Path("/tmp/selenium-stubs")
OUT_DIR = Path("/tmp/selenium-classes")

STUBS: dict[str, str] = {
    "org/openqa/selenium/remote/http/WebSocket.java": """
package org.openqa.selenium.remote.http;
public interface WebSocket { interface Listener {} }
""",
    "org/openqa/selenium/remote/http/HttpRequest.java": """
package org.openqa.selenium.remote.http;
public class HttpRequest {}
""",
    "org/openqa/selenium/remote/http/HttpResponse.java": """
package org.openqa.selenium.remote.http;
public class HttpResponse {}
""",
    "org/openqa/selenium/remote/http/HttpHandler.java": """
package org.openqa.selenium.remote.http;
public interface HttpHandler { HttpResponse execute(HttpRequest req); }
""",
    "org/openqa/selenium/remote/http/HttpClientName.java": """
package org.openqa.selenium.remote.http;
public @interface HttpClientName { String value(); }
""",
    "org/openqa/selenium/remote/http/ClientConfig.java": """
package org.openqa.selenium.remote.http;
import java.net.URL;
public class ClientConfig {
  public static ClientConfig defaultConfig() { return new ClientConfig(); }
  public ClientConfig baseUrl(URL u) { return this; }
}
""",
    "org/openqa/selenium/internal/Require.java": """
package org.openqa.selenium.internal;
public class Require {
  public static <T> T nonNull(String msg, T obj) {
    if (obj == null) throw new NullPointerException(msg);
    return obj;
  }
}
""",
}


def _ensure_classes_built() -> Path:
    """Compile HttpClient.java against stubs once per test session.

    Returns the directory containing the compiled .class output. Cached
    between calls within a pytest session via the OUT_DIR marker file.
    """
    marker = OUT_DIR / ".built"
    if marker.exists():
        return OUT_DIR

    if STUB_DIR.exists():
        shutil.rmtree(STUB_DIR)
    STUB_DIR.mkdir(parents=True)
    for rel, body in STUBS.items():
        target = STUB_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body.lstrip())

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    stub_sources = [str(p) for p in STUB_DIR.rglob("*.java")]
    r = subprocess.run(
        ["javac", "-d", str(OUT_DIR), "-sourcepath", str(STUB_DIR), *stub_sources],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"stub compile failed:\n{r.stderr}"

    r = subprocess.run(
        ["javac", "-d", str(OUT_DIR), "-classpath", str(OUT_DIR), str(HTTP_CLIENT_JAVA)],
        capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"HttpClient.java compile failed:\n{r.stderr}"

    marker.touch()
    return OUT_DIR


def _javap_dump(class_name: str) -> str:
    out_dir = _ensure_classes_built()
    r = subprocess.run(
        ["javap", "-v", "-classpath", str(out_dir), class_name],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"javap failed: {r.stderr}"
    return r.stdout


def _method_block(dump: str, method: str) -> str:
    """Slice the javap text dump for a single method's section."""
    pattern = re.compile(
        rf"^\s*public[^\n]*\b{re.escape(method)}\s*\(",
        re.MULTILINE,
    )
    m = pattern.search(dump)
    assert m, f"method {method} not found in javap output"
    end = pattern.search(dump, m.end())
    return dump[m.start(): end.start() if end else len(dump)]


# --- Track 1: behavioral / binary-level checks --------------------------------

def test_http_client_compiles():
    """HttpClient.java compiles cleanly against the package's API surface."""
    out = _ensure_classes_built()
    assert (out / "org/openqa/selenium/remote/http/HttpClient.class").exists()


def test_send_async_native_method_exists():
    """sendAsyncNative is still a declared method on the interface (sanity)."""
    block = _method_block(_javap_dump("org.openqa.selenium.remote.http.HttpClient"),
                          "sendAsyncNative")
    assert "ACC_ABSTRACT" in block, "sendAsyncNative should remain an abstract interface method"


def test_send_native_method_exists():
    """sendNative is still a declared method on the interface (sanity)."""
    block = _method_block(_javap_dump("org.openqa.selenium.remote.http.HttpClient"),
                          "sendNative")
    assert "ACC_ABSTRACT" in block, "sendNative should remain an abstract interface method"


def test_send_async_native_marked_deprecated_for_removal():
    """sendAsyncNative carries @Deprecated(forRemoval=true) at the bytecode level."""
    block = _method_block(_javap_dump("org.openqa.selenium.remote.http.HttpClient"),
                          "sendAsyncNative")
    assert "Deprecated: true" in block, (
        "sendAsyncNative is missing the Deprecated bytecode attribute. "
        f"Block was:\n{block[:1500]}"
    )
    assert re.search(r"java\.lang\.Deprecated\(\s*forRemoval=true", block), (
        "sendAsyncNative must be annotated @Deprecated(forRemoval = true). "
        f"javap output for the method:\n{block[:1500]}"
    )


def test_send_native_marked_deprecated_for_removal():
    """sendNative carries @Deprecated(forRemoval=true) at the bytecode level."""
    block = _method_block(_javap_dump("org.openqa.selenium.remote.http.HttpClient"),
                          "sendNative")
    assert "Deprecated: true" in block, (
        "sendNative is missing the Deprecated bytecode attribute. "
        f"Block was:\n{block[:1500]}"
    )
    assert re.search(r"java\.lang\.Deprecated\(\s*forRemoval=true", block), (
        "sendNative must be annotated @Deprecated(forRemoval = true). "
        f"javap output for the method:\n{block[:1500]}"
    )


def test_jdk_http_client_exposes_native_client():
    """JdkHttpClient exposes a public accessor for the underlying java.net.http.HttpClient.

    We can't easily compile JdkHttpClient.java standalone (it has heavy
    third-party deps), so we parse the source for a public method whose
    return type is ``java.net.http.HttpClient`` (with no parameters).
    """
    src = JDK_HTTP_CLIENT_JAVA.read_text()
    src_no_comments = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src_no_comments = re.sub(r"//[^\n]*", "", src_no_comments)

    pattern = re.compile(
        r"public\s+(?:final\s+)?java\.net\.http\.HttpClient\s+\w+\s*\(\s*\)\s*\{",
    )
    matches = pattern.findall(src_no_comments)
    assert matches, (
        "JdkHttpClient should declare a public no-arg method whose return type is "
        "java.net.http.HttpClient so callers can reach the underlying native client."
    )

    body_pattern = re.compile(
        r"public\s+(?:final\s+)?java\.net\.http\.HttpClient\s+(\w+)\s*\(\s*\)\s*\{\s*"
        r"return\s+(\w+)\s*;\s*\}",
    )
    body_match = body_pattern.search(src_no_comments)
    assert body_match, (
        "The accessor should simply return the existing private "
        "java.net.http.HttpClient field; no other signature passed the source check."
    )
    assert body_match.group(2) == "client", (
        f"Expected the accessor to return the existing 'client' field, got 'return {body_match.group(2)};'"
    )


def test_agents_md_documents_interface_conventions():
    """java/AGENTS.md gains conventions for interface design.

    Looser than the gold diff's exact wording — Track 2 (Gemini) judges
    semantic equivalence; this only enforces structural presence.
    """
    text = AGENTS_MD.read_text()

    heading = re.search(r"^#{1,6}\s*Interfaces?\s*$", text, re.MULTILINE | re.IGNORECASE)
    assert heading, (
        "java/AGENTS.md must add a heading for the new Interfaces convention "
        "section under '## Code conventions'."
    )

    section_start = heading.end()
    next_heading = re.search(r"^#{1,6}\s+\S", text[section_start:], re.MULTILINE)
    section = text[section_start: section_start + (next_heading.start() if next_heading else len(text))]
    section_lower = section.lower()

    assert "default" in section_lower, (
        "The new Interfaces section must mention the rule about providing "
        "default implementations for new interface methods."
    )
    assert "native" in section_lower, (
        "The new Interfaces section must mention that interfaces should not "
        "expose the native classes of their implementations."
    )


# --- Track 1 p2p: structural sanity (passes at base AND gold) -----------------

def test_http_client_source_well_formed():
    """HttpClient.java is parseable — guards against accidental syntax breakage."""
    src = HTTP_CLIENT_JAVA.read_text()
    assert "interface HttpClient" in src
    assert "sendAsyncNative" in src
    assert "sendNative" in src


def test_jdk_http_client_source_well_formed():
    """JdkHttpClient.java still imports java.net.http.HttpClient (sanity)."""
    src = JDK_HTTP_CLIENT_JAVA.read_text()
    assert "java.net.http.HttpClient" in src
    assert "class JdkHttpClient" in src


def test_agents_md_preserves_existing_sections():
    """The pre-existing Logging/Deprecation/Documentation conventions are intact."""
    text = AGENTS_MD.read_text()
    for heading in ("## Code conventions", "### Logging", "### Deprecation", "### Documentation"):
        assert heading in text, f"AGENTS.md should still contain the heading {heading!r}"
