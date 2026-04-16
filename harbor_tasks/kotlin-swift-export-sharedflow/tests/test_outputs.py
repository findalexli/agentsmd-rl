"""Tests for Swift Export SharedFlow support.

This validates that SharedFlow and MutableSharedFlow types are properly
handled in the Swift Export functionality.
"""
import subprocess
import sys
import os

REPO = "/workspace/kotlin"

# File paths for the modified source files
KOTLIN_RUNTIME_MODULE = f"{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt"
SIR_PROTOCOL_FROM_KT = f"{REPO}/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt"
SIR_TYPE_PROVIDER = f"{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt"
TYPE_BRIDGING = f"{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt"
TYPE_NAMER = f"{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt"
SWIFT_SUPPORT = f"{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"


def test_kotlin_runtime_module_has_shared_flow_protocols():
    """Verify KotlinRuntimeModule defines SharedFlow protocol declarations."""
    content = open(KOTLIN_RUNTIME_MODULE).read()

    # Check for SharedFlow protocol
    assert "kotlinSharedFlow: SirProtocol" in content, "Missing kotlinSharedFlow protocol"
    assert 'name = "KotlinSharedFlow"' in content, "Missing KotlinSharedFlow name"

    # Check for TypedSharedFlow protocol
    assert "kotlinTypedSharedFlow: SirProtocol" in content, "Missing kotlinTypedSharedFlow protocol"
    assert 'name = "KotlinTypedSharedFlow"' in content, "Missing KotlinTypedSharedFlow name"

    # Check for TypedSharedFlowImpl struct
    assert "kotlinTypedSharedFlowImpl: SirStruct" in content, "Missing kotlinTypedSharedFlowImpl struct"
    assert '_KotlinTypedSharedFlowImpl"' in content, "Missing _KotlinTypedSharedFlowImpl name"

    # Check for MutableSharedFlow protocol
    assert "kotlinMutableSharedFlow: SirProtocol" in content, "Missing kotlinMutableSharedFlow protocol"
    assert 'name = "KotlinMutableSharedFlow"' in content, "Missing KotlinMutableSharedFlow name"

    # Check for TypedMutableSharedFlow protocol
    assert "kotlinTypedMutableSharedFlow: SirProtocol" in content, "Missing kotlinTypedMutableSharedFlow protocol"
    assert 'name = "KotlinTypedMutableSharedFlow"' in content, "Missing KotlinTypedMutableSharedFlow name"

    # Check for TypedMutableSharedFlowImpl struct
    assert "kotlinTypedMutableSharedFlowImpl: SirStruct" in content, "Missing kotlinTypedMutableSharedFlowImpl struct"
    assert '_KotlinTypedMutableSharedFlowImpl"' in content, "Missing _KotlinTypedMutableSharedFlowImpl name"


def test_sir_protocol_has_shared_flow_class_ids():
    """Verify SirProtocolFromKtSymbol has SharedFlow class ID constants."""
    content = open(SIR_PROTOCOL_FROM_KT).read()

    # Check for SharedFlow class IDs
    assert "SHARED_FLOW_CLASS_ID" in content, "Missing SHARED_FLOW_CLASS_ID"
    assert "MUTABLE_SHARED_FLOW_CLASS_ID" in content, "Missing MUTABLE_SHARED_FLOW_CLASS_ID"

    # Check the class ID strings
    assert 'ClassId.fromString("kotlinx/coroutines/flow/SharedFlow")' in content, "Missing SharedFlow class ID string"
    assert 'ClassId.fromString("kotlinx/coroutines/flow/MutableSharedFlow")' in content, "Missing MutableSharedFlow class ID string"

    # Check CLASS_IDS list includes the new ones
    assert "SHARED_FLOW_CLASS_ID, MUTABLE_SHARED_FLOW_CLASS_ID" in content, "CLASS_IDS list missing SharedFlow entries"


def test_sir_protocol_support_protocol_mapping():
    """Verify SirProtocolFromKtSymbol maps SharedFlow types to protocols."""
    content = open(SIR_PROTOCOL_FROM_KT).read()

    # Check the when clause includes SharedFlow mappings
    assert "SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinSharedFlow" in content, "Missing SharedFlow mapping"
    assert "MUTABLE_SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinMutableSharedFlow" in content, "Missing MutableSharedFlow mapping"


