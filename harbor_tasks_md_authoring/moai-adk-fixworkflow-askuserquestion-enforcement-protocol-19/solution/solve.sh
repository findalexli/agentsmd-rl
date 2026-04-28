#!/usr/bin/env bash
set -euo pipefail

cd /workspace/moai-adk

# Idempotency guard
if grep -qF "| \"Schema \ub85c\ub4dc\uac00 \uadc0\ucc2e\uc73c\ub2c8 \uc774\ubc88\uc5d4 \uc0b0\ubb38\uc73c\ub85c \uc9c8\ubb38\ud558\uc790\" | AskUserQuestion/Task* \ub294 deferred tool. ToolS" ".claude/skills/moai/SKILL.md" && grep -qF "2026-04-24 \uc138\uc158\uc5d0\uc11c `AskUserQuestion` \ubbf8\uc0ac\uc6a9\uc73c\ub85c [HARD] \uaddc\uce59(\u00a71, \u00a78) \uc704\ubc18 \ubc18\ubcf5 \ubc1c\uc0dd. \uadfc\ubcf8 \uc6d0\uc778\uc740 **def" "CLAUDE.local.md" && grep -qF "- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are " "CLAUDE.md" && grep -qF "| \"Schema \ub85c\ub4dc\uac00 \uadc0\ucc2e\uc73c\ub2c8 \uc774\ubc88\uc5d4 \uc0b0\ubb38\uc73c\ub85c \uc9c8\ubb38\ud558\uc790\" | AskUserQuestion/Task* \ub294 deferred tool. ToolS" "internal/template/templates/.claude/skills/moai/SKILL.md" && grep -qF "- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are " "internal/template/templates/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/moai/SKILL.md b/.claude/skills/moai/SKILL.md
@@ -312,6 +312,8 @@ Last Updated: 2026-02-25
 | "I can run /moai run without a SPEC, it is just a tweak" | Without a SPEC, there is no acceptance criterion to check. Every run without a SPEC silently degrades quality tracking. |
 | "Parallel agents will just race, sequential is safer" | Independent tool calls are explicitly required to run in parallel. Sequentializing them wastes user time. |
 | "I will respond in English since it is technical" | Conversation language is a HARD rule. User-facing output must match the configured language, always. |
+| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |
+| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |
 
 <!-- moai:evolvable-end -->
 
@@ -324,6 +326,11 @@ Last Updated: 2026-02-25
 - AskUserQuestion with more than 4 options or containing emoji
 - Agent invocation prompt contains absolute paths to the main project when isolation is worktree
 - /moai run executed without a corresponding SPEC-XXX document
+- Response ends with "?" but no AskUserQuestion tool call accompanies it
+- Options listed as markdown (`- A:`, `- B:`, `Option X:`) without structured AskUserQuestion
+- Prose decision requests ("진행할까요?", "어느 것 선호?", "A or B?") instead of AskUserQuestion
+- First AskUserQuestion call in session without prior ToolSearch preload (produces InputValidationError)
+- Waiting for user's next message after prose question without AskUserQuestion tool call
 
 <!-- moai:evolvable-end -->
 
@@ -337,5 +344,9 @@ Last Updated: 2026-02-25
 - [ ] For non-trivial tasks, approach was explained and approved before code changes
 - [ ] SPEC-ID is referenced when /moai run, /moai sync, or /moai fix is invoked
 - [ ] TodoList used to decompose multi-file changes (3+ files)
+- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)
+- [ ] Every response containing "?" is accompanied by a structured AskUserQuestion tool call
+- [ ] Option lists (`- A:`, `- B:`) are routed through AskUserQuestion, not markdown-only
+- [ ] No silent "wait for user input" state after prose question (§8 Deferred Tool Preload Protocol)
 
 <!-- moai:evolvable-end -->
diff --git a/CLAUDE.local.md b/CLAUDE.local.md
@@ -1056,6 +1056,86 @@ v2.14.0 릴리스 과정에서 다음 문제 발생 → v2.15부터 방지:
 
 ---
 
