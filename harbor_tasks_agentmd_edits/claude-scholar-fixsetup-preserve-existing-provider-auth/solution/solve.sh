#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-scholar

# Idempotent: skip if already applied
if grep -q 'PERSIST_AUTH=false' scripts/setup.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/README.md b/README.md
index 0dc15f3..7124f9e 100644
--- a/README.md
+++ b/README.md
@@ -374,10 +374,10 @@ bash /tmp/claude-scholar/scripts/setup.sh
 ```
 
 The script will:
-- Preserve your existing provider/model choices unless you explicitly reconfigure them
-- Preserve existing API keys, auth files, permissions, and unrelated config fields
-- Merge Scholar-managed sections (features, agents, MCP, skills paths) into the existing config instead of overwriting the whole file
-- Copy or refresh skills, agents, scripts, and utilities under `~/.codex/` with backups for overwritten managed files
+- Silently preserve existing `config.toml` provider/model and existing `auth.json` credentials, and auto-detect common `*_API_KEY` env vars when `auth.json` is absent
+- For fresh installs, choose API provider (OpenAI or custom), model, and a custom API key env var name
+- Reuse an already-exported env var when available, then merge Scholar-specific sections (features, agents, MCP) into config
+- Copy skills, agents, scripts, and utils to `~/.codex/`
 
 **Includes**: All 55 skills, 15 agents, Zotero MCP config, Obsidian knowledge-base skills, and AGENTS.md.
 
diff --git a/README.zh-CN.md b/README.zh-CN.md
index 312a85c..ebf149f 100644
--- a/README.zh-CN.md
+++ b/README.zh-CN.md
@@ -367,10 +367,10 @@ bash /tmp/claude-scholar/scripts/setup.sh
 ```
 
 脚本会：
-- 保留你现有的 provider/model 选择，除非你明确要求重配
-- 保留已有 API keys、auth 文件、权限配置和无关字段
-- 将 Scholar 管理的部分（features、agents、MCP、skills 路径）增量合并到现有配置，而不是整体覆盖
-- 将 skills、agents、scripts、utils 刷新到 `~/.codex/`，并为被覆盖的受管文件创建备份
+- 静默保留已有 `config.toml` 中的 provider/model，以及现有 `auth.json` 凭据；若缺少 `auth.json`，还会自动探测常见 `*_API_KEY` env
+- 对 fresh install，选择 API provider（OpenAI 或自定义）、模型，以及自定义 API key env var 名
+- 若环境里已导出对应 env var，则直接复用，再把 Scholar 特有部分（features、agents、MCP）合并进配置
+- 将 skills、agents、scripts、utils 复制到 `~/.codex/`
 
 **包含**：所有 55 个技能、15 个代理、Zotero MCP 配置、Obsidian 知识库 skills 和 AGENTS.md。
 
diff --git a/scripts/setup.sh b/scripts/setup.sh
index 9fa9acf..bca3bdc 100755
--- a/scripts/setup.sh
+++ b/scripts/setup.sh
@@ -21,9 +21,11 @@ SKIPPED_COUNT=0
 # --- State flags ---
 SKIP_PROVIDER=false
 SKIP_AUTH=false
+PERSIST_AUTH=false
 PROVIDER_NAME=""
 PROVIDER_URL=""
 MODEL=""
+AUTH_ENV_VAR_NAME="OPENAI_API_KEY"
 API_KEY=""
 
 # --- Colors ---
@@ -120,9 +122,108 @@ copy_dir_safely() {
   done < <(find "$src_dir" -type f -print0)
 }
 
