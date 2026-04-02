#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q 'componentMatch' src/bun.js/bindings/webcore/URLPatternComponent.h; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/bench/snippets/urlpattern-detailed.mjs b/bench/snippets/urlpattern-detailed.mjs
new file mode 100644
index 00000000000..d7dd5137d95
--- /dev/null
+++ b/bench/snippets/urlpattern-detailed.mjs
@@ -0,0 +1,27 @@
+import { bench, group, run } from "../runner.mjs";
+
+// Common real-world pattern: routing with named params
+const routePattern = new URLPattern({ pathname: "/api/users/:id/posts/:postId" });
+const matchURL = "https://example.com/api/users/42/posts/123";
+const noMatchURL = "https://example.com/static/image.png";
+
+// Simple pathname pattern (most common)
+const simplePattern = new URLPattern({ pathname: "/api/:resource" });
+
+// Full URL string pattern
+const stringPattern = new URLPattern("https://*.example.com/foo/*");
+
+group("URLPattern.test() - hot path", () => {
+  bench("test() match - named groups", () => routePattern.test(matchURL));
+  bench("test() no-match - named groups", () => routePattern.test(noMatchURL));
+  bench("test() match - simple", () => simplePattern.test("https://example.com/api/items"));
+  bench("test() match - string pattern", () => stringPattern.test("https://sub.example.com/foo/bar"));
+});
+
+group("URLPattern.exec() - hot path", () => {
+  bench("exec() match - named groups", () => routePattern.exec(matchURL));
+  bench("exec() no-match - named groups", () => routePattern.exec(noMatchURL));
+  bench("exec() match - simple", () => simplePattern.exec("https://example.com/api/items"));
+});
+
+await run();
diff --git a/src/bun.js/bindings/webcore/URLPattern.cpp b/src/bun.js/bindings/webcore/URLPattern.cpp
index 17884dfe8af..17320b78bd7 100644
--- a/src/bun.js/bindings/webcore/URLPattern.cpp
+++ b/src/bun.js/bindings/webcore/URLPattern.cpp
@@ -338,7 +338,7 @@ ExceptionOr<void> URLPattern::compileAllComponents(ScriptExecutionContext& conte

     URLPatternUtilities::URLPatternStringOptions compileOptions { .ignoreCase = options.ignoreCase };

-    auto maybePathnameComponent = m_protocolComponent.matchSpecialSchemeProtocol(context)
+    auto maybePathnameComponent = m_protocolComponent.matchSpecialSchemeProtocol(context.globalObject())
         ? URLPatternUtilities::URLPatternComponent::compile(vm, processedInit.pathname, EncodingCallbackType::Path, URLPatternUtilities::URLPatternStringOptions { "/"_s, "/"_s, options.ignoreCase })
         : URLPatternUtilities::URLPatternComponent::compile(vm, processedInit.pathname, EncodingCallbackType::OpaquePath, compileOptions);
     if (maybePathnameComponent.hasException())
@@ -427,51 +427,32 @@ ExceptionOr<std::optional<URLPatternResult>> URLPattern::match(ScriptExecutionCo
             return { std::nullopt };
     }

-    auto protocolExecResult = m_protocolComponent.componentExec(context, protocol);
-    if (protocolExecResult.isNull() || protocolExecResult.isUndefined())
-        return { std::nullopt };
-
     auto* globalObject = context.globalObject();
     if (!globalObject)
         return { std::nullopt };
-    result.protocol = m_protocolComponent.createComponentMatchResult(globalObject, WTF::move(protocol), protocolExecResult);
-
-    auto usernameExecResult = m_usernameComponent.componentExec(context, username);
-    if (usernameExecResult.isNull() || usernameExecResult.isUndefined())
-        return { std::nullopt };
-    result.username = m_usernameComponent.createComponentMatchResult(globalObject, WTF::move(username), usernameExecResult);
-
-    auto passwordExecResult = m_passwordComponent.componentExec(context, password);
-    if (passwordExecResult.isNull() || passwordExecResult.isUndefined())
-        return { std::nullopt };
-    result.password = m_passwordComponent.createComponentMatchResult(globalObject, WTF::move(password), passwordExecResult);
-
-    auto hostnameExecResult = m_hostnameComponent.componentExec(context, hostname);
-    if (hostnameExecResult.isNull() || hostnameExecResult.isUndefined())
-        return { std::nullopt };
-    result.hostname = m_hostnameComponent.createComponentMatchResult(globalObject, WTF::move(hostname), hostnameExecResult);

-    auto pathnameExecResult = m_pathnameComponent.componentExec(context, pathname);
-    if (pathnameExecResult.isNull() || pathnameExecResult.isUndefined())
-        return { std::nullopt };
-    result.pathname = m_pathnameComponent.createComponentMatchResult(globalObject, WTF::move(pathname), pathnameExecResult);
-
-    auto portExecResult = m_portComponent.componentExec(context, port);
-    if (portExecResult.isNull() || portExecResult.isUndefined())
-        return { std::nullopt };
-    result.port = m_portComponent.createComponentMatchResult(globalObject, WTF::move(port), portExecResult);
-
-    auto searchExecResult = m_searchComponent.componentExec(context, search);
-    if (searchExecResult.isNull() || searchExecResult.isUndefined())
-        return { std::nullopt };
-    result.search = m_searchComponent.createComponentMatchResult(globalObject, WTF::move(search), searchExecResult);
+    Ref vm = context.vm();
+    JSC::JSLockHolder lock(vm);

-    auto hashExecResult = m_hashComponent.componentExec(context, hash);
-    if (hashExecResult.isNull() || hashExecResult.isUndefined())
+    auto tryMatch = [&](const URLPatternUtilities::URLPatternComponent& component, String&& input, URLPatternComponentResult& out) -> bool {
+        auto matched = component.componentMatch(globalObject, WTF::move(input));
+        if (!matched)
+            return false;
+        out = WTF::move(*matched);
+        return true;
+    };
+
+    if (!tryMatch(m_protocolComponent, WTF::move(protocol), result.protocol)
+        || !tryMatch(m_usernameComponent, WTF::move(username), result.username)
+        || !tryMatch(m_passwordComponent, WTF::move(password), result.password)
+        || !tryMatch(m_hostnameComponent, WTF::move(hostname), result.hostname)
+        || !tryMatch(m_pathnameComponent, WTF::move(pathname), result.pathname)
+        || !tryMatch(m_portComponent, WTF::move(port), result.port)
+        || !tryMatch(m_searchComponent, WTF::move(search), result.search)
+        || !tryMatch(m_hashComponent, WTF::move(hash), result.hash))
         return { std::nullopt };
-    result.hash = m_hashComponent.createComponentMatchResult(globalObject, WTF::move(hash), hashExecResult);

-    return { result };
+    return { WTF::move(result) };
 }

 // https://urlpattern.spec.whatmeans.org/#url-pattern-has-regexp-groups
