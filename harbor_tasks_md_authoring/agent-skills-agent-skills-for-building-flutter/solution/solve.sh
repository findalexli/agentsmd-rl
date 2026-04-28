#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "| Flutter (Dart) | Gemini Developer API | [flutter_setup.md](references/flutter_" "skills/firebase-ai-logic-basics/SKILL.md" && grep -qF "> **Choose the Right API Provider:** Always use `FirebaseAI.googleAI` (Gemini De" "skills/firebase-ai-logic-basics/references/flutter_setup.md" && grep -qF "See [references/flutter_setup.md](references/flutter_setup.md)." "skills/firebase-auth-basics/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/firebase-ai-logic-basics/SKILL.md b/skills/firebase-ai-logic-basics/SKILL.md
@@ -99,13 +99,16 @@ Consider that you do not need to hardcode model names (e.g., `gemini-flash-lite-
 | :---- | :---- | :---- |
 | Web Modular API | Gemini Developer API (Developer API) | firebase://docs/ai-logic/get-started  |
 | iOS (Swift) | Gemini Developer API | [ios_setup.md](references/ios_setup.md) |
+| Flutter (Dart) | Gemini Developer API | [flutter_setup.md](references/flutter_setup.md) |
 
 **Always use the most recent version of Gemini (gemini-flash-latest) unless another model is requested by the docs or the user. DO NOT USE gemini-1.5-flash**
 
 ## References
 
 [Web SDK code examples and usage patterns](references/usage_patterns_web.md)
 [iOS SDK code examples and usage patterns](references/ios_setup.md)
+[Flutter SDK code examples and usage patterns](references/flutter_setup.md)
+
 
 [Android (Kotlin) SDK usage patterns](references/usage_patterns_android.md)
 
diff --git a/skills/firebase-ai-logic-basics/references/flutter_setup.md b/skills/firebase-ai-logic-basics/references/flutter_setup.md
@@ -0,0 +1,79 @@
+# Flutter Setup for Firebase AI Logic
+
+This guide covers how to integrate Firebase AI Logic (Gemini API) into your Flutter applications.
+
+> [!IMPORTANT]
+> **Foundational Workflows & CLI-First Approach:**
+> 1. **Review Foundation:** Before implementing platform-specific code, ALWAYS review the foundational `firebase-basics` skill to ensure familiarity with core workflows.
+> 2. **Backend Provisioning via CLI:** Use the Firebase CLI for backend setup. Running `npx firebase-tools init ailogic` automatically enables the Gemini Developer API.
+> 3. **Client Configuration:** Use `flutterfire configure` strictly for generating `firebase_options.dart`. Avoid manual Console configuration.
+
+> [!NOTE]
+> `firebase_vertexai` has been replaced by `firebase_ai`. Always use `firebase_ai` for new projects.
+
+## Installation
+
+Add the necessary Firebase dependencies to your `pubspec.yaml`:
+
+```yaml
+dependencies:
+  flutter:
+    sdk: flutter
+  firebase_core: ^4.0.0
+  firebase_auth: ^6.0.0
+  firebase_ai: ^3.0.0
+```
+
+Run `flutter pub get` to install the packages.
+
+## Initialization
+
+Initialize Firebase and sign in (anonymously or via authenticated user) before using AI Logic.
+
+```dart
+import 'package:firebase_core/firebase_core.dart';
+import 'package:firebase_auth/firebase_auth.dart';
+import 'package:firebase_ai/firebase_ai.dart';
+
+void main() async {
+  WidgetsFlutterBinding.ensureInitialized();
+  await Firebase.initializeApp();
+  await FirebaseAuth.instance.signInAnonymously();
+  runApp(const MyApp());
+}
+```
+
+## Usage
+
+Use `FirebaseAI.googleAI` for the **Gemini Developer API**.
+
+> [!IMPORTANT]
+> **Choose the Right API Provider:** Always use `FirebaseAI.googleAI` (Gemini Developer API) as the default for prototyping and standard use. Avoid using the Vertex AI Gemini API unless your application specifically requires enterprise-grade scalability and is configured for the Blaze plan.
+
+### Text Generation
+
+```dart
+import 'package:firebase_ai/firebase_ai.dart';
+import 'package:firebase_auth/firebase_auth.dart';
+
+Future<String> generateText(String prompt) async {
+  final googleAI = FirebaseAI.googleAI(auth: FirebaseAuth.instance);
+  
+  // Use the latest Gemini Flash model
+  final model = googleAI.generativeModel(model: 'gemini-flash-latest');
+
+  final response = await model.generateContent([Content.text(prompt)]);
+  return response.text ?? 'No response';
+}
+```
+
+### Chat Session
+
+```dart
+final chat = model.startChat(history: [
+  Content.text('Hello, I am a user.'),
+  Content.model([TextPart('Hello! How can I help you today?')]),
+]);
+
+final response = await chat.sendMessage(Content.text('What is CBT?'));
+```
diff --git a/skills/firebase-auth-basics/SKILL.md b/skills/firebase-auth-basics/SKILL.md
@@ -79,6 +79,8 @@ Enable other providers in the Firebase Console.
 **Web**
 See [references/client_sdk_web.md](references/client_sdk_web.md).
 
+**Flutter**
+See [references/flutter_setup.md](references/flutter_setup.md).
 **Android (Kotlin)**
 See [references/client_sdk_android.md](references/client_sdk_android.md).
 
PATCH

echo "Gold patch applied."
