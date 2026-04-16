#!/bin/bash
set -e

cd /workspace/pulumi

# Apply the gold patch for pulumi/pulumi#22436
patch -p1 <<'PATCH'
diff --git a/sdk/go/auto/local_workspace.go b/sdk/go/auto/local_workspace.go
index 40fd96368b6..7ea53c9e6f1 100644
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
diff --git a/sdk/go/auto/local_workspace_test.go b/sdk/go/auto/local_workspace_test.go
index 40fd96368b6..a5192800ef1 100644
--- a/sdk/go/auto/local_workspace_test.go
+++ b/sdk/go/auto/local_workspace_test.go
@@ -3584,6 +3584,31 @@ func TestInstallWithUseLanguageVersionTools(t *testing.T) {
 	require.Equal(t, []string{"install", "--use-language-version-tools"}, m.capturedArgs)
 }

+func TestOrgGetSetDefault(t *testing.T) {
+	t.Parallel()
+
+	ctx := t.Context()
+
+	pDir := filepath.Join(".", "test", "testproj")
+	workspace, err := NewLocalWorkspace(ctx, WorkDir(pDir))
+	require.NoError(t, err)
+
+	// Save the current default so we can restore it.
+	original, err := workspace.OrgGetDefault(ctx)
+	require.NoError(t, err)
+
+	// Set a new default and verify.
+	err = workspace.OrgSetDefault(ctx, "definitely-not-pulumi")
+	require.NoError(t, err)
+	result, err := workspace.OrgGetDefault(ctx)
+	require.NoError(t, err)
+	assert.Equal(t, "definitely-not-pulumi", result)
+
+	// Restore the original default.
+	err = workspace.OrgSetDefault(ctx, original)
+	require.NoError(t, err)
+}
+
 func BenchmarkBulkSetConfigMixed(b *testing.B) {
 	ctx := b.Context()
 	stackName := FullyQualifiedStackName(pulumiOrg, "set_config_mixed", "dev")
diff --git a/sdk/go/auto/workspace.go b/sdk/go/auto/workspace.go
index 40fd96368b6..5c68a7a645c 100644
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
index 40fd96368b6..cf3b886439f 100644
--- a/sdk/python/lib/pulumi/automation/_local_workspace.py
+++ b/sdk/python/lib/pulumi/automation/_local_workspace.py
@@ -436,6 +436,13 @@ class LocalWorkspace(Workspace):
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
index 40fd96368b6..d2e5cd9ce8e 100644
--- a/sdk/python/lib/pulumi/automation/_workspace.py
+++ b/sdk/python/lib/pulumi/automation/_workspace.py
@@ -392,6 +392,22 @@ class Workspace(ABC):
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

diff --git a/sdk/python/lib/test/automation/test_local_workspace.py b/sdk/python/lib/test/automation/test_local_workspace.py
index 40fd96368b6..7ea53c9e6f1 100644
--- a/sdk/python/lib/test/automation/test_local_workspace.py
+++ b/sdk/python/lib/test/automation/test_local_workspace.py
@@ -191,6 +191,19 @@ class TestLocalWorkspace(unittest.TestCase):
         self.assertIsNotNone(result.user)
         self.assertIsNotNone(result.url)

+    def test_org_get_set_default_integration(self):
+        ws = LocalWorkspace()
+
+        # Save the current default so we can restore it.
+        original = ws.org_get_default()
+
+        # Set a new default and verify.
+        ws.org_set_default("definitely-not-pulumi")
+        self.assertEqual(ws.org_get_default(), "definitely-not-pulumi")
+
+        # Restore the original default.
+        ws.org_set_default(original)
+
     def test_stack_init(self):
         project_name = "python_test"
         project_settings = ProjectSettings(name=project_name, runtime="python")
PATCH

# Verify the patch was applied
echo "Verifying patch applied..."
grep -q "OrgGetDefault" sdk/go/auto/local_workspace.go
grep -q "OrgSetDefault" sdk/go/auto/workspace.go
grep -q "org_get_default" sdk/python/lib/pulumi/automation/_local_workspace.py
grep -q "org_set_default" sdk/python/lib/pulumi/automation/_workspace.py
echo "Patch applied successfully!"
