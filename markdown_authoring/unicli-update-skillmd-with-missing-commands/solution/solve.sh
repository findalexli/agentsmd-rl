#!/usr/bin/env bash
set -euo pipefail

cd /workspace/unicli

# Idempotency guard
if grep -qF "unicli exec Prefab.Save --path \"Player\" --assetPath \"Assets/Prefabs/Player.prefa" ".claude-plugin/unicli/skills/unicli/SKILL.md" && grep -qF "- `.claude-plugin/unicli/skills/unicli/SKILL.md` \u2014 Built-in Commands table and C" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude-plugin/unicli/skills/unicli/SKILL.md b/.claude-plugin/unicli/skills/unicli/SKILL.md
@@ -78,9 +78,17 @@ unicli exec GameObject.Find --includeInactive
 | `GameObject.GetComponents` | Get components on a GameObject |
 | `GameObject.SetActive` | Set active state |
 | `GameObject.GetHierarchy` | Get scene hierarchy tree |
+| `GameObject.AddComponent` | Add a component to a GameObject |
+| `GameObject.RemoveComponent` | Remove a component from a GameObject |
+| `Prefab.GetStatus` | Get prefab instance status |
+| `Prefab.Instantiate` | Instantiate a prefab into scene |
+| `Prefab.Save` | Save GameObject as prefab asset |
+| `Prefab.Apply` | Apply prefab overrides |
+| `Prefab.Unpack` | Unpack a prefab instance |
 | `AssetDatabase.Find` | Search assets |
 | `AssetDatabase.Import` | Import an asset |
 | `AssetDatabase.GetPath` | Get asset path by GUID |
+| `AssetDatabase.Delete` | Delete an asset |
 | `Project.Inspect` | Get project info |
 | `PackageManager.List` | List installed packages |
 | `PackageManager.Add` | Add a package |
@@ -116,6 +124,29 @@ unicli exec GameObject.Find --name "Main Camera" --json
 unicli exec GameObject.GetComponents --instanceId 1234 --json
 ```
 
+**Manage components:**
+
+```bash
+unicli exec GameObject.AddComponent --path "Player" --typeName BoxCollider --json
+unicli exec GameObject.RemoveComponent --componentInstanceId 1234 --json
+```
+
+**Prefab operations:**
+
+```bash
+unicli exec Prefab.GetStatus --path "MyPrefabInstance" --json
+unicli exec Prefab.Instantiate --assetPath "Assets/Prefabs/Enemy.prefab" --json
+unicli exec Prefab.Save --path "Player" --assetPath "Assets/Prefabs/Player.prefab" --json
+unicli exec Prefab.Apply --path "MyPrefabInstance" --json
+unicli exec Prefab.Unpack --path "MyPrefabInstance" --json
+```
+
+**Delete an asset:**
+
+```bash
+unicli exec AssetDatabase.Delete --path "Assets/Prefabs/Old.prefab" --json
+```
+
 **Check console output:**
 
 ```bash
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -66,6 +66,13 @@ UNICLI_PROJECT=src/UniCli.Unity .build/UniCli.Client exec TestRunner.RunEditMode
 UNICLI_PROJECT=src/UniCli.Unity .build/UniCli.Client exec TestRunner.RunPlayMode --json
 ```
 
+### Maintaining documentation
+
+When adding or modifying commands, update the following files to keep them in sync:
+
+- `README.md` — Available Commands table and Examples section
+- `.claude-plugin/unicli/skills/unicli/SKILL.md` — Built-in Commands table and Common Workflows section
+
 ### Tests requiring Unity connection
 
 The `exec` and `commands` subcommands require a connection to the Unity Editor. If the connection fails, retry a few times. If it still fails, ask the user to confirm that Unity Editor is running with the project open.
PATCH

echo "Gold patch applied."
