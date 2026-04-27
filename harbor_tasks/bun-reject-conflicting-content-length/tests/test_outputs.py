"""Behavioral tests for bun-uws HttpParser Content-Length validation.

Each test compiles a small driver against the agent's modified HttpParser.h
and feeds it a single raw HTTP request, then inspects the parser's verdict.
"""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/bun")
HEADER_DIR = REPO / "packages" / "bun-uws" / "src"
DRIVER_SRC = Path("/tmp/http_parser_driver.cpp")
DRIVER_BIN = Path("/tmp/http_parser_driver")

DRIVER_SOURCE = textwrap.dedent(r'''
    // Standalone test driver for packages/bun-uws/src/HttpParser.h.
    // Stubs out Bun's external symbols so the parser can be exercised without
    // the full Bun runtime.

    #include <cstdint>
    #include <cstring>
    #include <cstdlib>
    #include <iostream>
    #include <string>
    #include <string_view>
    #include <vector>

    extern "C" {
        size_t BUN_DEFAULT_MAX_HTTP_HEADER_SIZE = 16384;
        int16_t Bun__HTTPMethod__from(const char *str, size_t len) {
            (void)str; (void)len;
            return 0;
        }
    }

    #include "HttpParser.h"

    int main(int argc, char** argv) {
        if (argc < 2) {
            std::cerr << "usage: " << argv[0] << " <case>" << std::endl;
            return 2;
        }

        std::string which = argv[1];
        std::string req;

        if (which == "differing_cl") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 6\r\nContent-Length: 5\r\n\r\nABCDEF";
        } else if (which == "differing_cl_reversed") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\nContent-Length: 6\r\n\r\nABCDEF";
        } else if (which == "matching_cl") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\nContent-Length: 5\r\n\r\nHello";
        } else if (which == "empty_cl_first") {
            std::string smuggled = "GET /admin HTTP/1.1\r\nHost: x\r\n\r\n";
            req = "POST /api HTTP/1.1\r\nHost: target\r\nContent-Length:\r\nContent-Length: "
                  + std::to_string(smuggled.length()) + "\r\n\r\n" + smuggled;
        } else if (which == "single_cl") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nHello";
        } else if (which == "no_cl_get") {
            req = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";
        } else if (which == "te_chunked") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nHello\r\n0\r\n\r\n";
        } else if (which == "te_and_cl") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\nContent-Length: 5\r\n\r\nHello";
        } else if (which == "three_cl_all_match") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Length: 4\r\nContent-Length: 4\r\n\r\nWXYZ";
        } else if (which == "three_cl_one_off") {
            req = "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\nContent-Length: 4\r\nContent-Length: 5\r\n\r\nWXYZQ";
        } else {
            std::cerr << "unknown case: " << which << std::endl;
            return 2;
        }

        std::vector<char> buf(req.size() + 64, 0);
        std::memcpy(buf.data(), req.data(), req.size());

        uWS::HttpParser parser;
        bool isConnect = false;

        int requestSeen = 0;
        std::string seenBody;

        uWS::MoveOnlyFunction<void *(void *, uWS::HttpRequest *)> rh =
            [&](void *user, uWS::HttpRequest *r) -> void* {
                (void)r;
                requestSeen++;
                return user;
            };
        uWS::MoveOnlyFunction<void *(void *, std::string_view, bool)> dh =
            [&](void *user, std::string_view data, bool fin) -> void* {
                (void)fin;
                seenBody.append(data.data(), data.size());
                return user;
            };

        void *user = (void*)0xdeadbeef;

        auto result = parser.consumePostPadded(
            BUN_DEFAULT_MAX_HTTP_HEADER_SIZE,
            isConnect,
            true,
            false,
            buf.data(),
            (unsigned int) req.size(),
            user,
            nullptr,
            std::move(rh),
            std::move(dh)
        );

        if (result.isError()) {
            std::cout << "ERROR status=" << result.httpErrorStatusCode()
                      << " parserError=" << (int)result.parserError
                      << std::endl;
        } else {
            std::cout << "OK consumed=" << result.consumedBytes()
                      << " requestSeen=" << requestSeen
                      << " body=" << seenBody
                      << std::endl;
        }
        return 0;
    }
''').lstrip()


def _ensure_driver_src() -> None:
    if not DRIVER_SRC.is_file():
        DRIVER_SRC.write_text(DRIVER_SOURCE)