def test_sir_type_provider_has_shared_flow_mappings():
    """Verify SirTypeProviderImpl has SharedFlow type mappings."""
    content = open(SIR_TYPE_PROVIDER).read()

    # Check for class ID constants
    assert "SHARED_FLOW_CLASS_ID = ClassId.fromString" in content, "Missing SHARED_FLOW_CLASS_ID constant"
    assert "MUTABLE_SHARED_FLOW_CLASS_ID = ClassId.fromString" in content, "Missing MUTABLE_SHARED_FLOW_CLASS_ID constant"

    # Check FLOW_CLASS_IDS list includes the new ones
    assert "SHARED_FLOW_CLASS_ID, MUTABLE_SHARED_FLOW_CLASS_ID" in content.replace("\n", " "), "FLOW_CLASS_IDS missing SharedFlow entries"

    # Check the type mapping in SirTypedFlowType creation
    assert "SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedSharedFlow" in content, "Missing kotlinTypedSharedFlow mapping"
    assert "MUTABLE_SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlow" in content, "Missing kotlinTypedMutableSharedFlow mapping"


def test_type_bridging_has_shared_flow_bridges():
    """Verify TypeBridging maps SharedFlow types to their impl structs."""
    content = open(TYPE_BRIDGING).read()

    # Check for SharedFlow bridge mappings
    assert "kotlinTypedSharedFlow -> KotlinCoroutineSupportModule.kotlinTypedSharedFlowImpl" in content, "Missing kotlinTypedSharedFlow bridge"
    assert "kotlinTypedMutableSharedFlow -> KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlowImpl" in content, "Missing kotlinTypedMutableSharedFlow bridge"


def test_type_namer_has_shared_flow_naming():
    """Verify StandaloneSirTypeNamer names SharedFlow types correctly."""
    content = open(TYPE_NAMER).read()

    # Check for SharedFlow type naming
    assert 'kotlinTypedSharedFlow -> "kotlinx.coroutines.flow.SharedFlow' in content, "Missing SharedFlow type naming"
    assert 'kotlinTypedMutableSharedFlow -> "kotlinx.coroutines.flow.MutableSharedFlow' in content, "Missing MutableSharedFlow type naming"


def test_swift_support_has_shared_flow_protocols():
    """Verify KotlinCoroutineSupport.swift defines SharedFlow Swift protocols."""
    content = open(SWIFT_SUPPORT).read()

    # Check for KotlinSharedFlow protocol
    assert "public protocol KotlinSharedFlow: KotlinFlow" in content, "Missing KotlinSharedFlow protocol"
    assert "var replayCache" in content, "Missing replayCache in KotlinSharedFlow"

    # Check for KotlinTypedSharedFlow
    assert "public protocol KotlinTypedSharedFlow<Element>: KotlinTypedFlow" in content, "Missing KotlinTypedSharedFlow protocol"
    assert "struct _KotlinTypedSharedFlowImpl<Element>: KotlinTypedSharedFlow" in content, "Missing _KotlinTypedSharedFlowImpl"

    # Check for KotlinMutableSharedFlow
    assert "public protocol KotlinMutableSharedFlow: KotlinSharedFlow" in content, "Missing KotlinMutableSharedFlow protocol"
    assert "func emit(" in content, "Missing emit function"
    assert "func resetReplayCache()" in content, "Missing resetReplayCache function"
    assert "func tryEmit(" in content, "Missing tryEmit function"
    assert "subscriptionCount" in content, "Missing subscriptionCount property"

    # Check for KotlinTypedMutableSharedFlow
    assert "public protocol KotlinTypedMutableSharedFlow<Element>: KotlinTypedSharedFlow" in content, "Missing KotlinTypedMutableSharedFlow protocol"
    assert "struct _KotlinTypedMutableSharedFlowImpl<Element>: KotlinTypedMutableSharedFlow" in content, "Missing _KotlinTypedMutableSharedFlowImpl"

    # Check inheritance changes: KotlinStateFlow now extends KotlinSharedFlow
    assert "public protocol KotlinStateFlow: KotlinSharedFlow" in content, "KotlinStateFlow should extend KotlinSharedFlow"

    # Check KotlinTypedStateFlow now extends KotlinTypedSharedFlow
    assert "public protocol KotlinTypedStateFlow<Element>: KotlinTypedSharedFlow" in content, "KotlinTypedStateFlow should extend KotlinTypedSharedFlow"

    # Check KotlinMutableStateFlow now extends both
    assert "public protocol KotlinMutableStateFlow: KotlinStateFlow, KotlinMutableSharedFlow" in content, "KotlinMutableStateFlow should extend both"

    # Check KotlinTypedMutableStateFlow extends both
    assert "public protocol KotlinTypedMutableStateFlow<Element>: KotlinTypedStateFlow, KotlinTypedMutableSharedFlow" in content, "KotlinTypedMutableStateFlow should extend both"


