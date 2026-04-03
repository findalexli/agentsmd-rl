#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tuist

# Idempotent: skip if already applied
if grep -q 'let codeGeneratingResourceExtensions: Set<String> = \["xcassets"\]' \
    cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Apply core code fix to ResourcesProjectMapper.swift ---
git apply --whitespace=fix - <<'PATCH'
diff --git a/cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift b/cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift
index 892c8e92e0e9..b59bd56137a2 100644
--- a/cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift
+++ b/cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift
@@ -87,15 +87,24 @@ public struct ResourcesProjectMapper: ProjectMapping { // swiftlint:disable:this
                 buildableFolders: resourceBuildableFolders
             )
             modifiedTarget.sources = target.sources.filter { $0.path.extension != "metal" }
-            // Asset catalogs and string catalogs need to be included in the main target's sources
-            // build phase so Xcode generates typed asset symbols (mirroring SwiftPM's PIF builder).
-            let codeGeneratingResourceExtensions: Set<String> = ["xcassets", "xcstrings"]
+            // Asset catalogs need to be included in the main target's sources build phase so
+            // Xcode generates typed asset symbols (mirroring SwiftPM's PIF builder).
+            // String catalogs (.xcstrings) are NOT added to Sources because doing so triggers
+            // Xcode's string extraction which marks all strings as "stale" when the target uses
+            // a companion resource bundle (bundle: .module). Instead, xcstrings are kept in the
+            // main target's Resources phase so Xcode can correctly associate string references
+            // in Swift code with the catalog entries.
+            let codeGeneratingResourceExtensions: Set<String> = ["xcassets"]
             for resource in target.resources.resources {
                 if let ext = resource.path.extension, codeGeneratingResourceExtensions.contains(ext) {
                     modifiedTarget.sources.append(SourceFile(path: resource.path))
                 }
             }
-            modifiedTarget.resources.resources = []
+            // Keep xcstrings in the main target's resources so Xcode's string catalog editor
+            // can match string references in the target's Swift sources. Other resources are
+            // moved entirely to the companion bundle target.
+            let mainTargetRetainedResources = target.resources.resources.filter { $0.path.extension == "xcstrings" }
+            modifiedTarget.resources.resources = mainTargetRetainedResources
             modifiedTarget.copyFiles = []
             modifiedTarget.buildableFolders = remainingBuildableFolders
             modifiedTarget.dependencies.append(.target(

PATCH

# --- 2. Create example fixture: iOS app with static framework using xcstrings ---
FIXTURE_DIR="examples/xcode/generated_ios_app_with_static_framework_with_xcstrings"
mkdir -p "$FIXTURE_DIR/App/Sources"
mkdir -p "$FIXTURE_DIR/StaticFramework/Sources"
mkdir -p "$FIXTURE_DIR/StaticFramework/Resources"

cat > "$FIXTURE_DIR/README.md" <<'EOF'
# iOS app with a static framework using xcstrings

A workspace with an application that depends on a static framework containing `.xcstrings` string catalog resources. This fixture verifies that Xcode does not mark strings as stale during build when the static framework uses a companion resource bundle.

```
Workspace:
  - App:
    - App (iOS app)
  - StaticFramework:
    - StaticFramework (static iOS framework)
    - StaticFramework_StaticFramework (iOS bundle)
```

Dependencies:

- App -> StaticFramework
- StaticFramework -> StaticFramework_StaticFramework
EOF

cat > "$FIXTURE_DIR/Tuist.swift" <<'EOF'
import ProjectDescription

let tuist = Tuist(project: .tuist())
EOF

cat > "$FIXTURE_DIR/Workspace.swift" <<'EOF'
import ProjectDescription

let workspace = Workspace(
    name: "App",
    projects: [
        "App",
        "StaticFramework",
    ]
)
EOF

cat > "$FIXTURE_DIR/App/Project.swift" <<'EOF'
import ProjectDescription

let project = Project(
    name: "App",
    targets: [
        .target(
            name: "App",
            destinations: .iOS,
            product: .app,
            bundleId: "dev.tuist.App",
            deploymentTargets: .iOS("16.0"),
            sources: "Sources/**",
            dependencies: [
                .project(target: "StaticFramework", path: "../StaticFramework"),
            ]
        ),
    ]
)
EOF

cat > "$FIXTURE_DIR/App/Sources/AppApp.swift" <<'EOF'
import StaticFramework
import SwiftUI

@main
struct AppApp: App {
    var body: some Scene {
        WindowGroup {
            GreetingView()
        }
    }
}
EOF

cat > "$FIXTURE_DIR/StaticFramework/Project.swift" <<'EOF'
import ProjectDescription

let project = Project(
    name: "StaticFramework",
    targets: [
        .target(
            name: "StaticFramework",
            destinations: .iOS,
            product: .staticFramework,
            bundleId: "dev.tuist.StaticFramework",
            deploymentTargets: .iOS("16.0"),
            sources: "Sources/**",
            resources: ["Resources/**"]
        ),
    ]
)
EOF

cat > "$FIXTURE_DIR/StaticFramework/Sources/GreetingView.swift" <<'EOF'
import SwiftUI

public struct GreetingView: View {
    public init() {}

    public var body: some View {
        VStack {
            Text("greeting_hello", bundle: .module)
            Text("greeting_welcome", bundle: .module)
        }
    }
}
EOF

cat > "$FIXTURE_DIR/StaticFramework/Resources/Localizable.xcstrings" <<'EOF'
{
  "sourceLanguage" : "en",
  "strings" : {
    "greeting_hello" : {
      "localizations" : {
        "en" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "Hello!"
          }
        }
      }
    },
    "greeting_welcome" : {
      "localizations" : {
        "en" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "Welcome to the app"
          }
        }
      }
    }
  },
  "version" : "1.0"
}
EOF

echo "Patch applied successfully."
