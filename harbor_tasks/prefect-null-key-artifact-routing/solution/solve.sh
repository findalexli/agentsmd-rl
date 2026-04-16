#!/bin/bash
set -e

cd /workspace/prefect

# Apply the fix from PR #21454
patch -p1 <<'PATCH'
diff --git a/ui-v2/src/components/artifacts/artifact-card.tsx b/ui-v2/src/components/artifacts/artifact-card.tsx
index 97fd1bf064a7..038de6fabe49 100644
--- a/ui-v2/src/components/artifacts/artifact-card.tsx
+++ b/ui-v2/src/components/artifacts/artifact-card.tsx
@@ -11,6 +11,13 @@ export type ArtifactsCardProps = {
 	compact?: boolean;
 };

+const getArtifactId = (artifact: Artifact | ArtifactCollection): string => {
+	if ("latest_id" in artifact) {
+		return artifact.latest_id;
+	}
+	return artifact.id ?? "";
+};
+
 export const ArtifactCard = ({
 	artifact,
 	compact = false,
@@ -18,8 +25,21 @@ export const ArtifactCard = ({
 	const createdAtDate = useMemo(() => {
 		return formatDate(new Date(artifact.created ?? ""), "dateTime");
 	}, [artifact.created]);
+
+	const hasKey = Boolean(artifact.key);
+
+	const linkProps = hasKey
+		? ({
+				to: "/artifacts/key/$key",
+				params: { key: artifact.key as string },
+			} as const)
+		: ({
+				to: "/artifacts/artifact/$id",
+				params: { id: getArtifactId(artifact) },
+			} as const);
+
 	return (
-		<Link to="/artifacts/key/$key" params={{ key: artifact.key ?? "" }}>
+		<Link {...linkProps}>
 			<Card className="hover:shadow-lg hover:border-primary">
 				<CardHeader>
 					<p className="text-sm font-bold text-muted-foreground">
PATCH

# Verify the patch was applied
if ! grep -q "getArtifactId" ui-v2/src/components/artifacts/artifact-card.tsx; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Fix applied successfully"