+---
+
+## 19. AskUserQuestion Enforcement Protocol
+
+2026-04-24 세션에서 `AskUserQuestion` 미사용으로 [HARD] 규칙(§1, §8) 위반 반복 발생. 근본 원인은 **deferred tool 사전 로드 부재** + **산문 질문 편의주의**. v3.4.0부터 본 Enforcement Protocol을 [HARD] 운영 방침으로 고정.
+
+### §19.1 근본 원인 체인
+
+1. **1차 원인**: `AskUserQuestion`은 deferred tool. 세션 시작 시 schema 미로드 → 직접 호출 시 `InputValidationError` → agent가 회피 → 산문 질문으로 우회.
+2. **2차 원인**: Red Flags / Verification 체크리스트에 "응답 말미 `?` + AskUserQuestion 미호출" 탐지 규칙 부재.
+3. **3차 원인**: 규칙은 존재하나 매 세션 agent 해석에 의존. 편의주의("짧은 질문은 산문으로") 허용 관행.
+
+### §19.2 [HARD] 세션 시작 Preload (의무)
+
+모든 MoAI 세션은 첫 사용자 입력 수신 직후 다음 `ToolSearch` 호출을 실행해야 한다:
+
+```
+ToolSearch({
+  query: "select:AskUserQuestion,TaskCreate,TaskUpdate,TaskList,TaskGet",
+  max_results: 5
+})
+```
+
+Preload 완료 후에만 해당 tool 호출 가능. Preload 이전 호출 = HARD 위반 + `InputValidationError`.
+
+### §19.3 [HARD] Pre-Response Self-Check (응답 전송 전 필수)
+
+모든 사용자 응답 전송 전, 다음 4항목 자가 점검:
+
+1. **Question mark detection**: 응답에 `?`가 포함되었는가? → 있으면 `AskUserQuestion` tool call 동반 필수
+2. **Option list detection**: 응답에 선택지 구조(`- A:`, `- B:`, `Option X:`, `1.`)가 있는가? → structured `AskUserQuestion` 경유 필수
+3. **Schema load check**: `AskUserQuestion` schema 로드 상태 확인. 미로드 시 `ToolSearch` 선행
+4. **Silent-wait detection**: 산문 질문 후 사용자 응답 대기 상태인가? → `AskUserQuestion`으로 전환 필수
+
+점검 실패 시 = [HARD] 규칙 위반. 즉시 수정 필요.
+
+### §19.4 [HARD] Anti-Patterns (금지)
+
+| 패턴 | 왜 금지 | 올바른 방법 |
+|------|---------|-------------|
+| 응답 말미 `?`로 끝나는 산문 질문 | 사용자에게 무엇을 원하는지 불명확, silent wait | `AskUserQuestion` 호출 필수 |
+| "진행할까요?", "A or B?" 자연어 선택 요청 | structured 응답 아닌 free-form 기대 → 파싱 불가 | `AskUserQuestion` with 2-4 options |
+| 선택지를 markdown `- A:`, `- B:`로만 나열 | 사용자가 자연어로 답해야 함 | `AskUserQuestion` structured options |
+| `AskUserQuestion` 호출 전 `ToolSearch` 생략 | `InputValidationError` 발생 | §19.2 Preload 먼저 |
+| Silent "wait for next message" after prose | 사용자에게 정확한 응답 형식 미제공 | `AskUserQuestion` 또는 구체적 지시 |
+
+### §19.5 운영 적용 (Role별)
+
+**MoAI orchestrator**:
+- [HARD] 모든 사용자 결정 요청은 `AskUserQuestion` 경유
+- [HARD] 세션 시작 시 §19.2 preload 실행
+- [HARD] 응답 전송 전 §19.3 self-check 통과
+
+**Subagent (manager-*, expert-*, builder-*)**:
+- [HARD] `AskUserQuestion` 호출 금지 (agent-common-protocol §User Interaction Boundary)
+- 사용자 결정 필요 시 "missing inputs" 보고서로 orchestrator에 반환
+
+**User**:
+- 산문 질문 탐지 시 즉시 지적 (2026-04-24 세션 사례처럼)
+- 반복 위반 시 memory/feedback_askuserquestion_*.md에 기록
+
+### §19.6 Recovery Protocol (위반 발생 시)
+
+[HARD] 위반 탐지 즉시 다음 순서로 복구:
+
+1. 위반 인정 + 근본 원인 명시 (1/2/3차)
+2. `ToolSearch`로 schema preload
+3. 동일 질문을 `AskUserQuestion`으로 재구성 + 재전송
+4. `memory/feedback_askuserquestion_*.md`에 incident 기록
+5. 다음 응답부터 §19.3 self-check 엄격 적용
+
+### §19.7 관련 정책 참조
+
+- CLAUDE.md §1 HARD Rules (AskUserQuestion-Only + Deferred Tool Preload)
+- CLAUDE.md §8 User Interaction Architecture § Deferred Tool Preload Protocol
+- .claude/skills/moai/SKILL.md § Red Flags + Verification (deferred tool 관련 5+4 항목)
+- ~/.claude/projects/{hash}/memory/feedback_askuserquestion_enforcement.md (이번 incident 기록)
+
+---
+
 **Status**: Active (Local Development)
