#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "> - \u7528\u6237\u5982\u679c\u8981\u7684\u662f\u5999\u8bb0\u57fa\u7840\u4fe1\u606f\uff0c\u62ff\u5230 `minute_token` \u540e\u7528 `minutes minutes get`\uff1b\u7528\u6237\u5982\u679c\u8981\u7684\u662f\u9010\u5b57\u7a3f\u3001\u603b\u7ed3\u3001\u5f85\u529e\u3001\u7ae0\u8282" "skills/lark-minutes/SKILL.md" && grep -qF "| \u4f1a\u8bae\u5f55\u5236\u67e5\u8be2 | `lark-cli vc +recording --meeting-ids <id>` \u6216 `lark-cli vc +recording" "skills/lark-minutes/references/lark-minutes-download.md" && grep -qF "- \u5f53\u7528\u6237\u540c\u65f6\u63d0\u5230\u201c\u4f1a\u8bae / \u4f1a / \u5f00\u4f1a / \u67d0\u573a\u4f1a\u201d\u548c\u201c\u5999\u8bb0\u201d\u65f6\uff0c\u4f18\u5148\u5148\u5b9a\u4f4d\u4f1a\u8bae\uff1b\u5982\u679c\u8981\u7684\u662f\u5999\u8bb0\u4fe1\u606f\uff0c\u8d70 `vc +recording` \u2192 `minute" "skills/lark-minutes/references/lark-minutes-search.md" && grep -qF "> **\u5999\u8bb0\u8fb9\u754c**\uff1a`+notes` \u8d1f\u8d23\u7eaa\u8981\u5185\u5bb9\u3001\u9010\u5b57\u7a3f\u548c AI \u4ea7\u7269\uff1b\u5999\u8bb0\u57fa\u7840\u4fe1\u606f\u8bf7\u4f18\u5148\u770b [`+recording`](references/lark-" "skills/lark-vc/SKILL.md" && grep -qF "> **\u8fb9\u754c\u63d0\u9192\uff1a** \u5982\u679c\u7528\u6237\u660e\u786e\u8981\u7684\u662f\"\u5999\u8bb0\u4fe1\u606f\"\"\u5999\u8bb0\u8be6\u60c5\"\"\u5999\u8bb0\u94fe\u63a5\"\"minute_token\"\"\u6807\u9898\"\"\u65f6\u957f\"\"owner\"\u8fd9\u7c7b\u5999\u8bb0\u5143\u4fe1\u606f\uff0c\u5148\u7528\u672c\u547d" "skills/lark-vc/references/lark-vc-recording.md" && grep -qF "lark-cli minutes minutes get --params '{\"minute_token\":\"<MINUTE_TOKEN>\"}'" "skills/lark-vc/references/lark-vc-search.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-minutes/SKILL.md b/skills/lark-minutes/SKILL.md
@@ -25,13 +25,15 @@ metadata:
 2. 仅支持使用关键词、时间段、参与者、所有者等筛选条件搜索妙记记录，对于不支持的筛选条件，需要提示用户。
 3. 搜索结果存在多条数据时，务必注意分页数据获取，不要遗漏任何妙记记录。
 4. 如果是会议的妙记，应优先使用 [vc +search](../lark-vc/references/lark-vc-search.md) 先定位会议，再按需通过 [vc +recording](../lark-vc/references/lark-vc-recording.md) 获取 `minute_token`。
+5. 会议场景的妙记路由，以及"参与的妙记"如何解释，统一以 [minutes +search](references/lark-minutes-search.md) 为准。
 
 
 ### 2. 查看妙记基础信息
 
 1. 当用户只需要确认某条妙记的标题、封面、时长、所有者、URL 等基础信息时，使用 `minutes minutes get`。
 2. 如果用户给的是妙记 URL，应先从 URL 末尾提取 `minute_token`，再调用 `minutes minutes get`。