diff --git a/src/bun.js/bindings/webcore/URLPatternComponent.cpp b/src/bun.js/bindings/webcore/URLPatternComponent.cpp
index 0d7d8458fa9..81b9d4ced70 100644
--- a/src/bun.js/bindings/webcore/URLPatternComponent.cpp
+++ b/src/bun.js/bindings/webcore/URLPatternComponent.cpp
@@ -27,14 +27,11 @@
 #include "URLPatternComponent.h"

 #include "ExceptionOr.h"
-#include "ScriptExecutionContext.h"
 #include "URLPatternCanonical.h"
 #include "URLPatternParser.h"
 #include "URLPatternResult.h"
-#include <JavaScriptCore/JSCJSValue.h>
-#include <JavaScriptCore/JSString.h>
-#include <JavaScriptCore/RegExpObject.h>
-#include <ranges>
+#include <JavaScriptCore/RegExp.h>
+#include <JavaScriptCore/YarrFlags.h>

 namespace WebCore {
 using namespace JSC;
@@ -76,65 +73,41 @@ ExceptionOr<URLPatternComponent> URLPatternComponent::compile(Ref<JSC::VM> vm, S
 }

 // https://urlpattern.spec.whatmeans.org/#protocol-component-matches-a-special-scheme
-bool URLPatternComponent::matchSpecialSchemeProtocol(ScriptExecutionContext& context) const
+bool URLPatternComponent::matchSpecialSchemeProtocol(JSC::JSGlobalObject* globalObject) const
 {
-    Ref vm = context.vm();
-    JSC::JSLockHolder lock(vm);
-
     static constexpr std::array specialSchemeList { "ftp"_s, "file"_s, "http"_s, "https"_s, "ws"_s, "wss"_s };
-    auto contextObject = context.globalObject();
-    if (!contextObject)
-        return false;
-    auto protocolRegex = JSC::RegExpObject::create(vm, contextObject->regExpStructure(), m_regularExpression.get(), true);
-
-    auto isSchemeMatch = std::ranges::find_if(specialSchemeList, [context = Ref { context }, &vm, &protocolRegex](const String& scheme) {
-        auto maybeMatch = protocolRegex->exec(context->globalObject(), JSC::jsString(vm, scheme));
-        return !maybeMatch.isNull();
-    });
-
-    return isSchemeMatch != specialSchemeList.end();
-}

-JSC::JSValue URLPatternComponent::componentExec(ScriptExecutionContext& context, StringView comparedString) const
-{
-    Ref vm = context.vm();
-    JSC::JSLockHolder lock(vm);
-    auto throwScope = DECLARE_THROW_SCOPE(vm);
-
-    auto contextObject = context.globalObject();
-    if (!contextObject) {
-        throwTypeError(contextObject, throwScope, "URLPattern execution requires a valid execution context"_s);
-        return {};
+    auto* regExp = m_regularExpression.get();
+    for (auto scheme : specialSchemeList) {
+        if (regExp->match(globalObject, scheme, 0))
+            return true;
     }
-    auto regex = JSC::RegExpObject::create(vm, contextObject->regExpStructure(), m_regularExpression.get(), true);
-    return regex->exec(contextObject, JSC::jsString(vm, comparedString));
+    return false;
 }

+// Implements both "regexp matching" and "create a component match result":
 // https://urlpattern.spec.whatmeans.org/#create-a-component-match-result
-URLPatternComponentResult URLPatternComponent::createComponentMatchResult(JSC::JSGlobalObject* globalObject, String&& input, const JSC::JSValue& execResult) const
+std::optional<URLPatternComponentResult> URLPatternComponent::componentMatch(JSC::JSGlobalObject* globalObject, String&& input) const
 {
-    URLPatternComponentResult::GroupsRecord groups;
+    auto* regExp = m_regularExpression.get();
+    auto ovector = regExp->ovectorSpan();
+    int position = regExp->match(globalObject, input, 0, ovector);
+    if (position < 0)
+        return std::nullopt;

-    Ref vm = globalObject->vm();
-    auto throwScope = DECLARE_THROW_SCOPE(vm);
+    unsigned numSubpatterns = regExp->numSubpatterns();

-    auto lengthValue = execResult.get(globalObject, vm->propertyNames->length);
-    RETURN_IF_EXCEPTION(throwScope, {});
-    auto length = lengthValue.toIntegerOrInfinity(globalObject);
-    RETURN_IF_EXCEPTION(throwScope, {});
-    ASSERT(length >= 0 && std::isfinite(length));
-
-    for (unsigned index = 1; index < length; ++index) {
-        auto match = execResult.get(globalObject, index);
-        RETURN_IF_EXCEPTION(throwScope, {});
+    URLPatternComponentResult::GroupsRecord groups;
+    groups.reserveInitialCapacity(numSubpatterns);
+    for (unsigned i = 1; i <= numSubpatterns; ++i) {
+        int start = ovector[i * 2];
+        int end = ovector[i * 2 + 1];

         Variant<std::monostate, String> value;
-        if (!match.isNull() && !match.isUndefined()) {
-            value = match.toWTFString(globalObject);
-            RETURN_IF_EXCEPTION(throwScope, {});
-        }
+        if (start >= 0)
+            value = input.substring(start, end - start);

-        size_t groupIndex = index - 1;
+        size_t groupIndex = i - 1;
         String groupName = groupIndex < m_groupNameList.size() ? m_groupNameList[groupIndex] : emptyString();
         groups.append(URLPatternComponentResult::NameMatchPair { WTF::move(groupName), WTF::move(value) });
     }
diff --git a/src/bun.js/bindings/webcore/URLPatternComponent.h b/src/bun.js/bindings/webcore/URLPatternComponent.h
index 6a4d7a5e04a..2e6dc80b1dd 100644
--- a/src/bun.js/bindings/webcore/URLPatternComponent.h
+++ b/src/bun.js/bindings/webcore/URLPatternComponent.h
@@ -27,16 +27,16 @@

 #include <JavaScriptCore/Strong.h>
 #include <JavaScriptCore/StrongInlines.h>
+#include <optional>

 namespace JSC {
 class RegExp;
 class VM;
-class JSValue;
+class JSGlobalObject;
 }

 namespace WebCore {

-class ScriptExecutionContext;
 struct URLPatternComponentResult;
 enum class EncodingCallbackType : uint8_t;
 template<typename> class ExceptionOr;
@@ -49,9 +49,8 @@ class URLPatternComponent {
     static ExceptionOr<URLPatternComponent> compile(Ref<JSC::VM>, StringView, EncodingCallbackType, const URLPatternStringOptions&);
     const String& patternString() const { return m_patternString; }
     bool hasRegexGroupsFromPartList() const { return m_hasRegexGroupsFromPartList; }
-    bool matchSpecialSchemeProtocol(ScriptExecutionContext&) const;
-    JSC::JSValue componentExec(ScriptExecutionContext&, StringView) const;
-    URLPatternComponentResult createComponentMatchResult(JSC::JSGlobalObject*, String&& input, const JSC::JSValue& execResult) const;
+    bool matchSpecialSchemeProtocol(JSC::JSGlobalObject*) const;
+    std::optional<URLPatternComponentResult> componentMatch(JSC::JSGlobalObject*, String&& input) const;
     URLPatternComponent() = default;

 private:
diff --git a/src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp b/src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp
index 914b72a450d..4c97a465065 100644
--- a/src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp
+++ b/src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp
@@ -155,7 +155,7 @@ ExceptionOr<void> URLPatternConstructorStringParser::computeProtocolMatchSpecial
         return maybeProtocolComponent.releaseException();

     auto protocolComponent = maybeProtocolComponent.releaseReturnValue();
-    m_protocolMatchesSpecialSchemeFlag = protocolComponent.matchSpecialSchemeProtocol(context);
+    m_protocolMatchesSpecialSchemeFlag = protocolComponent.matchSpecialSchemeProtocol(context.globalObject());

     return {};
 }

PATCH
