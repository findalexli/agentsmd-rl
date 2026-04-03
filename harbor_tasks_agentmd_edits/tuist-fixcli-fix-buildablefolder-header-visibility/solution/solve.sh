#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tuist

# Idempotent: skip if already applied
if grep -q 'isPartOfSynchronizedGroup' cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index f39ec96a6870..b53b7dff2567 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -48,8 +48,8 @@ Examples:

 ## Workflow
 - The Xcode project is generated with Tuist running `tuist generate --no-open`
-- When compiling Swift changes, use `xcodebuild build -workspace Tuist.xcworkspace -scheme Tuist-Workspace` instead of `swift build`
-- When testing Swift changes, use `xcodebuild test -workspace Tuist.xcworkspace -scheme Tuist-Workspace -only-testing MyTests/SuiteTests` instead of `swift test`.
+- When compiling Swift changes, use `xcodebuild build -workspace Tuist.xcworkspace -scheme Tuist-Workspace CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY=""` instead of `swift build`
+- When testing Swift changes, use `xcodebuild test -workspace Tuist.xcworkspace -scheme Tuist-Workspace -only-testing MyTests/SuiteTests CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY=""` instead of `swift test`.
 - Prefer running test suites or individual test cases, and not the whole test target, for performance
 - When using `swift build`, `swift test`, or `swift package resolve` always include `--replace-scm-with-registry` to avoid switching packages from registry to source control resolution

diff --git a/cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift b/cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift
index 5f1e4ef8bc91..969f09001484 100644
--- a/cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift
+++ b/cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift
@@ -70,6 +70,7 @@ struct BuildPhaseGenerator: BuildPhaseGenerating {
         if shouldAddHeadersBuildPhase(target) {
             try generateHeadersBuildPhase(
                 headers: target.headers,
+                buildableFolders: target.buildableFolders,
                 pbxTarget: pbxTarget,
                 fileElements: fileElements,
                 pbxproj: pbxproj
@@ -345,6 +346,7 @@ struct BuildPhaseGenerator: BuildPhaseGenerating {

     func generateHeadersBuildPhase(
         headers: Headers?,
+        buildableFolders: [BuildableFolder],
         pbxTarget: PBXTarget,
         fileElements: ProjectFileElements,
         pbxproj: PBXProj
@@ -353,6 +355,10 @@ struct BuildPhaseGenerator: BuildPhaseGenerating {
         pbxproj.add(object: headersBuildPhase)
         pbxTarget.buildPhases.append(headersBuildPhase)

+        let isPartOfSynchronizedGroup: (AbsolutePath) -> Bool = { path in
+            buildableFolders.contains { path.isDescendant(of: $0.path) }
+        }
+
         let addHeader: (AbsolutePath, String?) throws -> PBXBuildFile = { path, accessLevel in
             guard let fileReference = fileElements.file(path: path) else {
                 throw BuildPhaseGenerationError.missingFileReference(path)
@@ -363,9 +369,18 @@ struct BuildPhaseGenerator: BuildPhaseGenerating {
             return PBXBuildFile(file: fileReference, settings: settings)
         }
         if let headers {
-            let pbxBuildFiles = try headers.private.sorted().map { try addHeader($0, "private") } +
-                headers.public.sorted().map { try addHeader($0, "public") } +
-                headers.project.sorted().map { try addHeader($0, nil) }
+            let pbxBuildFiles = try headers.private
+                .filter { !isPartOfSynchronizedGroup($0) }
+                .sorted()
+                .map { try addHeader($0, "private") } +
+                headers.public
+                .filter { !isPartOfSynchronizedGroup($0) }
+                .sorted()
+                .map { try addHeader($0, "public") } +
+                headers.project
+                .filter { !isPartOfSynchronizedGroup($0) }
+                .sorted()
+                .map { try addHeader($0, nil) }

             pbxBuildFiles.forEach { pbxproj.add(object: $0) }
             headersBuildPhase.files = pbxBuildFiles
diff --git a/cli/Sources/TuistGenerator/Generator/TargetGenerator.swift b/cli/Sources/TuistGenerator/Generator/TargetGenerator.swift
index 19c3b6dad6f6..b71eb30a11bb 100644
--- a/cli/Sources/TuistGenerator/Generator/TargetGenerator.swift
+++ b/cli/Sources/TuistGenerator/Generator/TargetGenerator.swift
@@ -227,12 +227,68 @@ struct TargetGenerator: TargetGenerating {
                 synchronizedGroup.exceptions?.append(exceptionSet)
             }

+            let targetHeadersInSynchronizedGroup = synchronizedHeaders(
+                buildableFolderPath: buildableFolder.path,
+                targetHeaders: target.headers,
+                buildableFolderExceptions: buildableFolder.exceptions
+            )
+            if !targetHeadersInSynchronizedGroup.public.isEmpty || !targetHeadersInSynchronizedGroup.private.isEmpty {
+                let exceptionSet = PBXFileSystemSynchronizedBuildFileExceptionSet(
+                    target: pbxTarget,
+                    membershipExceptions: [],
+                    publicHeaders: targetHeadersInSynchronizedGroup.public,
+                    privateHeaders: targetHeadersInSynchronizedGroup.private,
+                    additionalCompilerFlagsByRelativePath: [:],
+                    attributesByRelativePath: nil,
+                    platformFiltersByRelativePath: nil
+                )
+                pbxproj.add(object: exceptionSet)
+                synchronizedGroup.exceptions?.append(exceptionSet)
+            }
+
             if !explicitFolders.isEmpty {
                 synchronizedGroup.explicitFolders = explicitFolders
             }
         }
     }

+    private func synchronizedHeaders(
+        buildableFolderPath: AbsolutePath,
+        targetHeaders: Headers?,
+        buildableFolderExceptions: BuildableFolderExceptions
+    ) -> (public: [String], private: [String]) {
+        guard let targetHeaders else { return (public: [], private: []) }
+
+        let existingPublicHeaders = Set(
+            buildableFolderExceptions
+                .flatMap(\.publicHeaders)
+                .filter { $0.isDescendant(of: buildableFolderPath) }
+                .map { $0.relative(to: buildableFolderPath).pathString }
+        )
+        let existingPrivateHeaders = Set(
+            buildableFolderExceptions
+                .flatMap(\.privateHeaders)
+                .filter { $0.isDescendant(of: buildableFolderPath) }
+                .map { $0.relative(to: buildableFolderPath).pathString }
+        )
+
+        let publicHeaders = Set(
+            targetHeaders.public
+                .filter { $0.isDescendant(of: buildableFolderPath) }
+                .map { $0.relative(to: buildableFolderPath).pathString }
+        )
+        let privateHeaders = Set(
+            targetHeaders.private
+                .filter { $0.isDescendant(of: buildableFolderPath) }
+                .map { $0.relative(to: buildableFolderPath).pathString }
+        )
+
+        return (
+            public: Array(publicHeaders.subtracting(existingPublicHeaders)).sorted(),
+            private: Array(privateHeaders.subtracting(existingPrivateHeaders)).sorted()
+        )
+    }
+
     func generateTargetDependencies(
         path: AbsolutePath,
         targets: [Target],

PATCH

echo "Patch applied successfully."
