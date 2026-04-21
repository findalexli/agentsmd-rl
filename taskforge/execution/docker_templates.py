"""Runtime template selection for imported benchmark tasks.

This is deliberately small. It should grow from observed imported tasks, not
from an up-front attempt to mirror every upstream base image.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeTemplate:
    """A minimal runtime choice for rendering taskforge Dockerfiles."""

    language: str
    image: str
    setup_packages: tuple[str, ...] = ()
    setup_commands: tuple[str, ...] = ()
    notes: str = ""


_RUNTIME_TEMPLATES: dict[str, RuntimeTemplate] = {
    "python": RuntimeTemplate("python", "python:3.11-slim"),
    "javascript": RuntimeTemplate(
        "javascript", "node:20-bookworm-slim", ("python3", "python3-pip")
    ),
    "js": RuntimeTemplate("node", "node:20-bookworm-slim", ("python3", "python3-pip")),
    "typescript": RuntimeTemplate(
        "typescript", "node:20-bookworm-slim", ("python3", "python3-pip")
    ),
    "node": RuntimeTemplate(
        "node", "node:20-bookworm-slim", ("python3", "python3-pip")
    ),
    "go": RuntimeTemplate("go", "golang:1.22-bookworm", ("python3", "python3-pip")),
    "golang": RuntimeTemplate("go", "golang:1.22-bookworm", ("python3", "python3-pip")),
    "rust": RuntimeTemplate("rust", "rust:1.84-bookworm", ("python3", "python3-pip")),
    "julia": RuntimeTemplate(
        "julia",
        "julia:1.10-bookworm",
        ("python3", "python3-pip"),
        notes="matches julia_base-style rows on Julia 1.10",
    ),
    "java": RuntimeTemplate(
        "java", "eclipse-temurin:17-jdk", ("python3", "python3-pip", "maven")
    ),
    "java11": RuntimeTemplate(
        "java",
        "maven:3.9-eclipse-temurin-11",
        ("python3", "python3-pip", "ant", "unzip"),
        notes="matches java_11-style rows that need Maven/Ant on JDK 11",
    ),
    "java17": RuntimeTemplate(
        "java",
        "maven:3.9-eclipse-temurin-17",
        ("python3", "python3-pip", "ant", "unzip"),
        notes="matches java_17-style rows that need Maven/Ant on JDK 17",
    ),
    "java21": RuntimeTemplate(
        "java",
        "maven:3.9-eclipse-temurin-21",
        ("python3", "python3-pip", "ant", "unzip"),
        notes="matches java_21-style rows that need Maven/Ant on JDK 21",
    ),
    "kotlin": RuntimeTemplate(
        "kotlin",
        "eclipse-temurin:21-jdk",
        ("python3", "python3-pip", "wget", "unzip", "zip", "maven"),
        notes="minimal JDK 21 runtime for Gradle-wrapper Kotlin tasks",
    ),
    "kotlin11": RuntimeTemplate(
        "kotlin",
        "eclipse-temurin:11-jdk",
        ("python3", "python3-pip", "wget", "unzip", "zip", "maven"),
        notes="minimal JDK 11 runtime for Gradle-wrapper Kotlin tasks",
    ),
    "kotlin21": RuntimeTemplate(
        "kotlin",
        "eclipse-temurin:21-jdk",
        ("python3", "python3-pip", "wget", "unzip", "zip", "maven"),
        notes="minimal JDK 21 runtime for Gradle-wrapper Kotlin tasks",
    ),
    "clojure": RuntimeTemplate(
        "clojure",
        "eclipse-temurin:21-jdk",
        (
            "python3",
            "python3-pip",
            "wget",
            "unzip",
            "zip",
            "rlwrap",
            "nodejs",
            "npm",
        ),
        (
            'curl -fsSL "https://download.clojure.org/install/linux-install-1.11.3.1463.sh" -o /tmp/clojure-install.sh && bash /tmp/clojure-install.sh && rm -f /tmp/clojure-install.sh',
            'curl -fsSL "https://raw.githubusercontent.com/technomancy/leiningen/2.11.2/bin/lein" -o /usr/local/bin/lein && chmod +x /usr/local/bin/lein && lein --version || true',
        ),
        "installs Clojure tools.deps and Leiningen for clojure_base-style tasks",
    ),
    "csharp": RuntimeTemplate(
        "csharp",
        "mcr.microsoft.com/dotnet/sdk:8.0",
        ("python3", "python3-pip", "pkg-config", "cmake", "libssl-dev", "zlib1g-dev"),
    ),
    "c#": RuntimeTemplate(
        "csharp",
        "mcr.microsoft.com/dotnet/sdk:8.0",
        ("python3", "python3-pip", "pkg-config", "cmake", "libssl-dev", "zlib1g-dev"),
    ),
    "dart": RuntimeTemplate(
        "dart",
        "dart:stable-sdk",
        ("python3", "python3-pip", "pkg-config", "libssl-dev"),
    ),
    "elixir": RuntimeTemplate(
        "elixir",
        "elixir:1.16",
        (
            "python3",
            "python3-pip",
            "pkg-config",
            "cmake",
            "libssl-dev",
            "zlib1g-dev",
            "libgmp-dev",
            "libffi-dev",
        ),
        ("mix local.hex --force && mix local.rebar --force",),
    ),
    "php": RuntimeTemplate(
        "php",
        "php:8.3.16",
        (
            "python3",
            "python3-pip",
            "wget",
            "unzip",
            "libgd-dev",
            "libzip-dev",
            "libgmp-dev",
            "libftp-dev",
            "libcurl4-openssl-dev",
        ),
        (
            "docker-php-ext-install gd zip gmp ftp curl pcntl",
            "curl -sS https://getcomposer.org/installer | php -- --2.2 --install-dir=/usr/local/bin --filename=composer",
        ),
        "installs PHP extensions and Composer 2.2 for php_8.3.16-style tasks",
    ),
    "c": RuntimeTemplate(
        "c",
        "ubuntu:22.04",
        ("python3", "python3-pip", "autoconf", "automake", "libtool", "pkg-config"),
    ),
    "cpp": RuntimeTemplate(
        "cpp",
        "ubuntu:22.04",
        ("python3", "python3-pip", "autoconf", "automake", "libtool", "pkg-config"),
    ),
    "c++": RuntimeTemplate(
        "cpp",
        "ubuntu:22.04",
        ("python3", "python3-pip", "autoconf", "automake", "libtool", "pkg-config"),
    ),
}


def select_runtime_template(
    language: str = "", base_image_name: str = ""
) -> RuntimeTemplate:
    """Select a conservative runtime template.

    `base_image_name` is intentionally not blindly trusted because upstream rows
    can reference local image tags such as `c:latest`. The original value should
    remain in metadata; taskforge chooses an auditable base image.
    """

    base = base_image_name.strip().lower()
    if "kotlin" in base:
        if "jdk-11" in base or "jdk_11" in base:
            return _RUNTIME_TEMPLATES["kotlin11"]
        if "jdk-21" in base or "jdk_21" in base:
            return _RUNTIME_TEMPLATES["kotlin21"]
        return _RUNTIME_TEMPLATES["kotlin"]
    if "java_11" in base or "jdk-11" in base or "jdk_11" in base:
        return _RUNTIME_TEMPLATES["java11"]
    if "java_17" in base or "jdk-17" in base or "jdk_17" in base:
        return _RUNTIME_TEMPLATES["java17"]
    if "java_21" in base or "jdk-21" in base or "jdk_21" in base:
        return _RUNTIME_TEMPLATES["java21"]

    key = (language or "").strip().lower()
    if key in _RUNTIME_TEMPLATES:
        return _RUNTIME_TEMPLATES[key]

    if "node" in base:
        return _RUNTIME_TEMPLATES["node"]
    if "python" in base:
        return _RUNTIME_TEMPLATES["python"]
    if "golang" in base or base.startswith("go"):
        return _RUNTIME_TEMPLATES["go"]
    if "rust" in base:
        return _RUNTIME_TEMPLATES["rust"]
    if "julia" in base:
        return _RUNTIME_TEMPLATES["julia"]
    if "java" in base or "jdk" in base:
        return _RUNTIME_TEMPLATES["java"]
    if "clojure" in base:
        return _RUNTIME_TEMPLATES["clojure"]
    if "csharp" in base or "dotnet" in base:
        return _RUNTIME_TEMPLATES["csharp"]
    if "dart" in base:
        return _RUNTIME_TEMPLATES["dart"]
    if "elixir" in base:
        return _RUNTIME_TEMPLATES["elixir"]
    if "php" in base:
        return _RUNTIME_TEMPLATES["php"]
    if base.startswith("c:") or base.startswith("cpp:"):
        return _RUNTIME_TEMPLATES["c"]

    return RuntimeTemplate("unknown", "ubuntu:22.04", ("python3", "python3-pip"))