-3. 用户意图不明确时，默认先给基础元信息，帮助确认是否命中目标妙记。
+3. 如果是会议 / 日程上下文中的妙记基础信息，先通过 VC 链路拿到 `minute_token`，再调用 `minutes minutes get`。
+4. 用户意图不明确时，默认先给基础元信息，帮助确认是否命中目标妙记。
 
 > 使用 `lark-cli schema minutes.minutes.get` 可查看完整返回值结构。核心字段包含：`title`（标题）、`cover`（封面 URL）、`duration`（时长，毫秒）、`owner_id`（所有者 ID）、`url`（妙记链接）。
 
@@ -71,7 +73,8 @@ Minutes (妙记) ← minute_token 标识
 > - 用户说"妙记列表 / 搜索妙记 / 某个关键词的妙记" → `minutes +search`
 > - 用户只是想看"我的妙记 / 某段时间内的妙记 / 妙记列表"，不要先走 [lark-vc](../lark-vc/SKILL.md)，而应直接使用本 skill
 > - 用户如果同时提到"会议 / 会 / 开会 / 某场会"，即使也提到了"妙记"，也应优先走 [lark-vc](../lark-vc/SKILL.md) 先定位会议，再通过 [vc +recording](../lark-vc/references/lark-vc-recording.md) 获取 `minute_token`
-> - 用户说"我的妙记 / 我拥有的妙记 / 我参与的妙记"时，可将相关过滤条件映射为 `me`；`me` 表示当前用户
+> - 用户如果要的是妙记基础信息，拿到 `minute_token` 后用 `minutes minutes get`；用户如果要的是逐字稿、总结、待办、章节，再走 `vc +notes --minute-tokens`
+> - “我的妙记”“参与的妙记”等自然语言映射细则，以 [minutes +search](references/lark-minutes-search.md) 为准
 > - 结果有多页时，使用 `page_token` 持续翻页，直到确认没有更多结果
 > - `minutes +search` 单次最多返回 `200` 条；结果总数没有固定上限
 > - 用户说"这个妙记的标题 / 时长 / 封面 / 链接" → `minutes minutes get`
diff --git a/skills/lark-minutes/references/lark-minutes-download.md b/skills/lark-minutes/references/lark-minutes-download.md
@@ -93,7 +93,7 @@ API 限流 5 次/秒，批量下载时需注意控制频率。
 |------|---------|
 | 妙记 URL | 从 URL 末尾提取，如 `https://sample.feishu.cn/minutes/obcnq3b9jl72l83w4f149w9c` → `obcnq3b9jl72l83w4f149w9c` |
 | 妙记元信息查询 | `lark-cli minutes minutes get --params '{"minute_token": "obcn..."}'` |
-| 会议纪要查询 | `lark-cli vc +notes --meeting-ids <id>` 返回结果中关联的妙记 token |
+| 会议录制查询 | `lark-cli vc +recording --meeting-ids <id>` 或 `lark-cli vc +recording --calendar-event-ids <event_id>` |
 
 ## 常见错误与排查
 
diff --git a/skills/lark-minutes/references/lark-minutes-search.md b/skills/lark-minutes/references/lark-minutes-search.md
@@ -41,12 +41,17 @@ lark-cli minutes +search --participant-ids "ou_x,ou_y"
 # 按所有者过滤（open_id，逗号分隔）
 lark-cli minutes +search --owner-ids "ou_owner,ou_owner_2"
 
-# 查询我参与的妙记
+# 严格只查我作为参与者的妙记（不含我拥有）
 lark-cli minutes +search --participant-ids "me"
 
 # 查询我拥有的妙记
 lark-cli minutes +search --owner-ids "me"
 
+# 广义查询我参与的妙记（自然语言默认：我拥有 ∪ 我参与）
+lark-cli minutes +search --owner-ids "me" --start 2026-03-10 --end 2026-03-10
+lark-cli minutes +search --participant-ids "me" --start 2026-03-10 --end 2026-03-10
+# 然后按 token 去重合并两次结果
+
 # 多条件组合查询
 lark-cli minutes +search --owner-ids "ou_owner" --participant-ids "ou_x" --start "2026-03-10T00:00+08:00"
 
