#!/usr/bin/env bash
set -euo pipefail

cd /workspace/narrator-ai-cli-skill

# Idempotency guard
if grep -qF "> \u26a0\ufe0f **Language linkage**: Once the dubbing voice is confirmed, the narration sc" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: narrator-ai-cli
-version: "1.0.2"
+version: "1.0.3"
 license: MIT
 description: >-
   AI电影解说视频自动生成技能（AI解说大师 CLI Skill）。当用户需要创建电影解说视频、短剧解说、影视二创、AI配音旁白视频、film commentary、video narration、drama dubbing、movie narration时触发。内置93部电影素材、146首BGM、63种配音音色（11种语言）、90+解说模板。通过narrator-ai-cli命令行工具实现：搜片选片→选择模板→选BGM→选配音→生成文案→合成视频的全流程自动化。CLI client for Narrator AI (AI解说大师) video narration API. Use when user needs to create AI narration videos, manage narration tasks, browse dubbing/BGM/material resources, or automate video production.
@@ -235,6 +235,8 @@ narrator-ai-cli bgm list --search "单车" --json
 ### 3. Dubbing Voice
 
 > ⚠️ **Agent behavior**: Infer the target language from context; if ambiguous, ask the user before listing. Run `dubbing list --lang <language>` to filter, then present **all matching voices** (typically < 15 per language) — include name and tags. If the user has no preference, recommend **3 voices** with reasoning (e.g., "neutral tone fits documentary narration style") and wait for confirmation. Do NOT use a dubbing `id` or `dubbing_type` in any task until the user confirms both.
+>
+> ⚠️ **Language linkage**: Once the dubbing voice is confirmed, the narration script language must match. If the selected voice is **not Chinese (普通话)**, the agent MUST set the `language` parameter in the writing task (fast-writing or generate-writing) to the corresponding language — do NOT leave it at the default `"Chinese (中文)"`. Carry this language value forward from the dubbing selection step to the writing task creation step. If the user has already specified a `language` value, verify it matches the dubbing language; if they conflict, surface the mismatch and ask the user to resolve it before proceeding.
 
 ```bash
 narrator-ai-cli dubbing list --json                 # 63 voices, 11 languages
@@ -270,8 +272,8 @@ Use `learning_model_id` from template directly — **no need for popular-learnin
 
 1. Run `material list --json --page 1 --size 100`. Check `total` in the response — if `total > 100`, fetch subsequent pages until all items are retrieved. **Search programmatically using `grep -i` or `python3 -c` piped from the JSON output — do NOT rely on the terminal display, which may be truncated.** Repeat for each page until a match is found or all pages are exhausted.
 2. **Found in pre-built materials** → construct `confirmed_movie_json` from material fields (see mapping in Prerequisites § Source Files). Present the match to the user and **ask which mode**:
-   - **纯解说 / Pure narration (target_mode=1)**: `confirmed_movie_json` from material. **No `episodes_data`.**
-   - **原声混剪 / Original mix (target_mode=2)**: `confirmed_movie_json` from material + `episodes_data` using material's `srt_file_id` as `srt_oss_key`.
+   - **纯解说 / Pure narration (target_mode=1)**: Uses only movie metadata (title, synopsis, cast). Faster, no subtitle processing. Best for movies where the narration can be written from plot knowledge alone. **No `episodes_data`.**
+   - **原声混剪 / Original mix (target_mode=2)**: Uses the actual subtitle track from the material (`srt_file_id`) to align narration with the original dialogue and scenes. More authentic, closer to the source. Requires `episodes_data` with `srt_oss_key = material.srt_file_id`.
 3. **Not found in materials (known movie/drama)** → run `task search-movie` (see command below) → `target_mode=1`. Use returned `confirmed_movie_json`. **No `episodes_data`.**
 4. **Not found, user provides their own SRT (known movie)** → run `task search-movie` for `confirmed_movie_json` → `target_mode=2`. Use uploaded SRT as `srt_oss_key` in `episodes_data`.
 5. **Obscure/new drama, user provides SRT** → `target_mode=3`. `confirmed_movie_json` is optional. Use uploaded SRT in `episodes_data`.
@@ -304,40 +306,26 @@ Using the `target_mode`, `confirmed_movie_json`, and `episodes_data` determined
 
 ```bash
 # Case A1: Pre-built material found, user chose pure narration (target_mode=1)
