#!/bin/bash
set -e

cd /workspace/withastro-astro

# Apply the fix patch
cat <<'PATCH' | git apply
diff --git a/packages/integrations/vercel/src/serverless/middleware.ts b/packages/integrations/vercel/src/serverless/middleware.ts
index 2e63aa1..6f81f2a 100644
--- a/packages/integrations/vercel/src/serverless/middleware.ts
+++ b/packages/integrations/vercel/src/serverless/middleware.ts
@@ -127,12 +127,14 @@ export default async function middleware(request, context) {
 	const next = async () => {
 		const { vercel, ...locals } = ctx.locals;
 		const response = await fetch(new URL('/${NODE_PATH}', request.url), {
+			method: request.method,
 			headers: {
 				...Object.fromEntries(request.headers.entries()),
 				'${ASTRO_MIDDLEWARE_SECRET_HEADER}': '${middlewareSecret}',
 				'${ASTRO_PATH_HEADER}': request.url.replace(origin, ''),
 				'${ASTRO_LOCALS_HEADER}': trySerializeLocals(locals)
-			}
+			},
+			...(request.body ? { body: request.body, duplex: 'half' } : {}),
 		});
 		return new Response(response.body, {
 			status: response.status,
PATCH
