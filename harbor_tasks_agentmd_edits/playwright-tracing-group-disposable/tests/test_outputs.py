import subprocess
import json
import sys
from pathlib import Path
import re

# The repository path inside Docker
REPO = Path("/workspace/playwright")

def test_claude_md_includes_lint_instruction():
    """CLAUDE.md must include the lint instruction as per CLAUDE.md Commit Convention section."""
    claude_md = REPO / "CLAUDE.md"
    content = claude_md.read_text()
    
    # Check that the lint instruction was added
    assert "Before committing, run `npm run flint` and fix errors." in content, \
        "CLAUDE.md must include the pre-commit lint instruction"

def test_tracing_group_returns_disposable():
    """Tracing.group() must return a Disposable that calls groupEnd() on dispose."""
    tracing_ts = REPO / "packages" / "playwright-core" / "src" / "client" / "tracing.ts"
    content = tracing_ts.read_text()
    
    # Check that DisposableStub is imported
    assert "DisposableStub" in content, \
        "tracing.ts must import DisposableStub from './disposable'"
    
    # Check that the import statement is present
    assert 'import { DisposableStub } from' in content or "import { DisposableStub } from './disposable'" in content, \
        "Must import DisposableStub from disposable module"
    
    # Check that group() returns a DisposableStub
    # The fix should return new DisposableStub(() => this.groupEnd())
    assert "new DisposableStub" in content, \
        "group() must return new DisposableStub instance"
    
    assert "this.groupEnd()" in content, \
        "DisposableStub must call this.groupEnd() on dispose"

def test_types_d_ts_updated():
    """Type definitions must show Tracing.group() returns Promise<Disposable>."""
    # Check both type definition files
    types_files = [
        REPO / "packages" / "playwright-core" / "types" / "types.d.ts",
        REPO / "packages" / "playwright-client" / "types" / "types.d.ts",
    ]
    
    for types_file in types_files:
        content = types_file.read_text()
        
        # Find the Tracing interface's group method signature
        # Look for the pattern: group(...): Promise<Disposable>;
        pattern = r'group\s*\([^)]*\)\s*:\s*Promise<Disposable>'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match is not None, \
            f"{types_file.name}: Tracing.group() must return Promise<Disposable>, not Promise<void>"

def test_documentation_updated():
    """API documentation must reflect the Disposable return type."""
    doc_file = REPO / "docs" / "src" / "api" / "class-tracing.md"
    content = doc_file.read_text()
    
    # Check that the returns line was added
    assert "returns: <[Disposable]>" in content or "- returns:" in content, \
        "Documentation must indicate that Tracing.group() returns a Disposable"
