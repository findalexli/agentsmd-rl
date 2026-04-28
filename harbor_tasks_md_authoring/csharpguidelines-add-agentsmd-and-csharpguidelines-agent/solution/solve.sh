#!/usr/bin/env bash
set -euo pipefail

cd /workspace/csharpguidelines

# Idempotency guard
if grep -qF "description: 'Apply the Aviva Solutions C# coding guidelines when writing, revie" ".agents/skills/csharp-guidelines/SKILL.md" && grep -qF "A class or interface should have a single purpose within the system it functions" ".agents/skills/csharp-guidelines/references/class-design.md" && grep -qF "Try to focus comments on the *why* and *what* of a code block and not the *how*." ".agents/skills/csharp-guidelines/references/commenting.md" && grep -qF "The `dynamic` keyword has been introduced for interop with languages where prope" ".agents/skills/csharp-guidelines/references/framework.md" && grep -qF "- Remove redundant parentheses in expressions if they do not clarify precedence." ".agents/skills/csharp-guidelines/references/layout.md" && grep -qF "See the series on optional argument corner cases by Eric Lippert (part [one](htt" ".agents/skills/csharp-guidelines/references/maintainability.md" && grep -qF "If your method or local function needs a specific piece of data, define paramete" ".agents/skills/csharp-guidelines/references/member-design.md" && grep -qF "Since LINQ queries use deferred execution, returning `query` will actually retur" ".agents/skills/csharp-guidelines/references/misc-design.md" && grep -qF ".NET developers are already accustomed to the naming patterns the framework uses" ".agents/skills/csharp-guidelines/references/naming.md" && grep -qF "The consumption of the newer and performance related `ValueTask` and `ValueTask<" ".agents/skills/csharp-guidelines/references/performance.md" && grep -qF "This is the **dennisdoomen/CSharpGuidelines** repository \u2014 a community-maintaine" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/csharp-guidelines/SKILL.md b/.agents/skills/csharp-guidelines/SKILL.md
@@ -0,0 +1,188 @@
+﻿---
+name: csharp-guidelines
+description: 'Apply the Aviva Solutions C# coding guidelines when writing, reviewing, or refactoring C# code. Use this skill whenever generating or evaluating C# to ensure it follows the established style, design, naming, and maintainability rules.'
+---
+
+# C# Coding Guidelines
+
+Apply these rules whenever writing or reviewing C# code. Severity: **Must** = always enforce · **Should** = follow unless there is a clear reason not to · **May** = optional good practice.
+
+For detailed explanations and examples, see the reference files in `references/`.
+
+## Class Design
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1000 | Must | A class or interface should have a single purpose within the system it functions in. |
+| AV1001 | May | There should be no need to set additional properties before the object can be used for whatever purpose it was designed. |
+| AV1003 | Should | Interfaces should have a name that clearly explains their purpose or role in the system. |
+| AV1004 | May | If you want to expose an extension point from your class, expose it as an interface rather than as a base class. |
+| AV1005 | Should | Interfaces are a very effective mechanism for decoupling classes from each other: - They can prevent bidirectional as... |
+| AV1008 | May | With the exception of extension method containers, static classes very often lead to badly designed code. |
+| AV1010 | Must | Compiler warning [CS0114](https://docs.microsoft.com/en-us/dotnet/csharp/misc/cs0114) is issued when breaking [Polymo... |
+| AV1011 | Should | In other words, you should be able to pass an instance of a derived class wherever its base class is expected, withou... |
+| AV1013 | Must | Having dependencies from a base class to its sub-classes goes against proper object-oriented design and might prevent... |
+| AV1014 | Should | If you find yourself writing code like this then you might be violating the [Law of Demeter](http://en.wikipedia.org/... |
+| AV1020 | Must | This means that two classes know about each other's public members or rely on each other's internal behavior. |
+| AV1025 | Must | In general, if you find a lot of data-only classes in your code base, you probably also have a few (static) classes w... |
+| AV1026 | Must | Validate incoming arguments from public members. |
+
+→ Full details: [references/class-design.md](references/class-design.md)
+
+## Member Design
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1100 | Must | Properties should be stateless with respect to other properties, i.e. |
+| AV1105 | May | - If the work is more expensive than setting a field value. |
+| AV1110 | Must | Having properties that cannot be used at the same time typically signals a type that represents two conflicting conce... |
+| AV1115 | Must | Similarly to rule a method body should have a single responsibility. |
+| AV1125 | Should | A stateful object is an object that contains many properties and lots of behavior behind it. |
+| AV1130 | Should | You generally don't want callers to be able to change an internal collection, so don't return arrays, lists or other ... |
+| AV1135 | Must | Returning `null` can be unexpected by the caller. |
+| AV1137 | Should | If your method or local function needs a specific piece of data, define parameters as specific as that and don't take... |
+| AV1140 | May | Instead of using strings, integers and decimals for representing domain-specific types such as an ISBN number, an ema... |
+
+→ Full details: [references/member-design.md](references/member-design.md)
+
+## Miscellaneous Design
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1200 | Should | A code base that uses return values to report success or failure tends to have nested if-statements sprinkled all ove... |
+| AV1202 | Should | The message should explain the cause of the exception, and clearly describe what needs to be done to avoid the except... |
+| AV1205 | May | For example, if a method receives a `null` argument, it should throw `ArgumentNullException` instead of its base type... |
+| AV1210 | Must | Avoid swallowing errors by catching non-specific exceptions, such as `Exception`, `SystemException`, and so on, in ap... |
+| AV1215 | Should | When throwing or handling exceptions in code that uses `async`/`await` or a `Task` remember the following two rules: ... |
+| AV1220 | Must | An event that has no subscribers is `null`. |
+| AV1225 | Should | Complying with this guideline allows derived classes to handle a base class event by overriding the protected method. |
+| AV1230 | May | Consider providing events that are raised when certain properties are changed. |
+| AV1235 | Must | Often an event handler is used to handle similar events from multiple senders. |
+| AV1240 | Should | Instead of casting to and from the object type in generic types or methods, use `where` constraints or the `as` opera... |
+| AV1250 | Must | Consider the following code snippet public IEnumerable<GoldMember> GetGoldMemberCustomers() { const decimal GoldMembe... |
+| AV1251 | Must | In a class hierarchy, it is not necessary to know at which level a member is declared to use it. |
+
+→ Full details: [references/misc-design.md](references/misc-design.md)
+
+## Maintainability
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1500 | Must | A method that requires more than 7 statements is simply doing too much or has too many responsibilities. |
+| AV1501 | Must | To make a more conscious decision on which members to make available to other classes, first restrict the scope as mu... |
+| AV1502 | Should | Although a property like `customer.HasNoOrders` makes sense, avoid using it in a negative condition like this: bool h... |
+| AV1505 | May | All DLLs should be named according to the pattern *Company*.*Component*.dll where *Company* refers to your company's ... |
+| AV1506 | May | Use Pascal casing to name the file and don't use underscores. |
+| AV1507 | May | **Exception:** Nested types should be part of the same file. |
+| AV1508 | May | When using partial types and allocating a part per file, name each file after the logical part that part plays. |
+| AV1510 | May | Limit usage of fully qualified type names to prevent name clashing. |
+| AV1515 | Must | Don't use literal values, either numeric or strings, in your code, other than to define symbolic constants. |
+| AV1520 | Must | Use `var` for anonymous types (typically resulting from a LINQ query), or if the type is [evident](https://www.jetbra... |
+| AV1521 | Should | Avoid the C and Visual Basic styles where all variables have to be defined at the beginning of a block, but rather de... |
+| AV1522 | Must | Don't use confusing constructs like the one below: var result = someField = GetSomeMethod(); **Exception:** Multiple ... |
+| AV1523 | Should | Instead of: var startInfo = new ProcessStartInfo("myapp.exe"); startInfo.StandardOutput = Console.Output; startInfo.U... |
+| AV1525 | Must | It is usually bad style to compare a `bool`-type expression to `true` or `false`. |
+| AV1530 | Should | Updating the loop variable within the loop body is generally considered confusing, even more so if the loop variable ... |
+| AV1532 | Should | A method that nests loops is more difficult to understand than one with only a single loop. |
+| AV1535 | Should | Please note that this also avoids possible confusion in statements of the form: if (isActive) if (isVisible) Foo(); e... |
+| AV1536 | Must | Add a descriptive comment if the `default` block is supposed to be empty. |
+| AV1537 | Should | For example: void Foo(string answer) { if (answer == "no") { Console.WriteLine("You answered with No"); } else if (an... |
+| AV1540 | Should | One entry, one exit is a sound principle and keeps control flow readable. |
+| AV1545 | Should | Express your intentions directly. |
+| AV1546 | Must | Since .NET 6, interpolated strings are optimized at compile-time, which inlines constants and reduces memory allocati... |
+| AV1547 | Must | Consider the following example: if (member.HidesBaseClassMember && member.NodeType != NodeType.InstanceInitializer) {... |
+| AV1551 | Should | This guideline only applies to overloads that are intended to provide optional arguments. |
+| AV1553 | Must | The only valid reason for using C# 4.0's optional parameters is to replace the example from rule with a single method... |
+| AV1554 | Must | When an interface method defines an optional parameter, its default value is discarded during overload resolution unl... |
+| AV1555 | Must | C# 4.0's named arguments have been introduced to make it easier to call COM components that are known for offering ma... |
+| AV1561 | Must | To keep constructors, methods, delegates and local functions small and focused, do not use more than three parameters. |
+| AV1562 | Must | They make code less understandable and might cause people to introduce bugs. |
+| AV1564 | Should | Consider the following method signature: public Customer CreateCustomer(bool platinumLevel) { } On first sight this s... |
+| AV1568 | May | Never use a parameter as a convenient variable for storing temporary state. |
+| AV1570 | Must | If you use 'as' to safely upcast an interface reference to a certain type, always verify that the operation does not ... |
+| AV1575 | Must | Never check in code that is commented out. |
+| AV1580 | Should | Because debugger breakpoints cannot be set inside expressions, avoid overuse of nested method calls. |
+
+→ Full details: [references/maintainability.md](references/maintainability.md)
+
+## Naming Conventions
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1701 | Must | All identifiers (such as types, type members, parameters and variables) should be named using words from the American... |
+| AV1702 | Must | &#124; Language element &#124; Casing&#124; Example &#124; &#124;:--------------------&#124;:----------&#124;:-----------&#124; &#124; Namespace &#124; Pascal &#124; `Syste... |
+| AV1704 | May | In most cases they are a lazy excuse for not defining a clear and intention-revealing name. |
+| AV1705 | Must | For example, don't use `g_` or `s_` to distinguish static from non-static fields. |
+| AV1706 | Should | For example, use `ButtonOnClick` rather than `BtnOnClick`. |
+| AV1707 | Should | - Use functional names. |
+| AV1708 | Should | For example, the name IComponent uses a descriptive noun, ICustomAttributeProvider uses a noun phrase and IPersistabl... |
+| AV1709 | Should | - Always prefix type parameter names with the letter `T`. |
+| AV1710 | Must | class Employee { // Wrong! static GetEmployee() {...} DeleteEmployee() {...} // Right. |
+| AV1711 | May | .NET developers are already accustomed to the naming patterns the framework uses, so following this same pattern help... |
+| AV1712 | Must | Although technically correct, statements like the following can be confusing: bool b001 = lo == l0 ? I1 == 11 : lOl !... |
+| AV1715 | Should | - Name properties with nouns, noun phrases, or occasionally adjective phrases. |
+| AV1720 | Should | Name a method or local function using a verb like `Show` or a verb-object pair such as `ShowDialog`. |
+| AV1725 | May | For instance, the following namespaces are good examples of that guideline. |
+| AV1735 | Should | Name events with a verb or a verb phrase. |
+| AV1737 | May | For example, a close event that is raised before a window is closed would be called `Closing`, and one that is raised... |
+| AV1738 | May | It is good practice to prefix the method that handles an event with "On". |
+| AV1739 | May | If you use a lambda expression (for instance, to subscribe to an event) and the actual parameters of the event are ir... |
+| AV1745 | May | If the name of an extension method conflicts with another member or extension method, you must prefix the call with t... |
+| AV1755 | Should | The general convention for methods and local functions that return `Task` or `Task<TResult>` is to postfix them with ... |
+
+→ Full details: [references/naming.md](references/naming.md)
+
+## Performance
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV1800 | May | When a member or local function returns an `IEnumerable<T>` or other collection class that does not expose a `Count` ... |
+| AV1820 | Must | The usage of `async` won't automagically run something on a worker thread like `Task.Run` does. |
+| AV1825 | Must | If you do need to execute a CPU bound operation, use `Task.Run` to offload the work to a thread from the Thread Pool. |
+| AV1830 | Must | `await` does not block the current thread but simply instructs the compiler to generate a state-machine. |
+| AV1835 | Must | Consider the following asynchronous method: private async Task<string> GetDataAsync() { var result = await MyWebServi... |
+| AV1840 | Must | The consumption of the newer and performance related `ValueTask` and `ValueTask<T>` types is more restrictive than co... |
+
+→ Full details: [references/performance.md](references/performance.md)
+
+## Framework Usage
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV2201 | Must | For instance, use `object` instead of `Object`, `string` instead of `String`, and `int` instead of `Int32`. |
+| AV2202 | Must | Language syntax makes code more concise. |
+| AV2207 | May | Examples include connection strings, server addresses, etc. |
+| AV2210 | Must | Configure the development environment to use the highest available warning level for the C# compiler, and enable the ... |
+| AV2220 | May | Rather than: var query = from item in items where item.Length > 0 select item; prefer the use of extension methods fr... |
+| AV2221 | Should | Lambda expressions provide a more elegant alternative for anonymous methods. |
+| AV2230 | Must | The `dynamic` keyword has been introduced for interop with languages where properties and methods can appear and disa... |
+| AV2235 | Must | Using the new C# 5.0 keywords results in code that can still be read sequentially and also improves maintainability a... |
+
+→ Full details: [references/framework.md](references/framework.md)
+
+## Documentation & Comments
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV2301 | Must |  |
+| AV2305 | Should | Documenting your code allows Visual Studio, [Visual Studio Code](https://code.visualstudio.com/) or [Jetbrains Rider]... |
+| AV2306 | Should | Write the documentation of your type with other developers in mind. |
+| AV2307 | May | Following the MSDN online help style and word choice helps developers find their way through your documentation more ... |
+| AV2310 | Should | If you feel the need to explain a block of code using a comment, consider replacing that block with a method with a c... |
+| AV2316 | Must | Try to focus comments on the *why* and *what* of a code block and not the *how*. |
+| AV2318 | May | Annotating a block of code or some work to be done using a *TODO* or similar comment may seem a reasonable way of tra... |
+
+→ Full details: [references/commenting.md](references/commenting.md)
+
+## Layout
+
+| Rule | Severity | Summary |
+|------|----------|---------|
+| AV2400 | Must | - Keep the length of each line under 130 characters. |
+| AV2402 | May | // System namespaces come first. |
+| AV2406 | Must | Maintaining a common order allows other team members to find their way in your code more easily. |
+| AV2407 | Must | Regions require extra work without increasing the quality or the readability of code. |
+| AV2410 | Must | Favor expression-bodied member syntax over regular member syntax only when: - the body consists of a single statement... |
+
+→ Full details: [references/layout.md](references/layout.md)
+
diff --git a/.agents/skills/csharp-guidelines/references/class-design.md b/.agents/skills/csharp-guidelines/references/class-design.md
@@ -0,0 +1,125 @@
+﻿# Class Design (AV1000) — Detailed Reference
+
+## AV1000 — A class or interface should have a single purpose [Must]
+
+A class or interface should have a single purpose within the system it functions in. In general, a class either represents a primitive type like an email or ISBN number, an abstraction of some business concept, a plain data structure, or is responsible for orchestrating the interaction between other classes. It is never a combination of those. This rule is widely known as the [Single Responsibility Principle](https://8thlight.com/blog/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html), one of the S.O.L.I.D. principles.
+
+**Tip:** A class with the word `And` in it is an obvious violation of this rule.
+
+**Tip:** Use [Design Patterns](http://en.wikipedia.org/wiki/Design_pattern_(computer_science)) to communicate the intent of a class. If you can't assign a single design pattern to a class, chances are that it is doing more than one thing.
+
+**Note** If you create a class representing a primitive type you can greatly simplify its use by making it immutable.
+
+## AV1001 — Only create a constructor that returns a useful object [May]
+
+There should be no need to set additional properties before the object can be used for whatever purpose it was designed. However, if your constructor needs more than three parameters (which violates ), your class might have too much responsibility (and violates ).
+
+## AV1003 — An interface should be small and focused [Should]
+
+Interfaces should have a name that clearly explains their purpose or role in the system. Do not combine many vaguely related members on the same interface just because they were all on the same class. Separate the members based on the responsibility of those members, so that callers only need to call or implement the interface related to a particular task. This rule is more commonly known as the [Interface Segregation Principle](https://lostechies.com/wp-content/uploads/2011/03/pablos_solid_ebook.pdf).
+
+## AV1004 — Use an interface rather than a base class to support multiple implementations [May]
+
+If you want to expose an extension point from your class, expose it as an interface rather than as a base class. You don't want to force users of that extension point to derive their implementations from a base class that might have an undesired behavior. However, for their convenience you may implement a(n abstract) default implementation that can serve as a starting point.
+
+## AV1005 — Use an interface to decouple classes from each other [Should]
+
+Interfaces are a very effective mechanism for decoupling classes from each other:
+
+- They can prevent bidirectional associations.
+- They simplify the replacement of one implementation with another.
+- They allow the replacement of an expensive external service or resource with a temporary stub for use in a non-production environment.
+- They allow the replacement of the actual implementation with a dummy implementation or a fake object in a unit test.
+- Using a dependency injection framework you can centralize the choice of which class is used whenever a specific interface is requested.
+
+## AV1008 — Avoid static classes [May]
+
+With the exception of extension method containers, static classes very often lead to badly designed code. They are also very difficult, if not impossible, to test in isolation, unless you're willing to use some very hacky tools.
+
+**Note:** If you really need that static class, mark it as static so that the compiler can prevent instance members and instantiating your class. This relieves you of creating an explicit private constructor.
+
+## AV1010 — Don't suppress compiler warnings using the `new` keyword [Must]
+
+Compiler warning [CS0114](https://docs.microsoft.com/en-us/dotnet/csharp/misc/cs0114) is issued when breaking [Polymorphism](http://en.wikipedia.org/wiki/Polymorphism_in_object-oriented_programming), one of the most essential object-orientation principles.
+The warning goes away when you add the `new` keyword, but it keeps sub-classes difficult to understand. Consider the following two classes:
+
+	public class Book
+	{
+		public virtual void Print()
+		{
+			Console.WriteLine("Printing Book");
+		}
+	}
+
+	public class PocketBook : Book
+	{
+		public new void Print()
+		{
+			Console.WriteLine("Printing PocketBook");
+		}
+	}
+
+This will cause behavior that you would not normally expect from class hierarchies:
+
+	PocketBook pocketBook = new PocketBook();
+
+	pocketBook.Print(); // Outputs "Printing PocketBook "
+
+	((Book)pocketBook).Print(); // Outputs "Printing Book"
+
+It should not make a difference whether you call `Print()` through a reference to the base class or through the derived class.
+
+## AV1011 — It should be possible to treat a derived type as if it were a base type [Should]
+
+In other words, you should be able to pass an instance of a derived class wherever its base class is expected, without the callee knowing the derived class. A very notorious example of a violation of this rule is throwing a `NotImplementedException` when overriding methods from a base class. A less subtle example is not honoring the behavior expected by the base class.
+
+**Note:** This rule is also known as the Liskov Substitution Principle, one of the [S.O.L.I.D.](http://www.lostechies.com/blogs/chad_myers/archive/2008/03/07/pablo-s-topic-of-the-month-march-solid-principles.aspx) principles.
+
+## AV1013 — Don't refer to derived classes from the base class [Must]
+
+Having dependencies from a base class to its sub-classes goes against proper object-oriented design and might prevent other developers from adding new derived classes.
+
+## AV1014 — Avoid exposing the other objects an object depends on [Should]
+
+If you find yourself writing code like this then you might be violating the [Law of Demeter](http://en.wikipedia.org/wiki/Law_of_Demeter).
+
+	someObject.SomeProperty.GetChild().Foo()
+
+An object should not expose any other classes it depends on because callers may misuse that exposed property or method to access the object behind it. By doing so, you allow calling code to become coupled to the class you are using, and thereby limiting the chance that you can easily replace it in a future stage.
+
+**Note:** Using a class that is designed using the [Fluent Interface](http://en.wikipedia.org/wiki/Fluent_interface) pattern seems to violate this rule, but it is simply returning itself so that method chaining is allowed.
+
+**Exception:** Inversion of Control or Dependency Injection frameworks often require you to expose a dependency as a public property. As long as this property is not used for anything other than dependency injection I would not consider it a violation.
+
+## AV1020 — Avoid bidirectional dependencies [Must]
+
+This means that two classes know about each other's public members or rely on each other's internal behavior. Refactoring or replacing one of those classes requires changes on both parties and may involve a lot of unexpected work. The most obvious way of breaking that dependency is to introduce an interface for one of the classes and using Dependency Injection.
+
+**Exception:** Domain models such as defined in [Domain-Driven Design](http://domaindrivendesign.org/) tend to occasionally involve bidirectional associations that model real-life associations. In those cases, make sure they are really necessary, and if they are, keep them in.
+
+## AV1025 — Classes should have state and behavior [Must]
+
+In general, if you find a lot of data-only classes in your code base, you probably also have a few (static) classes with a lot of behavior (see ). Use the principles of object-orientation explained in this section and move the logic close to the data it applies to.
+
+**Exception:** The only exceptions to this rule are classes that are used to transfer data over a communication channel, also called [Data Transfer Objects](http://martinfowler.com/eaaCatalog/dataTransferObject.html), or a class that wraps several parameters of a method.
+
+## AV1026 — Classes should protect the consistency of their internal state [Must]
+
+Validate incoming arguments from public members. For example:
+
+	public void SetAge(int years)
+	{
+		AssertValueIsInRange(years, 0, 200, nameof(years));
+
+		this.age = years;
+	}
+
+Protect invariants on internal state. For example:
+
+	public void Render()
+	{
+		AssertNotDisposed();
+
+		// ...
+	}
+
diff --git a/.agents/skills/csharp-guidelines/references/commenting.md b/.agents/skills/csharp-guidelines/references/commenting.md
@@ -0,0 +1,30 @@
+﻿# Documentation & Comments (AV2300) — Detailed Reference
+
+## AV2301 — Write comments and documentation in US English [Must]
+
+
+
+## AV2305 — Document all `public`, `protected` and `internal` types and members [Should]
+
+Documenting your code allows Visual Studio, [Visual Studio Code](https://code.visualstudio.com/) or [Jetbrains Rider](https://www.jetbrains.com/rider/) to pop-up the documentation when your class is used somewhere else. Furthermore, by properly documenting your classes, tools can generate professionally looking class documentation.
+
+## AV2306 — Write XML documentation with other developers in mind [Should]
+
+Write the documentation of your type with other developers in mind. Assume they will not have access to the source code and try to explain how to get the most out of the functionality of your type.
+
+## AV2307 — Write MSDN-style documentation [May]
+
+Following the MSDN online help style and word choice helps developers find their way through your documentation more easily.
+
+## AV2310 — Avoid inline comments [Should]
+
+If you feel the need to explain a block of code using a comment, consider replacing that block with a method with a clear name.
+
+## AV2316 — Only write comments to explain complex algorithms or decisions [Must]
+
+Try to focus comments on the *why* and *what* of a code block and not the *how*. Avoid explaining the statements in words, but instead help the reader understand why you chose a certain solution or algorithm and what you are trying to achieve. If applicable, also mention that you chose an alternative solution because you ran into a problem with the obvious solution.
+
+## AV2318 — Don't use comments for tracking work to be done later [May]
+
+Annotating a block of code or some work to be done using a *TODO* or similar comment may seem a reasonable way of tracking work-to-be-done. But in reality, nobody really searches for comments like that. Use a work item tracking system to keep track of leftovers.
+
diff --git a/.agents/skills/csharp-guidelines/references/framework.md b/.agents/skills/csharp-guidelines/references/framework.md
@@ -0,0 +1,118 @@
+﻿# Framework Usage (AV2200) — Detailed Reference
+
+## AV2201 — Use C# type aliases instead of the types from the `System` namespace [Must]
+
+For instance, use `object` instead of `Object`, `string` instead of `String`, and `int` instead of `Int32`. These aliases have been introduced to make the primitive types first class citizens of the C# language, so use them accordingly. When referring to static members of those types, use `int.Parse()` instead of `Int32.Parse()`.
+
+**Exception:** For interop with other languages, it is custom to use the [CLS-compliant name](https://docs.microsoft.com/en-us/dotnet/standard/common-type-system) in type and member signatures, e.g. `HexToInt32Converter`, `GetUInt16`.
+
+## AV2202 — Prefer language syntax over explicit calls to underlying implementations [Must]
+
+Language syntax makes code more concise. The abstractions make later refactorings easier (and sometimes allow for extra optimizations).
+
+Prefer:
+
+	(string, int) tuple = ("", 1);
+
+rather than:
+
+	ValueTuple<string, int> tuple = new ValueTuple<string, int>("", 1);
+
+Prefer:
+
+	DateTime? startDate;
+
+rather than:
+
+	Nullable<DateTime> startDate;
+
+Prefer:
+
+	if (startDate != null) ...
+
+rather than:
+
+	if (startDate.HasValue) ...
+
+Prefer:
+
+	if (startDate > DateTime.Now) ...
+
+rather than:
+
+	if (startDate.HasValue && startDate.Value > DateTime.Now) ...
+
+Prefer:
+
+	(DateTime startTime, TimeSpan duration) tuple1 = GetTimeRange();
+	(DateTime startTime, TimeSpan duration) tuple2 = GetTimeRange();
+
+	if (tuple1 == tuple2) ...
+
+rather than:
+
+	if (tuple1.startTime == tuple2.startTime && tuple1.duration == tuple2.duration) ...
+
+## AV2207 — Don't hard-code strings that change based on the deployment [May]
+
+Examples include connection strings, server addresses, etc. Use `Resources`, the `ConnectionStrings` property of the `ConfigurationManager` class, or the `Settings` class generated by Visual Studio. Maintain the actual values into the `app.config` or `web.config` (and most definitely not in a custom configuration store).
+
+## AV2210 — Build with the highest warning level [Must]
+
+Configure the development environment to use the highest available warning level for the C# compiler, and enable the option **Treat warnings as errors**. This allows the compiler to enforce the highest possible code quality.
+
+## AV2220 — Avoid LINQ query syntax for simple expressions [May]
+
+Rather than:
+
+	var query = from item in items where item.Length > 0 select item;
+
+prefer the use of extension methods from the `System.Linq` namespace:
+
+	var query = items.Where(item => item.Length > 0);
+
+The second example is a bit less convoluted.
+
+## AV2221 — Use lambda expressions instead of anonymous methods [Should]
+
+Lambda expressions provide a more elegant alternative for anonymous methods. So instead of:
+
+	Customer customer = Array.Find(customers, delegate(Customer customer)
+	{
+		return customer.Name == "Tom";
+	});
+
+use a lambda expression:
+
+	Customer customer = Array.Find(customers, customer => customer.Name == "Tom");
+
+Or even better:
+
+	var customer = customers.FirstOrDefault(customer => customer.Name == "Tom");
+
+## AV2230 — Only use the `dynamic` keyword when talking to a dynamic object [Must]
+
+The `dynamic` keyword has been introduced for interop with languages where properties and methods can appear and disappear at runtime. Using it can introduce a serious performance bottleneck, because various compile-time checks (such as overload resolution) need to happen at runtime, again and again on each invocation. You'll get better performance using cached reflection lookups, `Activator.CreateInstance()` or pre-compiled expressions (see [here](https://andrewlock.net/benchmarking-4-reflection-methods-for-calling-a-constructor-in-dotnet/) for examples and benchmark results).
+
+While using `dynamic` may improve code readability, try to avoid it in library code (especially in hot code paths). However, keep things in perspective: we're talking microseconds here, so perhaps you'll gain more by optimizing your SQL statements first.
+
+## AV2235 — Favor `async`/`await` over `Task` continuations [Must]
+
+Using the new C# 5.0 keywords results in code that can still be read sequentially and also improves maintainability a lot, even if you need to chain multiple asynchronous operations. For example, rather than defining your method like this:
+
+	public Task<Data> GetDataAsync()
+	{
+		return MyWebService.FetchDataAsync()
+			.ContinueWith(t => new Data(t.Result));
+	}
+
+define it like this:
+
+	public async Task<Data> GetDataAsync()
+	{
+		string result = await MyWebService.FetchDataAsync();
+		return new Data(result);
+	}
+
+**Tip:** Even if you need to target .NET Framework 4.0 you can use the `async` and `await` keywords. Simply install the [Async Targeting Pack](http://www.microsoft.com/en-us/download/details.aspx?id=29576).
+
diff --git a/.agents/skills/csharp-guidelines/references/layout.md b/.agents/skills/csharp-guidelines/references/layout.md
@@ -0,0 +1,100 @@
+﻿# Layout (AV2400) — Detailed Reference
+
+## AV2400 — Use a common layout [Must]
+
+- Keep the length of each line under 130 characters.
+
+- Use an indentation of 4 spaces, and don't use tabs
+
+- Keep one space between keywords like `if` and the expression, but don't add spaces after `(` and before `)` such as: `if (condition == null)`.
+
+- Add a space around operators like `+`, `-`, `==`, etc.
+
+- Always put opening and closing curly braces on a new line.
+
+  Exception: simple properties/events without a body, such as: `public string Value { get; set; } = "default";`
+
+- Don't indent object/collection initializers and initialize each property on a new line, so use a format like this:
+
+		var dto = new ConsumerDto
+		{
+			Id = 123,
+			Name = "Microsoft",
+			PartnerShip = PartnerShip.Gold,
+			ShoppingCart =
+			{
+				["VisualStudio"] = 1
+			}
+		};
+
+- Don't indent lambda statement blocks and use a format like this:
+
+		methodThatTakesAnAction.Do(source =>
+		{
+			// do something like this
+		}
+
+- Keep expression-bodied-members on one line. Break long lines after the arrow sign, like this:
+
+		private string GetLongText =>
+			"ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC";
+
+- Put the entire LINQ statement on one line, or start each keyword at the same indentation, like this:
+
+		var query = from product in products where product.Price > 10 select product;
+
+  	or
+
+		var query =
+			from product in products
+			where product.Price > 10
+			select product;
+
+- Start the LINQ statement with all the `from` expressions and don't interweave them with restrictions.
+
+- Remove redundant parentheses in expressions if they do not clarify precedence. Add parentheses in expressions to avoid non-obvious precedence. For example, in nested conditional expressions: `overruled || (enabled && active)`, bitwise and shift operations: `foo | (bar >> size)`.
+
+- Add an empty line between multi-line statements, between multi-line members, after the closing curly braces, between unrelated code blocks, and between the `using` statements of different root namespaces.
+
+## AV2402 — Order and group namespaces according to the company [May]
+
+// System namespaces come first.
+	using System;
+	using System.Collections.Generic;
+	using System.Xml;
+
+	// Then any other namespaces in alphabetic order.
+	using AvivaSolutions.Business;
+	using AvivaSolutions.Standard;
+	using Telerik.WebControls;
+	using Telerik.Ajax;
+
+Using static directives and using alias directives should be written below regular using directives.
+Always place these directives at the top of the file, before any namespace declarations (not inside them).
+
+## AV2406 — Place members in a well-defined order [Must]
+
+Maintaining a common order allows other team members to find their way in your code more easily. In general, a source file should be readable from top to bottom, as if reading a book, to prevent readers from having to browse up and down through the code file.
+
+1. Private fields and constants
+2. Public constants
+3. Public static read-only fields
+4. Factory methods
+5. Constructors and the finalizer
+6. Events
+7. Public properties
+8. Other methods and private properties in calling order
+
+Declare local functions at the bottom of their containing method bodies (after all executable code).
+
+## AV2407 — Do not use `#region` [Must]
+
+Regions require extra work without increasing the quality or the readability of code. Instead they make code harder to view and refactor.
+
+## AV2410 — Use expression-bodied members appropriately [Must]
+
+Favor expression-bodied member syntax over regular member syntax only when:
+
+- the body consists of a single statement and
+- the body fits on a single line.
+
diff --git a/.agents/skills/csharp-guidelines/references/maintainability.md b/.agents/skills/csharp-guidelines/references/maintainability.md
@@ -0,0 +1,531 @@
+﻿# Maintainability (AV1500) — Detailed Reference
+
+## AV1500 — Methods should not exceed 7 statements [Must]
+
+A method that requires more than 7 statements is simply doing too much or has too many responsibilities. It also requires the human mind to analyze the exact statements to understand what the code is doing. Break it down into multiple small and focused methods with self-explaining names, but make sure the high-level algorithm is still clear.
+
+## AV1501 — Make all members `private` and types `internal sealed` by default [Must]
+
+To make a more conscious decision on which members to make available to other classes, first restrict the scope as much as possible. Then carefully decide what to expose as a public member or type.
+
+## AV1502 — Avoid conditions with double negatives [Should]
+
+Although a property like `customer.HasNoOrders` makes sense, avoid using it in a negative condition like this:
+
+	bool hasOrders = !customer.HasNoOrders;
+
+Double negatives are more difficult to grasp than simple expressions, and people tend to read over the double negative easily.
+
+## AV1505 — Name assemblies after their contained namespace [May]
+
+All DLLs should be named according to the pattern *Company*.*Component*.dll where *Company* refers to your company's name and *Component* contains one or more dot-separated clauses. For example `AvivaSolutions.Web.Controls.dll`.
+
+As an example, consider a group of classes organized under the namespace `AvivaSolutions.Web.Binding` exposed by a certain assembly. According to this guideline, that assembly should be called `AvivaSolutions.Web.Binding.dll`.
+
+**Exception:** If you decide to combine classes from multiple unrelated namespaces into one assembly, consider suffixing the assembly name with `Core`, but do not use that suffix in the namespaces. For instance, `AvivaSolutions.Consulting.Core.dll`.
+
+## AV1506 — Name a source file to the type it contains [May]
+
+Use Pascal casing to name the file and don't use underscores. Don't include (the number of) generic type parameters in the file name.
+
+## AV1507 — Limit the contents of a source code file to one type [May]
+
+**Exception:** Nested types should be part of the same file.
+
+**Exception:** Types that only differ by their number of generic type parameters should be part of the same file.
+
+## AV1508 — Name a source file to the logical function of the partial type [May]
+
+When using partial types and allocating a part per file, name each file after the logical part that part plays. For example:
+
+	// In MyClass.cs
+	public partial class MyClass
+	{...}
+
+	// In MyClass.Designer.cs
+	public partial class MyClass
+	{...}
+
+## AV1510 — Use `using` statements instead of fully qualified type names [May]
+
+Limit usage of fully qualified type names to prevent name clashing. For example, don't do this:
+
+	var list = new System.Collections.Generic.List<string>();
+
+Instead, do this:
+
+	using System.Collections.Generic;
+
+	var list = new List<string>();
+
+If you do need to prevent name clashing, use a `using` directive to assign an alias:
+
+	using Label = System.Web.UI.WebControls.Label;
+
+## AV1515 — Don't use "magic" numbers [Must]
+
+Don't use literal values, either numeric or strings, in your code, other than to define symbolic constants. For example:
+
+	public class Whatever
+	{
+		public static readonly Color PapayaWhip = new Color(0xFFEFD5);
+		public const int MaxNumberOfWheels = 18;
+		public const byte ReadCreateOverwriteMask = 0b0010_1100;
+	}
+
+Strings intended for logging or tracing are exempt from this rule. Literals are allowed when their meaning is clear from the context, and not subject to future changes, For example:
+
+	mean = (a + b) / 2; // okay
+	WaitMilliseconds(waitTimeInSeconds * 1000); // clear enough
+
+If the value of one constant depends on the value of another, attempt to make this explicit in the code.
+
+	public class SomeSpecialContainer
+	{
+		public const int MaxItems = 32;
+		public const int HighWaterMark = 3 * MaxItems / 4; // at 75%
+	}
+
+**Note:** An enumeration can often be used for certain types of symbolic constants.
+
+## AV1520 — Only use `var` when the type is evident [Must]
+
+Use `var` for anonymous types (typically resulting from a LINQ query), or if the type is [evident](https://www.jetbrains.com/help/resharper/2021.3/Using_var_Keyword_in_Declarations.html#use-var-when-evident-details).
+Never use `var` for [built-in types](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/built-in-types).
+
+	// Projection into anonymous type.
+	var largeOrders =
+		from order in dbContext.Orders
+		where order.Items.Count > 10 && order.TotalAmount > 1000
+		select new { order.Id, order.TotalAmount };
+
+	// Built-in types.
+	bool isValid = true;
+	string phoneNumber = "(unavailable)";
+	uint pageSize = Math.Max(itemCount, MaxPageSize);
+
+	// Types are evident.
+	var customer = new Customer();
+	var invoice = Invoice.Create(customer.Id);
+	var user = sessionCache.Resolve<User>("john.doe@mail.com");
+	var subscribers = new List<Subscriber>();
+	var summary = shoppingBasket.ToOrderSummary();
+
+	// All other cases.
+	IQueryable<Order> recentOrders = ApplyFilter(order => order.CreatedAt > DateTime.Now.AddDays(-30));
+	LoggerMessage message = Compose(context);
+	ReadOnlySpan<char> key = ExtractKeyFromPair("email=john.doe@mail.com");
+	IDictionary<Category, Product> productsPerCategory =
+		shoppingBasket.Products.ToDictionary(product => product.Category);
+
+## AV1521 — Declare and initialize variables as late as possible [Should]
+
+Avoid the C and Visual Basic styles where all variables have to be defined at the beginning of a block, but rather define and initialize each variable at the point where it is needed.
+
+## AV1522 — Assign each variable in a separate statement [Must]
+
+Don't use confusing constructs like the one below:
+
+	var result = someField = GetSomeMethod();
+
+**Exception:** Multiple assignments per statement are allowed by using out variables, is-patterns or deconstruction into tuples. Examples:
+
+	bool success = int.TryParse(text, out int result);
+
+	if ((items[0] is string text) || (items[1] is Action action))
+	{
+	}
+
+	(string name, string value) = SplitNameValuePair(text);
+
+## AV1523 — Favor object and collection initializers over separate statements [Should]
+
+Instead of:
+
+	var startInfo = new ProcessStartInfo("myapp.exe");
+	startInfo.StandardOutput = Console.Output;
+	startInfo.UseShellExecute = true;
+
+	var countries = new List();
+	countries.Add("Netherlands");
+	countries.Add("United States");
+
+	var countryLookupTable = new Dictionary<string, string>();
+	countryLookupTable.Add("NL", "Netherlands");
+	countryLookupTable.Add("US", "United States");
+
+Use [Object and Collection Initializers](http://msdn.microsoft.com/en-us/library/bb384062.aspx):
+
+	var startInfo = new ProcessStartInfo("myapp.exe")
+	{
+		StandardOutput = Console.Output,
+		UseShellExecute = true
+	};
+
+	var countries = new List { "Netherlands", "United States" };
+
+	var countryLookupTable = new Dictionary<string, string>
+	{
+		["NL"] = "Netherlands",
+		["US"] = "United States"
+	};
+
+## AV1525 — Don't make explicit comparisons to `true` or `false` [Must]
+
+It is usually bad style to compare a `bool`-type expression to `true` or `false`. For example:
+
+	while (condition == false) // wrong; bad style
+	while (condition != true) // also wrong
+	while (((condition == true) == true) == true) // where do you stop?
+	while (condition) // OK
+
+## AV1530 — Don't change a loop variable inside a `for` loop [Should]
+
+Updating the loop variable within the loop body is generally considered confusing, even more so if the loop variable is modified in more than one place.
+
+	for (int index = 0; index < 10; ++index)
+	{
+		if (someCondition)
+		{
+			index = 11; // Wrong! Use 'break' or 'continue' instead.
+		}
+	}
+
+## AV1532 — Avoid nested loops [Should]
+
+A method that nests loops is more difficult to understand than one with only a single loop. In fact, in most cases nested loops can be replaced with a much simpler LINQ query that uses the `from` keyword twice or more to *join* the data.
+
+## AV1535 — Always add a block after the keywords `if`, `else`, `do`, `while`, `for`, `foreach` and `case` [Should]
+
+Please note that this also avoids possible confusion in statements of the form:
+
+	if (isActive) if (isVisible) Foo(); else Bar(); // which 'if' goes with the 'else'?
+
+	// The right way:
+	if (isActive)
+	{
+		if (isVisible)
+		{
+			Foo();
+		}
+		else
+		{
+			Bar();
+		}
+	}
+
+## AV1536 — Always add a `default` block after the last `case` in a `switch` statement [Must]
+
+Add a descriptive comment if the `default` block is supposed to be empty. Moreover, if that block is not supposed to be reached throw an `InvalidOperationException` to detect future changes that may fall through the existing cases. This ensures better code, because all paths the code can travel have been thought about.
+
+	void Foo(string answer)
+	{
+		switch (answer)
+		{
+			case "no":
+			{
+			  Console.WriteLine("You answered with No");
+			  break;
+			}
+
+			case "yes":
+			{
+			  Console.WriteLine("You answered with Yes");
+			  break;
+			}
+
+			default:
+			{
+			  // Not supposed to end up here.
+			  throw new InvalidOperationException("Unexpected answer " + answer);
+			}
+		}
+	}
+
+## AV1537 — Finish every `if`-`else`-`if` statement with an `else` clause [Should]
+
+For example:
+
+	void Foo(string answer)
+	{
+		if (answer == "no")
+		{
+			Console.WriteLine("You answered with No");
+		}
+		else if (answer == "yes")
+		{
+			Console.WriteLine("You answered with Yes");
+		}
+		else
+		{
+			// What should happen when this point is reached? Ignored? If not,
+			// throw an InvalidOperationException.
+		}
+	}
+
+## AV1540 — Be reluctant with multiple `return` statements [Should]
+
+One entry, one exit is a sound principle and keeps control flow readable. However, if the method body is very small and complies with guideline  then multiple return statements may actually improve readability over some central boolean flag that is updated at various points.
+
+## AV1545 — Don't use an `if`-`else` construct instead of a simple (conditional) assignment [Should]
+
+Express your intentions directly. For example, rather than:
+
+	bool isPositive;
+
+	if (value > 0)
+	{
+		isPositive = true;
+	}
+	else
+	{
+		isPositive = false;
+	}
+
+write:
+
+	bool isPositive = value > 0;
+
+Or instead of:
+
+	string classification;
+
+	if (value > 0)
+	{
+		classification = "positive";
+	}
+	else
+	{
+		classification = "negative";
+	}
+
+	return classification;
+
+write:
+
+	return value > 0 ? "positive" : "negative";
+
+Or instead of:
+
+	int result;
+
+	if (offset == null)
+	{
+		result = -1;
+	}
+	else
+	{
+		result = offset.Value;
+	}
+
+	return result;
+
+write:
+
+	return offset ?? -1;
+
+Or instead of:
+
+	private DateTime? firstJobStartedAt;
+
+	public void RunJob()
+	{
+		if (firstJobStartedAt == null)
+		{
+			firstJobStartedAt = DateTime.UtcNow;
+		}
+	}
+
+write:
+
+	private DateTime? firstJobStartedAt;
+
+	public void RunJob()
+	{
+		firstJobStartedAt ??= DateTime.UtcNow;
+	}
+
+Or instead of:
+
+	if (employee.Manager != null)
+	{
+		return employee.Manager.Name;
+	}
+	else
+	{
+		return null;
+	}
+
+write:
+
+	return employee.Manager?.Name;
+
+## AV1546 — Prefer interpolated strings over concatenation or `string.Format`. [Must]
+
+Since .NET 6, interpolated strings are optimized at compile-time, which inlines constants and reduces memory allocations due to boxing and string copying.
+
+	// GOOD
+	string result = $"Welcome, {firstName} {lastName}!";
+
+	// BAD
+	string result = string.Format("Welcome, {0} {1}!", firstName, lastName);
+
+	// BAD
+	string result = "Welcome, " + firstName + " " + lastName + "!";
+
+	// BAD
+	string result = string.Concat("Welcome, ", firstName, " ", lastName, "!");
+
+## AV1547 — Encapsulate complex expressions in a property, method or local function [Must]
+
+Consider the following example:
+
+	if (member.HidesBaseClassMember && member.NodeType != NodeType.InstanceInitializer)
+	{
+		// do something
+	}
+
+In order to understand what this expression is about, you need to analyze its exact details and all of its possible outcomes. Obviously, you can add an explanatory comment on top of it, but it is much better to replace this complex expression with a clearly named method:
+
+	if (NonConstructorMemberUsesNewKeyword(member))
+	{
+		// do something
+	}
+
+	private bool NonConstructorMemberUsesNewKeyword(Member member)
+	{
+		return member.HidesBaseClassMember &&
+			member.NodeType != NodeType.InstanceInitializer;
+	}
+
+You still need to understand the expression if you are modifying it, but the calling code is now much easier to grasp.
+
+## AV1551 — Call the more overloaded method from other overloads [Should]
+
+This guideline only applies to overloads that are intended to provide optional arguments. Consider, for example, the following code snippet:
+
+	public class MyString
+	{
+		private string someText;
+
+		public int IndexOf(string phrase)
+		{
+			return IndexOf(phrase, 0);
+		}
+
+		public int IndexOf(string phrase, int startIndex)
+		{
+			return IndexOf(phrase, startIndex, someText.Length - startIndex);
+		}
+
+		public virtual int IndexOf(string phrase, int startIndex, int count)
+		{
+			return someText.IndexOf(phrase, startIndex, count);
+		}
+	}
+
+The class `MyString` provides three overloads for the `IndexOf` method, but two of them simply call the one with one more parameter. Notice that the same rule applies to class constructors; implement the most complete overload and call that one from the other overloads using the `this()` operator. Also notice that the parameters with the same name should appear in the same position in all overloads.
+
+**Important:** If you also want to allow derived classes to override these methods, define the most complete overload as a non-private `virtual` method that is called by all overloads.
+
+## AV1553 — Only use optional parameters to replace overloads [Must]
+
+The only valid reason for using C# 4.0's optional parameters is to replace the example from rule  with a single method like:
+
+	public virtual int IndexOf(string phrase, int startIndex = 0, int count = -1)
+	{
+		int length = count == -1 ? someText.Length - startIndex : count;
+		return someText.IndexOf(phrase, startIndex, length);
+	}
+
+Since strings, collections and tasks should never be `null` according to rule , if you have an optional parameter of these types with default value `null` then you must use overloaded methods instead.
+
+Strings, unlike other reference types, can have non-null default values. So an optional string parameter may be used to replace overloads with the condition of having a non-null default value.
+
+Regardless of optional parameters' types, following caveats always apply:
+
+1) The default values of the optional parameters are stored at the caller side. As such, changing the default argument without recompiling the calling code will not apply the new default value. Unless your method is private or internal, this aspect should be carefully considered before choosing optional parameters over method overloads.
+
+2) If optional parameters cause the method to follow and/or exit from alternative paths, overloaded methods are probably a better fit for your case.
+
+## AV1554 — Do not use optional parameters in interface methods or their concrete implementations [Must]
+
+When an interface method defines an optional parameter, its default value is discarded during overload resolution unless you call the concrete class through the interface reference.
+
+When a concrete implementation of an interface method sets a default argument for a parameter, the default value is discarded during overload resolution if you call the concrete class through the interface reference.
+
+See the series on optional argument corner cases by Eric Lippert (part [one](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-one), [two](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-two), [three](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-three), [four](https://docs.microsoft.com/en-us/archive/blogs/ericlippert/optional-argument-corner-cases-part-four)) for more details.
+
+## AV1555 — Avoid using named arguments [Must]
+
+C# 4.0's named arguments have been introduced to make it easier to call COM components that are known for offering many optional parameters. If you need named arguments to improve the readability of the call to a method, that method is probably doing too much and should be refactored.
+
+**Exception:** The only exception where named arguments improve readability is when calling a method of some code base you don't control that has a `bool` parameter, like this:
+
+	object[] myAttributes = type.GetCustomAttributes(typeof(MyAttribute), inherit: false);
+
+## AV1561 — Don't declare signatures with more than 3 parameters [Must]
+
+To keep constructors, methods, delegates and local functions small and focused, do not use more than three parameters. Do not use tuple parameters. Do not return tuples with more than two elements.
+
+If you want to use more parameters, use a structure or class to pass multiple arguments, as explained in the [Specification design pattern](http://en.wikipedia.org/wiki/Specification_pattern).
+In general, the fewer the parameters, the easier it is to understand the method. Additionally, unit testing a method with many parameters requires many scenarios to test.
+
+**Exception:** A parameter that is a collection of tuples is allowed.
+
+## AV1562 — Don't use `ref` or `out` parameters [Must]
+
+They make code less understandable and might cause people to introduce bugs. Instead, return compound objects or tuples.
+
+**Exception:** Calling and declaring members that implement the [TryParse](https://docs.microsoft.com/en-us/dotnet/api/system.int32.tryparse) pattern is allowed. For example:
+
+	bool success = int.TryParse(text, out int number);
+
+## AV1564 — Avoid signatures that take a `bool` parameter [Should]
+
+Consider the following method signature:
+
+	public Customer CreateCustomer(bool platinumLevel)
+	{
+	}
+
+On first sight this signature seems perfectly fine, but when calling this method you will lose this purpose completely:
+
+	Customer customer = CreateCustomer(true);
+
+Often, a method taking such a bool is doing more than one thing and needs to be refactored into two or more methods. An alternative solution is to replace the bool with an enumeration.
+
+## AV1568 — Don't use parameters as temporary variables [May]
+
+Never use a parameter as a convenient variable for storing temporary state. Even though the type of your temporary variable may be the same, the name usually does not reflect the purpose of the temporary variable.
+
+## AV1570 — Prefer `is` patterns over `as` operations [Must]
+
+If you use 'as' to safely upcast an interface reference to a certain type, always verify that the operation does not return `null`. Failure to do so may cause a `NullReferenceException` at a later stage if the object did not implement that interface.
+Pattern matching syntax prevents this and improves readability. For example, instead of:
+
+	var remoteUser = user as RemoteUser;
+	if (remoteUser != null)
+	{
+	}
+
+write:
+
+	if (user is RemoteUser remoteUser)
+	{
+	}
+
+## AV1575 — Don't comment out code [Must]
+
+Never check in code that is commented out. Instead, use a work item tracking system to keep track of some work to be done. Nobody knows what to do when they encounter a block of commented-out code. Was it temporarily disabled for testing purposes? Was it copied as an example? Should I delete it?
+
+## AV1580 — Write code that is easy to debug [Should]
+
+Because debugger breakpoints cannot be set inside expressions, avoid overuse of nested method calls. For example, a line like:
+
+	string result = ConvertToXml(ApplyTransforms(ExecuteQuery(GetConfigurationSettings(source))));
+
+requires extra steps to inspect intermediate method return values. On the other hard, were this expression broken into intermediate variables, setting a breakpoint on one of them would be sufficient.
+
+**Note** This does not apply to chaining method calls, which is a common pattern in fluent APIs.
+
diff --git a/.agents/skills/csharp-guidelines/references/member-design.md b/.agents/skills/csharp-guidelines/references/member-design.md
@@ -0,0 +1,51 @@
+﻿# Member Design (AV1100) — Detailed Reference
+
+## AV1100 — Allow properties to be set in any order [Must]
+
+Properties should be stateless with respect to other properties, i.e. there should not be a difference between first setting property `DataSource` and then `DataMember` or vice-versa.
+
+## AV1105 — Use a method instead of a property [May]
+
+- If the work is more expensive than setting a field value.
+- If it represents a conversion such as the `Object.ToString` method.
+- If it returns a different result each time it is called, even if the arguments didn't change. For example, the `NewGuid` method returns a different value each time it is called.
+- If the operation causes a side effect such as changing some internal state not directly related to the property (which violates the [Command Query Separation](http://martinfowler.com/bliki/CommandQuerySeparation.html) principle).
+
+**Exception:** Populating an internal cache or implementing [lazy-loading](http://www.martinfowler.com/eaaCatalog/lazyLoad.html) is a good exception.
+
+## AV1110 — Don't use mutually exclusive properties [Must]
+
+Having properties that cannot be used at the same time typically signals a type that represents two conflicting concepts. Even though those concepts may share some of their behavior and states, they obviously have different rules that do not cooperate.
+
+This violation is often seen in domain models and introduces all kinds of conditional logic related to those conflicting rules, causing a ripple effect that significantly increases the maintenance burden.
+
+## AV1115 — A property, method or local function should do only one thing [Must]
+
+Similarly to rule , a method body should have a single responsibility.
+
+## AV1125 — Don't expose stateful objects through static members [Should]
+
+A stateful object is an object that contains many properties and lots of behavior behind it. If you expose such an object through a static property or method of some other object, it will be very difficult to refactor or unit test a class that relies on such a stateful object. In general, introducing a construct like that is a great example of violating many of the guidelines of this chapter.
+
+A classic example of this is the `HttpContext.Current` property, part of ASP.NET. Many see the `HttpContext` class as a source of a lot of ugly code.
+
+## AV1130 — Return interfaces to unchangeable collections [Should]
+
+You generally don't want callers to be able to change an internal collection, so don't return arrays, lists or other collection classes directly. Instead, return an `IEnumerable<T>`, `IAsyncEnumerable<T>`, `IQueryable<T>`, `IReadOnlyCollection<T>`, `IReadOnlyList<T>`, `IReadOnlySet<T>` or `IReadOnlyDictionary<TKey, TValue>`.
+
+**Exception:** Immutable collections such as `ImmutableArray<T>`, `ImmutableList<T>` and `ImmutableDictionary<TKey, TValue>` prevent modifications from the outside and are thus allowed.
+
+## AV1135 — Properties, arguments and return values representing strings, collections or tasks should never be `null` [Must]
+
+Returning `null` can be unexpected by the caller. Always return an empty collection or an empty string instead of a `null` reference. When your member returns `Task` or `Task<T>`, return `Task.CompletedTask` or `Task.FromResult()`. This also prevents cluttering your code base with additional checks for `null`, or even worse, `string.IsNullOrEmpty()`.
+
+## AV1137 — Define parameters as specific as possible [Should]
+
+If your method or local function needs a specific piece of data, define parameters as specific as that and don't take a container object instead. For instance, consider a method that needs a connection string that is exposed through a central `IConfiguration` interface. Rather than taking a dependency on the entire configuration, just define a parameter for the connection string. This not only prevents unnecessary coupling, it also improves maintainability in the long run.
+
+**Note:** An easy trick to remember this guideline is the *Don't ship the truck if you only need a package*.
+
+## AV1140 — Consider using domain-specific value types rather than primitives [May]
+
+Instead of using strings, integers and decimals for representing domain-specific types such as an ISBN number, an email address or amount of money, consider creating dedicated value objects that wrap both the data and the validation rules that apply to it. By doing this, you prevent ending up having multiple implementations of the same business rules, which both improves maintainability and prevents bugs.
+
diff --git a/.agents/skills/csharp-guidelines/references/misc-design.md b/.agents/skills/csharp-guidelines/references/misc-design.md
@@ -0,0 +1,104 @@
+﻿# Miscellaneous Design (AV1200) — Detailed Reference
+
+## AV1200 — Throw exceptions rather than returning some kind of status value [Should]
+
+A code base that uses return values to report success or failure tends to have nested if-statements sprinkled all over the code. Quite often, a caller forgets to check the return value anyway. Structured exception handling has been introduced to allow you to throw exceptions and catch or replace them at a higher layer. In most systems it is quite common to throw exceptions whenever an unexpected situation occurs.
+
+## AV1202 — Provide a rich and meaningful exception message text [Should]
+
+The message should explain the cause of the exception, and clearly describe what needs to be done to avoid the exception.
+
+## AV1205 — Throw the most specific exception that is appropriate [May]
+
+For example, if a method receives a `null` argument, it should throw `ArgumentNullException` instead of its base type `ArgumentException`.
+
+## AV1210 — Don't swallow errors by catching generic exceptions [Must]
+
+Avoid swallowing errors by catching non-specific exceptions, such as `Exception`, `SystemException`, and so on, in application code. Only in top-level code, such as a last-chance exception handler, you should catch a non-specific exception for logging purposes and a graceful shutdown of the application.
+
+## AV1215 — Properly handle exceptions in asynchronous code [Should]
+
+When throwing or handling exceptions in code that uses `async`/`await` or a `Task` remember the following two rules:
+
+- Exceptions that occur within an `async`/`await` block and inside a `Task`'s action are propagated to the awaiter.
+- Exceptions that occur in the code preceding the asynchronous block are propagated to the caller.
+
+## AV1220 — Always check an event handler delegate for `null` [Must]
+
+An event that has no subscribers is `null`. So before invoking, always make sure that the delegate list represented by the event variable is not `null`.
+Invoke using the null conditional operator, because it additionally prevents conflicting changes to the delegate list from concurrent threads.
+
+	event EventHandler<NotifyEventArgs> Notify;
+
+	protected virtual void OnNotify(NotifyEventArgs args)
+	{
+		Notify?.Invoke(this, args);
+	}
+
+## AV1225 — Use a protected virtual method to raise each event [Should]
+
+Complying with this guideline allows derived classes to handle a base class event by overriding the protected method. The name of the protected virtual method should be the same as the event name prefixed with `On`. For example, the protected virtual method for an event named `TimeChanged` is named `OnTimeChanged`.
+
+**Note:** Derived classes that override the protected virtual method are not required to call the base class implementation. The base class must continue to work correctly even if its implementation is not called.
+
+## AV1230 — Consider providing property-changed events [May]
+
+Consider providing events that are raised when certain properties are changed. Such an event should be named `PropertyChanged`, where `Property` should be replaced with the name of the property with which this event is associated
+
+**Note:** If your class has many properties that require corresponding events, consider implementing the `INotifyPropertyChanged` interface instead. It is often used in the [Presentation Model](http://martinfowler.com/eaaDev/PresentationModel.html) and [Model-View-ViewModel](http://msdn.microsoft.com/en-us/magazine/dd419663.aspx) patterns.
+
+## AV1235 — Don't pass `null` as the `sender` argument when raising an event [Must]
+
+Often an event handler is used to handle similar events from multiple senders. The sender argument is then used to get to the source of the event. Always pass a reference to the source (typically `this`) when raising the event. Furthermore don't pass `null` as the event data parameter when raising an event. If there is no event data, pass `EventArgs.Empty` instead of `null`.
+
+**Exception:** On static events, the sender argument should be `null`.
+
+## AV1240 — Use generic constraints if applicable [Should]
+
+Instead of casting to and from the object type in generic types or methods, use `where` constraints or the `as` operator to specify the exact characteristics of the generic parameter. For example:
+
+	class SomeClass
+	{
+	}
+
+	// Don't
+	class MyClass
+	{
+		void SomeMethod(T t)
+		{
+			object temp = t;
+			SomeClass obj = (SomeClass) temp;
+		}
+	}
+
+	// Do
+	class MyClass where T : SomeClass
+	{
+		void SomeMethod(T t)
+		{
+			SomeClass obj = t;
+		}
+	}
+
+## AV1250 — Evaluate the result of a LINQ expression before returning it [Must]
+
+Consider the following code snippet
+
+	public IEnumerable<GoldMember> GetGoldMemberCustomers()
+	{
+		const decimal GoldMemberThresholdInEuro = 1_000_000;
+
+		var query =
+			from customer in db.Customers
+			where customer.Balance > GoldMemberThresholdInEuro
+			select new GoldMember(customer.Name, customer.Balance);
+
+		return query;
+	}
+
+Since LINQ queries use deferred execution, returning `query` will actually return the expression tree representing the above query. Each time the caller evaluates this result using a `foreach` loop or similar, the entire query is re-executed resulting in new instances of `GoldMember` every time. Consequently, you cannot use the `==` operator to compare multiple `GoldMember` instances. Instead, always explicitly evaluate the result of a LINQ query using `ToList()`, `ToArray()` or similar methods.
+
+## AV1251 — Do not use `this` and `base` prefixes unless it is required [Must]
+
+In a class hierarchy, it is not necessary to know at which level a member is declared to use it. Refactoring derived classes is harder if that level is fixed in the code.
+
diff --git a/.agents/skills/csharp-guidelines/references/naming.md b/.agents/skills/csharp-guidelines/references/naming.md
@@ -0,0 +1,159 @@
+﻿# Naming Conventions (AV1700) — Detailed Reference
+
+## AV1701 — Use US English [Must]
+
+All identifiers (such as types, type members, parameters and variables) should be named using words from the American English language.
+
+- Choose easily readable, preferably grammatically correct names. For example, `HorizontalAlignment` is more readable than `AlignmentHorizontal`.
+- Favor readability over brevity. The property name `CanScrollHorizontally` is better than `ScrollableX` (an obscure reference to the X-axis).
+- Avoid using names that conflict with keywords of widely used programming languages.
+
+## AV1702 — Use proper casing for language elements [Must]
+
+| Language element | Casing| Example |
+|:--------------------|:----------|:-----------|
+| Namespace | Pascal | `System.Drawing` |
+| Type parameter | Pascal | `TView` |
+| Interface | Pascal | `IBusinessService`
+| Class, struct | Pascal | `AppDomain`
+| Enum | Pascal | `ErrorLevel` |
+| Enum member | Pascal | `FatalError` |
+| Resource key | Pascal | `SaveButtonTooltipText` |
+| Constant field | Pascal | `MaximumItems` |
+| Private static readonly field | Pascal | `RedValue` |
+| Private field | Camel | `listItem` |
+| Non-private field | Pascal | `MainPanel` |
+| Property | Pascal | `BackColor` |
+| Event | Pascal | `Click` |
+| Method | Pascal | `ToString` |
+| Local function | Pascal | `FormatText` |
+| Parameter | Camel | `typeName` |
+| Tuple element names | Pascal | `(string First, string Last) name = ("John", "Doe");` <br/>`var name = (First: "John", Last: "Doe");` <br/>`(string First, string Last) GetName() => ("John", "Doe");` |
+| Variables declared using tuple syntax | Camel | `(string first, string last) = ("John", "Doe");` <br/>`var (first, last) = ("John", "Doe");` <br/> |
+| Local variable | Camel | `listOfValues` |
+
+**Note:** in case of ambiguity, the rule higher in the table wins.
+
+## AV1704 — Don't include numbers in variables, parameters and type members [May]
+
+In most cases they are a lazy excuse for not defining a clear and intention-revealing name.
+
+## AV1705 — Don't prefix fields [Must]
+
+For example, don't use `g_` or `s_` to distinguish static from non-static fields. A method in which it is difficult to distinguish local variables from member fields is generally too big. Examples of incorrect identifier names are: `_currentUser`, `mUserName`, `m_loginTime`.
+
+## AV1706 — Don't use abbreviations [Should]
+
+For example, use `ButtonOnClick` rather than `BtnOnClick`. Avoid single character variable names, such as `i` or `q`. Use `index` or `query` instead.
+
+**Exceptions:** Use well-known acronyms and abbreviations that are widely accepted or well-known in your work domain. For instance, use acronym `UI` instead of `UserInterface` and abbreviation `Id` instead of `Identity`.
+
+## AV1707 — Name members, parameters and variables according to their meaning and not their type [Should]
+
+- Use functional names. For example, `GetLength` is a better name than `GetInt`.
+- Don't use terms like `Enum`, `Class` or `Struct` in a name.
+- Identifiers that refer to a collection type should have plural names.
+- Don't include the type in variable names, except to avoid clashes with other variables.
+
+## AV1708 — Name types using nouns, noun phrases or adjective phrases [Should]
+
+For example, the name IComponent uses a descriptive noun, ICustomAttributeProvider uses a noun phrase and IPersistable uses an adjective.
+Bad examples include `SearchExamination` (a page to search for examinations), `Common` (does not end with a noun, and does not explain its purpose) and `SiteSecurity` (although the name is technically okay, it does not say anything about its purpose).
+
+Don't include terms like `Utility` or `Helper` in classes. Classes with names like that are usually static classes and are introduced without considering object-oriented principles (see also ).
+
+## AV1709 — Name generic type parameters with descriptive names [Should]
+
+- Always prefix type parameter names with the letter `T`.
+- Always use a descriptive name unless a single-letter name is completely self-explanatory and a longer name would not add value. Use the single letter `T` as the type parameter in that case.
+- Consider indicating constraints placed on a type parameter in the name of the parameter. For example, a parameter constrained to `ISession` may be called `TSession`.
+
+## AV1710 — Don't repeat the name of a class or enumeration in its members [Must]
+
+class Employee
+	{
+		// Wrong!
+		static GetEmployee() {...}
+		DeleteEmployee() {...}
+
+		// Right.
+		static Get() {...}
+		Delete() {...}
+
+		// Also correct.
+		AddNewJob() {...}
+		RegisterForMeeting() {...}
+	}
+
+## AV1711 — Name members similarly to members of related .NET Framework classes [May]
+
+.NET developers are already accustomed to the naming patterns the framework uses, so following this same pattern helps them find their way in your classes as well. For instance, if you define a class that behaves like a collection, provide members like `Add`, `Remove` and `Count` instead of `AddItem`, `Delete` or `NumberOfItems`.
+
+## AV1712 — Avoid short names or names that can be mistaken for other names [Must]
+
+Although technically correct, statements like the following can be confusing:
+
+	bool b001 = lo == l0 ? I1 == 11 : lOl != 101;
+
+## AV1715 — Properly name properties [Should]
+
+- Name properties with nouns, noun phrases, or occasionally adjective phrases.
+- Name boolean properties with an affirmative phrase. E.g. `CanSeek` instead of `CannotSeek`.
+- Consider prefixing boolean properties with `Is`, `Has`, `Can`, `Allows`, or `Supports`.
+- Consider giving a property the same name as its type. When you have a property that is strongly typed to an enumeration, the name of the property can be the same as the name of the enumeration. For example, if you have an enumeration named `CacheLevel`, a property that returns one of its values can also be named `CacheLevel`.
+
+## AV1720 — Name methods and local functions using verbs or verb-object pairs [Should]
+
+Name a method or local function using a verb like `Show` or a verb-object pair such as `ShowDialog`. A good name should give a hint on the *what* of a member, and if possible, the *why*.
+
+Also, don't include `And` in the name of a method or local function. That implies that it is doing more than one thing, which violates the Single Responsibility Principle explained in .
+
+## AV1725 — Name namespaces using names, layers, verbs and features [May]
+
+For instance, the following namespaces are good examples of that guideline.
+
+	AvivaSolutions.Commerce.Web
+	NHibernate.Extensibility
+	Microsoft.ServiceModel.WebApi
+	Microsoft.VisualStudio.Debugging
+	FluentAssertion.Primitives
+	CaliburnMicro.Extensions
+
+**Note:** Never allow namespaces to contain the name of a type, but a noun in its plural form (e.g. `Collections`) is usually OK.
+
+## AV1735 — Use a verb or verb phrase to name an event [Should]
+
+Name events with a verb or a verb phrase. For example: `Click`, `Deleted`, `Closing`, `Minimizing`, and `Arriving`. For example, the declaration of the `Search` event may look like this:
+
+	public event EventHandler<SearchArgs> Search;
+
+## AV1737 — Use `-ing` and `-ed` to express pre-events and post-events [May]
+
+For example, a close event that is raised before a window is closed would be called `Closing`, and one that is raised after the window is closed would be called `Closed`. Don't use `Before` or `After` prefixes or suffixes to indicate pre and post events.
+
+Suppose you want to define events related to the deletion of an object. Avoid defining the `Deleting` and `Deleted` events as `BeginDelete` and `EndDelete`. Define those events as follows:
+
+- `Deleting`: Occurs just before the object is getting deleted.
+- `Delete`: Occurs when the object needs to be deleted by the event handler.
+- `Deleted`: Occurs when the object is already deleted.
+
+## AV1738 — Prefix an event handler with "On" [May]
+
+It is good practice to prefix the method that handles an event with "On". For example, a method that handles its own `Closing` event should be named `OnClosing`. And a method that handles the `Click` event of its `okButton` field should be named `OkButtonOnClick`.
+
+## AV1739 — Use an underscore for irrelevant lambda parameters [May]
+
+If you use a lambda expression (for instance, to subscribe to an event) and the actual parameters of the event are irrelevant, use the following convention to make that explicit:
+
+	button.Click += (_, __) => HandleClick();
+
+**Note** If using C# 9 or higher, use a single underscore (discard) for all unused lambda parameters and variables.
+
+## AV1745 — Group extension methods in a class suffixed with Extensions [May]
+
+If the name of an extension method conflicts with another member or extension method, you must prefix the call with the class name. Having them in a dedicated class with the `Extensions` suffix improves readability.
+
+## AV1755 — Postfix asynchronous methods with `Async` or `TaskAsync` [Should]
+
+The general convention for methods and local functions that return `Task` or `Task<TResult>` is to postfix them with `Async`. But if such a method already exists, use `TaskAsync` instead.
+
diff --git a/.agents/skills/csharp-guidelines/references/performance.md b/.agents/skills/csharp-guidelines/references/performance.md
@@ -0,0 +1,55 @@
+﻿# Performance (AV1800) — Detailed Reference
+
+## AV1800 — Consider using `Any()` to determine whether an `IEnumerable<T>` is empty [May]
+
+When a member or local function returns an `IEnumerable<T>` or other collection class that does not expose a `Count` property, use the `Any()` extension method rather than `Count()` to determine whether the collection contains items. If you do use `Count()`, you risk that iterating over the entire collection might have a significant impact (such as when it really is an `IQueryable<T>` to a persistent store).
+
+**Note:** If you return an `IEnumerable<T>` to prevent changes from calling code as explained in , and you're developing in .NET 4.5 or higher, consider the new read-only classes.
+
+## AV1820 — Only use `async` for low-intensive long-running activities [Must]
+
+The usage of `async` won't automagically run something on a worker thread like `Task.Run` does. It just adds the necessary logic to allow releasing the current thread, and marshal the result back on that same thread if a long-running asynchronous operation has completed. In other words, use `async` only for I/O bound operations.
+
+## AV1825 — Prefer `Task.Run` or `Task.Factory.StartNew` for CPU-intensive activities [Must]
+
+If you do need to execute a CPU bound operation, use `Task.Run` to offload the work to a thread from the Thread Pool. For long-running operations use `Task.Factory.StartNew` with `TaskCreationOptions.LongRunning` parameter to create a new thread. Remember that you have to marshal the result back to your main thread manually.
+
+## AV1830 — Beware of mixing up `async`/`await` with `Task.Wait` [Must]
+
+`await` does not block the current thread but simply instructs the compiler to generate a state-machine. However, `Task.Wait` blocks the thread and may even cause deadlocks (see ).
+
+## AV1835 — Beware of `async`/`await` deadlocks in special environments (e.g. WPF) [Must]
+
+Consider the following asynchronous method:
+
+	private async Task<string> GetDataAsync()
+	{
+		var result = await MyWebService.GetDataAsync();
+		return result.ToString();
+	}
+
+Now when a button event handler is implemented like this:
+
+	public async void Button1_Click(object sender, RoutedEventArgs e)
+	{
+		var data = GetDataAsync().Result;
+		textBox1.Text = data;
+	}
+
+You will likely end up with a deadlock. Why? Because the `Result` property getter will block until the `async` operation has completed, but since an `async` method _could_ automatically marshal the result back to the original thread (depending on the current `SynchronizationContext` or `TaskScheduler`) and WPF uses a single-threaded synchronization context, they'll be waiting on each other. A similar problem can also happen on UWP, WinForms, classical ASP.NET (not ASP.NET Core) or a Windows Store C#/XAML app. Read more about this [here](https://devblogs.microsoft.com/pfxteam/await-and-ui-and-deadlocks-oh-my/).
+
+## AV1840 — Await `ValueTask` and `ValueTask<T>` directly and exactly once [Must]
+
+The consumption of the newer and performance related `ValueTask` and `ValueTask<T>` types is more restrictive than consuming `Task` or `Task<T>`. Starting with .NET Core 2.1 the `ValueTask<T>` is not only able to wrap the result `T` or a `Task<T>`, with this version it is also possible to wrap a `IValueTaskSource` / `IValueTaskSource<T>` which gives the developer extra support for reuse and pooling. This enhanced support might lead to unwanted side-effects, as the ValueTask-returning developer might reuse the underlying object after it got awaited. The safest way to consume a `ValueTask` / `ValueTask<T>` is to directly `await` it once, or call `.AsTask()` to get a `Task` / `Task<T>` to overcome these limitations.
+
+	// OK / GOOD
+	int bytesRead = await stream.ReadAsync(buffer, cancellationToken);
+
+	// OK / GOOD
+	int bytesRead = await stream.ReadAsync(buffer, cancellationToken).ConfigureAwait(false);
+
+	// OK / GOOD - Get task if you want to overcome the limitations exposed by ValueTask / ValueTask<T>
+	Task<int> task = stream.ReadAsync(buffer, cancellationToken).AsTask();
+
+Other usage patterns might still work (like saving the `ValueTask` / `ValueTask<T>` into a variable and awaiting later), but may lead to misuse eventually. Not awaiting a `ValueTask` / `ValueTask<T>` may also cause unwanted side-effects. Read more about `ValueTask` / `ValueTask<T>` and the correct usage [here](https://devblogs.microsoft.com/dotnet/understanding-the-whys-whats-and-whens-of-valuetask/).
+
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,39 @@
+# AGENTS.md — C# Coding Guidelines Repository
+
+## About this repository
+
+This is the **dennisdoomen/CSharpGuidelines** repository — a community-maintained reference for C# coding standards covering all C# versions up to v10. The site is built with **Jekyll** (Ruby) and hosted on GitHub Pages.
+
+## Repository structure
+
+| Path | Purpose |
+|------|---------|
+| `_rules/*.md` | Individual guideline rules. Each file has YAML frontmatter (`rule_id`, `rule_category`, `title`, `severity`) followed by Markdown body. |
+| `_pages/*.md` | Category landing pages that aggregate rules by `rule_category`. |
+| `_includes/` | Shared Markdown partials (introduction, cheatsheet content). |
+| `_layouts/` | Jekyll layouts, including `rule-category` which renders rules per page. |
+| `_data/navigation.yml` | Sidebar navigation definition. |
+| `_sass/` | SCSS styles. |
+| `_config.yml` | Jekyll site configuration. |
+
+## Working with rules
+
+- Each rule lives in `_rules/<id>.md`. The filename matches `rule_id`.
+- `severity` values: `1` = Must · `2` = Should · `3` = May
+- Valid `rule_category` values: `class-design`, `member-design`, `misc`, `maintainability`, `naming-conventions`, `performance`, `dotnet-framework-usage`, `commenting`, `layout`
+- Rule body is standard Markdown. Jekyll/Liquid template syntax (`{{ site.default_rule_prefix }}`) is used for cross-references — preserve this when editing existing rules.
+
+## Building the site
+
+```bash
+bundle install
+bundle exec jekyll serve
+```
+
+Or use `start_site.bat` on Windows.
+
+## Skills
+
+When writing or reviewing **C# code** (not site/template code), apply the guidelines defined in:
+
+→ [`.agents/skills/csharp-guidelines/SKILL.md`](.agents/skills/csharp-guidelines/SKILL.md)
PATCH

echo "Gold patch applied."
