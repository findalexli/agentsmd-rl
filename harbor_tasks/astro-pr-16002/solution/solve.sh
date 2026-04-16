#!/bin/bash
set -e

cd /workspace/astro

# Check if already applied
if grep -q "res.on('close', () => stream.destroy())" packages/integrations/partytown/src/sirv.ts; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/integrations/node/src/serve-app.ts b/packages/integrations/node/src/serve-app.ts
index d3e11264c601..e7fa0437fb3f 100644
--- a/packages/integrations/node/src/serve-app.ts
+++ b/packages/integrations/node/src/serve-app.ts
@@ -20,19 +20,24 @@ async function readErrorPageFromDisk(

 	for (const filePath of filePaths) {
 		const fullPath = path.join(client, filePath);
+		// Declare stream outside try so it's accessible in catch for cleanup.
+		let stream: ReturnType<typeof createReadStream> | undefined;
 		try {
-			const stream = createReadStream(fullPath);
+			stream = createReadStream(fullPath);
 			// Wait for the stream to open successfully or error
 			await new Promise<void>((resolve, reject) => {
-				stream.once('open', () => resolve());
-				stream.once('error', reject);
+				stream!.once('open', () => resolve());
+				stream!.once('error', reject);
 			});
 			const webStream = Readable.toWeb(stream) as ReadableStream;
 			return new Response(webStream, {
 				headers: { 'Content-Type': 'text/html; charset=utf-8' },
 			});
 		} catch {
-			// File doesn't exist or can't be read, try next pattern
+			// File doesn't exist or can't be read, try next pattern.
+			// Destroy the stream to release the file descriptor if it was
+			// partially opened before the error fired.
+			stream?.destroy();
 		}
 	}

diff --git a/packages/integrations/partytown/src/sirv.ts b/packages/integrations/partytown/src/sirv.ts
index c1e394441be4..fac4d08769f9 100644
--- a/packages/integrations/partytown/src/sirv.ts
+++ b/packages/integrations/partytown/src/sirv.ts
@@ -126,7 +126,9 @@ function send(req, res, file, stats, headers) {
 	}

 	res.writeHead(code, headers);
-	fs.createReadStream(file, opts).pipe(res);
+	const stream = fs.createReadStream(file, opts);
+	stream.pipe(res);
+	res.on('close', () => stream.destroy());
 }

 const ENCODING = {
PATCH

echo "Patch applied successfully"
