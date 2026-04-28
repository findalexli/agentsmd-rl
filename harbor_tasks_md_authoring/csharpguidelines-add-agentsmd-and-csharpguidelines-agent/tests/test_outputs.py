"""Behavioral checks for csharpguidelines-add-agentsmd-and-csharpguidelines-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/csharpguidelines")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/SKILL.md')
    assert "description: 'Apply the Aviva Solutions C# coding guidelines when writing, reviewing, or refactoring C# code. Use this skill whenever generating or evaluating C# to ensure it follows the established s" in text, "expected to find: " + "description: 'Apply the Aviva Solutions C# coding guidelines when writing, reviewing, or refactoring C# code. Use this skill whenever generating or evaluating C# to ensure it follows the established s"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/SKILL.md')
    assert '| AV1702 | Must | &#124; Language element &#124; Casing&#124; Example &#124; &#124;:--------------------&#124;:----------&#124;:-----------&#124; &#124; Namespace &#124; Pascal &#124; `Syste... |' in text, "expected to find: " + '| AV1702 | Must | &#124; Language element &#124; Casing&#124; Example &#124; &#124;:--------------------&#124;:----------&#124;:-----------&#124; &#124; Namespace &#124; Pascal &#124; `Syste... |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/SKILL.md')
    assert 'Apply these rules whenever writing or reviewing C# code. Severity: **Must** = always enforce · **Should** = follow unless there is a clear reason not to · **May** = optional good practice.' in text, "expected to find: " + 'Apply these rules whenever writing or reviewing C# code. Severity: **Must** = always enforce · **Should** = follow unless there is a clear reason not to · **May** = optional good practice.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/class-design.md')
    assert 'A class or interface should have a single purpose within the system it functions in. In general, a class either represents a primitive type like an email or ISBN number, an abstraction of some busines' in text, "expected to find: " + 'A class or interface should have a single purpose within the system it functions in. In general, a class either represents a primitive type like an email or ISBN number, an abstraction of some busines'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/class-design.md')
    assert 'Interfaces should have a name that clearly explains their purpose or role in the system. Do not combine many vaguely related members on the same interface just because they were all on the same class.' in text, "expected to find: " + 'Interfaces should have a name that clearly explains their purpose or role in the system. Do not combine many vaguely related members on the same interface just because they were all on the same class.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/class-design.md')
    assert "If you want to expose an extension point from your class, expose it as an interface rather than as a base class. You don't want to force users of that extension point to derive their implementations f" in text, "expected to find: " + "If you want to expose an extension point from your class, expose it as an interface rather than as a base class. You don't want to force users of that extension point to derive their implementations f"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/commenting.md')
    assert 'Try to focus comments on the *why* and *what* of a code block and not the *how*. Avoid explaining the statements in words, but instead help the reader understand why you chose a certain solution or al' in text, "expected to find: " + 'Try to focus comments on the *why* and *what* of a code block and not the *how*. Avoid explaining the statements in words, but instead help the reader understand why you chose a certain solution or al'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/commenting.md')
    assert 'Documenting your code allows Visual Studio, [Visual Studio Code](https://code.visualstudio.com/) or [Jetbrains Rider](https://www.jetbrains.com/rider/) to pop-up the documentation when your class is u' in text, "expected to find: " + 'Documenting your code allows Visual Studio, [Visual Studio Code](https://code.visualstudio.com/) or [Jetbrains Rider](https://www.jetbrains.com/rider/) to pop-up the documentation when your class is u'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/commenting.md')
    assert 'Annotating a block of code or some work to be done using a *TODO* or similar comment may seem a reasonable way of tracking work-to-be-done. But in reality, nobody really searches for comments like tha' in text, "expected to find: " + 'Annotating a block of code or some work to be done using a *TODO* or similar comment may seem a reasonable way of tracking work-to-be-done. But in reality, nobody really searches for comments like tha'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/framework.md')
    assert 'The `dynamic` keyword has been introduced for interop with languages where properties and methods can appear and disappear at runtime. Using it can introduce a serious performance bottleneck, because ' in text, "expected to find: " + 'The `dynamic` keyword has been introduced for interop with languages where properties and methods can appear and disappear at runtime. Using it can introduce a serious performance bottleneck, because '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/framework.md')
    assert 'For instance, use `object` instead of `Object`, `string` instead of `String`, and `int` instead of `Int32`. These aliases have been introduced to make the primitive types first class citizens of the C' in text, "expected to find: " + 'For instance, use `object` instead of `Object`, `string` instead of `String`, and `int` instead of `Int32`. These aliases have been introduced to make the primitive types first class citizens of the C'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/framework.md')
    assert 'Examples include connection strings, server addresses, etc. Use `Resources`, the `ConnectionStrings` property of the `ConfigurationManager` class, or the `Settings` class generated by Visual Studio. M' in text, "expected to find: " + 'Examples include connection strings, server addresses, etc. Use `Resources`, the `ConnectionStrings` property of the `ConfigurationManager` class, or the `Settings` class generated by Visual Studio. M'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/layout.md')
    assert '- Remove redundant parentheses in expressions if they do not clarify precedence. Add parentheses in expressions to avoid non-obvious precedence. For example, in nested conditional expressions: `overru' in text, "expected to find: " + '- Remove redundant parentheses in expressions if they do not clarify precedence. Add parentheses in expressions to avoid non-obvious precedence. For example, in nested conditional expressions: `overru'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/layout.md')
    assert 'Maintaining a common order allows other team members to find their way in your code more easily. In general, a source file should be readable from top to bottom, as if reading a book, to prevent reade' in text, "expected to find: " + 'Maintaining a common order allows other team members to find their way in your code more easily. In general, a source file should be readable from top to bottom, as if reading a book, to prevent reade'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/layout.md')
    assert '- Add an empty line between multi-line statements, between multi-line members, after the closing curly braces, between unrelated code blocks, and between the `using` statements of different root names' in text, "expected to find: " + '- Add an empty line between multi-line statements, between multi-line members, after the closing curly braces, between unrelated code blocks, and between the `using` statements of different root names'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/maintainability.md')
    assert 'See the series on optional argument corner cases by Eric Lippert (part [one](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-one), [two](https://docs.mic' in text, "expected to find: " + 'See the series on optional argument corner cases by Eric Lippert (part [one](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-one), [two](https://docs.mic'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/maintainability.md')
    assert 'The class `MyString` provides three overloads for the `IndexOf` method, but two of them simply call the one with one more parameter. Notice that the same rule applies to class constructors; implement ' in text, "expected to find: " + 'The class `MyString` provides three overloads for the `IndexOf` method, but two of them simply call the one with one more parameter. Notice that the same rule applies to class constructors; implement '[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/maintainability.md')
    assert 'A method that requires more than 7 statements is simply doing too much or has too many responsibilities. It also requires the human mind to analyze the exact statements to understand what the code is ' in text, "expected to find: " + 'A method that requires more than 7 statements is simply doing too much or has too many responsibilities. It also requires the human mind to analyze the exact statements to understand what the code is '[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/member-design.md')
    assert "If your method or local function needs a specific piece of data, define parameters as specific as that and don't take a container object instead. For instance, consider a method that needs a connectio" in text, "expected to find: " + "If your method or local function needs a specific piece of data, define parameters as specific as that and don't take a container object instead. For instance, consider a method that needs a connectio"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/member-design.md')
    assert 'Instead of using strings, integers and decimals for representing domain-specific types such as an ISBN number, an email address or amount of money, consider creating dedicated value objects that wrap ' in text, "expected to find: " + 'Instead of using strings, integers and decimals for representing domain-specific types such as an ISBN number, an email address or amount of money, consider creating dedicated value objects that wrap '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/member-design.md')
    assert 'A stateful object is an object that contains many properties and lots of behavior behind it. If you expose such an object through a static property or method of some other object, it will be very diff' in text, "expected to find: " + 'A stateful object is an object that contains many properties and lots of behavior behind it. If you expose such an object through a static property or method of some other object, it will be very diff'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/misc-design.md')
    assert 'Since LINQ queries use deferred execution, returning `query` will actually return the expression tree representing the above query. Each time the caller evaluates this result using a `foreach` loop or' in text, "expected to find: " + 'Since LINQ queries use deferred execution, returning `query` will actually return the expression tree representing the above query. Each time the caller evaluates this result using a `foreach` loop or'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/misc-design.md')
    assert 'A code base that uses return values to report success or failure tends to have nested if-statements sprinkled all over the code. Quite often, a caller forgets to check the return value anyway. Structu' in text, "expected to find: " + 'A code base that uses return values to report success or failure tends to have nested if-statements sprinkled all over the code. Quite often, a caller forgets to check the return value anyway. Structu'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/misc-design.md')
    assert 'Often an event handler is used to handle similar events from multiple senders. The sender argument is then used to get to the source of the event. Always pass a reference to the source (typically `thi' in text, "expected to find: " + 'Often an event handler is used to handle similar events from multiple senders. The sender argument is then used to get to the source of the event. Always pass a reference to the source (typically `thi'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/naming.md')
    assert '.NET developers are already accustomed to the naming patterns the framework uses, so following this same pattern helps them find their way in your classes as well. For instance, if you define a class ' in text, "expected to find: " + '.NET developers are already accustomed to the naming patterns the framework uses, so following this same pattern helps them find their way in your classes as well. For instance, if you define a class '[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/naming.md')
    assert '- Consider giving a property the same name as its type. When you have a property that is strongly typed to an enumeration, the name of the property can be the same as the name of the enumeration. For ' in text, "expected to find: " + '- Consider giving a property the same name as its type. When you have a property that is strongly typed to an enumeration, the name of the property can be the same as the name of the enumeration. For '[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/naming.md')
    assert "For example, don't use `g_` or `s_` to distinguish static from non-static fields. A method in which it is difficult to distinguish local variables from member fields is generally too big. Examples of " in text, "expected to find: " + "For example, don't use `g_` or `s_` to distinguish static from non-static fields. A method in which it is difficult to distinguish local variables from member fields is generally too big. Examples of "[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/performance.md')
    assert 'The consumption of the newer and performance related `ValueTask` and `ValueTask<T>` types is more restrictive than consuming `Task` or `Task<T>`. Starting with .NET Core 2.1 the `ValueTask<T>` is not ' in text, "expected to find: " + 'The consumption of the newer and performance related `ValueTask` and `ValueTask<T>` types is more restrictive than consuming `Task` or `Task<T>`. Starting with .NET Core 2.1 the `ValueTask<T>` is not '[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/performance.md')
    assert 'You will likely end up with a deadlock. Why? Because the `Result` property getter will block until the `async` operation has completed, but since an `async` method _could_ automatically marshal the re' in text, "expected to find: " + 'You will likely end up with a deadlock. Why? Because the `Result` property getter will block until the `async` operation has completed, but since an `async` method _could_ automatically marshal the re'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/csharp-guidelines/references/performance.md')
    assert 'When a member or local function returns an `IEnumerable<T>` or other collection class that does not expose a `Count` property, use the `Any()` extension method rather than `Count()` to determine wheth' in text, "expected to find: " + 'When a member or local function returns an `IEnumerable<T>` or other collection class that does not expose a `Count` property, use the `Any()` extension method rather than `Count()` to determine wheth'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the **dennisdoomen/CSharpGuidelines** repository — a community-maintained reference for C# coding standards covering all C# versions up to v10. The site is built with **Jekyll** (Ruby) and hos' in text, "expected to find: " + 'This is the **dennisdoomen/CSharpGuidelines** repository — a community-maintained reference for C# coding standards covering all C# versions up to v10. The site is built with **Jekyll** (Ruby) and hos'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Valid `rule_category` values: `class-design`, `member-design`, `misc`, `maintainability`, `naming-conventions`, `performance`, `dotnet-framework-usage`, `commenting`, `layout`' in text, "expected to find: " + '- Valid `rule_category` values: `class-design`, `member-design`, `misc`, `maintainability`, `naming-conventions`, `performance`, `dotnet-framework-usage`, `commenting`, `layout`'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Rule body is standard Markdown. Jekyll/Liquid template syntax (`{{ site.default_rule_prefix }}`) is used for cross-references — preserve this when editing existing rules.' in text, "expected to find: " + '- Rule body is standard Markdown. Jekyll/Liquid template syntax (`{{ site.default_rule_prefix }}`) is used for cross-references — preserve this when editing existing rules.'[:80]