@@ -86,11 +91,22 @@ lark-cli minutes +search --query "预算复盘" --format json
 在 `--owner-ids` 和 `--participant-ids` 中可使用 `me`，表示当前登录用户。该值会在本地解析为当前用户的 `open_id`，无需手动先查询自己的用户 ID。
 若当前环境尚未完成用户登录，或 CLI 无法解析出当前用户的 `open_id`，则应先执行 `lark-cli auth login`，再重新执行搜索。
 
-### 4. 支持分页
+### 4. 自然语言中的“参与的妙记”默认按并集理解
+
+当用户说"我参与的妙记""我参加过的妙记""参与过的妙记"时，默认理解为"我涉及的全部妙记"：
+
+- 我拥有的妙记：`--owner-ids me`
+- 我作为参与者的妙记：`--participant-ids me`
+
+不要只跑一次 `--participant-ids me` 就直接下结论，也不要把 `--owner-ids me` 和 `--participant-ids me` 同时塞进一次查询里赌接口语义。应分别查询后，按 `token` 做并集去重。
+
+只有在用户明确说"仅我参与但不是我拥有""别人拥有但我参与""只看参与者身份"时，才只使用 `--participant-ids`。
+
+### 5. 支持分页
 
 当返回 `has_more=true` 时，使用响应中的 `page_token` 配合 `--page-token` 获取下一页结果。
 
-### 5. 日期型 `--end` 包含当天整天
+### 6. 日期型 `--end` 包含当天整天
 
 当 `--end` 传入的是仅日期格式（如 `2026-03-10`）时，CLI 会将它解释为当天 `23:59:59`，而不是当天 `00:00:00`。
 CLI 会先按输入的本地日历日语义解析，再标准化为 RFC3339 时间戳发给 API；在 dry-run 或排查请求体时，看到的 `Z` 结尾时间表示同一个绝对时间点的 UTC 表示，不改变“按当天整天查询”的语义。
@@ -102,11 +118,19 @@ CLI 会先按输入的本地日历日语义解析，再标准化为 RFC3339 时
 
 如果用户说“昨天的妙记”“今天的妙记”“某一天内的妙记”，应把 `--start` 和 `--end` 都设置为同一天，而不是把 `--end` 设成下一天。
 
-### 6. 会议的妙记先定位会议
+### 7. 会议的妙记先定位会议
 
 如果用户明确要找某场会议的妙记，或同时提到“会议 / 开会 / 会”和“妙记”，应优先使用 `vc +search` 先定位会议，再按需通过 `vc +recording` 获取 `minute_token`，不要直接按妙记时间范围或关键词搜索。
 只有在无法通过会议搜索定位目标会议，或用户明确要求按妙记维度检索时，才回退到 `minutes +search`。
 
+如果用户要的是"某场会议的妙记信息""某个日程对应的妙记详情""minute\_token""妙记链接""标题""时长""owner"，正确链路是：
+
+1. `vc +search` 或 `calendar +agenda` 先定位会议 / 日程
+2. `vc +recording` 获取 `minute_token`
+3. `minutes minutes get` 查询妙记基础信息
+
+不要为了查"妙记信息"直接走 `vc +notes --meeting-ids`。`vc +notes` 只适用于逐字稿、总结、待办、章节等纪要内容。
+
 <br />
 
 ## 时间格式
@@ -141,7 +165,7 @@ lark-cli minutes +search --query "预算复盘" --page-size 20 --page-token '<PA
 ## 搜索结果中的下一步
 
 搜索结果中的 `token` 可直接作为 `minute_token` 用于继续查询妙记产物：
-通常先用搜索结果中的 `token` 获取妙记基础信息，确认描述、链接等元数据是否命中目标；需要进一步查看内容时，再继续查询关联的纪要产物。
+通常先用搜索结果中的 `token` 获取妙记基础信息，确认描述、链接等元数据是否命中目标；只有需要进一步查看逐字稿、总结、待办、章节时，再继续查询关联的纪要产物。
 
 如果你已经确定目标妙记，优先直接复用搜索结果中的 `token`，避免重复搜索。
 
@@ -166,8 +190,9 @@ lark-cli vc +notes --minute-tokens obcnhijv43vq6bcsl5xasfb2
 ## 提示
 
 - 当用户说“我的妙记”时，优先理解为 `--owner-ids me`。