-#   confirmed_movie_json from material data; no episodes_data
+#   No episodes_data. confirmed_movie_json mapped from material fields — see Prerequisites § Source Files.
 narrator-ai-cli task create fast-writing --json -d @request.json
 # request.json:
 # {
 #   "learning_model_id": "...",
 #   "target_mode": "1",
 #   "playlet_name": "飞驰人生",
-#   "confirmed_movie_json": {
-#     "local_title": "<material.name>",
-#     "title": "<material.title>",
-#     "year": "<material.year>",
-#     "genre": "<material.type>",
-#     "summary": "<material.story_info>",
-#     "stars": <material.character_name (parsed array)>
-#   },
+#   "confirmed_movie_json": {<mapped from material — see field mapping table in Prerequisites>},
 #   "model": "flash"
 # }
 
 # Case A2: Pre-built material found, user chose original mix (target_mode=2)
-#   confirmed_movie_json from material data; episodes_data uses material.srt_file_id
+#   episodes_data uses material.srt_file_id. confirmed_movie_json from material fields.
 narrator-ai-cli task create fast-writing --json -d @request.json
 # request.json:
 # {
 #   "learning_model_id": "...",
 #   "target_mode": "2",
 #   "playlet_name": "飞驰人生",
-#   "confirmed_movie_json": {
-#     "local_title": "<material.name>",
-#     "title": "<material.title>",
-#     "year": "<material.year>",
-#     "genre": "<material.type>",
-#     "summary": "<material.story_info>",
-#     "stars": <material.character_name (parsed array)>
-#   },
+#   "confirmed_movie_json": {<mapped from material — see field mapping table in Prerequisites>},
 #   "episodes_data": [{"srt_oss_key": "<material.srt_file_id>", "num": 1}],
 #   "model": "flash"
 # }
@@ -366,22 +354,23 @@ narrator-ai-cli task create fast-writing --json -d '{
 
 | Parameter | Type | Required | Default | Description |
 |-----------|------|----------|---------|-------------|
-| `learning_model_id` | str | One of two | - | Style model ID (from template or popular-learning) |
-| `learning_srt` | str | One of two | - | Reference SRT file_id (when no template available) |
+| `learning_model_id` | str | Exactly one (mutually exclusive with `learning_srt`) | - | Style model ID from a pre-built template or popular-learning result. **Do not provide both.** |
+| `learning_srt` | str | Exactly one (mutually exclusive with `learning_model_id`) | - | Reference SRT file_id. Only use when no template or popular-learning model is available. **Do not provide both.** |
 | `target_mode` | str | Yes | - | "1"=Hot Drama, "2"=Original Mix, "3"=New Drama |
 | `playlet_name` | str | Yes | - | Movie/drama name |
+| `playlet_num` | str | No | "1" | Episode/part number. Use `"1"` for single-episode content; increment for multi-part series. |
 | `confirmed_movie_json` | obj | mode=1,2; optional mode=3 | - | From material data (mode=2 pre-built) or `search-movie` result (mode=1, mode=2 user SRT). Never fabricate. |
-| `episodes_data` | list | mode=2,3 | - | [{srt_oss_key, num}] |
+| `episodes_data` | list | mode=2,3 | - | For fast-writing: `[{srt_oss_key, num}]`. For fast-clip-data: `[{video_oss_key, srt_oss_key, negative_oss_key, num}]` — the video fields are added at the clip-data step. |
 | `model` | str | No | "pro" | "pro" (higher quality, 15pts/char) or "flash" (faster, 5pts/char) |
-| `language` | str | No | "Chinese (中文)" | Output language |
+| `language` | str | No | "Chinese (中文)" | Output language for the narration script. **Must match the selected dubbing voice language.** If the dubbing voice is non-Chinese, this param must be set explicitly — never leave it at the default when a non-Chinese voice is selected. |
 | `perspective` | str | No | "third_person" | "first_person" or "third_person" |
 | `target_character_name` | str | 1st person | - | Required when perspective=first_person |
 | `custom_script_result_path` | str | No | - | Custom script result path |
 | `webhook_url` | str | No | - | Async callback URL |
 | `webhook_token` | str | No | - | Callback authentication token |
 | `webhook_data` | str | No | - | Passthrough data for callback |
 