def test_swift_support_has_nonmutating_setter():
    """Verify MutableStateFlow value setter is marked nonmutating."""
    content = open(SWIFT_SUPPORT).read()

    # Check for nonmutating setter in KotlinTypedMutableStateFlow
    assert "nonmutating set" in content, "Missing nonmutating setter"


def test_swift_support_has_compare_and_set():
    """Verify MutableStateFlow has compareAndSet method."""
    content = open(SWIFT_SUPPORT).read()

    # Check for compareAndSet in KotlinMutableStateFlow protocol
    assert "func compareAndSet(expect:" in content or "func compareAndSet(" in content, "Missing compareAndSet in protocol"

    # Check for compareAndSet in KotlinTypedMutableStateFlow extension
    assert "public func compareAndSet(expect:" in content or "public func compareAndSet(" in content, "Missing compareAndSet in extension"


"""
Repo CI pass-to-pass tests - these run actual commands to verify repo state.
"""


def test_git_repo_at_base_commit():
    """Verify git repo is at expected base commit or has it as ancestor (pass_to_pass)."""
    # Check if base commit is an ancestor of current HEAD (works for both NOP and Gold tests)
    r = subprocess.run(
        ["git", "-C", REPO, "merge-base", "--is-ancestor", "75e54d4c71aa279aba4cc23066beb2abda5a9e69", "HEAD"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Base commit 75e54d4c71a is not an ancestor of current HEAD"


def test_git_no_uncommitted_changes():
    """Verify no uncommitted changes in repo (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    # Should be empty (no changes)
    assert r.stdout.strip() == "", f"Repo has uncommitted changes:\n{r.stdout}"


def test_modified_files_exist():
    """Verify all modified files exist in repo (pass_to_pass)."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt",
        "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift",
    ]

    for rel_path in files_to_check:
        full_path = f"{REPO}/{rel_path}"
        r = subprocess.run(
            ["test", "-f", full_path],
            capture_output=True, timeout=30
        )
        assert r.returncode == 0, f"File does not exist: {rel_path}"


def test_kotlin_files_have_content():
    """Verify Kotlin source files have meaningful content (pass_to_pass)."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt",
    ]

    for rel_path in files_to_check:
        full_path = f"{REPO}/{rel_path}"
        # Check file has at least 100 lines (meaningful content)
        r = subprocess.run(
            ["wc", "-l", full_path],
            capture_output=True, text=True, timeout=30
        )
        assert r.returncode == 0, f"wc command failed for {rel_path}"
        line_count = int(r.stdout.strip().split()[0])
        assert line_count > 100, f"File {rel_path} has too few lines: {line_count}"


def test_swift_support_file_valid():
    """Verify Swift support file is valid Swift code (pass_to_pass)."""
    swift_file = f"{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"

    # Check file exists and has Swift content
    r = subprocess.run(
        ["head", "-5", swift_file],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Cannot read Swift file: {r.stderr}"

    # Check it contains Swift indicators
    content = r.stdout
    assert "import" in content or "protocol" in content or "class" in content or "struct" in content, \
        "Swift file missing expected content indicators"


def test_kotlin_files_syntax_valid():
    """Verify Kotlin source files have valid syntax via Python validation (pass_to_pass)."""
    validation_script = f"""
import sys
files = [
    "{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt",
    "{REPO}/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
    "{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt",
    "{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt",
    "{REPO}/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt",
]
errors = []
for f in files:
    try:
        content = open(f).read()
        if content.count("{{") != content.count("}}"):
            errors.append(f"Unbalanced braces in {{f}}")
        if content.count("(") != content.count(")"):
            errors.append(f"Unbalanced parens in {{f}}")
        if content.count("[") != content.count("]"):
            errors.append(f"Unbalanced brackets in {{f}}")
    except Exception as e:
        errors.append(f"Error reading {{f}}: {{e}}")
if errors:
    print("\\n".join(errors))
    sys.exit(1)
print("OK")
"""
    r = subprocess.run(
        ["python3", "-c", validation_script],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Kotlin syntax validation failed:\n{r.stderr or r.stdout}"


# Static tests - these read files directly (origin: static)


def test_file_syntax_valid_static():
    """Verify Kotlin source files have valid syntax by checking for balanced braces (static)."""
    files_to_check = [
        KOTLIN_RUNTIME_MODULE,
        SIR_PROTOCOL_FROM_KT,
        SIR_TYPE_PROVIDER,
        TYPE_BRIDGING,
        TYPE_NAMER,
    ]

    for filepath in files_to_check:
        content = open(filepath).read()
        # Check for balanced braces (simple heuristic)
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Unbalanced braces in {filepath}: {open_braces} vs {close_braces}"

        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"Unbalanced parens in {filepath}: {open_parens} vs {close_parens}"
