#!/usr/bin/env bash
set -euo pipefail

TARGET="js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte"

# Idempotency: check if fix is already applied
if grep -q 'current_header_id' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte b/js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte
index af651492c5..b447ce378e 100644
--- a/js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte
+++ b/js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte
@@ -15,6 +15,7 @@
 		guide_slug: {
 			text: string;
 			href: string;
+			level: number;
 		}[];
 		guide_names: {
 			category: string;
@@ -29,6 +30,19 @@
 	let guide_names = data.guide_names;
 	let guide_slug = data.guide_slug;

+	let header_targets: { [key: string]: HTMLElement } = {};
+	let current_header_id: string = "";
+
+	$: if (y !== undefined && guide_slug.length > 0) {
+		for (const slug of guide_slug) {
+			const id = slug.href.slice(1);
+			const el = document.getElementById(id);
+			if (el && y >= el.offsetTop - 100) {
+				current_header_id = id;
+			}
+		}
+	}
+
 	const COLORS = [
 		"bg-green-50 dark:bg-green-900/30",
 		"bg-yellow-50 dark:bg-yellow-900/30",
@@ -239,7 +253,7 @@
 			{/each}
 		</div>
 	</nav>
-	<div class="w-full lg:w-8/12 mx-auto">
+	<div class="w-full lg:w-8/12 lg:min-w-0 lg:pl-8">
 		<div
 			class="flex items-center p-4 border-b border-t border-slate-900/10 lg:hidden dark:border-slate-50/[0.06]"
 		>
@@ -344,6 +358,37 @@
 			{/if}
 		</div>
 	</div>
+
+	{#if guide_slug.length > 0}
+		<div
+			class="float-right top-8 hidden sticky h-screen overflow-y-auto lg:block lg:w-2/12"
+		>
+			<div class="mx-8">
+				<a
+					class="text-sm tracking-wider font-semibold text-gray-600 dark:text-gray-300 py-2 block"
+					href="#"
+				>
+					{guide_page.pretty_name}
+				</a>
+				<ul class="space-y-2 list-none">
+					{#each guide_slug as slug}
+						<li style="padding-left: {(slug.level - 2) * 0.75}rem">
+							<a
+								bind:this={header_targets[slug.href.slice(1)]}
+								href={slug.href}
+								class="block text-sm transition-colors py-1 {current_header_id ===
+								slug.href.slice(1)
+									? 'text-orange-500 font-medium'
+									: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'}"
+							>
+								{slug.text}
+							</a>
+						</li>
+					{/each}
+				</ul>
+			</div>
+		</div>
+	{/if}
 </div>

 <svelte:window bind:scrollY={y} />

PATCH

echo "Patch applied successfully."
