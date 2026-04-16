"""
Tests for selenium-node-command-interceptor task.
Verifies the NodeCommandInterceptor SPI feature for Selenium Grid.
"""

import subprocess
import os
import re

REPO = "/workspace/selenium"


class TestNodeCommandInterceptorInterface:
    """Tests for the NodeCommandInterceptor interface (fail_to_pass)."""

    def test_interceptor_interface_exists(self):
        """NodeCommandInterceptor.java interface file must exist."""
        interface_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java"
        )
        assert os.path.isfile(interface_path), (
            f"NodeCommandInterceptor.java not found at {interface_path}"
        )

    def test_interceptor_has_isEnabled_method(self):
        """Interface must declare isEnabled(Config) method."""
        interface_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java"
        )
        with open(interface_path, 'r') as f:
            content = f.read()

        # Check for isEnabled method signature
        assert re.search(
            r'boolean\s+isEnabled\s*\(\s*Config\s+\w+\s*\)',
            content
        ), "Interface must have isEnabled(Config config) method"

    def test_interceptor_has_initialize_method(self):
        """Interface must declare initialize(Config, EventBus) method."""
        interface_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java"
        )
        with open(interface_path, 'r') as f:
            content = f.read()

        # Check for initialize method signature
        assert re.search(
            r'void\s+initialize\s*\(\s*Config\s+\w+\s*,\s*EventBus\s+\w+\s*\)',
            content
        ), "Interface must have initialize(Config, EventBus) method"

    def test_interceptor_has_intercept_method(self):
        """Interface must declare intercept(SessionId, HttpRequest, Callable) method."""
        interface_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java"
        )
        with open(interface_path, 'r') as f:
            content = f.read()

        # Check for intercept method signature
        assert re.search(
            r'HttpResponse\s+intercept\s*\(\s*SessionId\s+\w+\s*,\s*HttpRequest\s+\w+\s*,\s*Callable<HttpResponse>\s+\w+\s*\)',
            content
        ), "Interface must have intercept(SessionId, HttpRequest, Callable<HttpResponse>) method"

    def test_interceptor_extends_closeable(self):
        """Interface must extend Closeable for resource cleanup."""
        interface_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java"
        )
        with open(interface_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'interface\s+NodeCommandInterceptor\s+extends\s+Closeable',
            content
        ), "Interface must extend Closeable"


class TestLocalNodeInterceptorSupport:
    """Tests for LocalNode interceptor support (fail_to_pass)."""

    def test_local_node_has_interceptors_field(self):
        """LocalNode must have an interceptors field."""
        local_node_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNode.java"
        )
        with open(local_node_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'private\s+final\s+List<NodeCommandInterceptor>\s+interceptors',
            content
        ), "LocalNode must have List<NodeCommandInterceptor> interceptors field"

    def test_builder_has_add_interceptor_method(self):
        """LocalNode.Builder must have addInterceptor method."""
        local_node_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNode.java"
        )
        with open(local_node_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'public\s+Builder\s+addInterceptor\s*\(\s*NodeCommandInterceptor\s+\w+\s*\)',
            content
        ), "Builder must have addInterceptor(NodeCommandInterceptor) method"

    def test_execute_with_interceptors_method_exists(self):
        """LocalNode must have executeWithInterceptors private method."""
        local_node_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNode.java"
        )
        with open(local_node_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'private\s+HttpResponse\s+executeWithInterceptors\s*\(',
            content
        ), "LocalNode must have executeWithInterceptors method"

    def test_interceptor_chaining_builds_from_last_to_first(self):
        """Interceptor chain must be built from last to first for correct ordering."""
        local_node_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNode.java"
        )
        with open(local_node_path, 'r') as f:
            content = f.read()

        # The loop should iterate in reverse order
        assert re.search(
            r'for\s*\(\s*int\s+i\s*=\s*interceptors\.size\(\)\s*-\s*1\s*;\s*i\s*>=\s*0\s*;\s*i--\s*\)',
            content
        ), "Interceptor chain must be built from last to first (reverse iteration)"