-**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` until `status=2`. Extract `file_ids[0]`:
+**Output**: Creation response contains only `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. The completed task response contains `file_ids`:
 
 ```json
 {
@@ -393,7 +382,7 @@ narrator-ai-cli task create fast-writing --json -d '{
 }
 ```
 
-Save: `task_id` from creation response (for fast-clip-data `task_id` input), `file_ids[0]` (for fast-clip-data `file_id` input).
+Save: `task_id` from the **creation response** (for fast-clip-data `task_id` input). Save `file_ids[0]` from the **completed task poll response** (for fast-clip-data `file_id` input).
 
 ### Step 2: Fast Clip Data
 
@@ -416,19 +405,19 @@ narrator-ai-cli task create fast-clip-data --json -d '{
 {"code": 10000, "message": "", "data": {"task_id": ""}}
 ```
 
-Save `data.task_id`. Poll `task query <task_id> --json` until `status=2`. On success, read `task_order_num` from the task record — this is the `order_num` required for video-composing (step 3).
+Save `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. On success, read `task_order_num` from the task record — this is the `order_num` required for video-composing (step 3).
 
 ### Step 3: Video Composing
 
-**IMPORTANT**: `order_num` comes from fast-clip-data (step 2). This is the **only required parameter**.
+**IMPORTANT**: `order_num` comes from fast-clip-data (step 2) task record's task_order_num. This is the **only required parameter**.
 
 ```bash
 narrator-ai-cli task create video-composing --json -d '{
-  "order_num": "<task_order_num from step 2>"
+  "order_num": "<task_order_num>"
 }'
 ```
 
