#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'fixed inset-0 z-50 bg-white dark:bg-neutral-900 lg:hidden' js/_website/src/lib/components/Header.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.changeset/tender-turtles-live.md b/.changeset/tender-turtles-live.md
new file mode 100644
index 00000000000..882ae726e4a
--- /dev/null
+++ b/.changeset/tender-turtles-live.md
@@ -0,0 +1,5 @@
+---
+"website": minor
+---
+
+feat:improve mobile menu in docs
diff --git a/js/_website/src/lib/components/Header.svelte b/js/_website/src/lib/components/Header.svelte
index b62ceb52d74..c7f0b3e1e98 100644
--- a/js/_website/src/lib/components/Header.svelte
+++ b/js/_website/src/lib/components/Header.svelte
@@ -10,15 +10,28 @@
 	import LogoDownloadMenu from "./LogoDownloadMenu.svelte";
 	import { theme } from "$lib/stores/theme";

+	const nav_links = [
+		{ label: "API", href: "/docs" },
+		{ label: "Guides", href: "/guides" },
+		{ label: "HTML Components", href: "/custom-components/html-gallery" }
+	];
+
+	const community_links = [
+		{
+			label: "File an Issue",
+			href: "https://github.com/gradio-app/gradio/issues/new/choose"
+		},
+		{ label: "Discord", href: "https://discord.gg/feTf9x3ZSB" },
+		{ label: "Github", href: "https://github.com/gradio-app/gradio" }
+	];
+
 	let click_nav = false;
 	let show_help_menu = false;
-	let show_nav = false;
 	let is_scrolled = false;
 	let ready = false;
 	let show_logo_menu = false;
 	let logo_menu_x = 0;
 	let logo_menu_y = 0;
-	$: show_nav = click_nav || $store?.lg;
 	$: current_logo = $theme === "dark" ? gradio_logo_dark : gradio_logo;

 	$: if (browser && !ready) {
@@ -69,10 +82,9 @@

 {#if ready}
 	<div
-		class:shadow={show_nav}
-		class="w-full mx-auto p-1.5 flex flex-wrap justify-between flex-row sticky top-4 items-center text-base z-40 lg:py-1.5 lg:gap-6 rounded-[10px] mb-4 transition-all duration-300 border {is_scrolled
-			? 'backdrop-blur-sm bg-gray-50/80 dark:bg-neutral-800/80 lg:w-[70%] lg:max-w-4xl lg:px-6 border-gray-200 dark:border-neutral-700'
-			: 'container lg:px-4 border-transparent'}"
+		class="w-full mx-2 lg:mx-auto p-1.5 flex justify-between flex-row sticky top-0 lg:top-4 items-center text-base z-40 lg:py-1.5 lg:rounded-[10px] mb-4 transition-all duration-300 border {is_scrolled
+			? 'backdrop-blur-sm bg-gray-50/80 dark:bg-neutral-800/80 lg:w-[70%] lg:max-w-4xl lg:px-6 border-gray-200 dark:border-neutral-700 lg:gap-3'
+			: 'container lg:px-4 border-transparent lg:gap-6'}"
 	>
 		<a
 			href="/"
@@ -81,42 +93,37 @@
 		>
 			<img src={current_logo} alt="Gradio logo" class="h-10" />
 		</a>
