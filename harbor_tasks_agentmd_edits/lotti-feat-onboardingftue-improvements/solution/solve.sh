#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'Cover Art Nano Banana Pro' lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1a26acd2ee..87e76db5d7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,17 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0

 ## [Unreleased]

+## [0.9.811] - 2026-01-11
+### Changed
+- Gemini FTUE Streamlined: Reduced default prompts from 18 to 9 with optimized model assignments
+  - Gemini Pro: Checklists, Coding Prompts, Image Prompts (complex reasoning tasks)
+  - Gemini Flash: Audio Transcription, Task Summary, Image Analysis (fast processing)
+  - Nano Banana Pro: Cover Art generation (with reasoning mode enabled for reliable image output)
+- Gemini Setup Modal: Now dismissible by tapping outside (temporary skip)
+  - Tapping outside closes the modal but doesn't permanently dismiss it
+  - Modal will reappear on next app start, allowing users to set up later
+  - "Don't Show Again" button still permanently dismisses the prompt
+
 ## [0.9.810] - 2026-01-11
 ### Fixed
 - Flatpak: Fixed keyring access error by adding D-Bus permission for org.freedesktop.secrets
diff --git a/flatpak/com.matthiasn.lotti.metainfo.xml b/flatpak/com.matthiasn.lotti.metainfo.xml
index c7875290bf..74ef1a3866 100644
--- a/flatpak/com.matthiasn.lotti.metainfo.xml
+++ b/flatpak/com.matthiasn.lotti.metainfo.xml
@@ -31,6 +31,11 @@
   <launchable type="desktop-id">com.matthiasn.lotti.desktop</launchable>
   <icon type="stock">com.matthiasn.lotti</icon>
   <releases>
+    <release version="0.9.811" date="2026-01-11">
+      <description>
+        <p>Gemini FTUE Streamlined: Simplified the first-time user experience by reducing default prompts from 18 to 9 with optimized model assignments. Gemini Pro handles complex reasoning tasks (Checklists, Coding Prompts, Image Prompts), Gemini Flash handles fast processing (Audio Transcription, Task Summary, Image Analysis), and Nano Banana Pro handles Cover Art generation with reasoning mode enabled for reliable image output. The Gemini Setup Modal is now dismissible by tapping outside for a temporary skip - it will reappear on next app start, while "Don't Show Again" still permanently dismisses it.</p>
+      </description>
+    </release>
     <release version="0.9.810" date="2026-01-11">
       <description>
         <p>Flatpak Fixes: Resolved several console warnings in the Flatpak version. Fixed keyring access error by adding D-Bus permission for org.freedesktop.secrets, enabling secure storage to work properly. Fixed cursor theme warning by exposing host cursor theme paths. Removed invalid fontconfig overrides that caused "Cannot load default config file" errors. Added Flatpak-specific icon path to eliminate application icon warnings.</p>
diff --git a/lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart b/lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart
index ba681c2ca6..d63be1fe97 100644
--- a/lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart
+++ b/lib/features/ai/ui/settings/services/provider_prompt_setup_service.dart
@@ -838,115 +838,75 @@ extension GeminiFtueSetup on ProviderPromptSetupService {
     );
   }

