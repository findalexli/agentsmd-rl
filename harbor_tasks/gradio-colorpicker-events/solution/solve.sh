#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

git apply - <<'PATCH'
diff --git a/js/colorpicker/shared/Colorpicker.svelte b/js/colorpicker/shared/Colorpicker.svelte
index 51a94449f5..039028c475 100644
--- a/js/colorpicker/shared/Colorpicker.svelte
+++ b/js/colorpicker/shared/Colorpicker.svelte
@@ -164,25 +164,22 @@
 	class="dialog-button"
 	style:background={value}
 	{disabled}
-	on:click={() => {
+	onfocus={on_focus}
+	onblur={on_blur}
+	onclick={() => {
 		update_mouse_from_color(value);
 		dialog_open = !dialog_open;
 	}}
 />

-<svelte:window on:mousemove={handle_move} on:mouseup={handle_end} />
+<svelte:window onmousemove={handle_move} onmouseup={handle_end} />

 {#if dialog_open}
-	<div
-		class="color-picker"
-		on:focus
-		on:blur
-		use:click_outside={handle_click_outside}
-	>
+	<div class="color-picker" use:click_outside={handle_click_outside}>
 		<!-- svelte-ignore a11y-no-static-element-interactions -->
 		<div
 			class="color-gradient"
-			on:mousedown={handle_sl_down}
+			onmousedown={handle_sl_down}
 			style="--hue:{hue}"
 			bind:this={sl_wrap}
 		>
@@ -193,7 +190,7 @@
 			/>
 		</div>
 		<!-- svelte-ignore a11y-no-static-element-interactions -->
-		<div class="hue-slider" on:mousedown={handle_hue_down} bind:this={hue_wrap}>
+		<div class="hue-slider" onmousedown={handle_hue_down} bind:this={hue_wrap}>
 			<div
 				class="marker"
 				style:background={"hsl(" + hue + ", 100%, 50%)"}
@@ -208,11 +205,16 @@
 					<input
 						type="text"
 						bind:value={color_string}
-						on:change={(e) => {
+						onchange={(e) => {
 							value = e.currentTarget.value;
 						}}
+						onkeydown={(e) => {
+							if (e.key === "Enter") {
+								on_submit();
+							}
+						}}
 					/>
-					<button class="eyedropper" on:click={request_eyedropper}>
+					<button class="eyedropper" onclick={request_eyedropper}>
 						{#if eyedropper_supported}
 							<Eyedropper />
 						{/if}
@@ -224,7 +226,7 @@
 						<button
 							class="button"
 							class:active={current_mode === value}
-							on:click={() => {
+							onclick={() => {
 								current_mode = value;
 							}}>{label}</button
 						>
PATCH
