#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# ── 1. submit.ts: non-queue error path — add dynamic broken flag ────────────
# Replace the hardcoded fire_event block (lines ~240-248) with one that checks
# BROKEN_CONNECTION_MSG and sets broken dynamically.
node -e "
const fs = require('fs');
const f = 'client/js/src/utils/submit.ts';
let s = fs.readFileSync(f, 'utf8');

// Non-queue error path: add is_connection_error check
const old1 = \`} else {
							fire_event({
								type: \"status\",
								stage: \"error\",
								endpoint: _endpoint,
								fn_index,
								message: output.error,
								queue: false,
								time: new Date()
							});\`;
const new1 = \`} else {
							const is_connection_error =
								output?.error === BROKEN_CONNECTION_MSG;
							fire_event({
								type: \"status\",
								stage: \"error\",
								endpoint: _endpoint,
								fn_index,
								message: output.error,
								broken: is_connection_error,
								queue: false,
								time: new Date()
							});\`;

if (s.includes(old1)) {
  s = s.replace(old1, new1);
} else {
  console.log('submit.ts non-queue path: already patched or context changed');
}

// Queue/SSE error path: replace broken:false with dynamic check
const old2 = \`} else if (status !== 200) {
						fire_event({
							type: \"status\",
							stage: \"error\",
							broken: false,
							message: response.detail,
							queue: true,
							endpoint: _endpoint,
							fn_index,
							time: new Date(),
							visible: true
						});\`;
const new2 = \`} else if (status !== 200) {
						const is_connection_error =
							response?.error === BROKEN_CONNECTION_MSG;
						fire_event({
							type: \"status\",
							stage: \"error\",
							broken: is_connection_error,
							message: is_connection_error
								? BROKEN_CONNECTION_MSG
								: response.detail || response.error,
							queue: true,
							endpoint: _endpoint,
							fn_index,
							time: new Date(),
							visible: true
						});\`;

if (s.includes(old2)) {
  s = s.replace(old2, new2);
} else {
  console.log('submit.ts queue path: already patched or context changed');
}

fs.writeFileSync(f, s);
console.log('submit.ts patched');
"

# ── 2. dependency.ts: add connection_lost tracking and callback ─────────────
node -e "
const fs = require('fs');
const f = 'js/core/src/dependency.ts';
let s = fs.readFileSync(f, 'utf8');

// Add on_connection_lost_cb and connection_lost properties
const old1 = \`log_cb: LogCallback;

	loading_stati = new LoadingStatus();\`;
const new1 = \`log_cb: LogCallback;
	on_connection_lost_cb: () => void;

	loading_stati = new LoadingStatus();
	connection_lost = false;\`;

if (s.includes(old1)) {
  s = s.replace(old1, new1);
} else {
  console.log('dependency.ts properties: already patched or context changed');
}

// Add on_connection_lost_cb to constructor parameter list
const old2 = \`add_to_api_calls: (payload: Payload) => void
	) {\`;
const new2 = \`add_to_api_calls: (payload: Payload) => void,
		on_connection_lost_cb: () => void
	) {\`;

if (s.includes(old2)) {
  s = s.replace(old2, new2);
} else {
  console.log('dependency.ts constructor params: already patched or context changed');
}

// Assign the callback in constructor body
const old3 = \`this.add_to_api_calls = add_to_api_calls;
		this.log_cb = log_cb;\`;
const new3 = \`this.add_to_api_calls = add_to_api_calls;
		this.log_cb = log_cb;
		this.on_connection_lost_cb = on_connection_lost_cb;\`;

if (s.includes(old3)) {
  s = s.replace(old3, new3);
} else {
  console.log('dependency.ts constructor body: already patched or context changed');
}

// Add early return in dispatch method
const old4 = \`async dispatch(event_meta: DispatchFunction | DispatchEvent): Promise<void> {
		let deps: Dependency[] | undefined;\`;
const new4 = \`async dispatch(event_meta: DispatchFunction | DispatchEvent): Promise<void> {
		if (this.connection_lost) return;
		let deps: Dependency[] | undefined;\`;

if (s.includes(old4)) {
  s = s.replace(old4, new4);
} else {
  console.log('dependency.ts dispatch: already patched or context changed');
}

// Add broken/session error handling before the existing error handler
const old5 = \`} else if (result.stage === \"error\") {
									if (Array.isArray(result?.message)) {\`;
const new5 = \`} else if (result.stage === \"error\") {
									if (result.broken || result.session_not_found) {
										if (!this.connection_lost) {
											this.connection_lost = true;
											this.on_connection_lost_cb();
										}
										this.loading_stati.update({
											status: \"complete\",
											fn_index: dep.id,
											stream_state: null
										});
										this.update_loading_stati_state();
										break submit_loop;
									}
									if (Array.isArray(result?.message)) {\`;

if (s.includes(old5)) {
  s = s.replace(old5, new5);
} else {
  console.log('dependency.ts error handler: already patched or context changed');
}

fs.writeFileSync(f, s);
console.log('dependency.ts patched');
"

# ── 3. Blocks.svelte: add reconnection handler and wire it up ──────────────
node -e "
const fs = require('fs');
const f = 'js/core/src/Blocks.svelte';
let s = fs.readFileSync(f, 'utf8');

// Add reconnect_interval state variable after messages state
const old1 = \`let messages: (ToastMessage & { fn_index: number })[] = \$state([]);\`;
const new1 = \`let messages: (ToastMessage & { fn_index: number })[] = \$state([]);
	let reconnect_interval: ReturnType<typeof setInterval> | null = null;\`;

if (s.includes(old1) && !s.includes('reconnect_interval')) {
  s = s.replace(old1, new1);
} else {
  console.log('Blocks.svelte reconnect_interval: already patched or context changed');
}

// Add handle_connection_lost function before DependencyManager construction
const old2 = \`let dep_manager = new DependencyManager(\`;
const new2 = \`function handle_connection_lost(): void {
		messages = messages.filter((m) => m.type !== \"error\");

		++_error_id;
		messages.push({
			title: \"Connection Lost\",
			message: LOST_CONNECTION_MESSAGE,
			fn_index: -1,
			type: \"error\",
			id: _error_id,
			duration: null,
			visible: true
		});

		reconnect_interval = setInterval(async () => {
			try {
				const status = await app.reconnect();
				if (status === \"connected\" || status === \"changed\") {
					clearInterval(reconnect_interval!);
					reconnect_interval = null;
					window.location.reload();
				}
			} catch (e) {
				// server still unreachable
				console.debug(e);
			}
		}, 2000);
	}

	let dep_manager = new DependencyManager(\`;

if (s.includes(old2) && !s.includes('handle_connection_lost')) {
  s = s.replace(old2, new2);
} else {
  console.log('Blocks.svelte handle_connection_lost: already patched or context changed');
}

// Pass handle_connection_lost to DependencyManager constructor
const old3 = \`new_message,
		add_to_api_calls
	);\`;
const new3 = \`new_message,
		add_to_api_calls,
		handle_connection_lost
	);\`;

if (s.includes(old3)) {
  s = s.replace(old3, new3);
} else {
  console.log('Blocks.svelte DependencyManager args: already patched or context changed');
}

// Add clearInterval cleanup on teardown
const old4 = \`return () => {
			mut.disconnect();
			res.disconnect();
		};\`;
const new4 = \`return () => {
			mut.disconnect();
			res.disconnect();
			if (reconnect_interval) clearInterval(reconnect_interval);
		};\`;

if (s.includes(old4) && !s.includes('clearInterval(reconnect_interval)')) {
  s = s.replace(old4, new4);
} else {
  console.log('Blocks.svelte cleanup: already patched or context changed');
}

fs.writeFileSync(f, s);
console.log('Blocks.svelte patched');
"
