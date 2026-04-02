#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if the no-op dispatcher override is already removed, skip
if ! grep -q 'GRADIO_BROWSER_TEST' js/utils/src/utils.svelte.ts; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/spa/vite.config.ts b/js/spa/vite.config.ts
index a3c902233f..144b00e9df 100644
--- a/js/spa/vite.config.ts
+++ b/js/spa/vite.config.ts
@@ -172,14 +172,19 @@ export default defineConfig(({ mode, isSsrBuild }) => {
 			},
 			browser: {
 				enabled: true,
-				provider: playwright(),
+				provider: playwright({
+					contextOptions: {
+						permissions: [
+							"camera",
+							"microphone",
+							"clipboard-read",
+							"clipboard-write"
+						]
+					}
+				}),
 				instances: [
 					{
-						browser: "chromium",
-						// headless: false,
-						context: {
-							permissions: ["camera", "microphone"]
-						}
+						browser: "chromium"
 					}
 				]
 			}
diff --git a/js/textbox/shared/Textbox.svelte b/js/textbox/shared/Textbox.svelte
index dc22ed814e..994d790106 100644
--- a/js/textbox/shared/Textbox.svelte
+++ b/js/textbox/shared/Textbox.svelte
@@ -73,6 +73,7 @@
 		oncopy?: (data: CopyData) => void;
 	} = $props();

+	// svelte-ignore non_reactive_update
 	let el: HTMLTextAreaElement | HTMLInputElement;
 	let copied = $state(false);
 	let timer: NodeJS.Timeout;
@@ -81,6 +82,7 @@
 	let user_has_scrolled_up = $state(false);
 	let _max_lines = $state(1);