def _compile_driver() -> None:
    if DRIVER_BIN.exists():
        return
    if not HEADER_DIR.is_dir():
        raise AssertionError(
            f"missing bun-uws sources at {HEADER_DIR}; the docker image was not "
            "built from the expected base commit"
        )
    _ensure_driver_src()
    cmd = [
        "g++",
        "-std=c++20",
        "-O0",
        "-g",
        f"-I{HEADER_DIR}",
        str(DRIVER_SRC),
        "-o",
        str(DRIVER_BIN),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (
        "failed to compile test driver against modified HttpParser.h:\n"
        f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
    )


def _run_case(case: str, timeout: int = 10) -> str:
    _compile_driver()
    proc = subprocess.run(
        [str(DRIVER_BIN), case],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert proc.returncode == 0, (
        f"driver crashed for case={case}: rc={proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return proc.stdout.strip()


# ---------------------------------------------------------------------------
# fail-to-pass
# ---------------------------------------------------------------------------

def test_compiles_against_modified_header():
    """Driver must compile against HttpParser.h after the agent's fix."""
    if DRIVER_BIN.exists():
        DRIVER_BIN.unlink()
    _compile_driver()
    assert DRIVER_BIN.exists()


def test_rejects_two_differing_content_length_headers():
    """Two Content-Length headers with different values must be rejected as a
    400 Bad Request with parser error INVALID_CONTENT_LENGTH."""
    out = _run_case("differing_cl")
    assert out.startswith("ERROR"), f"parser accepted differing duplicate Content-Length: {out!r}"
    assert "status=3" in out, f"expected 400 Bad Request (status=3): {out!r}"
    assert "parserError=2" in out, f"expected INVALID_CONTENT_LENGTH (parserError=2): {out!r}"


def test_rejects_two_differing_content_length_headers_reversed_order():
    """Ordering of conflicting Content-Length values must not matter."""
    out = _run_case("differing_cl_reversed")
    assert out.startswith("ERROR"), f"parser accepted differing CL (reversed): {out!r}"
    assert "status=3" in out
    assert "parserError=2" in out


def test_rejects_three_content_length_headers_one_differs():
    """A single differing value among multiple Content-Length headers must be rejected."""
    out = _run_case("three_cl_one_off")
    assert out.startswith("ERROR"), f"parser accepted 3 CL with one different: {out!r}"
    assert "parserError=2" in out


def test_rejects_empty_first_content_length_followed_by_smuggled():
    """An empty-valued Content-Length followed by a real one is a smuggling
    vector and must be rejected before the request body is interpreted."""
    out = _run_case("empty_cl_first")
    assert out.startswith("ERROR"), (
        "empty Content-Length followed by a real Content-Length was accepted; "
        f"this allows request smuggling. driver output: {out!r}"
    )
    assert "parserError=2" in out, f"expected INVALID_CONTENT_LENGTH: {out!r}"


def test_smuggled_request_is_not_processed_when_first_cl_is_empty():
    """Stronger framing of the smuggling check: even if the parser reported a
    success rather than an error, it must NOT have surfaced the smuggled inner
    request to the application (requestSeen must not be 2)."""
    out = _run_case("empty_cl_first")
    assert "requestSeen=2" not in out, (
        "parser surfaced a second (smuggled) request to the application: "
        f"{out!r}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: pre-existing behavior we must not regress
# ---------------------------------------------------------------------------

def test_accepts_single_content_length():
    """A single Content-Length header is the common case and must be accepted."""
    out = _run_case("single_cl")
    assert out.startswith("OK"), f"single Content-Length was rejected: {out!r}"
    assert "requestSeen=1" in out
    assert "body=Hello" in out


def test_accepts_no_content_length():
    """A GET request with no body and no Content-Length must be accepted."""
    out = _run_case("no_cl_get")
    assert out.startswith("OK"), f"no-body GET was rejected: {out!r}"
    assert "requestSeen=1" in out


def test_accepts_two_matching_content_length_headers():
    """RFC 9112 6.3 permits duplicate Content-Length headers if every value is
    identical; the parser must accept them and deliver the body unchanged."""
    out = _run_case("matching_cl")
    assert out.startswith("OK"), f"matching duplicate Content-Length was rejected: {out!r}"
    assert "requestSeen=1" in out
    assert "body=Hello" in out


def test_accepts_three_matching_content_length_headers():
    """Three identical Content-Length headers must also be accepted."""
    out = _run_case("three_cl_all_match")
    assert out.startswith("OK"), f"three matching Content-Length headers rejected: {out!r}"
    assert "body=WXYZ" in out


def test_accepts_chunked_transfer_encoding():
    """A chunked-encoded request (no Content-Length) must still be accepted."""
    out = _run_case("te_chunked")
    assert out.startswith("OK"), f"chunked TE rejected: {out!r}"
    assert "requestSeen=1" in out


def test_rejects_transfer_encoding_with_content_length():
    """The pre-existing rule that a request with both Transfer-Encoding and
    Content-Length is rejected must continue to hold (not regressed by the new
    Content-Length scan)."""
    out = _run_case("te_and_cl")
    assert out.startswith("ERROR"), f"TE+CL was accepted: {out!r}"
    assert "status=3" in out


def test_header_compiles_with_strict_warnings():
    """Repo-CI-style p2p: the modified header must compile cleanly under -Wall."""
    if DRIVER_BIN.exists():
        DRIVER_BIN.unlink()
    _ensure_driver_src()
    proc = subprocess.run(
        [
            "g++",
            "-std=c++20",
            "-O0",
            "-Wall",
            "-Wno-unused-parameter",
            "-Wno-unused-variable",
            f"-I{HEADER_DIR}",
            "-fsyntax-only",
            str(DRIVER_SRC),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"strict-warnings compile failed:\n"
        f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
    )
