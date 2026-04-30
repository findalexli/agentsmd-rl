"""Behavioral checks for awesome-reviewers-add-2025-ai-developer-superpower (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-reviewers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/ai-assisted-development/SKILL.md')
    assert 'AI is transforming how developers work. A large majority of developers are using or planning to use AI tools in their development process. Tools like GitHub Copilot and ChatGPT can generate code, writ' in text, "expected to find: " + 'AI is transforming how developers work. A large majority of developers are using or planning to use AI tools in their development process. Tools like GitHub Copilot and ChatGPT can generate code, writ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/ai-assisted-development/SKILL.md')
    assert '- **Validate AI Output:** Always review and test code produced by AI. Treat AI suggestions as helpful drafts, not final solutions. It’s a critical skill to critique and improve AI-generated code – add' in text, "expected to find: " + '- **Validate AI Output:** Always review and test code produced by AI. Treat AI suggestions as helpful drafts, not final solutions. It’s a critical skill to critique and improve AI-generated code – add'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/ai-assisted-development/SKILL.md')
    assert '- **Stay in Control:** Use AI to augment your work, not replace your thinking. Be aware of known limitations (AI might produce insecure or incorrect code). Maintain rigorous quality practices (code re' in text, "expected to find: " + '- **Stay in Control:** Use AI to augment your work, not replace your thinking. Be aware of known limitations (AI might produce insecure or incorrect code). Maintain rigorous quality practices (code re'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-readability/SKILL.md')
    assert 'Writing **clean code** is a superpower for long-term productivity. Developers should prioritize clarity and explicitness over clever brevity. Code that clearly communicates its intent is easier for te' in text, "expected to find: " + 'Writing **clean code** is a superpower for long-term productivity. Developers should prioritize clarity and explicitness over clever brevity. Code that clearly communicates its intent is easier for te'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-readability/SKILL.md')
    assert '- **Clarity Over Cleverness:** Opt for explicit and straightforward code constructs rather than implicit or overly clever ones. For instance, use clear type conversions and named constants instead of ' in text, "expected to find: " + '- **Clarity Over Cleverness:** Opt for explicit and straightforward code constructs rather than implicit or overly clever ones. For instance, use clear type conversions and named constants instead of '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-readability/SKILL.md')
    assert '- **Maintainability:** Keep code structure simple and organized. Write code in a way that reduces cognitive load on the reader – e.g. clear logic flow and consistent style. Clean, readable code is eas' in text, "expected to find: " + '- **Maintainability:** Keep code structure simple and organized. Write code in a way that reduces cognitive load on the reader – e.g. clear logic flow and consistent style. Clean, readable code is eas'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-refactoring/SKILL.md')
    assert 'Great developers continually refactor code to make it simpler and more efficient. Over time, software accumulates complexity; refactoring is the skill of untangling that complexity. By breaking down l' in text, "expected to find: " + 'Great developers continually refactor code to make it simpler and more efficient. Over time, software accumulates complexity; refactoring is the skill of untangling that complexity. By breaking down l'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-refactoring/SKILL.md')
    assert '- **Eliminate Redundancy:** Refactor to remove duplicate or convoluted code. Break down complex boolean expressions or chained operations into simpler steps. Simplifying tricky code by using clearer c' in text, "expected to find: " + '- **Eliminate Redundancy:** Refactor to remove duplicate or convoluted code. Break down complex boolean expressions or chained operations into simpler steps. Simplifying tricky code by using clearer c'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/code-refactoring/SKILL.md')
    assert '- **Simplify Complex Logic:** Reduce nesting and complexity in control flow. Apply the “exit early” principle to handle edge cases upfront and avoid deep nested `if`/`else` blocks. For example, return' in text, "expected to find: " + '- **Simplify Complex Logic:** Reduce nesting and complexity in control flow. Apply the “exit early” principle to handle edge cases upfront and avoid deep nested `if`/`else` blocks. For example, return'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/data-ml/SKILL.md')
    assert 'Software is increasingly data-driven, and developers who can handle data and ML have a strong advantage. Python’s ongoing popularity is largely due to its use in data science and machine learning. Bei' in text, "expected to find: " + 'Software is increasingly data-driven, and developers who can handle data and ML have a strong advantage. Python’s ongoing popularity is largely due to its use in data science and machine learning. Bei'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/data-ml/SKILL.md')
    assert '- **Data-Driven Decision Making:** Use data to inform development decisions. This could mean instrumenting your app with analytics (and then querying that data), or A/B testing features. A developer w' in text, "expected to find: " + '- **Data-Driven Decision Making:** Use data to inform development decisions. This could mean instrumenting your app with analytics (and then querying that data), or A/B testing features. A developer w'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/data-ml/SKILL.md')
    assert '- **Learn Data Tools:** Gain proficiency with data-focused languages and libraries. For example, Python paired with libraries such as NumPy and Pandas is extremely popular for data tasks. This enables' in text, "expected to find: " + '- **Learn Data Tools:** Gain proficiency with data-focused languages and libraries. For example, Python paired with libraries such as NumPy and Pandas is extremely popular for data tasks. This enables'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/devops-cloud/SKILL.md')
    assert 'DevOps and cloud skills combine software development with IT operations. Modern developers are expected to deploy and run their code in the cloud, using platforms like AWS, Azure, or GCP. In 2024, AWS' in text, "expected to find: " + 'DevOps and cloud skills combine software development with IT operations. Modern developers are expected to deploy and run their code in the cloud, using platforms like AWS, Azure, or GCP. In 2024, AWS'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/devops-cloud/SKILL.md')
    assert '- **CI/CD Automation:** Embrace continuous integration and deployment. Automate build, test, and deployment workflows using tools like GitHub Actions, Jenkins, or GitLab CI. Containerization (e.g. Doc' in text, "expected to find: " + '- **CI/CD Automation:** Embrace continuous integration and deployment. Automate build, test, and deployment workflows using tools like GitHub Actions, Jenkins, or GitLab CI. Containerization (e.g. Doc'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/devops-cloud/SKILL.md')
    assert '- **Cloud Platform Proficiency:** Learn to deploy and manage applications on cloud services (AWS, Azure, GCP). AWS remains hugely popular, used by over half of developers, due to its broad ecosystem. ' in text, "expected to find: " + '- **Cloud Platform Proficiency:** Learn to deploy and manage applications on cloud services (AWS, Azure, GCP). AWS remains hugely popular, used by over half of developers, due to its broad ecosystem. '[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/documentation/SKILL.md')
    assert 'Effective developers write code and documentation. This includes inline comments explaining non-obvious code and higher-level docs that describe modules and systems. Good documentation ensures that kn' in text, "expected to find: " + 'Effective developers write code and documentation. This includes inline comments explaining non-obvious code and higher-level docs that describe modules and systems. Good documentation ensures that kn'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/documentation/SKILL.md')
    assert '- **Project Documentation:** Adhere to your project’s documentation standards for things like API docs, developer guides, or maintainers lists. For instance, if contributing to an open-source project,' in text, "expected to find: " + '- **Project Documentation:** Adhere to your project’s documentation standards for things like API docs, developer guides, or maintainers lists. For instance, if contributing to an open-source project,'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/documentation/SKILL.md')
    assert '- **Comment for Clarity:** Add explanatory comments where code isn’t self-explanatory – for example, to clarify complex algorithms, workarounds, or important decisions. A brief comment can save others' in text, "expected to find: " + '- **Comment for Clarity:** Add explanatory comments where code isn’t self-explanatory – for example, to clarify complex algorithms, workarounds, or important decisions. A brief comment can save others'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/full-stack-development/SKILL.md')
    assert 'Full-stack developers can build end-to-end applications, handling both the client-side and server-side. This is the most common developer role – about one in three developers identifies as full-stack.' in text, "expected to find: " + 'Full-stack developers can build end-to-end applications, handling both the client-side and server-side. This is the most common developer role – about one in three developers identifies as full-stack.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/full-stack-development/SKILL.md')
    assert '- **Unified Tech Stack:** Leverage technologies that allow sharing code or language between client and server. For example, using Node.js for server-side enables using JavaScript/TypeScript in both fr' in text, "expected to find: " + '- **Unified Tech Stack:** Leverage technologies that allow sharing code or language between client and server. For example, using Node.js for server-side enables using JavaScript/TypeScript in both fr'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/full-stack-development/SKILL.md')
    assert '- **Integrate Databases & APIs:** Be comfortable designing database schemas and building RESTful or GraphQL APIs. Full-stack work often involves linking the UI to persistent storage and external servi' in text, "expected to find: " + '- **Integrate Databases & APIs:** Be comfortable designing database schemas and building RESTful or GraphQL APIs. Full-stack work often involves linking the UI to persistent storage and external servi'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/secure-coding/SKILL.md')
    assert 'In the age of constant cyber threats, security is everyone’s job. Developers are on the front lines of safeguarding applications, from locking down APIs to securing cloud deployments. This skill means' in text, "expected to find: " + 'In the age of constant cyber threats, security is everyone’s job. Developers are on the front lines of safeguarding applications, from locking down APIs to securing cloud deployments. This skill means'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/secure-coding/SKILL.md')
    assert '- **Cloud & API Security:** Be aware of security for the platforms you use. Protect cloud infrastructure with appropriate configurations and services and secure your APIs with authentication, authoriz' in text, "expected to find: " + '- **Cloud & API Security:** Be aware of security for the platforms you use. Protect cloud infrastructure with appropriate configurations and services and secure your APIs with authentication, authoriz'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/secure-coding/SKILL.md')
    assert '- **Follow Security Best Practices:** Adhere to well-known secure coding standards like the OWASP Top 10. Validate inputs, use proper authentication and error handling, and keep dependencies up to dat' in text, "expected to find: " + '- **Follow Security Best Practices:** Adhere to well-known secure coding standards like the OWASP Top 10. Validate inputs, use proper authentication and error handling, and keep dependencies up to dat'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/team-collaboration/SKILL.md')
    assert 'Building software is usually a team effort. Strong collaboration skills – communicating with team members, reviewing each other’s code, and following shared conventions – are essential. Many developer' in text, "expected to find: " + 'Building software is usually a team effort. Strong collaboration skills – communicating with team members, reviewing each other’s code, and following shared conventions – are essential. Many developer'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/team-collaboration/SKILL.md')
    assert '- **Code Review Mastery:** Engage in code reviews regularly. Read others’ code and provide helpful suggestions, and incorporate feedback from reviewers on your code. For example, if reviewers suggest ' in text, "expected to find: " + '- **Code Review Mastery:** Engage in code reviews regularly. Read others’ code and provide helpful suggestions, and incorporate feedback from reviewers on your code. For example, if reviewers suggest '[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/team-collaboration/SKILL.md')
    assert '- **Open Source Engagement:** Consider contributing to open-source projects or internal company repositories. This exposes you to large-scale codebases and different perspectives. It’s also a great wa' in text, "expected to find: " + '- **Open Source Engagement:** Consider contributing to open-source projects or internal company repositories. This exposes you to large-scale codebases and different perspectives. It’s also a great wa'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/testing-debugging/SKILL.md')
    assert 'Writing robust software requires verifying that it works as intended. Developers are expected to build automated tests for their code and use debugging skills to quickly isolate issues. Thorough testi' in text, "expected to find: " + 'Writing robust software requires verifying that it works as intended. Developers are expected to build automated tests for their code and use debugging skills to quickly isolate issues. Thorough testi'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/testing-debugging/SKILL.md')
    assert '- **Systematic Debugging:** When bugs arise, debug methodically. Reproduce issues in a controlled environment, use breakpoints or logging to inspect state, and bisect changes if necessary. Once fixed,' in text, "expected to find: " + '- **Systematic Debugging:** When bugs arise, debug methodically. Reproduce issues in a controlled environment, use breakpoints or logging to inspect state, and bisect changes if necessary. Once fixed,'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/testing-debugging/SKILL.md')
    assert '- **Quality Tools:** Employ linters and formatters to catch issues and enforce standards automatically. For example, use ESLint or Prettier so style issues are fixed upfront, freeing code reviews to f' in text, "expected to find: " + '- **Quality Tools:** Employ linters and formatters to catch issues and enforce standards automatically. For example, use ESLint or Prettier so style issues are fixed upfront, freeing code reviews to f'[:80]