-  /// Gets all prompt configurations for FTUE (9 types × 2 variants = 18 prompts).
+  /// Gets all prompt configurations for FTUE.
+  ///
+  /// Model assignments:
+  /// - Gemini Pro: Cover Art, Coding, Image Prompts, Checklists (complex reasoning)
+  /// - Gemini Flash: All other text prompts (fast processing)
+  /// - Nano Banana Pro: Image generation (cover art output)
   List<FtuePromptConfig> _getFtuePromptConfigs() {
     return const [
-      // Audio Transcription
+      // Audio Transcription -> Flash (fast processing)
       FtuePromptConfig(
         template: audioTranscriptionPrompt,
         modelVariant: 'flash',
         promptName: 'Audio Transcription Gemini Flash',
       ),
-      FtuePromptConfig(
-        template: audioTranscriptionPrompt,
-        modelVariant: 'pro',
-        promptName: 'Audio Transcription Gemini Pro',
-      ),

-      // Audio Transcription with Task Context
+      // Audio Transcription with Task Context -> Flash (fast processing)
       FtuePromptConfig(
         template: audioTranscriptionWithTaskContextPrompt,
         modelVariant: 'flash',
         promptName: 'Audio Transcription (Task Context) Gemini Flash',
       ),
-      FtuePromptConfig(
-        template: audioTranscriptionWithTaskContextPrompt,
-        modelVariant: 'pro',
-        promptName: 'Audio Transcription (Task Context) Gemini Pro',
-      ),

-      // Task Summary
+      // Task Summary -> Flash (fast processing)
       FtuePromptConfig(
         template: taskSummaryPrompt,
         modelVariant: 'flash',
         promptName: 'Task Summary Gemini Flash',
       ),
-      FtuePromptConfig(
-        template: taskSummaryPrompt,
-        modelVariant: 'pro',
-        promptName: 'Task Summary Gemini Pro',
-      ),

-      // Checklist Updates
-      FtuePromptConfig(
-        template: checklistUpdatesPrompt,
-        modelVariant: 'flash',
-        promptName: 'Checklist Gemini Flash',
-      ),
+      // Checklist Updates -> Pro (complex reasoning needed)
       FtuePromptConfig(
         template: checklistUpdatesPrompt,
         modelVariant: 'pro',
         promptName: 'Checklist Gemini Pro',
       ),

-      // Image Analysis
+      // Image Analysis -> Flash (fast processing)
       FtuePromptConfig(
         template: imageAnalysisPrompt,
         modelVariant: 'flash',
         promptName: 'Image Analysis Gemini Flash',
       ),
-      FtuePromptConfig(
-        template: imageAnalysisPrompt,
-        modelVariant: 'pro',
-        promptName: 'Image Analysis Gemini Pro',
-      ),

-      // Image Analysis in Task Context
+      // Image Analysis in Task Context -> Flash (fast processing)
       FtuePromptConfig(
         template: imageAnalysisInTaskContextPrompt,
         modelVariant: 'flash',
         promptName: 'Image Analysis (Task Context) Gemini Flash',
       ),
-      FtuePromptConfig(
-        template: imageAnalysisInTaskContextPrompt,
-        modelVariant: 'pro',
-        promptName: 'Image Analysis (Task Context) Gemini Pro',
-      ),

-      // Generate Coding Prompt
-      FtuePromptConfig(
-        template: promptGenerationPrompt,
-        modelVariant: 'flash',
-        promptName: 'Coding Prompt Gemini Flash',
-      ),
+      // Generate Coding Prompt -> Pro (complex reasoning needed)
       FtuePromptConfig(
         template: promptGenerationPrompt,
         modelVariant: 'pro',
         promptName: 'Coding Prompt Gemini Pro',
       ),

-      // Generate Image Prompt
-      FtuePromptConfig(
-        template: imagePromptGenerationPrompt,
-        modelVariant: 'flash',
-        promptName: 'Image Prompt Gemini Flash',
-      ),
+      // Generate Image Prompt -> Pro (complex reasoning needed)
       FtuePromptConfig(
         template: imagePromptGenerationPrompt,
         modelVariant: 'pro',
         promptName: 'Image Prompt Gemini Pro',
       ),

-      // Cover Art Generation (uses image model for Pro variant)
-      FtuePromptConfig(
-        template: coverArtGenerationPrompt,
-        modelVariant: 'flash',
-        promptName: 'Cover Art Gemini Flash',
-      ),
+      // Cover Art Generation -> Nano Banana Pro (image generation model)
       FtuePromptConfig(
         template: coverArtGenerationPrompt,
-        modelVariant: 'image', // Uses Nano Banana Pro
-        promptName: 'Cover Art Gemini Pro',
+        modelVariant: 'image', // Uses Nano Banana Pro for image generation
+        promptName: 'Cover Art Nano Banana Pro',
       ),
     ];
   }