class TestLocalNodeFactoryLoadsInterceptors:
    """Tests for LocalNodeFactory interceptor loading (fail_to_pass)."""

    def test_factory_uses_service_loader(self):
        """Factory must use ServiceLoader to discover interceptors."""
        factory_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java"
        )
        with open(factory_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'ServiceLoader\.load\s*\(\s*NodeCommandInterceptor\.class\s*\)',
            content
        ), "Factory must use ServiceLoader.load(NodeCommandInterceptor.class)"

    def test_factory_calls_is_enabled(self):
        """Factory must call isEnabled before adding interceptor."""
        factory_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java"
        )
        with open(factory_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'interceptor\.isEnabled\s*\(\s*config\s*\)',
            content
        ), "Factory must call interceptor.isEnabled(config)"

    def test_factory_calls_initialize(self):
        """Factory must call initialize on enabled interceptors."""
        factory_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java"
        )
        with open(factory_path, 'r') as f:
            content = f.read()

        assert re.search(
            r'interceptor\.initialize\s*\(',
            content
        ), "Factory must call interceptor.initialize()"


class TestBuildBazelDependencies:
    """Tests for Bazel BUILD file updates (fail_to_pass)."""

    def test_grid_build_exports_interceptor(self):
        """Grid BUILD.bazel must export NodeCommandInterceptor in service_uses."""
        build_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/BUILD.bazel"
        )
        with open(build_path, 'r') as f:
            content = f.read()

        assert "org.openqa.selenium.grid.node.NodeCommandInterceptor" in content, (
            "Grid BUILD.bazel must list NodeCommandInterceptor in service_uses"
        )

    def test_node_build_has_events_dep(self):
        """Node BUILD.bazel must depend on events package."""
        build_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/BUILD.bazel"
        )
        with open(build_path, 'r') as f:
            content = f.read()

        assert "//java/src/org/openqa/selenium/events" in content, (
            "Node BUILD.bazel must depend on events package"
        )


class TestInterceptorResourceCleanup:
    """Tests for interceptor lifecycle management (fail_to_pass)."""

    def test_local_node_closes_interceptors_on_shutdown(self):
        """LocalNode shutdown hook must close all interceptors."""
        local_node_path = os.path.join(
            REPO,
            "java/src/org/openqa/selenium/grid/node/local/LocalNode.java"
        )
        with open(local_node_path, 'r') as f:
            content = f.read()

        # Check for interceptor cleanup in shutdown hook
        assert re.search(
            r'for\s*\(\s*NodeCommandInterceptor\s+interceptor\s*:\s*interceptors\s*\)',
            content
        ), "LocalNode must iterate over interceptors during shutdown"

        assert re.search(
            r'interceptor\.close\s*\(\s*\)',
            content
        ), "LocalNode must call interceptor.close() during shutdown"


class TestBazelCompilation:
    """Tests for Bazel compilation (pass_to_pass)."""

    def test_grid_node_library_compiles(self):
        """Grid node library must compile successfully."""
        result = subprocess.run(
            ["bazel", "build", "//java/src/org/openqa/selenium/grid/node:node"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO
        )
        assert result.returncode == 0, (
            f"Bazel build failed:\nSTDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )

    def test_local_node_test_compiles(self):
        """LocalNode test must compile successfully."""
        result = subprocess.run(
            ["bazel", "build", "//java/test/org/openqa/selenium/grid/node/local:LocalNodeTest"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO
        )
        assert result.returncode == 0, (
            f"Bazel build failed:\nSTDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )


class TestRepoUnitTests:
    """Tests for repo unit tests (pass_to_pass)."""

    def test_repo_local_node_unit_tests(self):
        """LocalNode unit tests pass on base commit (pass_to_pass)."""
        result = subprocess.run(
            ["bazel", "test", "//java/test/org/openqa/selenium/grid/node/local:SmallTests"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO
        )
        assert result.returncode == 0, (
            f"LocalNode unit tests failed:\nSTDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )

    def test_repo_node_unit_tests(self):
        """Node unit tests pass on base commit (pass_to_pass)."""
        result = subprocess.run(
            ["bazel", "test", "//java/test/org/openqa/selenium/grid/node:small-tests"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO
        )
        assert result.returncode == 0, (
            f"Node unit tests failed:\nSTDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )


class TestRepoBuildFiles:
    """Tests for Bazel BUILD file linting (pass_to_pass)."""

    def test_repo_buildifier_lint(self):
        """Buildifier lint check passes on modified BUILD files (pass_to_pass)."""
        result = subprocess.run(
            [
                "bazel", "run", "//:buildifier", "--",
                "--lint=warn", "-mode=check",
                "java/src/org/openqa/selenium/grid/node/BUILD.bazel",
                "java/src/org/openqa/selenium/grid/BUILD.bazel",
                "java/test/org/openqa/selenium/grid/node/local/BUILD.bazel"
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO
        )
        assert result.returncode == 0, (
            f"Buildifier lint failed:\nSTDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )
