"""Behavioral checks for debbie.codes-add-unified-agent-skill-addcontent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/debbie.codes")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert 'Start the dev server, open the relevant page with `playwright-cli`, confirm the new content appears, and take a screenshot. See [references/environment.md](references/environment.md) for details.' in text, "expected to find: " + 'Start the dev server, open the relevant page with `playwright-cli`, confirm the new content appears, and take a screenshot. See [references/environment.md](references/environment.md) for details.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert 'Create in the appropriate `content/<type>/` directory with a kebab-case filename. Follow the exact frontmatter schema from the content-type reference file.' in text, "expected to find: " + 'Create in the appropriate `content/<type>/` directory with a kebab-case filename. Follow the exact frontmatter schema from the content-type reference file.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert 'Commit only the content file, push, and create a PR. Do NOT commit screenshots. See [references/environment.md](references/environment.md) for details.' in text, "expected to find: " + 'Commit only the content file, push, and create a PR. Do NOT commit screenshots. See [references/environment.md](references/environment.md) for details.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/blog.md')
    assert 'description: How I use AI agents and MCP tools to automate publishing and updating podcasts, videos, and other content on my website.' in text, "expected to find: " + 'description: How I use AI agents and MCP tools to automate publishing and updating podcasts, videos, and other content on my website.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/blog.md')
    assert 'description: A look back at 2022 — from Google interviews to being hired by Microsoft, speaking at conferences, and lots of sport.' in text, "expected to find: " + 'description: A look back at 2022 — from Google interviews to being hired by Microsoft, speaking at conferences, and lots of sport.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/blog.md')
    assert 'Extract the **complete article content** from the page — do not summarize or truncate. Convert HTML to clean markdown:' in text, "expected to find: " + 'Extract the **complete article content** from the page — do not summarize or truncate. Convert HTML to clean markdown:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'Metadata extracted from external pages (titles, descriptions, dates) may contain special characters. When using scraped values in shell commands (e.g., `git commit -m` or `gh pr create`), ensure title' in text, "expected to find: " + 'Metadata extracted from external pages (titles, descriptions, dates) may contain special characters. When using scraped values in shell commands (e.g., `git commit -m` or `gh pr create`), ensure title'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'git stash pop || { echo "git stash pop reported conflicts. Resolve them with your usual Git workflow (e.g. git status, fix files, commit) and run \'git stash drop\' if needed."; }' in text, "expected to find: " + 'git stash pop || { echo "git stash pop reported conflicts. Resolve them with your usual Git workflow (e.g. git status, fix files, commit) and run \'git stash drop\' if needed."; }'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'YouTube and other sites may show cookie consent dialogs. After the first snapshot, check for "Accept all" or similar buttons and click them before extracting metadata.' in text, "expected to find: " + 'YouTube and other sites may show cookie consent dialogs. After the first snapshot, check for "Accept all" or similar buttons and click them before extracting metadata.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/podcast.md')
    assert "description: What happens when AI comes to your web testing tool? Debbie O'Brien talks about the latest features in Playwright, including Playwright MCP." in text, "expected to find: " + "description: What happens when AI comes to your web testing tool? Debbie O'Brien talks about the latest features in Playwright, including Playwright MCP."[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/podcast.md')
    assert 'If neither method works, download the image with `curl` and ask the user to upload it manually to Cloudinary under `debbie.codes/podcasts/`.' in text, "expected to find: " + 'If neither method works, download the image with `curl` and ask the user to upload it manually to Cloudinary under `debbie.codes/podcasts/`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/podcast.md')
    assert 'image: https://res.cloudinary.com/debsobrien/image/upload/c_thumb,w_200/v1633724388/debbie.codes/podcasts/dotnet-rocks_ui02cg' in text, "expected to find: " + 'image: https://res.cloudinary.com/debsobrien/image/upload/c_thumb,w_200/v1633724388/debbie.codes/podcasts/dotnet-rocks_ui02cg'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert 'After handling cookie consent (see environment.md), take a snapshot. The initial view shows relative dates ("7 days ago"). Click the "...more" button to expand the description — this reveals the exact' in text, "expected to find: " + 'After handling cookie consent (see environment.md), take a snapshot. The initial view shows relative dates ("7 days ago"). Click the "...more" button to expand the description — this reveals the exact'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert 'description: "Learn how to supercharge your end-to-end testing strategy by combining Playwright with the Playwright MCP Server for AI-assisted workflows."' in text, "expected to find: " + 'description: "Learn how to supercharge your end-to-end testing strategy by combining Playwright with the Playwright MCP Server for AI-assisted workflows."'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert 'Check with: `grep -h "^tags:" content/videos/*.md | sed \'s/tags: \\[//;s/\\]//;s/, /\\n/g\' | sed \'s/^ *//\' | sort -u`' in text, "expected to find: " + 'Check with: `grep -h "^tags:" content/videos/*.md | sed \'s/tags: \\[//;s/\\]//;s/, /\\n/g\' | sed \'s/^ *//\' | sort -u`'[:80]

