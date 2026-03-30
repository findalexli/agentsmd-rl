#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

cat > /tmp/patch.diff << 'PATCH'
diff --git a/client/js/src/utils/submit.ts b/client/js/src/utils/submit.ts
index 7a95947c48..5694837c73 100644
--- a/client/js/src/utils/submit.ts
+++ b/client/js/src/utils/submit.ts
@@ -237,12 +237,15 @@ export function submit(
 						time: new Date()
 					});
 				} else {
+					const is_connection_error =
+						output?.error === BROKEN_CONNECTION_MSG;
 					fire_event({
 						type: "status",
 						stage: "error",
 						endpoint: _endpoint,
 						fn_index,
 						message: output.error,
+						broken: is_connection_error,
 						queue: false,
 						time: new Date()
 					});
@@ -464,11 +467,15 @@ export function submit(
 					});
 					close();
 				} else if (status !== 200) {
+					const is_connection_error =
+						response?.error === BROKEN_CONNECTION_MSG;
 					fire_event({
 						type: "status",
 						stage: "error",
-						broken: false,
-						message: response.detail,
+						broken: is_connection_error,
+						message: is_connection_error
+							? BROKEN_CONNECTION_MSG
+							: response.detail || response.error,
 						queue: true,
 						endpoint: _endpoint,
 						fn_index,
diff --git a/js/core/src/Blocks.svelte b/js/core/src/Blocks.svelte
index 58de19813e..3efab27035 100644
--- a/js/core/src/Blocks.svelte
+++ b/js/core/src/Blocks.svelte
@@ -104,6 +104,7 @@
 	});

 	let messages: (ToastMessage & { fn_index: number })[] = $state([]);
+	let reconnect_interval: ReturnType<typeof setInterval> | null = null;

 	function gradio_event_dispatcher(
 		id: number,
@@ -206,6 +207,35 @@
 		api_calls = [...api_calls, last_api_call];
 	};

+	function handle_connection_lost(): void {
+		messages = messages.filter((m) => m.type !== "error");
+
+		++_error_id;
+		messages.push({
+			title: "Connection Lost",
+			message: LOST_CONNECTION_MESSAGE,
+			fn_index: -1,
+			type: "error",
+			id: _error_id,
+			duration: null,
+			visible: true
+		});
+
+		reconnect_interval = setInterval(async () => {
+			try {
+				const status = await app.reconnect();
+				if (status === "connected" || status === "changed") {
+					clearInterval(reconnect_interval!);
+					reconnect_interval = null;
+					window.location.reload();
+				}
+			} catch (e) {
+				// server still unreachable
+				console.debug(e);
+			}
+		}, 2000);
+	}
+
 	let dep_manager = new DependencyManager(
 		dependencies,
 		app,
@@ -213,7 +243,8 @@
 		app_tree.get_state.bind(app_tree),
 		app_tree.rerender.bind(app_tree),
 		new_message,
-		add_to_api_calls
+		add_to_api_calls,
+		handle_connection_lost
 	);

 	$effect(() => {
@@ -426,6 +457,7 @@
 		return () => {
 			mut.disconnect();
 			res.disconnect();
+			if (reconnect_interval) clearInterval(reconnect_interval);
 		};
 	});

diff --git a/js/core/src/dependency.ts b/js/core/src/dependency.ts
index ead2f3030f..0c3508b5cc 100644
--- a/js/core/src/dependency.ts
+++ b/js/core/src/dependency.ts
@@ -205,8 +205,10 @@ export class DependencyManager {
 	get_state_cb: GetStateCallback;
 	rerender_cb: RerenderCallback;
 	log_cb: LogCallback;
+	on_connection_lost_cb: () => void;

 	loading_stati = new LoadingStatus();
+	connection_lost = false;

 	constructor(
 		dependencies: IDependency[],
@@ -226,13 +228,15 @@ export class DependencyManager {
 			duration?: number | null,
 			visible?: boolean
 		) => void,
-		add_to_api_calls: (payload: Payload) => void
+		add_to_api_calls: (payload: Payload) => void,
+		on_connection_lost_cb: () => void
 	) {
 		this.add_to_api_calls = add_to_api_calls;
 		this.log_cb = log_cb;
 		this.update_state_cb = update_state_cb;
 		this.get_state_cb = get_state_cb;
 		this.rerender_cb = rerender_cb;
+		this.on_connection_lost_cb = on_connection_lost_cb;
 		this.client = client;
 		this.reload(
 			dependencies,
@@ -318,6 +322,7 @@ export class DependencyManager {
 	 * @returns a value if there is no backend fn, a 'submission' if there is a backend fn, or null if there is no dependency
 	 */
 	async dispatch(event_meta: DispatchFunction | DispatchEvent): Promise<void> {
+		if (this.connection_lost) return;
 		let deps: Dependency[] | undefined;
 		if (event_meta.type === "fn") {
 			const dep = this.dependencies_by_fn.get(event_meta.fn_index!);
@@ -484,6 +489,19 @@ export class DependencyManager {
 								});
 								this.update_loading_stati_state();
 							} else if (result.stage === "error") {
+								if (result.broken || result.session_not_found) {
+									if (!this.connection_lost) {
+										this.connection_lost = true;
+										this.on_connection_lost_cb();
+									}
+									this.loading_stati.update({
+										status: "complete",
+										fn_index: dep.id,
+										stream_state: null
+									});
+									this.update_loading_stati_state();
+									break submit_loop;
+								}
 								if (Array.isArray(result?.message)) {
 									result.message.forEach((m: ValidationError, i) => {
 										this.update_state_cb(
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
