#!/bin/bash
set -euo pipefail

cd /workspace/pulumi

# Idempotency check: if the patch has already been applied, just exit.
if grep -q "OrgGetDefault returns the default organization for the current backend" sdk/go/auto/local_workspace.go 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch inline (no external fetch).
git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260401--auto-python--add-org-commands-to-automation-api.yaml b/changelog/pending/20260401--auto-python--add-org-commands-to-automation-api.yaml
new file mode 100644
index 000000000000..a041de454698
--- /dev/null
+++ b/changelog/pending/20260401--auto-python--add-org-commands-to-automation-api.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: feat
+  scope: auto/python
+  description: Add org get-default and set-default commands to Automation API
diff --git a/changelog/pending/20260401--sdk-go--add-org-commands-to-automation-api.yaml b/changelog/pending/20260401--sdk-go--add-org-commands-to-automation-api.yaml
new file mode 100644
index 000000000000..75b5d26c5a15
--- /dev/null
+++ b/changelog/pending/20260401--sdk-go--add-org-commands-to-automation-api.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: feat
+  scope: sdk/go
+  description: Add org get-default and set-default commands to Automation API
diff --git a/sdk/go/auto/local_workspace.go b/sdk/go/auto/local_workspace.go
index 3b6f0398a4c2..238fef98fd52 100644
--- a/sdk/go/auto/local_workspace.go
+++ b/sdk/go/auto/local_workspace.go
@@ -562,6 +562,24 @@ func (l *LocalWorkspace) WhoAmIDetails(ctx context.Context) (WhoAmIResult, error
 	return WhoAmIResult{User: strings.TrimSpace(stdout)}, nil
 }

+// OrgGetDefault returns the default organization for the current backend.
+func (l *LocalWorkspace) OrgGetDefault(ctx context.Context) (string, error) {
+	stdout, stderr, errCode, err := l.runPulumiCmdSync(ctx, "org", "get-default")
+	if err != nil {
+		return "", newAutoError(fmt.Errorf("could not get default organization: %w", err), stdout, stderr, errCode)
+	}
+	return strings.TrimSpace(stdout), nil
+}
+
+// OrgSetDefault sets the default organization for the current backend.
+func (l *LocalWorkspace) OrgSetDefault(ctx context.Context, orgName string) error {
+	stdout, stderr, errCode, err := l.runPulumiCmdSync(ctx, "org", "set-default", orgName)
+	if err != nil {
+		return newAutoError(fmt.Errorf("could not set default organization: %w", err), stdout, stderr, errCode)
+	}
+	return nil
+}
+
 // Stack returns a summary of the currently selected stack, if any.
 func (l *LocalWorkspace) Stack(ctx context.Context) (*StackSummary, error) {
 	stacks, err := l.ListStacks(ctx)
diff --git a/sdk/go/auto/workspace.go b/sdk/go/auto/workspace.go
index fe3228a9db04..0e5d8d012501 100644
--- a/sdk/go/auto/workspace.go
+++ b/sdk/go/auto/workspace.go
@@ -124,6 +124,10 @@ type Workspace interface {
 	// WhoAmIDetails returns detailed information about the currently
 	// logged-in Pulumi identity.
 	WhoAmIDetails(ctx context.Context) (WhoAmIResult, error)
+	// OrgGetDefault returns the default organization for the current backend.
+	OrgGetDefault(context.Context) (string, error)
+	// OrgSetDefault sets the default organization for the current backend.
+	OrgSetDefault(ctx context.Context, orgName string) error
 	// ChangeStackSecretsProvider edits the secrets provider for the given stack.
 	ChangeStackSecretsProvider(
 		ctx context.Context, stackName, newSecretsProvider string, opts *ChangeSecretsProviderOptions,
diff --git a/sdk/python/lib/pulumi/automation/_local_workspace.py b/sdk/python/lib/pulumi/automation/_local_workspace.py
index 74778f4af12d..3df13e99a884 100644
--- a/sdk/python/lib/pulumi/automation/_local_workspace.py
+++ b/sdk/python/lib/pulumi/automation/_local_workspace.py
@@ -436,6 +436,13 @@ def who_am_i(self) -> WhoAmIResult:
         result = self._run_pulumi_cmd_sync(["whoami"])
         return WhoAmIResult(user=result.stdout.strip())

+    def org_get_default(self) -> str:
+        result = self._run_pulumi_cmd_sync(["org", "get-default"])
+        return result.stdout.strip()
+
+    def org_set_default(self, org_name: str) -> None:
+        self._run_pulumi_cmd_sync(["org", "set-default", org_name])
+
     def stack(self) -> Optional[StackSummary]:
         stacks = self.list_stacks()
         for stack in stacks:
diff --git a/sdk/python/lib/pulumi/automation/_workspace.py b/sdk/python/lib/pulumi/automation/_workspace.py
index 4a8b55883214..526429751ba4 100644
--- a/sdk/python/lib/pulumi/automation/_workspace.py
+++ b/sdk/python/lib/pulumi/automation/_workspace.py
@@ -392,6 +392,22 @@ def who_am_i(self) -> WhoAmIResult:
         :returns: WhoAmIResult
         """

+    @abstractmethod
+    def org_get_default(self) -> str:
+        """
+        Returns the default organization for the current backend.
+
+        :returns: str
+        """
+
+    @abstractmethod
+    def org_set_default(self, org_name: str) -> None:
+        """
+        Sets the default organization for the current backend.
+
+        :param str org_name: The name of the organization to set as the default.
+        """
+
     @abstractmethod
     def stack(self) -> Optional[StackSummary]:
         """
PATCH

echo "Patch applied successfully."
