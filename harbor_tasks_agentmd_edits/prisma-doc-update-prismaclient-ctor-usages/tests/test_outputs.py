"""
Task: prisma-doc-update-prismaclient-ctor-usages
Repo: prisma @ 76bb95b96b663cfbd622a7d1d62f78619f2cff2c
PR:   29260

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/prisma"

JS_GEN = f"{REPO}/packages/client-generator-js/src/TSClient/PrismaClient.ts"
TS_GEN = f"{REPO}/packages/client-generator-ts/src/TSClient/PrismaClient.ts"
README = f"{REPO}/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structural validity
# ---------------------------------------------------------------------------



    assert "PrismaClientClass" in js_content, \
        "client-generator-js PrismaClient.ts must contain PrismaClientClass"
    assert "getPrismaClientClassDocComment" in ts_content, \
        "client-generator-ts PrismaClient.ts must contain getPrismaClientClassDocComment"
    assert "Prisma" in readme_content, "README.md must mention Prisma"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — generator JSDoc examples
# ---------------------------------------------------------------------------


def test_generator_js_adapter_example():
    """JS generator JSDoc @example must show adapter-based PrismaClient instantiation."""
    content = Path(JS_GEN).read_text()

    assert "@example" in content, "JSDoc should contain @example"
    example_idx = content.index("@example")
    # Grab a window around the @example to find the code snippet
    example_section = content[example_idx:example_idx + 600]

    assert "adapter" in example_section, \
        "JSDoc @example should show adapter-based instantiation (e.g., adapter: new PrismaPg(...))"


def test_generator_ts_adapter_example():
    """TS generator JSDoc @example must show adapter-based PrismaClient instantiation."""
    content = Path(TS_GEN).read_text()

    assert "@example" in content, "JSDoc should contain @example"
    example_idx = content.index("@example")
    example_section = content[example_idx:example_idx + 600]

    assert "adapter" in example_section, \
        "JSDoc @example should show adapter-based instantiation (e.g., adapter: new PrismaPg(...))"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update
# ---------------------------------------------------------------------------



    marker = "Import and instantiate"
    assert marker in content, "README should have 'Import and instantiate' section"
    section_start = content.index(marker)

    # Get the introductory text before the first code block in this section
    section_text = content[section_start:section_start + 800]
    first_code_block = section_text.find("```")
    intro_text = section_text[:first_code_block] if first_code_block > 0 else section_text[:400]

    # The intro paragraph (not a footnote/note) should mention adapter requirement
    intro_lower = intro_text.lower()
    assert "adapter" in intro_lower, \
        "Instantiation section intro should mention adapter as a requirement, not just as a note"



    marker = "Import and instantiate"
    assert marker in content
    section_start = content.index(marker)
    # Look at the instantiation section (enough to cover examples)
    section_text = content[section_start:section_start + 1200]

    # Extract code blocks from this section
    code_blocks = re.findall(r"```\w*\n(.*?)```", section_text, re.DOTALL)

    for block in code_blocks:
        for line in block.strip().split("\n"):
            stripped = line.strip()
            # Bare constructor: new PrismaClient() with no arguments
            if re.search(r"new PrismaClient\(\s*\)", stripped):
                assert False, (
                    f"README should not show bare 'new PrismaClient()' without adapter "
                    f"in a code example: {stripped}"
                )