@@ -1016,9 +976,9 @@ extension GeminiFtueSetup on ProviderPromptSetupService {
   /// instead of fragile name-based matching.
   ///
   /// Auto-selection rules:
-  /// - Checklist, Coding Prompt: Pro model
-  /// - Image Generation: Nano Banana Pro (image model)
-  /// - Everything else: Flash with thinking
+  /// - Checklist, Coding Prompt, Image Prompt: Pro model (complex reasoning)
+  /// - Image Generation: Nano Banana Pro (image model with reasoning enabled)
+  /// - Everything else: Flash (fast processing)
   Map<AiResponseType, List<String>> _buildFtueAutomaticPrompts(
     List<AiConfigPrompt> prompts, {
     required String flashModelId,
@@ -1039,45 +999,44 @@ extension GeminiFtueSetup on ProviderPromptSetupService {
           ?.id;
     }

-    // Audio Transcription -> Flash
+    // Audio Transcription -> Flash (fast processing)
     final audioFlash = findPromptId('audio_transcription', flashModelId);
     if (audioFlash != null) {
       map[AiResponseType.audioTranscription] = [audioFlash];
     }

-    // Image Analysis (task context) -> Flash
+    // Image Analysis (task context) -> Flash (fast processing)
     final imageFlash =
         findPromptId('image_analysis_task_context', flashModelId);
     if (imageFlash != null) {
       map[AiResponseType.imageAnalysis] = [imageFlash];
     }

-    // Task Summary -> Flash
+    // Task Summary -> Flash (fast processing)
     final summaryFlash = findPromptId('task_summary', flashModelId);
     if (summaryFlash != null) {
       map[AiResponseType.taskSummary] = [summaryFlash];
     }

-    // Checklist Updates -> Pro (needs stronger reasoning)
+    // Checklist Updates -> Pro (complex reasoning needed)
     final checklistPro = findPromptId('checklist_updates', proModelId);
     if (checklistPro != null) {
       map[AiResponseType.checklistUpdates] = [checklistPro];
     }

-    // Prompt Generation -> Pro (code prompts need stronger reasoning)
+    // Prompt Generation -> Pro (complex reasoning needed for code prompts)
     final promptGenPro = findPromptId('prompt_generation', proModelId);
     if (promptGenPro != null) {
       map[AiResponseType.promptGeneration] = [promptGenPro];
     }

-    // Image Prompt Generation -> Flash
-    final imagePromptFlash =
-        findPromptId('image_prompt_generation', flashModelId);
-    if (imagePromptFlash != null) {
-      map[AiResponseType.imagePromptGeneration] = [imagePromptFlash];
+    // Image Prompt Generation -> Pro (complex reasoning needed)
+    final imagePromptPro = findPromptId('image_prompt_generation', proModelId);
+    if (imagePromptPro != null) {
+      map[AiResponseType.imagePromptGeneration] = [imagePromptPro];
     }

-    // Image Generation -> Image model (Nano Banana Pro)
+    // Image Generation -> Nano Banana Pro (image model with reasoning enabled)
     final imageGenImage = findPromptId('cover_art_generation', imageModelId);
     if (imageGenImage != null) {
       map[AiResponseType.imageGeneration] = [imageGenImage];
diff --git a/lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart b/lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart
index 896261d9a1..78a75d1d3f 100644
--- a/lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart
+++ b/lib/features/ai/ui/settings/widgets/ftue_setup_dialog.dart
@@ -7,7 +7,7 @@ import 'package:lotti/widgets/buttons/lotti_tertiary_button.dart';
 ///
 /// Displays a preview of what will be created:
 /// - 3 models (Flash, Pro, Nano Banana Pro)
-/// - 18 prompts (Flash and Pro variants for 9 prompt types)
+/// - 9 prompts (optimized assignment: Pro for complex tasks, Flash for fast processing)
 /// - 1 category (Test Category Gemini Enabled)
 class FtueSetupDialog extends StatelessWidget {
   const FtueSetupDialog({
@@ -156,8 +156,8 @@ class FtueSetupDialog extends StatelessWidget {
           _buildPreviewItem(
             context,
             icon: Icons.chat_bubble_outline,
-            title: '18 Prompts',
-            subtitle: 'Flash & Pro variants for 9 prompt types',
+            title: '9 Prompts',
+            subtitle: 'Optimized: Pro for complex tasks, Flash for speed',
           ),
           const SizedBox(height: 8),

diff --git a/lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart b/lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart
index 38f74bb5e6..3e0a33cbe8 100644
--- a/lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart
+++ b/lib/features/ai/ui/settings/widgets/gemini_setup_prompt_modal.dart
@@ -22,7 +22,8 @@ class GeminiSetupPromptModal extends StatelessWidget {

   /// Shows the Gemini setup prompt modal.
   ///
-  /// Returns true if user chose to set up, false if dismissed.
+  /// Returns true if user chose to set up, false if dismissed permanently,
+  /// null if dismissed temporarily (by tapping outside).
   /// Callbacks are invoked after the dialog is fully closed to avoid
   /// Hero animation conflicts during navigation.
   static Future<void> show(
@@ -30,9 +31,9 @@ class GeminiSetupPromptModal extends StatelessWidget {
     required VoidCallback onSetUp,
     required VoidCallback onDismiss,
   }) async {
-    final result = await showDialog<bool>(
+    // barrierDismissible defaults to true, allowing temporary dismissal by tapping outside
+    final result = await showDialog<bool?>(
       context: context,
-      barrierDismissible: false,
       barrierColor: Colors.black87,
       builder: (dialogContext) => GeminiSetupPromptModal(
         onSetUp: () => Navigator.of(dialogContext).pop(true),
@@ -43,10 +44,15 @@ class GeminiSetupPromptModal extends StatelessWidget {
     // Use post-frame callback to invoke callbacks after dialog animation completes
     // This prevents Hero animation conflicts during navigation
     SchedulerBinding.instance.addPostFrameCallback((_) {
-      if (result ?? false) {
-        onSetUp();
-      } else {
-        onDismiss();
+      // Three states: true = set up, false = permanent dismiss, null = temporary dismiss
+      switch (result) {
+        case true:
+          onSetUp();
+        case false:
+          onDismiss();
+        case null:
+          // Tapped outside - do nothing, dialog will reappear next time
+          break;
       }
     });
   }
diff --git a/pubspec.yaml b/pubspec.yaml
index 8eee96da09..a4844e2e0d 100644
--- a/pubspec.yaml
+++ b/pubspec.yaml
@@ -1,7 +1,7 @@
 name: lotti
 description: Achieve your goals and keep your data private with Lotti.
 publish_to: 'none'
-version: 0.9.810+3617
+version: 0.9.811+3618

 msix_config:
   display_name: LottiApp
diff --git a/test/features/ai/ui/settings/inference_provider_edit_page_test.dart b/test/features/ai/ui/settings/inference_provider_edit_page_test.dart
index 96b3629bdc..93c1a3b632 100644
--- a/test/features/ai/ui/settings/inference_provider_edit_page_test.dart
+++ b/test/features/ai/ui/settings/inference_provider_edit_page_test.dart
@@ -867,9 +867,9 @@ void main() {
       await tester.pumpAndSettle();

       // Verify prompts were created
-      // FTUE creates: 3 models + 18 prompts (9 types × 2 variants)
+      // FTUE creates: 3 models + 9 prompts (optimized assignment)
       final promptsCreated = savedConfigs.whereType<AiConfigPrompt>().length;
-      expect(promptsCreated, equals(18));
+      expect(promptsCreated, equals(9));
     });

     testWidgets('skips prompt creation when user declines',
diff --git a/test/features/ai/ui/settings/widgets/ftue_setup_dialog_test.dart b/test/features/ai/ui/settings/widgets/ftue_setup_dialog_test.dart
index ec6a37fba3..077439bb02 100644
--- a/test/features/ai/ui/settings/widgets/ftue_setup_dialog_test.dart
+++ b/test/features/ai/ui/settings/widgets/ftue_setup_dialog_test.dart
@@ -28,7 +28,7 @@ void main() {

       expect(find.text('What will be created:'), findsOneWidget);
       expect(find.text('3 Models'), findsOneWidget);
-      expect(find.text('18 Prompts'), findsOneWidget);
+      expect(find.text('9 Prompts'), findsOneWidget);
       expect(find.text('1 Category'), findsOneWidget);
     });

@@ -44,7 +44,7 @@ void main() {
       expect(
           find.text('Flash, Pro, and Nano Banana Pro (image)'), findsOneWidget);
       expect(
-        find.text('Flash & Pro variants for 9 prompt types'),
+        find.text('Optimized: Pro for complex tasks, Flash for speed'),
         findsOneWidget,
       );
       expect(find.text('Test Category Gemini Enabled'), findsOneWidget);
diff --git a/test/features/ai/ui/settings/widgets/gemini_setup_prompt_modal_test.dart b/test/features/ai/ui/settings/widgets/gemini_setup_prompt_modal_test.dart
index 14da09cd0e..bb6b7c0d48 100644
--- a/test/features/ai/ui/settings/widgets/gemini_setup_prompt_modal_test.dart
+++ b/test/features/ai/ui/settings/widgets/gemini_setup_prompt_modal_test.dart
@@ -120,5 +120,47 @@ void main() {

       expect(setUpCalled, isTrue);
     });
+
+    testWidgets(
+        'tapping outside modal dismisses temporarily without calling callbacks',
+        (tester) async {
+      var setUpCalled = false;
+      var dismissCalled = false;
+
+      await tester.pumpWidget(
+        MaterialApp(
+          home: Builder(
+            builder: (context) => ElevatedButton(
+              onPressed: () {
+                GeminiSetupPromptModal.show(
+                  context,
+                  onSetUp: () => setUpCalled = true,
+                  onDismiss: () => dismissCalled = true,
+                );
+              },
+              child: const Text('Open Modal'),
+            ),
+          ),
+        ),
+      );
+
+      await tester.tap(find.text('Open Modal'));
+      await tester.pumpAndSettle();
+
+      expect(find.text('Set Up AI Features?'), findsOneWidget);
+
+      // Tap outside the modal (on the barrier)
+      await tester.tapAt(const Offset(10, 10));
+      await tester.pumpAndSettle();
+
+      // Extra pump to process the post-frame callback
+      await tester.pump();
+
+      // Modal should be dismissed but neither callback should be called
+      // This allows the modal to reappear on next app start
+      expect(find.text('Set Up AI Features?'), findsNothing);
+      expect(setUpCalled, isFalse);
+      expect(dismissCalled, isFalse);
+    });
   });
 }
diff --git a/whisper_server/README.md b/whisper_server/README.md
index bda507d12a..6d4056e04c 100644
--- a/whisper_server/README.md
+++ b/whisper_server/README.md
@@ -33,11 +33,27 @@ A high-performance, production-ready Python FastAPI server that provides local W
 ## Setup

 ### **1. Install Dependencies**
+
+Choose the requirements file for your platform:
+
 ```bash
 cd whisper_server
+
+# For CUDA GPUs (NVIDIA):
 pip install -r requirements.txt
+
+# For Apple Silicon (M1/M2/M3):
+pip install -r requirements_apple_silicon.txt
+
+# For Linux (CPU or generic):
+pip install -r requirements_linux.txt
 ```

+**Platform-specific notes**:
+- **requirements.txt**: Full CUDA support with flash attention and 8-bit quantization
+- **requirements_apple_silicon.txt**: Optimized for MPS acceleration on Apple Silicon
+- **requirements_linux.txt**: Simplified dependencies for Linux without CUDA
+
 **Note**: Some optimizations require specific hardware/software:
 - **Flash Attention**: Requires CUDA and may need compilation
 - **8-bit Quantization**: Works best with CUDA GPUs
diff --git a/whisper_server/requirements_linux.txt b/whisper_server/requirements_linux.txt
new file mode 100644
index 0000000000..db2f813858
--- /dev/null
+++ b/whisper_server/requirements_linux.txt
@@ -0,0 +1,8 @@
+torch==2.9.1
+fastapi>=0.100.0,<1.0.0
+uvicorn>=0.15.0,<1.0.0
+pydantic>=2.7.0,<3.0.0
+transformers>=4.30.0
+librosa>=0.10.0
+soundfile>=0.12.0
+audioread>=3.0.0

PATCH

echo "Patch applied successfully."