-**Version**: 3.3.0 (Phase 8: §18.0 운영 원칙 5 Framework 명시화 + Release Drafter 구성 완료)
+**Version**: 3.4.0 (Phase 9: §19 AskUserQuestion Enforcement Protocol 공식 채택)
 **Last Updated**: 2026-04-24
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -11,6 +11,7 @@ MoAI is the Strategic Orchestrator for Claude Code. All tasks must be delegated
 - [HARD] No XML in User Responses: Never display XML tags in user-facing responses
 - [HARD] Markdown Output: Use Markdown for all user-facing communication
 - [HARD] AskUserQuestion-Only Interaction: ALL questions directed at the user MUST go through AskUserQuestion (See Section 8)
+- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling without schema produces InputValidationError. (See Section 8 Deferred Tool Preload Protocol)
 - [HARD] Context-First Discovery: Conduct Socratic interview via AskUserQuestion when context is insufficient before executing non-trivial tasks (See Section 7)
 - [HARD] Approach-First Development: Explain approach and get approval before writing code (See Section 7)
 - [HARD] Multi-File Decomposition: Split work when modifying 3+ files (See Section 7)
@@ -316,6 +317,37 @@ Exceptions (free-form text questions permitted ONLY when):
 - AskUserQuestion is technically unavailable (e.g., inside a subagent — should not happen since subagents must not ask users)
 - The question is actually a statement of status, not a question
 