-- 当用户说“我参与的妙记”时，优先理解为 `--participant-ids me`。
-- 当用户同时提到“会议 / 会 / 开会 / 某场会”和“妙记”时，优先先定位会议；只有无法定位目标会议时，再回退到妙记搜索。
+- 当用户说“我参与的妙记”“我参加过的妙记”时，默认理解为 `--owner-ids me` 与 `--participant-ids me` 两次查询后的并集。
+- 当用户明确说“仅我参与但不是我拥有”时，才优先理解为 `--participant-ids me`。
+- 当用户同时提到“会议 / 会 / 开会 / 某场会”和“妙记”时，优先先定位会议；如果要的是妙记信息，走 `vc +recording` → `minutes minutes get`，只有要纪要内容时才走 `vc +notes --minute-tokens`。
 - 必须使用 `--format json` 输出，你更加擅长解析 JSON 数据。
 - 排查参数与请求结构时优先使用 `--dry-run`。
 - 搜索的时间范围最大为 1 个月，如果需要搜索更长时间范围的妙记，需要拆分为多次时间范围为一个月查询。
@@ -178,3 +203,4 @@ lark-cli vc +notes --minute-tokens obcnhijv43vq6bcsl5xasfb2
 - [lark-vc-notes](../../lark-vc/references/lark-vc-notes.md) -- 基于 `minute_token` 获取逐字稿、总结、待办、章节等产物
 - [lark-shared](../../lark-shared/SKILL.md) -- 认证和全局参数
 - [lark-vc](../../lark-vc/SKILL.md) -- 视频会议全部命令
+
diff --git a/skills/lark-vc/SKILL.md b/skills/lark-vc/SKILL.md
@@ -87,7 +87,9 @@ Meeting (视频会议)
 > **优先级**：当用户搜索历史会议时，应优先使用 `vc +search` 而非 `calendar events search`。calendar 的搜索面向日程，vc 的搜索面向已结束的会议记录，支持按参会人、组织者、会议室等维度过滤。
 >
 > **路由规则**：如果用户在问“开过的会”“今天开了哪些会”“最近参加过什么会”“已结束的会议”“历史会议记录”，优先使用 `vc +search`。只有在查询未来日程、待开的会、agenda 时才优先使用 [lark-calendar](../lark-calendar/SKILL.md)。
-> 
+>
+> **妙记边界**：`+notes` 负责纪要内容、逐字稿和 AI 产物；妙记基础信息请优先看 [`+recording`](references/lark-vc-recording.md) 与 [lark-minutes](../lark-minutes/SKILL.md)。
+>
 > **特殊情况**: 当用户查询“今天有哪些会议”时，通过 `vc +search` 查询今天开过的会议记录，同时使用 lark-calendar 技能查询今天还未开始的会议，统一整理后展示给用户。
 
 ## Shortcuts（推荐优先使用）
diff --git a/skills/lark-vc/references/lark-vc-recording.md b/skills/lark-vc/references/lark-vc-recording.md
@@ -5,6 +5,8 @@
 
 通过 meeting_id 或 calendar_event_id 查询对应的 minute_token。这是 VC 域和 Minutes 域之间的桥梁命令。只读操作。
 
+> **边界提醒：** 如果用户明确要的是"妙记信息""妙记详情""妙记链接""minute_token""标题""时长""owner"这类妙记元信息，先用本命令拿到 `minute_token`，再调用 `minutes minutes get`。不要直接切到 `vc +notes`；`vc +notes` 只用于纪要内容和逐字稿。
+
 本 skill 对应 shortcut：`lark-cli vc +recording`。
 
 ## 命令