+	// svelte-ignore state_referenced_locally
 	const show_textbox_border = !submit_btn;

 	$effect(() => {
@@ -145,8 +147,12 @@

 	async function handle_copy(): Promise<void> {
 		if ("clipboard" in navigator) {
-			await navigator.clipboard.writeText(value);
-			oncopy?.({ value: value });
+			try {
+				await navigator.clipboard.writeText(value);
+				oncopy?.({ value: value });
+			} catch (e) {
+				console.error("COPYING CLIPBOARD FAILED", e);
+			}
 			copy_feedback();
 		}
 	}
@@ -283,10 +289,9 @@
 	}
 </script>

-<!-- svelte-ignore a11y-autofocus -->
 <label class:container class:show_textbox_border>
 	{#if show_label && buttons && buttons.length > 0}
-		<IconButtonWrapper {buttons} {oncustombuttonclick}>
+		<IconButtonWrapper {buttons} on_custom_button_click={oncustombuttonclick}>
 			{#if buttons.some((btn) => typeof btn === "string" && btn === "copy")}
 				<IconButton
 					Icon={copied ? Check : Copy}
@@ -306,6 +311,7 @@
 	<div class="input-container">
 		{#if lines === 1 && _max_lines === 1}
 			{#if type === "text"}
+				<!-- svelte-ignore a11y_autofocus -->
 				<input
 					data-testid="textbox"
 					type="text"
@@ -332,6 +338,7 @@
 					lang={html_attributes?.lang}
 				/>
 			{:else if type === "password"}
+				<!-- svelte-ignore a11y_autofocus -->
 				<input
 					data-testid="password"
 					type="password"
@@ -356,6 +363,7 @@
 					lang={html_attributes?.lang}
 				/>
 			{:else if type === "email"}
+				<!-- svelte-ignore a11y_autofocus -->
 				<input
 					data-testid="textbox"
 					type="email"
@@ -381,6 +389,7 @@
 				/>
 			{/if}
 		{:else}
+			<!-- svelte-ignore a11y_autofocus -->
 			<textarea
 				data-testid="textbox"
 				use:text_area_resize={value}
@@ -407,13 +416,14 @@
 				tabindex={html_attributes?.tabindex}
 				enterkeyhint={html_attributes?.enterkeyhint}
 				lang={html_attributes?.lang}
-			/>
+			></textarea>
 		{/if}
 		{#if submit_btn}
 			<button
 				class="submit-button"
 				class:padded-button={submit_btn !== true}
 				onclick={handle_submit}
+				data-testid="submit-button"
 			>
 				{#if submit_btn === true}
 					<Send />
@@ -427,6 +437,7 @@
 				class="stop-button"
 				class:padded-button={stop_btn !== true}
 				onclick={handle_stop}
+				data-testid="stop-button"
 			>
 				{#if stop_btn === true}
 					<Square fill="none" stroke_width={2.5} />
diff --git a/js/tootils/src/index.ts b/js/tootils/src/index.ts
index 129c2f6691..5ac7a8723c 100644
--- a/js/tootils/src/index.ts
+++ b/js/tootils/src/index.ts
@@ -172,7 +172,6 @@ export interface ActionReturn<
 }

 export { expect } from "@playwright/test";
-export * from "./render";

 export const drag_and_drop_file = async (
 	page: Page,
diff --git a/js/tootils/src/render.ts b/js/tootils/src/render.ts
index 7170166a8e..6a13767251 100644
--- a/js/tootils/src/render.ts
+++ b/js/tootils/src/render.ts
@@ -10,10 +10,9 @@ import type {
 	queries,
 	Queries,
 	BoundFunction,
-	EventType,
-	FireObject
+	EventType
 } from "@testing-library/dom";
-import { spy, type Spy } from "tinyspy";
+import { vi, type Mock } from "vitest";
 import { GRADIO_ROOT, allowed_shared_props } from "@gradio/utils";
 import type { LoadingStatus } from "@gradio/statustracker";
 import { _ } from "svelte-i18n";
@@ -62,8 +61,9 @@ export async function render<
 	_container?: HTMLElement
 ): Promise<
 	RenderResult<T> & {
-		listen: typeof listen;
-		wait_for_event: typeof wait_for_event;
+		listen: (event_name: string) => Mock;
+		set_data: (data: Record<string, any>) => Promise<void>;
+		get_data: () => Promise<Record<string, any>>;
 	}
 > {
 	let container: HTMLElement;
@@ -81,16 +81,42 @@ export async function render<

 	const id = Math.floor(Math.random() * 1000000);

-	const mockRegister = (): void => {};
+	let component_set_data: (data: Record<string, any>) => void;
+	let component_get_data: () => Promise<Record<string, any>>;

-	const mockDispatcher = (_id: number, event: string, data: any): void => {
-		const e = new CustomEvent("gradio", {
-			bubbles: true,
-			detail: { data, id: _id, event }
-		});
-		target.dispatchEvent(e);
+	const mock_register = (
+		_id: number,
+		set_data: (data: Record<string, any>) => void,
+		get_data: () => Promise<Record<string, any>>
+	): void => {
+		component_set_data = set_data;
+		component_get_data = get_data;
 	};

+	const event_listeners = new Map<string, Set<(data: any) => void>>();
+
+	function notify_listeners(event: string, data: any): void {
+		const listeners = event_listeners.get(event);
+		if (listeners) {
+			for (const listener of listeners) {
+				listener(data);
+			}
+		}
+	}
+
+	const dispatcher = (_id: number, event: string, data: any): void => {
+		notify_listeners(event, data);
+	};
+
+	function listen(event_name: string): Mock {
+		const fn = vi.fn();
+		if (!event_listeners.has(event_name)) {
+			event_listeners.set(event_name, new Set());
+		}
+		event_listeners.get(event_name)!.add(fn);
+		return fn;
+	}
+
 	const i18nFormatter = (s: string | null | undefined): string => s ?? "";

 	const shared_props_obj: Record<string, any> = {
@@ -105,8 +131,8 @@ export async function render<
 		api_prefix: "",
 		server: {} as any,
 		show_label: true,
-		register_component: () => {},
-		dispatcher: () => {}
+		register_component: mock_register,
+		dispatcher
 	};

 	const component_props_obj: Record<string, any> = {
@@ -134,10 +160,7 @@ export async function render<

 	const component = mount(ComponentConstructor, {
 		target,
-		props: componentProps,
-		context: new Map([
-			[GRADIO_ROOT, { register: mockRegister, dispatcher: mockDispatcher }]
-		])
+		props: componentProps
 	}) as T;

 	containerCache.set(container, { target, component });
@@ -145,11 +168,20 @@ export async function render<

 	await tick();

-	type event_name = string;
-
 	return {
 		container,
 		component,
+		listen,
+		set_data: async (data: Record<string, any>) => {
+			const r = component_set_data(data);
+			// we double tick here because the event may trigger state update inside  the component
+			// the event may _only_ be fired in response to these state updates.
+			// so we want everything to settle before returning and continuing with the test.
+			await tick();
+			await tick();
+			return r;
+		},
+		get_data: () => component_get_data(),
 		//@ts-ignore
 		debug: (el = container): void => console.warn(prettyDOM(el)),
 		unmount: (): void => {
@@ -179,6 +211,13 @@ export function cleanup(): void {
 	Array.from(containerCache.keys()).forEach(cleanupAtContainer);
 }

+type AsyncFireObject = {
+	[K in EventType]: (
+		element: Document | Element | Window | Node,
+		options?: object
+	) => Promise<boolean>;
+};
+
 export const fireEvent = Object.keys(dtlFireEvent).reduce((acc, key) => {
 	const _key = key as EventType;
 	return {
@@ -188,11 +227,15 @@ export const fireEvent = Object.keys(dtlFireEvent).reduce((acc, key) => {
 			options: object = {}
 		): Promise<boolean> => {
 			const event = dtlFireEvent[_key](element, options);
+			// we double tick here because the event may trigger state update inside  the component
+			// the event may _only_ be fired in response to these state updates.
+			// so we want everything to settle before returning and continuing with the test.
+			await tick();
 			await tick();
 			return event;
 		}
 	};
-}, {} as FireObject);
+}, {} as AsyncFireObject);

 export type FireFunction = (
 	element: Document | Element | Window,
@@ -200,7 +243,3 @@ export type FireFunction = (
 ) => Promise<boolean>;

 export * from "@testing-library/dom";
-
-function isCustomEvent(event: Event): event is CustomEvent {
-	return "detail" in event;
-}
diff --git a/js/utils/src/utils.svelte.ts b/js/utils/src/utils.svelte.ts
index a6bb30b592..127e8dec1f 100644
--- a/js/utils/src/utils.svelte.ts
+++ b/js/utils/src/utils.svelte.ts
@@ -409,12 +409,6 @@ export class Gradio<T extends object = {}, U extends object = {}> {
 		}

 		this.load_component = this.shared.load_component;
-		// @ts-ignore
-		if (!is_browser || _props.props?.__GRADIO_BROWSER_TEST__) {
-			// Provide a no-op dispatcher for test environments
-			this.dispatcher = () => {};
-			return;
-		}

 		this.register_component = this.shared.register_component || (() => {});
 		this.dispatcher = this.shared.dispatcher || (() => {});

PATCH

echo "Patch applied successfully."
