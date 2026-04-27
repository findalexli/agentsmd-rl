"""Tests for selenium PR #17257: OSGI-friendly Read.resourceAsString overload.

Strategy: Read.java has no Selenium-specific dependencies, so we compile it
standalone with javac and exercise it from small inline Java helper programs.
The 2-arg overload `resourceAsString(Class, String)` is the substantive
addition and is verified by reflection + classloader behaviour.
"""

import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/workspace/selenium"
JAVA_SRC = f"{REPO}/java/src"
JAVA_TEST = f"{REPO}/java/test"

LIBS = "/opt/libs"
JUNIT_JAR = f"{LIBS}/junit-platform-console-standalone.jar"
ASSERTJ_JAR = f"{LIBS}/assertj-core.jar"

TEST_RESOURCES = "/workspace/test-resources"

BUILD = "/tmp/seltask-build"
EXTRA_CL = "/tmp/seltask-extracl"


def setup_module(_module):
    """Compile Read.java once at the start of the test module."""
    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD, exist_ok=True)

    if os.path.isdir(EXTRA_CL):
        shutil.rmtree(EXTRA_CL)
    os.makedirs(EXTRA_CL, exist_ok=True)

    r = subprocess.run(
        [
            "javac",
            "-d",
            BUILD,
            f"{JAVA_SRC}/org/openqa/selenium/io/Read.java",
        ],
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        "Read.java did not compile (this means the agent's edit broke "
        f"the file):\n{r.stderr.decode()}"
    )


def _compile_and_run(java_src: str, mainclass: str, runtime_cp: str = "",
                     extra_compile_cp: str = "", timeout: int = 60):
    """Write java_src to a temp dir, compile against BUILD, run, return CompletedProcess.

    Returns a tuple (compile_proc, run_proc). run_proc is None if compile failed.
    """
    tdir = tempfile.mkdtemp(prefix="seltask_")
    src_path = os.path.join(tdir, f"{mainclass}.java")
    Path(src_path).write_text(java_src)

    compile_cp = BUILD if not extra_compile_cp else f"{BUILD}:{extra_compile_cp}"
    compile_proc = subprocess.run(
        ["javac", "-cp", compile_cp, "-d", tdir, src_path],
        capture_output=True,
        timeout=timeout,
    )
    if compile_proc.returncode != 0:
        return compile_proc, None

    full_cp = f"{BUILD}:{tdir}"
    if runtime_cp:
        full_cp = f"{full_cp}:{runtime_cp}"
    run_proc = subprocess.run(
        ["java", "-cp", full_cp, mainclass],
        capture_output=True,
        timeout=timeout,
    )
    return compile_proc, run_proc


# ----------------------------- pass-to-pass -----------------------------

