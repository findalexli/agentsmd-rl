#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'apply_prompt_edits' posthog/api/services/llm_prompt.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/posthog/api/llm_prompt.py b/posthog/api/llm_prompt.py
index 46ce564dc401..f4195b9e0860 100644
--- a/posthog/api/llm_prompt.py
+++ b/posthog/api/llm_prompt.py
@@ -30,6 +30,7 @@
 from posthog.api.routing import TeamAndOrgViewSetMixin
 from posthog.api.services.llm_prompt import (
     LLMPromptDuplicateNameConflictError,
+    LLMPromptEditError,
     LLMPromptNotFoundError,
     LLMPromptVersionConflictError,
     LLMPromptVersionLimitError,
@@ -260,7 +261,8 @@ def update_by_name(self, request: Request, prompt_name: str = "", **kwargs) -> R
                 self.team,
                 user=cast(User, request.user),
                 prompt_name=prompt_name,
-                prompt_payload=payload.validated_data["prompt"],
+                prompt_payload=payload.validated_data.get("prompt"),
+                edits=payload.validated_data.get("edits"),
                 base_version=payload.validated_data["base_version"],
             )
         except LLMPromptNotFoundError:
@@ -283,6 +285,14 @@ def update_by_name(self, request: Request, prompt_name: str = "", **kwargs) -> R
                 },
                 status=status.HTTP_400_BAD_REQUEST,
             )