-		{#if !show_nav}
-			<svg
-				class="h-8 w-8 lg:hidden text-gray-900 dark:text-gray-300"
-				viewBox="-10 -10 20 20"
-				on:click={() => (click_nav = !click_nav)}
-			>
-				<rect x="-7" y="-6" width="14" height="2" fill="currentColor" />
-				<rect x="-7" y="-1" width="14" height="2" fill="currentColor" />
-				<rect x="-7" y="4" width="14" height="2" fill="currentColor" />
-			</svg>
-		{:else}
+
+		<button
+			class="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-700 transition-colors"
+			on:click={() => (click_nav = !click_nav)}
+			aria-label={click_nav ? "Close menu" : "Open menu"}
+		>
 			<svg
-				class="h-5 w-5 lg:hidden mr-2 text-gray-900 dark:text-gray-300"
-				viewBox="-10 -10 70 70"
-				width="50"
-				height="50"
+				class="h-5 w-5 text-gray-700 dark:text-gray-300"
+				fill="none"
 				stroke="currentColor"
-				stroke-width="10"
-				stroke-linecap="round"
-				on:click={() => (click_nav = !click_nav)}
+				viewBox="0 0 24 24"
 			>
-				<line x1="0" y1="0" x2="50" y2="50" />
-				<line x1="50" y1="0" x2="0" y2="50" />
+				<path
+					stroke-linecap="round"
+					stroke-linejoin="round"
+					stroke-width="2"
+					d="M4 6h16M4 12h16M4 18h16"
+				/>
 			</svg>
-		{/if}
+		</button>
+
 		<nav
-			class:hidden={!show_nav}
-			class="flex w-full flex-col gap-3 px-4 py-2 lg:flex lg:w-auto lg:flex-row lg:gap-6 text-gray-900 dark:text-gray-300 lg:items-center lg:justify-center lg:flex-1 lg:text-sm"
+			class="hidden lg:flex lg:w-auto lg:flex-row text-gray-900 dark:text-gray-300 lg:items-center lg:justify-center lg:flex-1 lg:text-sm {is_scrolled
+				? 'lg:gap-3'
+				: 'lg:gap-6'}"
 		>