@@ -83,7 +85,17 @@ lark-cli vc +recording --meeting-ids xxx
 lark-cli minutes +download --minute-token <minute_token>
 ```
 
-### 场景 2：知道 meeting_id，想获取完整纪要（含 AI 产物）
+### 场景 2：知道 meeting_id，想查询妙记基础信息
+
+```bash
+# 第 1 步：通过 meeting_id 查询录制，拿到 minute_token
+lark-cli vc +recording --meeting-ids xxx
+
+# 第 2 步：使用上一步返回的 minute_token 查询妙记基础信息
+lark-cli minutes minutes get --params '{"minute_token":"<minute_token>"}'
+```
+
+### 场景 3：知道 meeting_id，想获取完整纪要（含 AI 产物）
 
 ```bash
 # 第 1 步：通过 meeting_id 查询录制，拿到 minute_token
@@ -93,7 +105,7 @@ lark-cli vc +recording --meeting-ids xxx
 lark-cli vc +notes --minute-tokens <minute_token>
 ```
 
-### 场景 3：先搜索会议，再获取录制并下载
+### 场景 4：先搜索会议，再获取录制并下载
 
 ```bash
 # 第 1 步：搜索历史会议，拿到 meeting_ids
@@ -106,7 +118,7 @@ lark-cli vc +recording --meeting-ids <ids>
 lark-cli minutes +download --minute-token <token>
 ```
 
-### 场景 4：从日历事件获取录制
+### 场景 5：从日历事件获取录制
 
 ```bash
 # 第 1 步：通过日历 event_id 查询录制，拿到 minute_token
@@ -131,7 +143,7 @@ lark-cli minutes +download --minute-token <minute_token>
 - 默认使用 `--format json` 输出，Agent 更擅长解析 JSON 数据。
 - 排查参数与请求结构时优先使用 `--dry-run`。
 - `minute_token` 从录制 URL 尾段解析（`https://meetings.feishu.cn/minutes/{minute_token}`）。
-- 拿到 `minute_token` 后可直接传给 `minutes +download` 或 `vc +notes --minute-tokens`。
+- 拿到 `minute_token` 后，如果要妙记基础信息，优先传给 `minutes minutes get`；如果要下载媒体文件，传给 `minutes +download`；如果要逐字稿、总结、待办、章节，再传给 `vc +notes --minute-tokens`。
 
 ## 参考
 
diff --git a/skills/lark-vc/references/lark-vc-search.md b/skills/lark-vc/references/lark-vc-search.md
@@ -130,11 +130,16 @@ lark-cli vc +search --query "周会" --page-size 15 --page-token "<PAGE_TOKEN>"
 
 ## 搜索结果中的下一步
 
-搜索结果中的 `meeting_id` 可直接用于继续查询会议纪要：
+搜索结果中的 `meeting_id` 可直接用于继续查询会议纪要或妙记：
 
 ```bash
-# 根据 meeting_id 获取会议纪要
+# 如果要会议纪要 / 逐字稿 / AI 总结 / 待办 / 章节
 lark-cli vc +notes --meeting-ids <MEETING_ID>
+
+# 如果要会议对应的妙记信息 / minute_token / 妙记链接
+lark-cli vc +recording --meeting-ids <MEETING_ID>
+# 然后再用返回的 minute_token 调用：
+lark-cli minutes minutes get --params '{"minute_token":"<MINUTE_TOKEN>"}'
 ```
 
 ## 常见错误与排查
@@ -151,9 +156,11 @@ lark-cli vc +notes --meeting-ids <MEETING_ID>
 - 排查参数与请求结构时优先使用 `--dry-run`。
 - 搜索的时间范围最大为 1 个月，如果需要搜索更长时间范围的会议，需要拆分为多次时间范围为一个月查询。
 - 不要使用 `yesterday`、`today` 这类相对时间字面量；请先转换成明确日期，例如 `2026-03-10`。
+- 用户如果明确问的是“妙记信息”而不是“纪要内容”，不要默认走 `vc +notes`；应先用 `vc +recording`。
 
 ## 参考
 
 - [lark-vc](../SKILL.md) -- 视频会议全部命令
+- [lark-vc-recording](lark-vc-recording.md) -- 查询会议对应的 minute_token
 - [lark-vc-notes](lark-vc-notes.md) -- 获取会议纪要
 - [lark-shared](../../lark-shared/SKILL.md) -- 认证和全局参数
PATCH

echo "Gold patch applied."
