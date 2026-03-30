#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

git apply - <<'PATCH'
diff --git a/js/audio/shared/MinimalAudioPlayer.svelte b/js/audio/shared/MinimalAudioPlayer.svelte
index 47034729b6..177bb48c77 100644
--- a/js/audio/shared/MinimalAudioPlayer.svelte
+++ b/js/audio/shared/MinimalAudioPlayer.svelte
@@ -16,10 +16,10 @@

 	let container: HTMLDivElement;
 	let waveform: WaveSurfer | undefined;
-	let playing = false;
-	let duration = 0;
-	let currentTime = 0;
-	let waveform_ready = false;
+	let playing = $state(false);
+	let duration = $state(0);
+	let currentTime = $state(0);
+	let waveform_ready = $state(false);

 	let resolved_src = $derived(value.url);

diff --git a/js/audio/shared/MinimalAudioRecorder.svelte b/js/audio/shared/MinimalAudioRecorder.svelte
index b788ab576d..27c7f1ddf6 100644
--- a/js/audio/shared/MinimalAudioRecorder.svelte
+++ b/js/audio/shared/MinimalAudioRecorder.svelte
@@ -33,14 +33,14 @@

 	let container: HTMLDivElement;
 	let waveform: WaveSurfer | undefined;
-	let record: RecordPlugin | undefined;
-	let seconds = 0;
+	let record: RecordPlugin | undefined = $state();
+	let seconds = $state(0);
 	let interval: NodeJS.Timeout;
-	let is_recording = false;
-	let has_started = false;
-	let mic_devices: MediaDeviceInfo[] = [];
-	let selected_device_id: string = "";
-	let show_device_selection = false;
+	let is_recording = $state(false);
+	let has_started = $state(false);
+	let mic_devices: MediaDeviceInfo[] = $state([]);
+	let selected_device_id: string = $state("");
+	let show_device_selection = $state(false);

 	const start_interval = (): void => {
 		clearInterval(interval);
@@ -168,9 +168,15 @@
 		has_started === false &&
 		mic_devices.length <= 1
 	) {
-		record.startMic({ deviceId: selected_device_id }).then(() => {
-			record?.startRecording();
-		});
+		record
+			.startMic({ deviceId: selected_device_id })
+			.then(() => {
+				record?.startRecording();
+			})
+			.catch((err) => {
+				console.error("Failed to access microphone:", err);
+				onclear?.();
+			});
 	} else if (!recording && is_recording && record) {
 		record.stopRecording();
 		seconds = 0;
@@ -229,7 +235,11 @@
 	<button
 		class="stop-button"
 		onclick={() => {
-			recording = false;
+			if (is_recording) {
+				recording = false;
+			} else {
+				onclear?.();
+			}
 		}}
 		aria-label="Stop recording"
 	>
PATCH