-			<a class="thin-link" href="/docs">API</a>
-			<a class="thin-link" href="/guides">Guides</a>
-			<a class="thin-link" href="/custom-components/html-gallery"
-				>HTML Components</a
-			>
+			{#each nav_links as { label, href }}
+				<a class="thin-link" {href}>{label}</a>
+			{/each}
 			<div
-				class="help-menu-container flex flex-col gap-3 lg:group lg:relative lg:flex lg:cursor-pointer lg:items-center lg:gap-3"
+				class="help-menu-container lg:group lg:relative lg:flex lg:cursor-pointer lg:items-center lg:gap-3"
 			>
 				<button
 					type="button"
@@ -124,67 +131,118 @@
 					on:click={() => (show_help_menu = !show_help_menu)}
 				>
 					<span>Community</span>
-					{#if show_help_menu}
-						<svg
-							class="h-4 w-4 text-gray-900 dark:text-gray-300 pointer-events-none"
-							xmlns="http://www.w3.org/2000/svg"
-							viewBox="0 0 20 20"
-							fill="currentColor"
-						>
-							<path
-								d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"
-								transform="scale (1, -1)"
-								transform-origin="center"
-							/>
-						</svg>
-					{:else}
-						<svg
-							class="h-4 w-4 text-gray-900 dark:text-gray-300 pointer-events-none"
-							xmlns="http://www.w3.org/2000/svg"
-							viewBox="0 0 20 20"
-							fill="currentColor"
-						>
-							<path
-								d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"
-							/>
-						</svg>
-					{/if}
+					<svg
+						class="h-4 w-4 text-gray-900 dark:text-gray-300 pointer-events-none transition-transform {show_help_menu
+							? 'rotate-180'
+							: ''}"
+						xmlns="http://www.w3.org/2000/svg"
+						viewBox="0 0 20 20"
+						fill="currentColor"
+					>
+						<path
+							d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"
+						/>
+					</svg>
 				</button>
 				{#if show_help_menu}
 					<div
-						class="help-menu flex flex-col gap-0 lg:absolute lg:top-9 lg:w-48 bg-white dark:bg-neutral-800 lg:backdrop-blur-sm lg:shadow-lg lg:group-hover:flex lg:sm:right-0 lg:rounded-lg border border-gray-200 dark:border-neutral-700"
+						class="help-menu absolute top-9 w-48 bg-white dark:bg-neutral-800 backdrop-blur-sm shadow-lg right-0 rounded-lg border border-gray-200 dark:border-neutral-700 flex flex-col gap-0"
 					>
-						<a
-							class="inline-block pl-8 lg:px-4 lg:pl-4 lg:py-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 lg:hover:bg-gray-100/80 dark:lg:hover:bg-neutral-700/50 transition-colors text-sm"
-							href="https://github.com/gradio-app/gradio/issues/new/choose"
-							target="_blank">File an Issue</a
-						>
-						<a
-							class="inline-block pl-8 lg:px-4 lg:pl-4 lg:py-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 lg:hover:bg-gray-100/80 dark:lg:hover:bg-neutral-700/50 transition-colors text-sm"
-							target="_blank"
-							href="https://discord.gg/feTf9x3ZSB">Discord</a
-						>
-						<!-- <a
-						class="inline-block pl-8 lg:px-4 lg:pl-4 lg:py-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 lg:hover:bg-gray-100/80 dark:lg:hover:bg-neutral-700/50 transition-colors text-sm"
-						target="_blank"
-						href="https://gradio.curated.co/">Newsletter</a
-					> -->
-						<a
-							class="inline-block pl-8 lg:px-4 lg:pl-4 lg:py-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 lg:hover:bg-gray-100/80 dark:lg:hover:bg-neutral-700/50 transition-colors text-sm"
-							target="_blank"
-							href="https://github.com/gradio-app/gradio"
-						>
-							Github
-						</a>
+						{#each community_links as { label, href }, i}
+							<a
+								class="px-4 py-2.5 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100/80 dark:hover:bg-neutral-700/50 transition-colors text-sm {i ===
+								0
+									? 'rounded-t-lg'
+									: ''} {i === community_links.length - 1
+									? 'rounded-b-lg'
+									: ''}"
+								{href}
+								target="_blank">{label}</a
+							>
+						{/each}
 					</div>
 				{/if}
 			</div>
 		</nav>
+
 		<div class="hidden lg:flex items-center gap-4 lg:flex-shrink-0">
 			<Search />
 			<ThemeToggle />
 		</div>
 	</div>
+
+	{#if click_nav}
+		<div class="fixed inset-0 z-50 bg-white dark:bg-neutral-900 lg:hidden">
+			<div
+				class="container mx-2 lg:mx-auto flex flex-col h-full p-1.5 border border-transparent"
+			>
+				<div
+					class="flex justify-between items-center pb-4 border-b border-gray-100 dark:border-neutral-800"
+				>
+					<a href="/" on:click={() => (click_nav = false)}>
+						<img src={current_logo} alt="Gradio logo" class="h-10" />
+					</a>
+					<button
+						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors"
+						on:click={() => (click_nav = false)}
+						aria-label="Close menu"
+					>
+						<svg
+							class="h-5 w-5 text-gray-700 dark:text-gray-300"
+							fill="none"
+							stroke="currentColor"
+							viewBox="0 0 24 24"
+						>
+							<path
+								stroke-linecap="round"
+								stroke-linejoin="round"
+								stroke-width="2"
+								d="M6 18L18 6M6 6l12 12"
+							/>
+						</svg>
+					</button>
+				</div>
+
+				<nav
+					class="flex flex-col flex-1 overflow-y-auto py-4 text-gray-900 dark:text-gray-100"
+				>
+					{#each nav_links as { label, href }}
+						<a
+							{href}
+							on:click={() => (click_nav = false)}
+							class="py-4 text-lg border-b border-gray-100 dark:border-neutral-800 hover:text-orange-500 transition-colors"
+							>{label}</a
+						>
+					{/each}
+
+					<div class="py-4 border-b border-gray-100 dark:border-neutral-800">
+						<span
+							class="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500"
+							>Community</span
+						>
+						<div class="flex flex-col mt-3 gap-1">
+							{#each community_links as { label, href }}
+								<a
+									{href}
+									target="_blank"
+									on:click={() => (click_nav = false)}
+									class="py-2.5 text-base text-gray-700 dark:text-gray-300 hover:text-orange-500 transition-colors"
+									>{label}</a
+								>
+							{/each}
+						</div>
+					</div>
+				</nav>
+
+				<div
+					class="py-4 border-t border-gray-100 dark:border-neutral-800 flex items-center gap-4"
+				>
+					<Search />
+					<ThemeToggle />
+				</div>
+			</div>
+		</div>
+	{/if}
 {/if}

 <LogoDownloadMenu bind:show={show_logo_menu} x={logo_menu_x} y={logo_menu_y} />

PATCH

echo "Patch applied successfully."
