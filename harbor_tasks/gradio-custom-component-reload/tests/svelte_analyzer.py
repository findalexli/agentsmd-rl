"""
Svelte script analyzer for verifying behavioral patterns.

This module provides utilities to parse Svelte files and verify behavioral
patterns in $effect blocks, cleanup functions, and runtime usage.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class EffectAnalysis:
    """Analysis results for a single $effect block."""
    raw_content: str
    reads_reactive_vars: bool = False
    has_early_return_guard: bool = False
    returns_cleanup: bool = False
    cleanup_calls_unmount: bool = False
    mounts_component: bool = False
    mount_var_name: Optional[str] = None


@dataclass
class SvelteAnalysis:
    """Complete analysis of a Svelte component file."""
    imports: List[str] = field(default_factory=list)
    effects: List[EffectAnalysis] = field(default_factory=list)
    runtime_type: Optional[Dict[str, Any]] = None
    has_module_level_comp_var: bool = False
    has_inspect_call: bool = False


def extract_script_content(content: str) -> str:
    """Extract the content within <script> tags."""
    match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def parse_imports(script: str) -> List[str]:
    """Parse import statements from script."""
    imports = []
    # Match: import { x, y } from "module" or import x from "module"
    pattern = r'import\s+(?:\{([^}]+)\}|(\w+))\s+from\s+["\']([^"\']+)["\']'
    for match in re.finditer(pattern, script):
        if match.group(1):  # Named imports
            names = [n.strip() for n in match.group(1).split(',')]
            imports.extend(names)
        elif match.group(2):  # Default import
            imports.append(match.group(2))
    return imports


def find_variable_declarations(script: str) -> Dict[str, str]:
    """Find module-level variable declarations and their types."""
    vars = {}
    # Match: let varName; or let varName = ...;
    pattern = r'^\s*let\s+(\w+)\s*(?:[:=]|;|$)'
    for match in re.finditer(pattern, script, re.MULTILINE):
        vars[match.group(1)] = "variable"
    return vars


def extract_effect_blocks(script: str) -> List[str]:
    """Extract $effect block contents."""
    effects = []
    # Match $effect(() => { ... }) or $effect(() => ...)
    pattern = r'\$effect\s*\(\s*\(\s*\)\s*=>\s*\{?([^}]*(?:\{[^}]*\}[^}]*)*)\}?\s*\)'
    for match in re.finditer(pattern, script, re.DOTALL):
        effects.append(match.group(1))
    return effects


def analyze_effect(effect_content: str) -> EffectAnalysis:
    """Analyze an $effect block for behavioral patterns."""
    analysis = EffectAnalysis(raw_content=effect_content)

    # Check for early return guard (if (!el || !runtime || !component) return)
    guard_pattern = r'if\s*\(\s*!\w+\s*(&&|\|\|)\s*(!\w+.*)\)\s*return'
    analysis.has_early_return_guard = bool(re.search(guard_pattern, effect_content))

    # Alternative: check for any early return with negation
    if not analysis.has_early_return_guard:
        alt_guard = r'if\s*\([^)]*!\w+[^)]*\)\s*return'
        analysis.has_early_return_guard = bool(re.search(alt_guard, effect_content))

    # Check for reactive prop reads (reading node.props.xxx)
    prop_read_pattern = r'node\.props\.(\w+)|const\s+_\w+\s*=\s*node\.props'
    analysis.reads_reactive_vars = bool(re.search(prop_read_pattern, effect_content))

    # Also check for runtime reads
    if not analysis.reads_reactive_vars:
        runtime_read = r'const\s+_\w+\s*=\s*runtime|_\w+\s*=\s*\w+.*runtime'
        analysis.reads_reactive_vars = bool(re.search(runtime_read, effect_content))

    # Check for mount call and capture variable name
    mount_pattern = r'(?:const|let)\s+(\w+)\s*=\s*(\w+)\.mount\('
    mount_match = re.search(mount_pattern, effect_content)
    if mount_match:
        analysis.mounts_component = True
        analysis.mount_var_name = mount_match.group(1)

    # Check for return statement that returns a function
    return_pattern = r'return\s*\(\s*\)\s*=>\s*\{?([^}]*)\}?'
    return_match = re.search(return_pattern, effect_content)
    if return_match:
        analysis.returns_cleanup = True
        cleanup_body = return_match.group(1)
        # Check if cleanup calls unmount on the mounted variable
        if analysis.mount_var_name:
            unmount_pattern = rf'{re.escape(analysis.mount_var_name)}\)'
            analysis.cleanup_calls_unmount = bool(re.search(unmount_pattern, cleanup_body))

    return analysis


def analyze_runtime_type(script: str) -> Optional[Dict[str, Any]]:
    """Analyze the runtime type definition for mount/unmount."""
    # Look for: let runtime = $derived(...) as { mount: ..., unmount: ... }
    runtime_pattern = r'let\s+runtime\s*=\s*\$derived\s*\([^)]*\)\s*as\s*\{([^}]+)\}'
    match = re.search(runtime_pattern, script, re.DOTALL)
    if match:
        type_body = match.group(1)
        return {
            'has_mount': 'mount' in type_body,
            'has_unmount': 'unmount' in type_body and 'umount' not in type_body.split('unmount')[0].split('mount')[-1],
            'has_umount_typo': re.search(r'\bumount\b', type_body) is not None,
            'raw': type_body
        }
    return None


def analyze_svelte_component(content: str) -> SvelteAnalysis:
    """Perform complete behavioral analysis of a Svelte component."""
    analysis = SvelteAnalysis()

    script = extract_script_content(content)
    if not script:
        return analysis

    # Parse imports
    analysis.imports = parse_imports(script)

    # Check for $inspect
    analysis.has_inspect_call = '$inspect' in script

    # Check for module-level comp variable
    vars = find_variable_declarations(script)
    analysis.has_module_level_comp_var = 'comp' in vars

    # Analyze runtime type
    analysis.runtime_type = analyze_runtime_type(script)

    # Analyze $effect blocks
    effect_blocks = extract_effect_blocks(script)
    for block in effect_blocks:
        analysis.effects.append(analyze_effect(block))

    return analysis


def verify_effect_has_cleanup_behavior(content: str) -> tuple[bool, str]:
    """
    Verify that $effect properly cleans up component on re-run.

    The behavioral requirement: when the effect re-runs (due to node/prop changes),
    it should unmount the previous component instance before mounting a new one.

    Returns: (pass, message)
    """
    analysis = analyze_svelte_component(content)

    if not analysis.effects:
        return False, "No $effect block found"

    for effect in analysis.effects:
        if not effect.mounts_component:
            continue  # Not the mounting effect

        # The effect that mounts should:
        # 1. Read reactive vars (so it re-runs when props change)
        if not effect.reads_reactive_vars:
            return False, "Effect does not read reactive props - won't re-run on prop changes"

        # 2. Return a cleanup function
        if not effect.returns_cleanup:
            return False, "Effect does not return a cleanup function"

        # 3. Cleanup should call unmount on the mounted instance
        if not effect.cleanup_calls_unmount:
            return False, "Cleanup function does not unmount the component instance"

        return True, "Effect properly mounts and returns cleanup"

    return False, "No effect found that mounts components"


def verify_effect_remounts_on_change(content: str) -> tuple[bool, str]:
    """
    Verify that effect re-mounts component when node changes.

    The behavioral requirement: the effect must re-run when the node is replaced
    during dev reload, not guard against re-mounting with a stale variable.

    Returns: (pass, message)
    """
    analysis = analyze_svelte_component(content)

    if not analysis.effects:
        return False, "No $effect block found"

    # Should NOT have module-level comp variable (prevents re-triggering)
    if analysis.has_module_level_comp_var:
        return False, "Module-level 'comp' variable prevents effect re-triggering"

    for effect in analysis.effects:
        if not effect.mounts_component:
            continue

        # Should read reactive vars to trigger re-run
        if not effect.reads_reactive_vars:
            return False, "Effect does not read reactive variables - won't re-run on changes"

        # Should have early return guard (not !comp guard)
        if not effect.has_early_return_guard:
            return False, "Effect missing proper early-return guard"

        return True, "Effect properly configured to re-mount on changes"

    return False, "No mounting effect found"


def verify_no_debug_logging(content: str) -> tuple[bool, str]:
    """Verify no debug logging calls in component."""
    if '$inspect' in content:
        return False, "$inspect debug call present"
    return True, "No debug logging found"


def verify_unmount_spelling(content: str) -> tuple[bool, str]:
    """
    Verify correct spelling of unmount in runtime type.

    The behavioral requirement: the runtime type must have 'unmount' not 'umount'.
    """
    analysis = analyze_svelte_component(content)

    if not analysis.runtime_type:
        return False, "Could not find runtime type definition"

    if analysis.runtime_type.get('has_umount_typo'):
        return False, "'umount' typo found in runtime type"

    if not analysis.runtime_type.get('has_unmount'):
        return False, "'unmount' not found in runtime type"

    return True, "Runtime type has correct 'unmount' spelling"