+### Deferred Tool Preload Protocol [HARD]
+
+[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError`. Load schemas via `ToolSearch` BEFORE first use.
+
+Preload triggers (execute ToolSearch immediately when any condition matches):
+- Session start after first user input received
+- Before any complex / multi-step task begins
+- Before invoking Socratic interview (Section 7 Rule 5)
+- When user decision is required ("Should I proceed?", "Which option?", "선택", "진행 여부")
+- Immediately before first TaskCreate/Update/List/Get call
+
+Preload command (once per session, BEFORE any user-facing question):
+```
+ToolSearch({query: "select:AskUserQuestion,TaskCreate,TaskUpdate,TaskList,TaskGet", max_results: 5})
+```
+
+Anti-patterns (PROHIBITED — these constitute HARD violation of §1):
+- Prose question ending with "?" + no accompanying AskUserQuestion tool call
+- Natural language decision requests: "진행할까요?", "어느 것을 선호하시나요?", "A or B?"
+- Listing options as markdown only (`- A:`, `- B:`) without structured AskUserQuestion
+- Calling AskUserQuestion without prior ToolSearch preload (produces InputValidationError)
+- Converting a user decision into a "wait for next message" without AskUserQuestion
+
+Pre-response self-check (MANDATORY before sending any user-facing response):
+1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call
+2. Does the response list options (`- A:`, `1.`, `Option X:`)? → MUST use structured AskUserQuestion
+3. Is the deferred tool schema loaded? → If not, call ToolSearch FIRST
+4. Am I silently waiting for user input after prose question? → Convert to AskUserQuestion
+
+Self-check failure = HARD rule violation. Treat as critical defect requiring immediate correction.
+
 ### Socratic Interview via AskUserQuestion [HARD]
 
 When context is insufficient (see Section 7 Rule 5 triggers), MoAI conducts a Socratic interview using AskUserQuestion rounds.
diff --git a/internal/template/templates/.claude/skills/moai/SKILL.md b/internal/template/templates/.claude/skills/moai/SKILL.md
@@ -312,6 +312,8 @@ Last Updated: 2026-02-25
 | "I can run /moai run without a SPEC, it is just a tweak" | Without a SPEC, there is no acceptance criterion to check. Every run without a SPEC silently degrades quality tracking. |
 | "Parallel agents will just race, sequential is safer" | Independent tool calls are explicitly required to run in parallel. Sequentializing them wastes user time. |
 | "I will respond in English since it is technical" | Conversation language is a HARD rule. User-facing output must match the configured language, always. |
+| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |
+| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |
 
 <!-- moai:evolvable-end -->
 
@@ -324,6 +326,11 @@ Last Updated: 2026-02-25
 - AskUserQuestion with more than 4 options or containing emoji
 - Agent invocation prompt contains absolute paths to the main project when isolation is worktree
 - /moai run executed without a corresponding SPEC-XXX document
+- Response ends with "?" but no AskUserQuestion tool call accompanies it
+- Options listed as markdown (`- A:`, `- B:`, `Option X:`) without structured AskUserQuestion
+- Prose decision requests ("진행할까요?", "어느 것 선호?", "A or B?") instead of AskUserQuestion
+- First AskUserQuestion call in session without prior ToolSearch preload (produces InputValidationError)
+- Waiting for user's next message after prose question without AskUserQuestion tool call
 
 <!-- moai:evolvable-end -->
 
@@ -337,5 +344,9 @@ Last Updated: 2026-02-25
 - [ ] For non-trivial tasks, approach was explained and approved before code changes
 - [ ] SPEC-ID is referenced when /moai run, /moai sync, or /moai fix is invoked
 - [ ] TodoList used to decompose multi-file changes (3+ files)
+- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)
+- [ ] Every response containing "?" is accompanied by a structured AskUserQuestion tool call
+- [ ] Option lists (`- A:`, `- B:`) are routed through AskUserQuestion, not markdown-only
+- [ ] No silent "wait for user input" state after prose question (§8 Deferred Tool Preload Protocol)
 
 <!-- moai:evolvable-end -->
diff --git a/internal/template/templates/CLAUDE.md b/internal/template/templates/CLAUDE.md
@@ -11,6 +11,7 @@ MoAI is the Strategic Orchestrator for Claude Code. All tasks must be delegated
 - [HARD] No XML in User Responses: Never display XML tags in user-facing responses
 - [HARD] Markdown Output: Use Markdown for all user-facing communication
 - [HARD] AskUserQuestion-Only Interaction: ALL questions directed at the user MUST go through AskUserQuestion (See Section 8)
+- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling without schema produces InputValidationError. (See Section 8 Deferred Tool Preload Protocol)
 - [HARD] Context-First Discovery: Conduct Socratic interview via AskUserQuestion when context is insufficient before executing non-trivial tasks (See Section 7)
 - [HARD] Approach-First Development: Explain approach and get approval before writing code (See Section 7)
 - [HARD] Multi-File Decomposition: Split work when modifying 3+ files (See Section 7)
@@ -316,6 +317,37 @@ Exceptions (free-form text questions permitted ONLY when):
 - AskUserQuestion is technically unavailable (e.g., inside a subagent — should not happen since subagents must not ask users)
 - The question is actually a statement of status, not a question
 
+### Deferred Tool Preload Protocol [HARD]
+
+[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError`. Load schemas via `ToolSearch` BEFORE first use.
+
+Preload triggers (execute ToolSearch immediately when any condition matches):
+- Session start after first user input received
+- Before any complex / multi-step task begins
+- Before invoking Socratic interview (Section 7 Rule 5)
+- When user decision is required ("Should I proceed?", "Which option?", "선택", "진행 여부")
+- Immediately before first TaskCreate/Update/List/Get call
+
+Preload command (once per session, BEFORE any user-facing question):
+```
+ToolSearch({query: "select:AskUserQuestion,TaskCreate,TaskUpdate,TaskList,TaskGet", max_results: 5})
+```
+
+Anti-patterns (PROHIBITED — these constitute HARD violation of §1):
+- Prose question ending with "?" + no accompanying AskUserQuestion tool call
+- Natural language decision requests: "진행할까요?", "어느 것을 선호하시나요?", "A or B?"
+- Listing options as markdown only (`- A:`, `- B:`) without structured AskUserQuestion
+- Calling AskUserQuestion without prior ToolSearch preload (produces InputValidationError)
+- Converting a user decision into a "wait for next message" without AskUserQuestion
+
+Pre-response self-check (MANDATORY before sending any user-facing response):
+1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call
+2. Does the response list options (`- A:`, `1.`, `Option X:`)? → MUST use structured AskUserQuestion
+3. Is the deferred tool schema loaded? → If not, call ToolSearch FIRST
+4. Am I silently waiting for user input after prose question? → Convert to AskUserQuestion
+
+Self-check failure = HARD rule violation. Treat as critical defect requiring immediate correction.
+
 ### Socratic Interview via AskUserQuestion [HARD]
 
 When context is insufficient (see Section 7 Rule 5 triggers), MoAI conducts a Socratic interview using AskUserQuestion rounds.
PATCH

echo "Gold patch applied."