def test_to_byte_array_basic():
    """p2p: Read.toByteArray returns the input bytes unchanged."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        import java.io.ByteArrayInputStream;
        import java.nio.charset.StandardCharsets;

        public class CheckBytes {
            public static void main(String[] args) throws Exception {
                byte[] in = "Hello, world".getBytes(StandardCharsets.UTF_8);
                byte[] out = Read.toByteArray(new ByteArrayInputStream(in));
                if (in.length != out.length) {
                    System.out.println("LENGTH_MISMATCH:" + in.length + "/" + out.length);
                    System.exit(2);
                }
                for (int i = 0; i < in.length; i++) {
                    if (in[i] != out[i]) {
                        System.out.println("BYTE_MISMATCH:" + i);
                        System.exit(3);
                    }
                }
                System.out.println("OK");
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckBytes")
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"run failed: stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout


def test_to_string_basic():
    """p2p: Read.toString round-trips a UTF-8 byte stream."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        import java.io.ByteArrayInputStream;
        import java.nio.charset.StandardCharsets;

        public class CheckString {
            public static void main(String[] args) throws Exception {
                String input = "héllo, wörld";
                byte[] bytes = input.getBytes(StandardCharsets.UTF_8);
                String result = Read.toString(new ByteArrayInputStream(bytes));
                if (!input.equals(result)) {
                    System.out.println("MISMATCH:" + result);
                    System.exit(2);
                }
                System.out.println("OK");
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckString")
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0
    assert b"OK" in rp.stdout


def test_one_arg_resource_as_string_still_works():
    """p2p: backward compat — the original 1-arg resourceAsString still
    loads a resource via Read's classloader."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;

        public class CheckOneArg {
            public static void main(String[] args) throws Exception {
                String s = Read.resourceAsString("/org/openqa/selenium/remote/isDisplayed.js");
                if (s == null || s.isEmpty()) {
                    System.out.println("EMPTY");
                    System.exit(2);
                }
                if (!s.contains("function(){")) {
                    System.out.println("WRONG_CONTENT:" + s);
                    System.exit(3);
                }
                System.out.println("OK");
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckOneArg", runtime_cp=TEST_RESOURCES)
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout


def test_upstream_read_test_passes():
    """p2p: the upstream JUnit ReadTest passes (planted resource fixture)."""
    cp_compile = (
        f"{BUILD}:{JUNIT_JAR}:{ASSERTJ_JAR}"
    )
    test_src = f"{JAVA_TEST}/org/openqa/selenium/io/ReadTest.java"
    tdir = tempfile.mkdtemp(prefix="seltask_junit_")
    cr = subprocess.run(
        ["javac", "-cp", cp_compile, "-d", tdir, test_src],
        capture_output=True,
        timeout=120,
    )
    assert cr.returncode == 0, (
        f"ReadTest.java did not compile:\n{cr.stderr.decode()}"
    )
    full_cp = f"{BUILD}:{tdir}:{JUNIT_JAR}:{ASSERTJ_JAR}:{TEST_RESOURCES}"
    rr = subprocess.run(
        [
            "java",
            "-jar",
            JUNIT_JAR,
            "execute",
            "--class-path",
            full_cp,
            "--select-class",
            "org.openqa.selenium.io.ReadTest",
            "--fail-if-no-tests",
            "--disable-banner",
        ],
        capture_output=True,
        timeout=180,
    )
    assert rr.returncode == 0, (
        f"upstream JUnit run failed:\n"
        f"stdout:\n{rr.stdout.decode()}\nstderr:\n{rr.stderr.decode()}"
    )


# ----------------------------- fail-to-pass -----------------------------

def test_two_arg_overload_compiles():
    """f2p: A caller that uses Read.resourceAsString(Class, String) compiles
    only when the new overload exists on Read."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        public class CheckTwoArgCompile {
            public static void main(String[] args) {
                // Compilation alone fails on base where the overload doesn't exist.
                String s = Read.resourceAsString(
                    CheckTwoArgCompile.class,
                    "/org/openqa/selenium/remote/isDisplayed.js");
                System.out.println(s == null ? "NULL" : "STR_LEN_" + s.length());
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckTwoArgCompile",
                              runtime_cp=TEST_RESOURCES)
    assert cp.returncode == 0, (
        "The 2-arg overload Read.resourceAsString(Class, String) is missing "
        "from Read.java — compilation failed:\n" + cp.stderr.decode()
    )
    assert rp is not None and rp.returncode == 0, (
        f"runtime failure: stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"STR_LEN_" in rp.stdout


def test_two_arg_returns_resource_content():
    """f2p: the new overload returns the resource content correctly."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        public class CheckTwoArgContent {
            public static void main(String[] args) {
                String s = Read.resourceAsString(
                    Read.class,
                    "/org/openqa/selenium/remote/isDisplayed.js");
                if (s == null || s.isEmpty()) {
                    System.out.println("EMPTY");
                    System.exit(2);
                }
                if (!s.contains("function(){")) {
                    System.out.println("WRONG:" + s);
                    System.exit(3);
                }
                System.out.println("OK");
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckTwoArgContent",
                              runtime_cp=TEST_RESOURCES)
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout


def test_two_arg_uses_provided_class_classloader():
    """f2p: the new overload must resolve resources via the *provided* class's
    ClassLoader, not Read's. Simulates the OSGI scenario.

    We build a separate URLClassLoader at /tmp/seltask-extracl/ that contains:
      - Probe.class (compiled there only)
      - /myresource.txt   (a sibling resource at that classloader's root)

    /tmp/seltask-extracl/ is *not* on Read's (system) classpath, so a broken
    impl that delegates to Read.class.getResourceAsStream cannot find the
    resource.
    """
    # 1. Compile Probe.java only into the extra classloader's directory.
    probe_src = textwrap.dedent("""
        public class Probe { }
    """)
    probe_path = os.path.join(EXTRA_CL, "Probe.java")
    Path(probe_path).write_text(probe_src)
    cr = subprocess.run(
        ["javac", "-d", EXTRA_CL, probe_path],
        capture_output=True, timeout=60,
    )
    assert cr.returncode == 0, cr.stderr.decode()

    # 2. Plant a resource only visible to the extra classloader.
    Path(os.path.join(EXTRA_CL, "myresource.txt")).write_text(
        "RESOURCE-FROM-EXTRA-CLASSLOADER"
    )

    # 3. Driver program that loads Probe via its own URLClassLoader, then
    #    asks Read to read the sibling resource using Probe.class.
    src = textwrap.dedent("""
        import java.io.File;
        import java.net.URL;
        import java.net.URLClassLoader;
        import org.openqa.selenium.io.Read;

        public class CheckClassloader {
            public static void main(String[] args) throws Exception {
                File dir = new File("__EXTRA_CL__");
                URL[] urls = new URL[] { dir.toURI().toURL() };
                URLClassLoader extra = new URLClassLoader(urls,
                    ClassLoader.getSystemClassLoader().getParent());
                Class<?> probe = Class.forName("Probe", false, extra);

                if (probe.getClassLoader() != extra) {
                    System.out.println("WRONG_CL:" + probe.getClassLoader());
                    System.exit(2);
                }

                String s = Read.resourceAsString(probe, "/myresource.txt");
                if (!"RESOURCE-FROM-EXTRA-CLASSLOADER".equals(s)) {
                    System.out.println("WRONG_CONTENT:" + s);
                    System.exit(3);
                }
                System.out.println("OK");
            }
        }
    """).replace("__EXTRA_CL__", EXTRA_CL)

    cp, rp = _compile_and_run(src, "CheckClassloader")
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"The 2-arg overload did not load the resource via the provided "
        f"class's ClassLoader (OSGI scenario). "
        f"stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout


def test_two_arg_null_class_throws_npe():
    """f2p: a null `resourceOwner` argument must raise NullPointerException
    with a message identifying the parameter as the class owning the resource."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        import java.lang.reflect.InvocationTargetException;
        import java.lang.reflect.Method;

        public class CheckNullClass {
            public static void main(String[] args) throws Exception {
                Method m = Read.class.getMethod(
                    "resourceAsString", Class.class, String.class);
                try {
                    m.invoke(null, (Object) null, "/foo");
                    System.out.println("NO_THROW");
                    System.exit(2);
                } catch (InvocationTargetException ite) {
                    Throwable cause = ite.getCause();
                    if (!(cause instanceof NullPointerException)) {
                        System.out.println("WRONG_TYPE:" + cause);
                        System.exit(3);
                    }
                    String msg = cause.getMessage();
                    if (msg == null || !msg.contains("Class owning the resource")) {
                        System.out.println("WRONG_MSG:" + msg);
                        System.exit(4);
                    }
                    System.out.println("OK");
                }
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckNullClass")
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"null-class behaviour wrong: stdout={rp.stdout.decode()} "
        f"stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout


def test_one_arg_method_marked_deprecated():
    """f2p: the original 1-arg method must be retained but annotated
    @Deprecated so callers receive a deprecation warning."""
    src = textwrap.dedent("""
        import org.openqa.selenium.io.Read;
        import java.lang.reflect.Method;

        public class CheckDeprecated {
            public static void main(String[] args) throws Exception {
                Method m = Read.class.getMethod("resourceAsString", String.class);
                if (!m.isAnnotationPresent(Deprecated.class)) {
                    System.out.println("NOT_DEPRECATED");
                    System.exit(2);
                }
                System.out.println("OK");
            }
        }
    """)
    cp, rp = _compile_and_run(src, "CheckDeprecated")
    assert cp.returncode == 0, cp.stderr.decode()
    assert rp is not None and rp.returncode == 0, (
        f"stdout={rp.stdout.decode()} stderr={rp.stderr.decode()}"
    )
    assert b"OK" in rp.stdout