+# ============================================================
+# Helpers
+# ============================================================
+mask_secret() {
+  local value="$1"
+  local length=${#value}
+  if [ "$length" -le 12 ]; then
+    printf '%s' "$value"
+    return
+  fi
+  printf '%s...%s' "${value:0:8}" "${value: -4}"
+}
+
+validate_env_var_name() {
+  local name="$1"
+  [[ "$name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || error "Invalid env var name: $name"
+}
+
+read_auth_entry() {
+  local file="$1"
+  [ -f "$file" ] || return 0
+  node -e '
+    const fs = require("fs");
+    try {
+      const data = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
+      for (const [key, value] of Object.entries(data)) {
+        if (typeof value === "string" && value.length > 0) {
+          process.stdout.write(`${key}	${value}`);
+          break;
+        }
+      }
+    } catch (error) {}
+  ' "$file"
+}
+
+normalize_env_prefix() {
+  local raw="$1"
+  printf '%s' "$raw" \
+    | tr '[:lower:]-./' '[:upper:]___' \
+    | sed 's/[^A-Z0-9_]/_/g; s/__*/_/g; s/^_//; s/_$//'
+}
+
+collect_api_key_candidates() {
+  local provider="$1"
+  local normalized_provider=""
+  local -a candidates=()
+
+  if [ -n "$provider" ]; then
+    normalized_provider=$(normalize_env_prefix "$provider")
+    if [ -n "$normalized_provider" ]; then
+      candidates+=("${normalized_provider}_API_KEY")
+    fi
+  fi
+
+  candidates+=(
+    "OPENAI_API_KEY"
+    "ANTHROPIC_API_KEY"
+    "OPENROUTER_API_KEY"
+    "GEMINI_API_KEY"
+    "GOOGLE_API_KEY"
+    "DEEPSEEK_API_KEY"
+    "DASHSCOPE_API_KEY"
+    "SILICONFLOW_API_KEY"
+    "XAI_API_KEY"
+    "GROQ_API_KEY"
+    "MISTRAL_API_KEY"
+    "COHERE_API_KEY"
+    "TOGETHER_API_KEY"
+    "FIREWORKS_API_KEY"
+    "MOONSHOT_API_KEY"
+    "ZHIPU_API_KEY"
+  )
+
+  printf '%s\n' "${candidates[@]}" | awk '!seen[$0]++'
+}
+
+detect_existing_env_auth() {
+  local provider="$1"
+  local candidate=""
+  local value=""
+
+  while IFS= read -r candidate; do
+    [ -n "$candidate" ] || continue
+    value="${!candidate:-}"
+    if [ -n "$value" ]; then
+      AUTH_ENV_VAR_NAME="$candidate"
+      API_KEY="$value"
+      PERSIST_AUTH=true
+      info "No auth.json found; detected $candidate from environment and will persist it for Codex compatibility"
+      return 0
+    fi
+  done < <(collect_api_key_candidates "$provider")
+
+  return 1
+}
+
+# ============================================================
+# Step 1: Check prerequisites
+# ============================================================
 check_deps() {
   command -v git >/dev/null || error "Git is required."
-  command -v python3 >/dev/null || error "Python 3 is required."
+  command -v node >/dev/null || error "Node.js is required."
   if ! command -v codex >/dev/null; then
     warn "Codex CLI not found. Install: npm i -g @openai/codex"
   fi
@@ -135,27 +236,33 @@ detect_existing() {
     local cur_model cur_provider
     cur_model=$(grep '^model ' "$CODEX_HOME/config.toml" 2>/dev/null | head -1 | sed 's/.*= *"//;s/".*//' || true)
     cur_provider=$(grep '^model_provider ' "$CODEX_HOME/config.toml" 2>/dev/null | head -1 | sed 's/.*= *"//;s/".*//' || true)
-    [ -n "$cur_model" ] && info "  Current model: $cur_model"
-    [ -n "$cur_provider" ] && info "  Current provider: $cur_provider"
-    echo ""
-    read -rp "Keep existing provider/model config? [Y/n]: " keep_config
-    if [ "$keep_config" != "n" ] && [ "$keep_config" != "N" ]; then
-      SKIP_PROVIDER=true
-      info "Keeping existing provider/model configuration"
+    PROVIDER_NAME="$cur_provider"
+    if [ -n "$cur_model" ]; then
+      info "  Current model: $cur_model"
+    fi
+    if [ -n "$cur_provider" ]; then
+      info "  Current provider: $cur_provider"
     fi
+    SKIP_PROVIDER=true
+    info "Detected existing provider/model configuration; keeping it without prompting"
   fi
 
   if [ -f "$CODEX_HOME/auth.json" ]; then
-    local existing_key
-    existing_key=$(grep -o '"OPENAI_API_KEY"[[:space:]]*:[[:space:]]*"[^"]*"' "$CODEX_HOME/auth.json" 2>/dev/null | sed 's/.*: *"//;s/"$//' || true)
-    if [ -n "$existing_key" ]; then
-      local masked="${existing_key:0:8}...${existing_key: -4}"
-      info "Existing API key found: $masked"
-      read -rp "Keep existing API key? [Y/n]: " keep_key
-      if [ "$keep_key" != "n" ] && [ "$keep_key" != "N" ]; then
-        SKIP_AUTH=true
-        info "Keeping existing API key"
-      fi
+    local auth_entry existing_key_name existing_key_value
+    auth_entry=$(read_auth_entry "$CODEX_HOME/auth.json")
+    if [ -n "$auth_entry" ]; then
+      IFS=$'	' read -r existing_key_name existing_key_value <<< "$auth_entry"
+      AUTH_ENV_VAR_NAME="$existing_key_name"
+      info "Existing auth.json credential found: $AUTH_ENV_VAR_NAME=$(mask_secret "$existing_key_value")"
+    else
+      info "Existing auth.json found; leaving it untouched"
+    fi
+    SKIP_AUTH=true
+    info "Detected existing authentication configuration; keeping it without prompting"
+  elif [ "$SKIP_PROVIDER" = true ]; then
+    SKIP_AUTH=true
+    if ! detect_existing_env_auth "$PROVIDER_NAME"; then
+      info "Existing Codex config detected; installer will not prompt for credentials or overwrite your current auth flow"
     fi
   fi
 }
@@ -199,28 +306,57 @@ choose_provider() {
   info "Provider: $PROVIDER_NAME | URL: $PROVIDER_URL | Model: $MODEL"
 }
 
+# ============================================================
+# Step 4: Configure API key (skipped if existing auth kept)
+# ============================================================
 configure_api_key() {
   if [ "$SKIP_AUTH" = true ]; then
     return
   fi
 
   echo ""
-  read -rp "Enter API key (OPENAI_API_KEY, or press Enter to skip): " API_KEY
+  read -rp "API key env var name (default: $AUTH_ENV_VAR_NAME): " input_env_name
+  AUTH_ENV_VAR_NAME="${input_env_name:-$AUTH_ENV_VAR_NAME}"
+  validate_env_var_name "$AUTH_ENV_VAR_NAME"
+
+  local env_value="${!AUTH_ENV_VAR_NAME:-}"
+  if [ -n "$env_value" ]; then
+    API_KEY="$env_value"
+    PERSIST_AUTH=true
+    info "Detected $AUTH_ENV_VAR_NAME in current environment; will reuse it without prompting for the key again"
+    return
+  fi
+
+  read -rsp "Enter API key for $AUTH_ENV_VAR_NAME (or press Enter to skip): " API_KEY
+  echo ""
   if [ -z "$API_KEY" ]; then
-    warn "No API key set. Make sure OPENAI_API_KEY is in your environment."
+    warn "No API key set. Make sure $AUTH_ENV_VAR_NAME is available in your environment before running Codex."
     SKIP_AUTH=true
+    return
   fi
+
+  PERSIST_AUTH=true
 }
 
 generate_fresh_config() {
   local template="$1"
   local target="$2"
 
-  sed -e "s|__MODEL__|$MODEL|g" \
-      -e "s|__PROVIDER_NAME__|$PROVIDER_NAME|g" \
-      -e "s|__PROVIDER_URL__|$PROVIDER_URL|g" \
-      "$template" > "$target"
-  info "Generated config.toml (model=$MODEL, provider=$PROVIDER_NAME)"
+  [ -f "$template" ] || error "Template config.toml not found at $template"
+
+  if [ "$SKIP_PROVIDER" = true ]; then
+    merge_scholar_config "$target" "$template"
+  else
+    if [ -f "$target" ]; then
+      cp "$target" "${target}.bak"
+      info "Backed up config.toml → config.toml.bak"
+    fi
+    sed -e "s|__MODEL__|$MODEL|g" \
+        -e "s|__PROVIDER_NAME__|$PROVIDER_NAME|g" \
+        -e "s|__PROVIDER_URL__|$PROVIDER_URL|g" \
+        "$template" > "$target"
+    info "Generated config.toml (model=$MODEL, provider=$PROVIDER_NAME)"
+  fi
 }
 
 merge_scholar_config() {
@@ -232,10 +368,14 @@ import os
 import pathlib
 import re
 
+  if ! grep -q '^\[features\]' "$target" 2>/dev/null; then
+    cat >> "$target" << 'FEATURES'
 
 def read(path: str) -> str:
     return pathlib.Path(path).read_text()
 
+  if ! grep -q '\[mcp_servers\.zotero\]' "$target" 2>/dev/null; then
+    cat >> "$target" << 'MCP'
 
 def extract_section_block(text: str, header: str) -> str:
     pattern = rf"(^\[{re.escape(header)}\]\n(?:.*\n)*?)(?=^\[|\Z)"
@@ -243,45 +383,9 @@ def extract_section_block(text: str, header: str) -> str:
     return m.group(1).rstrip() if m else ""
 
 
-def extract_agent_sections(text: str):
-    pattern = r"(^\[agents\.[^\]]+\]\n(?:.*\n)*?)(?=^\[|\Z)"
-    return re.findall(pattern, text, flags=re.M)
-
-
-target_path = os.environ['TARGET_PATH']
-template_path = os.environ['TEMPLATE_PATH']
-target = read(target_path)
-template = read(template_path)
-added = []
-
-for section in ['features', 'mcp_servers.zotero', 'mcp_servers.zotero.env']:
-    if f'[{section}]' not in target:
-        block = extract_section_block(template, section)
-        if block:
-            target += '\n\n' + block + '\n'
-            added.append(section)
-
-for block in extract_agent_sections(template):
-    header = re.search(r'^\[(agents\.[^\]]+)\]$', block, flags=re.M).group(1)
-    if f'[{header}]' not in target:
-        target += '\n\n' + block.rstrip() + '\n'
-        added.append(header)
-
-pathlib.Path(target_path).write_text(target.rstrip() + '\n')
-print(','.join(added))
-PY
-}
-
-generate_config() {
-  local template="$SRC_DIR/config.toml"
-  local target="$CODEX_HOME/config.toml"
-
-  [ -f "$template" ] || error "Template config.toml not found at $template"
-
-  if [ -f "$target" ]; then
-    backup_path "$target"
-    cp "$target" "${target}.bak"
-    info "Backed up config.toml → config.toml.bak"
+  if ! grep -q '\[agents\.' "$target" 2>/dev/null; then
+    sed -n '/^# --- Research Workflow/,$ p' "$template" >> "$target"
+    added=$((added + 1))
   fi
 
   if [ "$SKIP_PROVIDER" = true ]; then
@@ -297,8 +401,11 @@ generate_config() {
   fi
 }
 
+# ============================================================
+# Step 6: Write auth.json (only when installer captured a key)
+# ============================================================
 write_auth() {
-  if [ "$SKIP_AUTH" = true ]; then
+  if [ "$PERSIST_AUTH" != true ]; then
     return
   fi
 
@@ -308,28 +415,45 @@ write_auth() {
     cp "$target" "${target}.bak"
     info "Backed up auth.json → auth.json.bak"
   fi
-  cat > "$target" <<EOF
-{
-  "OPENAI_API_KEY": "$API_KEY"
-}
-EOF
+
+  node -e '
+    const fs = require("fs");
+    const envName = process.argv[1];
+    const apiKey = process.argv[2];
+    const target = process.argv[3];
+    const payload = {};
+    payload[envName] = apiKey;
+    if (envName !== "OPENAI_API_KEY") {
+      payload.OPENAI_API_KEY = apiKey;
+    }
+    fs.writeFileSync(target, JSON.stringify(payload, null, 2) + "\n");
+  ' "$AUTH_ENV_VAR_NAME" "$API_KEY" "$target"
   chmod 600 "$target"
-  info "Wrote auth.json (permissions: 600)"
+
+  if [ "$AUTH_ENV_VAR_NAME" = "OPENAI_API_KEY" ]; then
+    info "Wrote auth.json (permissions: 600)"
+  else
+    info "Wrote auth.json with $AUTH_ENV_VAR_NAME and OPENAI_API_KEY for Codex compatibility (permissions: 600)"
+  fi
 }
 
 copy_components() {
   if [ -d "$SRC_DIR/skills" ]; then
     copy_dir_safely "$SRC_DIR/skills" "$CODEX_HOME/skills"
   fi
+
   if [ -d "$SRC_DIR/agents" ]; then
     copy_dir_safely "$SRC_DIR/agents" "$CODEX_HOME/agents"
   fi
+
   if [ -f "$SRC_DIR/AGENTS.md" ]; then
     copy_file_safely "$SRC_DIR/AGENTS.md" "$CODEX_HOME/AGENTS.md"
   fi
+
   if [ -d "$SRC_DIR/scripts" ]; then
     copy_dir_safely "$SRC_DIR/scripts" "$CODEX_HOME/scripts"
   fi
+
   if [ -d "$SRC_DIR/utils" ]; then
     copy_dir_safely "$SRC_DIR/utils" "$CODEX_HOME/utils"
   fi
@@ -338,11 +462,7 @@ copy_components() {
 }
 
 configure_mcp() {
-  if ! grep -q '\[mcp_servers\.zotero\]' "$CODEX_HOME/config.toml" 2>/dev/null; then
-    return
-  fi
-
-  if awk '/\[mcp_servers\.zotero\]/{flag=1;next}/^\[/{flag=0}flag && /enabled = true/{found=1}END{exit(found?0:1)}' "$CODEX_HOME/config.toml"; then
+  if grep -q 'enabled = true' "$CODEX_HOME/config.toml" 2>/dev/null; then
     info "Zotero MCP already enabled"
     return
   fi

PATCH

echo "Patch applied successfully."