-**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` until `status=2`. Extract `video_url` from results:
+**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. Extract `video_url` from results:
 
 ```json
 {
@@ -442,78 +431,198 @@ Note: `type_name` is `video_composing` (no BGM) or `video_composing_2` (with BGM
 
 ### Step 4 (Optional): Magic Video — Visual Template
 
-> ⚠️ **Agent restriction**: Do NOT auto-create magic-video tasks. Only create when the user explicitly requests a visual template. Present available templates as options and let the user choose.
+> ⚠️ **Agent restriction**: Do NOT auto-create magic-video tasks. Only create when the user explicitly requests a visual template. Present the template catalog, explain options, let the user choose. Multiple templates can be selected — each produces a separate output video.
 
-```bash
-# List templates first
-narrator-ai-cli task templates --json
+**Visual Templates** is a value-added service applied after video composing:
+- Adds professional subtitle styles and branded layouts to the finished video
+- Multiple templates may be selected simultaneously (one output video per template)
+- Pricing: **30 points/minute** (based on output video duration)
 
-# One-stop mode (from video-composing task_id)
-narrator-ai-cli task create magic-video --json -d '{
-  "task_id": "<task_id from step 3>",
-  "template_name": ["template_name"]
-}'
+#### Template Catalog
 
-# Staged mode (from clip-data/fast-clip-data file_ids[0])
-narrator-ai-cli task create magic-video --json -d '{
-  "file_id": "<file_ids[0] from clip-data or fast-clip-data results>",
-  "template_name": ["template_name"]
-}'
+Fetch real-time template details (params, descriptions, pricing):
+
+```bash
+curl -X GET "https://openapi.jieshuo.cn/v2/task/commentary/get_magic_template_info" \
+    -H "app-key: $NARRATOR_APP_KEY"
 ```
 
-Optional: template_params (per-template params dict), mode (one_stop/staged), clip_data (JSON object for staged mode)
+Templates are organized by distribution platform and aspect ratio:
 
-**Output**: sub_tasks with rendered video URLs
+**油管 (YouTube)**
 
-## Standard Path Workflow
+| Aspect Ratio | Template Name | Configurable Params |
+|---|---|---|
+| 9:16 垂直 | 竖屏·合规剧集 | 主标题, 底部免责文案, 侧边警示语, 分集设置 |
+| 9:16 垂直 | 竖屏·柔光剧集 | 分集设置 |
+| 9:16 垂直 | 竖屏·模糊剧集 | 主标题, 分集设置 |
+| 9:16 垂直 | 竖屏·简约剧集 | 分集设置 |
+| 9:16 垂直 | 竖屏·黑金剧集 | 主标题, 副标题, 分集设置 |
+| 16:9 水平 | 横屏·沉浸剧集 | 分集设置 |
+| 16:9 水平 | 横屏·电影剧集 | 主标题, 副标题, 分集设置 |
+| 16:9 水平 | 横屏·简约剧集 | 分集设置 |
+
+**抖音 (TikTok / Douyin)**
+
+| Aspect Ratio | Template Name | Configurable Params |
+|---|---|---|
+| 1:1 矩形 | 方屏·简约剧集 | 主标题, 水印文案, 分集设置 |
+| 1:1 矩形 | 方屏·雅致剧集 | 主标题, 分集设置 |
+| 9:16 垂直 | 竖屏·流光剧集 | 顶部标语, 侧边文案, 分集设置 |
 
-### Step 0: Find Source Material
+**油管短视频 (YouTube Shorts)**
 
-> ⚠️ **Agent behavior**: Confirm the movie or drama name with the user before proceeding. Then run `material list --json --page 1 --size 100` to fetch pre-built materials. Check `total` in the response — if `total > 100`, fetch subsequent pages until all items are retrieved. **Search programmatically using `grep -i` or `python3 -c` piped from the JSON output — do NOT rely on the terminal display, which may be truncated and can miss items.**
+| Aspect Ratio | Template Name | Configurable Params |
+|---|---|---|
+| 9:16 垂直 | 竖屏·精准剧集 | 分集设置 |
+| 9:16 垂直 | 竖屏·重磅剧集 | 副标题 ⚠️, 分集设置 |
 
-```bash
-narrator-ai-cli material list --json --page 1 --size 100
-# If total > 100, fetch more pages: --page 2 --size 100, etc.
-```
+#### Template Param Reference
 
-Response structure:
+> ⚠️ **Agent behavior**: When the user selects a template, proactively walk through each of its configurable params, explain what it controls, and ask the user for a value. Only proceed to task creation once every param is confirmed or explicitly left at default.
 
-```json
-{
-  "total": 101,
-  "page": 1,
-  "size": 100,
-  "items": [
-    {
-      "id": "<material_id>",
-      "name": "极限职业",
-      "title": "Extreme Job",
-      "year": "2019",
-      "type": "喜剧片",
-      "story_info": "...",
-      "character_name": "[柳承龙 (Ryu Seung-ryong), 李荷妮 (Lee Ha-nee), ...]",
-      "cover": "https://...",
-      "video_file_id": "<video_file_id>",
-      "srt_file_id": "<srt_file_id>"
-    }
-  ]
-}
-```
+> ⚠️ **Language awareness**: All text params (`main_title`, `sub_title`, `bottom_disclaimer_text`, `vertical_text_content`, `watermark_text`, `slogan`) have **Chinese default values hardcoded in the template** and do NOT auto-adapt to the target language. When the narration target language is **not Chinese**, the agent MUST:
+> 1. **Never submit Chinese default values.** Submitting Chinese defaults will result in Chinese text appearing in a non-Chinese video — this is always wrong.
+> 2. **Proactively provide localized values for every text param in the template.** Do not ask the user whether they want localization — assume yes and act on it.
+> 3. **Translate the standard defaults to the target language and confirm with the user before submitting.** Do not skip this — even if the user hasn't mentioned it. Required translations by language:
+>    - `bottom_disclaimer_text` default `本故事纯属虚构 请勿模仿` → e.g. English: `This story is purely fictional. Do not imitate.`
+>    - `vertical_text_content` default `影视效果 请勿模仿 合理安排生活` → e.g. English: `Cinematic effects only. Do not imitate. Manage your life wisely.`
+>    - `main_title`, `sub_title`, `watermark_text`, `slogan` — if left empty, AI may still generate Chinese; proactively ask for user input or suggest a translated value.
+> 4. **This rule applies even when the user does not explicitly mention language.** The target language flows through the entire pipeline as a single chain: **dubbing voice language → narration script `language` param → magic-video template text params.** If the dubbing voice is non-Chinese, all three must be set to the matching language. Never treat these as independent decisions.
+> 5. **All user-facing questions in this section (the "Ask the user" prompts below) must be asked in the same language as the ongoing conversation.** Do not default to Chinese if the conversation is in another language.
+> 6. **Scope note**: This rule governs magic-video **template text params** only. The `language` param in fast-writing / generate-writing controls the narration script language and is handled at the writing step. Both are downstream consequences of the dubbing language selection and must be consistent.
+
+All params are optional — omitting them lets AI auto-generate where supported. The table below explains what each param does and **how to fill it appropriately**.
+
+---
+
+**`segment_count` — 分集设置** (`int`, present in all templates)
+
+Controls how the video is split into episodes:
+
+| Value | Behavior | When to use |
+|---|---|---|
+| `0` (default) | AI auto-determines episode count based on content length | Recommended for most cases; let AI decide |
+| `-1` | No splitting — output as a single video | When the source is short or the user wants one file |
+| `1`, `2`, `3`… | Force exactly N episodes | When the user has a specific series structure in mind |
+
+> Ask the user: "要分集吗？留 0 让 AI 自动判断，还是指定集数，或者 -1 不分集？"
+
+---
+
+**`main_title` — 主标题** (`string`, templates: 竖屏·合规剧集, 竖屏·模糊剧集, 竖屏·黑金剧集, 横屏·电影剧集, 方屏·简约剧集, 方屏·雅致剧集)
+
+The primary title displayed prominently on screen.
+
+- **Leave empty (recommended)**: AI generates the most fitting title from the content
+- **Fill in**: When the user wants a custom series name, channel brand name, or the AI-generated title doesn't meet their expectation
+- **Format tip**: Keep under 10–12 characters for vertical layouts; under 16 for horizontal. Avoid punctuation that may break layout.
+- ⚠️ **Non-Chinese narration**: See Language Awareness rule above — leaving empty may cause AI to generate a Chinese title.
+
+> Ask the user whether they want a custom title, or prefer AI to generate one. (Ask in the conversation language — see Language Awareness rule 5.)
+
+---
+
+**`sub_title` — 副标题** (`string`, templates: 竖屏·黑金剧集, 横屏·电影剧集, 竖屏·重磅剧集)
+
+Secondary text displayed near the main title.
+
+- **Leave empty (recommended)**: AI auto-generates a short tagline
+- **Fill in**: When the user wants a specific promotional slogan or episode label
+- ⚠️ **Special behavior in 竖屏·重磅剧集**: filling `sub_title` will **completely override the main title display** — the value you enter replaces whatever would appear as the main title. Only fill this if the user specifically wants to override the title.
+- ⚠️ **Non-Chinese narration**: See Language Awareness rule above — leaving empty may cause AI to generate a Chinese tagline.
+
+> Ask the user whether they want a custom subtitle. For 竖屏·重磅剧集, warn that filling this field will override the main title. (Ask in the conversation language — see Language Awareness rule 5.)
+
+---
+
+**`bottom_disclaimer_text` — 底部免责文案** (`string`, template: 竖屏·合规剧集 only)
+
+Disclaimer text pinned to the bottom of the screen — required for compliance on many platforms.
+
+- **Chinese narration — keep default**: Default value is `本故事纯属虚构 请勿模仿` — covers standard platform compliance requirements
+- **Non-Chinese narration — MUST translate**: The default is Chinese and will display as Chinese text in a non-Chinese video. Translate to the target language (e.g. English: `This story is purely fictional. Do not imitate.`) and confirm with the user before submitting. **Do not submit the Chinese default for non-Chinese narration.**
+- **Customize**: When the user's content has a specific legal disclaimer or the platform requires different wording
+- **Do not leave blank**: An empty value removes the disclaimer, which may cause compliance issues on distribution platforms
+
+> **Chinese narration**: "底部免责文案保留默认「本故事纯属虚构 请勿模仿」就好，有特殊合规需求才需要改。" — **Non-Chinese narration**: Translate the default to the target language, show the translated value to the user, and ask for confirmation or edits before submitting.
+
+---
+
+**`vertical_text_content` — 侧边警示语 / 侧边文案** (`string`, templates: 竖屏·合规剧集, 竖屏·流光剧集)
+
+Vertical text displayed along the side edge of the screen.
+
+- **Chinese narration — keep default**: Default is `影视效果 请勿模仿 合理安排生活` — standard compliance phrasing
+- **Non-Chinese narration — MUST translate**: The default is Chinese and will display as Chinese text in a non-Chinese video. Translate to the target language (e.g. English: `Cinematic effects only. Do not imitate. Manage your life wisely.`) and confirm with the user before submitting. **Do not submit the Chinese default for non-Chinese narration.**
+- **Customize**: When the user wants a channel-specific watermark phrase or branded vertical tagline
+- **Format tip**: Keep concise; the text renders vertically, so shorter phrases look cleaner
+
+> **Chinese narration**: "侧边文案保留默认合规文案即可，如需换成频道专属文案可以自定义。" — **Non-Chinese narration**: Translate the default to the target language, show the translated value to the user, and ask for confirmation or edits before submitting.
+
+---
+
+**`watermark_text` — 水印文案** (`string`, template: 方屏·简约剧集 only)
+
+Copyright/brand text that roams randomly across the frame as a floating watermark.
+
+- **Leave empty**: No watermark displayed
+- **Fill in**: When the user wants copyright protection or channel branding (e.g., `@ChannelName`, `© Studio Name`)
+- **Format tip**: Short phrases work best (under 15 characters); long text may look cluttered as it moves across the frame
+- ⚠️ **Non-Chinese narration**: See Language Awareness rule above — value must be in the target language.
+
+> Ask the user if they want a watermark. If yes, ask for the text. (Ask in the conversation language — see Language Awareness rule 5.)
+
+---
+
+**`slogan` — 顶部标语** (`string`, template: 竖屏·流光剧集 only)
+
+Custom text that fills the entire top title bar, overriding whatever the AI would generate.
+
+- **Leave empty (recommended)**: AI auto-generates a contextually appropriate top title
+- **Fill in**: Only when the user has a fixed brand slogan or exclusive tagline they want locked in. Once filled, AI title generation for this slot is completely bypassed.
+- ⚠️ **Non-Chinese narration**: See Language Awareness rule above — leaving empty may cause AI to generate a Chinese slogan.
+
+> Ask the user if they want a fixed top slogan. (Ask in the conversation language — see Language Awareness rule 5.)
+
+#### Creating a Magic Video
+
+Input is the `task_id` returned from video-composing (step 3).
+
+> ⚠️ **Agent behavior — mandatory pre-submission confirmation**: Before running any `magic-video` create command, the agent MUST display the full request parameters to the user in a readable format (templates selected, all `template_params` values for each template), then explicitly ask for confirmation. Do NOT submit until the user confirms. This applies every time a `magic-video` task is created — including multiple calls within the same session. Ask in the conversation language (not necessarily Chinese).
 
 ```bash
-# Search programmatically — do NOT rely on truncated terminal output:
-narrator-ai-cli material list --json --page 1 --size 100 | grep -i "目标影片名"
-narrator-ai-cli material list --json --page 1 --size 100 \
-  | python3 -c "import json, sys; items = json.load(sys.stdin).get('items', []); \
-[print(json.dumps(i, ensure_ascii=False)) for i in items if '关键词' in i.get('name','') or '关键词' in i.get('title','')]"
+# Without custom params (AI handles all defaults)
+narrator-ai-cli task create magic-video --json -d '{
+  "task_id": "<task_id from step 3>",
+  "template_name": ["竖屏·黑金剧集", "横屏·电影剧集"]
+}'
+
+# With custom params — key is template name, value is a params dict
+narrator-ai-cli task create magic-video --json -d '{
+  "task_id": "<task_id from step 3>",
+  "template_name": ["竖屏·合规剧集"],
+  "template_params": {
+    "竖屏·合规剧集": {
+      "segment_count": 0,
+      "bottom_disclaimer_text": "本故事纯属虚构 请勿模仿",
+      "vertical_text_content": "影视效果 请勿模仿 合理安排生活"
+    }
+  }
+}'
 ```
 
-> `video_file_id` — the video file ID for this pre-built material (used as `video_oss_key` and `negative_oss_key`)
-> `srt_file_id` — the subtitle (SRT) file ID for this pre-built material (used as `srt_oss_key`)
+**Output**: `sub_tasks` array — one entry per template, each with a rendered video URL
+
+## Standard Path Workflow
+
+### Step 0: Find Source Material
+
+> ⚠️ **Agent behavior**: Confirm the movie or drama name with the user before proceeding. For material list usage, pagination, and programmatic search, see **Prerequisites § Source Files**.
 
 **Decision flow:**
 
-1. Fetch all pages (start with `--page 1 --size 100`, repeat if `total > fetched count`). **Search programmatically** using `grep -i` or `python3 -c` on the JSON output — do NOT scan the terminal display. Repeat per page until match found or all pages exhausted.
+1. Run `material list --json` (all pages). Search programmatically — do NOT rely on terminal display.
 2. **Found in pre-built materials** → use the material's `video_file_id` as `video_oss_key`/`negative_oss_key` and `srt_file_id` as `srt_oss_key` in `episodes_data` for Step 2 (generate-writing). No need to upload files.
 3. **Not found** → guide user to upload their own video and SRT files via `file upload` (see Prerequisites § Source Files). Use the returned `file_id` values as `video_oss_key`/`negative_oss_key` and `srt_oss_key` in `episodes_data`.
 
@@ -531,7 +640,7 @@ narrator-ai-cli task create popular-learning --json -d '{
 
 **model_version**: `advanced` (高级版) or `standard` (标准版)
 
-**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` until `status=2`. Parse `task_result` JSON string → `agent_unique_code` is the `learning_model_id`:
+**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. Parse `task_result` JSON string → `agent_unique_code` is the `learning_model_id`:
 
 ```json
 {
@@ -568,7 +677,9 @@ narrator-ai-cli task create generate-writing --json -d '{
 
 Optional: `refine_srt_gaps` (bool) — enables AI scene analysis. **Only set to `true` when user explicitly requests it.**
 
-**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` until `status=2`. Extract `task_result` (narration script file path) and `order_info` from results:
+> ⚠️ **Language linkage**: If the selected dubbing voice is non-Chinese, add `"language": "<target language>"` to this request to match. Do not omit this param for non-Chinese dubbing — the default is Chinese.
+
+**Output**: On creation returns `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. Extract `task_result` (narration script file path) and `order_info` from results:
 
 ```json
 {
@@ -602,11 +713,12 @@ narrator-ai-cli task create clip-data --json -d '{
 {"code": 10000, "message": "", "data": {"task_id": ""}}
 ```
 
-Save `data.task_id`. Poll `task query <task_id> --json` until `status=2`. On success, read `task_order_num` from the task record — this is the `order_num` required for video-composing (step 4).
+Save `data.task_id`. Poll `task query <task_id> --json` every 5 seconds until `status=2`. On success, read `task_order_num` from the task record — this is the `order_num` required for video-composing (step 4).
+
+### Step 4-5: Video Composing & Magic Video
 
-### Step 4-5: Same as Fast Path Steps 3-4
+Same commands as Fast Path Steps 3–4. The only difference: `order_num` for video-composing comes from **clip-data** (this step's Step 3) `task_order_num`, not from fast-clip-data. In both paths, video-composing always uses the `task_order_num` from the immediately preceding clip step.
 
-**IMPORTANT**: video-composing uses `order_num` from **clip-data (step 3)** `order_info.order_num`, NOT from generate-writing.
 
 ## Standalone Tasks
 
@@ -628,8 +740,31 @@ Optional: clone_model (default: pro). Output: task_id with audio result.
 
 ## Task Management
 
+> ⚠️ **Agent behavior — standard polling pattern**: Always use the `while` loop below when monitoring a task. Never use a `for` loop with a fixed iteration count (it may exhaust before the task finishes). The loop below runs until status `2` (success) or `3` (failed) and cannot be silently interrupted mid-run.
+
+```bash
+# Standard polling loop — use this every time a task needs to be monitored
+TASK_ID="<task_id>"
+while true; do
+  result=$(narrator-ai-cli task query "$TASK_ID" --json 2>&1)
+  status=$(echo "$result" | python3 -c "
+import json, sys
+try:
+    d = json.load(sys.stdin)
+    tasks = d.get('tasks') or d.get('data', {}).get('tasks', [])
+    print(tasks[0].get('status', '') if tasks else '')
+except Exception:
+    print('')
+" 2>/dev/null)
+  echo "[$(date '+%H:%M:%S')] task=$TASK_ID status=$status"
+  [ "$status" = "2" ] && echo "Done." && break
+  [ "$status" = "3" ] && echo "Failed:" && echo "$result" && break
+  sleep 5
+done
+```
+
 ```bash
-# Query task status (poll until status 2=success or 3=failed)
+# Single query (for spot-checks only — do not use in automated polling)
 narrator-ai-cli task query <task_id> --json
 
 # List tasks with filters
@@ -684,6 +819,7 @@ narrator-ai-cli task types -V
 
 ```bash
 narrator-ai-cli file upload ./video.mp4 --json       # 3-step: presigned → OSS → callback
+narrator-ai-cli file transfer --link "<url>" --json  # import by HTTP/Baidu/PikPak link (alternative to upload)
 narrator-ai-cli file list --json                       # pagination, --search filter
 narrator-ai-cli file info <file_id> --json             # name, path, size, category, timestamps
 narrator-ai-cli file download <file_id> --json         # returns presigned URL (time-limited)
@@ -760,16 +896,14 @@ CLI exits code 1 on any error, prints to stderr.
     │                  ││                        ▼
     ▼                  ││              fast-clip-data
  clip-data             ││              IN: task_id + file_id
- IN: generate-writing  ││              OUT: file_ids[0]
-     task_id           ││                  order_info.order_num
- OUT: file_ids[0]      ││                        │
-     order_info        ││                        │
-     .order_num ───────┴┴────────────────────────┘
+ IN: generate-writing  ││              OUT: clip task task_id
+     task_id           ││                 
+ OUT: clip task task_id ───────┴┴────────────────────────┘
                         │
                         ▼
                  video-composing
-                 IN: order_num (from clip-data or fast-clip-data!)
-                     bgm, dubbing, dubbing_type
+                 IN: order_num = task_order_num from preceding clip step
+                     (clip-data in Standard Path; fast-clip-data in Fast Path)
                  OUT: task_id, tasks[0].video_url
                         │
                         ▼
@@ -783,9 +917,9 @@ CLI exits code 1 on any error, prints to stderr.
 
 1. **`confirmed_movie_json` is required for target_mode=1 and target_mode=2, optional for target_mode=3.** When a pre-built material is found, construct it from material fields directly (no `search-movie` needed). For mode=1 or mode=2 with user-uploaded SRT (no material), always run `search-movie` — never fabricate this value.
 2. **Source file_ids from `file list` or `material list`.** Never guess file_ids.
-3. **Tasks are async.** Create returns `task_id` → poll `task query <task_id> --json` until status `2` (success) or `3` (failed).
+3. **Tasks are async.** Create returns `task_id` → poll `task query <task_id> --json` every **5 seconds** until status `2` (success) or `3` (failed). Most tasks complete in 30 seconds to several minutes; do not poll faster than 5 s to avoid unnecessary API load.
 4. **`search-movie` may take 60+ seconds** (Gradio backend, cached 24h). Set adequate timeout.
-5. **video-composing uses the clip-data step's `order_info.order_num`** (clip-data in Standard Path, fast-clip-data in Fast Path). NOT the writing step's order_num — this is the most common mistake.
+5. **video-composing always uses `task_order_num` from the immediately preceding clip step** as its `order_num` param — clip-data in Standard Path, fast-clip-data in Fast Path. Never use the writing step's order_num.
 6. **Prefer pre-built narration templates** over running popular-learning. Use `task narration-styles --json` to list, browse https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc for preview.
 7. **Use `-d @file.json`** for large request bodies to avoid shell quoting issues.
 8. **Use `task verify`** before creating expensive tasks to catch missing/invalid materials early.
PATCH

echo "Gold patch applied."