+        except LLMPromptEditError as err:
+            return Response(
+                {
+                    "detail": err.message,
+                    "edit_index": err.edit_index,
+                },
+                status=status.HTTP_400_BAD_REQUEST,
+            )

         report_user_action(
             cast(User, request.user),
diff --git a/posthog/api/llm_prompt_serializers.py b/posthog/api/llm_prompt_serializers.py
index 1c8f8c15888c..8e008fb1861f 100644
--- a/posthog/api/llm_prompt_serializers.py
+++ b/posthog/api/llm_prompt_serializers.py
@@ -81,8 +81,29 @@ def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
         return attrs


+class LLMPromptEditOperationSerializer(serializers.Serializer):
+    old = serializers.CharField(
+        help_text="Text to find in the current prompt. Must match exactly once.",
+    )
+    new = serializers.CharField(
+        help_text="Replacement text.",
+    )
+
+
 class LLMPromptPublishSerializer(serializers.Serializer):
-    prompt = serializers.JSONField(help_text="Prompt payload to publish as a new version.")
+    prompt = serializers.JSONField(
+        required=False,
+        help_text="Full prompt payload to publish as a new version. Mutually exclusive with edits.",
+    )
+    edits = LLMPromptEditOperationSerializer(
+        many=True,
+        required=False,
+        help_text=(
+            "List of find/replace operations to apply to the current prompt version. "
+            "Each edit's 'old' text must match exactly once. Edits are applied sequentially. "
+            "Mutually exclusive with prompt."
+        ),
+    )
     base_version = serializers.IntegerField(
         min_value=1,
         help_text="Latest version you are editing from. Used for optimistic concurrency checks.",
@@ -91,6 +112,22 @@ class LLMPromptPublishSerializer(serializers.Serializer):
     def validate_prompt(self, value: Any) -> Any:
         return validate_prompt_payload_size(value)

+    def validate_edits(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
+        if len(value) == 0:
+            raise serializers.ValidationError("At least one edit operation is required.")
+        return value
+
+    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
+        has_prompt = "prompt" in attrs
+        has_edits = "edits" in attrs
+
+        if has_prompt and has_edits:
+            raise serializers.ValidationError("Provide either 'prompt' or 'edits', not both.")
+        if not has_prompt and not has_edits:
+            raise serializers.ValidationError("Either 'prompt' or 'edits' is required.")
+
+        return attrs
+

 class LLMPromptSerializer(serializers.ModelSerializer):
     created_by = UserBasicSerializer(read_only=True)
@@ -155,14 +192,14 @@ def validate_name(self, value: str) -> str:
     def validate_prompt(self, value: Any) -> Any:
         return validate_prompt_payload_size(value)

-    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
+    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
         team = self.context["get_team"]()
-        name = data.get("name")
+        name = attrs.get("name")

         if self.instance is None:
             if name and LLMPrompt.objects.filter(name=name, team=team, deleted=False).exists():
                 raise serializers.ValidationError({"name": "A prompt with this name already exists."}, code="unique")
-            return data
+            return attrs

         if name is not None and self.instance.name != name:
             raise serializers.ValidationError(
@@ -170,13 +207,13 @@ def validate(self, data: dict[str, Any]) -> dict[str, Any]:
                 code="immutable",
             )

-        if "prompt" in data:
+        if "prompt" in attrs:
             raise serializers.ValidationError(
                 {"prompt": "Prompt content is versioned and cannot be updated in place. Create a new version instead."},
                 code="immutable",
             )

-        return data
+        return attrs

     def create(self, validated_data: dict[str, Any]) -> LLMPrompt:
         request = self.context["request"]
diff --git a/posthog/api/services/llm_prompt.py b/posthog/api/services/llm_prompt.py
index 4b7a83370f1e..cb75cac74e57 100644
--- a/posthog/api/services/llm_prompt.py
+++ b/posthog/api/services/llm_prompt.py
@@ -1,3 +1,4 @@
+import json
 from dataclasses import dataclass
 from typing import Any

@@ -5,6 +6,7 @@
 from django.db import IntegrityError, transaction
 from django.db.models import QuerySet

+from posthog.api.llm_prompt_serializers import MAX_PROMPT_PAYLOAD_BYTES
 from posthog.exceptions_capture import capture_exception
 from posthog.models import Team, User
 from posthog.models.llm_prompt import LLMPrompt, annotate_llm_prompt_version_history_metadata
@@ -28,6 +30,58 @@ class LLMPromptVersionLimitError(Exception):
     max_version: int


+@dataclass
+class LLMPromptEditError(Exception):
+    message: str
+    edit_index: int
+
+
+def apply_prompt_edits(prompt_content: Any, edits: list[dict[str, str]]) -> Any:
+    """Apply sequential find/replace edits to a prompt.
+
+    If the prompt is a string, edits operate on it directly.
+    If it's a JSON structure, it's serialized to a string for editing then parsed back.
+    Each edit's 'old' text must match exactly once.
+    """
+    is_string = isinstance(prompt_content, str)
+    text = prompt_content if is_string else json.dumps(prompt_content, indent=2, ensure_ascii=False)
+
+    for i, edit in enumerate(edits):
+        old = edit["old"]
+        new = edit["new"]
+        count = text.count(old)
+        if count == 0:
+            raise LLMPromptEditError(
+                message="Text to replace was not found in the prompt.",
+                edit_index=i,
+            )
+        if count > 1:
+            raise LLMPromptEditError(
+                message=f"Text to replace matches {count} times — provide more context to make it unique.",
+                edit_index=i,
+            )
+        text = text.replace(old, new, 1)
+
+    result = text if is_string else None
+    if result is None:
+        try:
+            result = json.loads(text)
+        except json.JSONDecodeError as err:
+            raise LLMPromptEditError(
+                message=f"Edits produced invalid JSON: {err}",
+                edit_index=len(edits) - 1,
+            ) from err
+
+    result_bytes = len(json.dumps(result, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
+    if result_bytes > MAX_PROMPT_PAYLOAD_BYTES:
+        raise LLMPromptEditError(
+            message=f"Resulting prompt exceeds the {MAX_PROMPT_PAYLOAD_BYTES} byte size limit.",
+            edit_index=len(edits) - 1,
+        )
+
+    return result
+
+
 def get_active_prompt_queryset(team: Team) -> QuerySet[LLMPrompt]:
     return annotate_llm_prompt_version_history_metadata(
         LLMPrompt.objects.filter(team=team, deleted=False).select_related("created_by")
@@ -89,7 +143,8 @@ def publish_prompt_version(
     *,
     user: User,
     prompt_name: str,
-    prompt_payload: Any,
+    prompt_payload: Any | None = None,
+    edits: list[dict[str, str]] | None = None,
     base_version: int,
 ) -> LLMPrompt:
     with transaction.atomic():
@@ -107,11 +162,16 @@ def publish_prompt_version(
         if current_latest.version >= MAX_PROMPT_VERSION:
             raise LLMPromptVersionLimitError(max_version=MAX_PROMPT_VERSION)

+        if edits is not None:
+            resolved_payload = apply_prompt_edits(current_latest.prompt, edits)
+        else:
+            resolved_payload = prompt_payload
+
         LLMPrompt.objects.filter(pk=current_latest.pk).update(is_latest=False)
         published_prompt = LLMPrompt.objects.create(
             team=team,
             name=current_latest.name,
-            prompt=prompt_payload,
+            prompt=resolved_payload,
             version=current_latest.version + 1,
             is_latest=True,
             created_by=user,
diff --git a/products/llm_analytics/mcp/prompts.yaml b/products/llm_analytics/mcp/prompts.yaml
index af9ae7bea2d8..e6bdd933bedd 100644
--- a/products/llm_analytics/mcp/prompts.yaml
+++ b/products/llm_analytics/mcp/prompts.yaml
@@ -64,6 +64,14 @@ tools:
         title: Update prompt
         description: |
             Publish a new version of an existing LLM prompt by name. Name is immutable after creation.
+            You can either provide the full prompt content via 'prompt', or use 'edits' for incremental
+            find/replace updates. Each edit must have 'old' (text to find, must match exactly once) and
+            'new' (replacement text). Edits are applied sequentially. Only one of 'prompt' or 'edits'
+            may be provided.
+        include_params:
+            - prompt
+            - edits
+            - base_version
     prompt-duplicate:
         operation: llm_prompts_name_duplicate_create
         enabled: true
diff --git a/products/llm_analytics/skills/skills-store/SKILL.md b/products/llm_analytics/skills/skills-store/SKILL.md
index 3b91ec7be7e5..46bf4917139f 100644
--- a/products/llm_analytics/skills/skills-store/SKILL.md
+++ b/products/llm_analytics/skills/skills-store/SKILL.md
@@ -72,7 +72,10 @@ posthog:prompt-get
 { "prompt_name": "my-new-skill" }
 ```

-Then update using the version from the response:
+Then update using the version from the response.
+You can either send the full prompt, or use `edits` for incremental find/replace changes:
+
+### Full replacement

 ```json
 posthog:prompt-update
@@ -83,6 +86,24 @@ posthog:prompt-update
 }
 ```

+### Incremental edits
+
+For small changes, use `edits` instead of resending the entire prompt.
+Each edit's `old` text must match exactly once in the current version:
+
+```json
+posthog:prompt-update
+{
+  "prompt_name": "my-new-skill",
+  "edits": [
+    { "old": "old text to find", "new": "replacement text" }
+  ],
+  "base_version": 1
+}
+```
+
+Only one of `prompt` or `edits` may be provided, not both.
+
 ## Porting a local skill

 To move a skill from a local file (e.g. `~/.claude/skills/` or `.agents/skills/`) into PostHog:

PATCH

echo "Patch applied successfully."
