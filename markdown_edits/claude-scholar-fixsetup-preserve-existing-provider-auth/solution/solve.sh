#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-scholar

# Idempotent: skip if already applied
if grep -q 'PERSIST_AUTH=false' scripts/setup.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# The PR merge had a corrupted merge_scholar_config function.
# We need to write a correct version directly.

cat > scripts/setup.sh <<'SETUP_EOF'
#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Counters ---
BACKUP_COUNT=0
UPDATED_COUNT=0
SKIPPED_COUNT=0

# --- State flags ---
SKIP_PROVIDER=false
SKIP_AUTH=false
PERSIST_AUTH=false
PROVIDER_NAME=""
PROVIDER_URL=""
MODEL=""
AUTH_ENV_VAR_NAME="OPENAI_API_KEY"
API_KEY=""

# --- Colors ---
info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; exit 1; }
bold()  { echo -e "\033[1m$*\033[0m"; }

# --- Presets ---
PRESET_NAMES=(openai custom)
PRESET_LABELS=("OpenAI API" "Custom/OpenAI-compatible")
PRESET_URLS=("https://api.openai.com/v1" "")
PRESET_MODELS=("gpt-4o" "")

# ============================================================
# Backup utilities
# ============================================================
backup_path() {
  local target="$1"
  [ -e "$target" ] || return 0
  local backup_dir="$CODEX_HOME/.backups/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$backup_dir"
  local rel
  rel=$(basename "$target")
  cp -R "$target" "$backup_dir/$rel"
  BACKUP_COUNT=$((BACKUP_COUNT + 1))
}

copy_file_safely() {
  local src_file="$1"
  local target_file="$2"
  mkdir -p "$(dirname "$target_file")"
  if [ -f "$target_file" ] && cmp -s "$src_file" "$target_file"; then
    SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    return 0
  fi
  if [ -e "$target_file" ]; then
    backup_path "$target_file"
    [ -d "$target_file" ] && rm -rf "$target_file"
  fi
  cp -p "$src_file" "$target_file"
  UPDATED_COUNT=$((UPDATED_COUNT + 1))
}

copy_dir_safely() {
  local src_dir="$1"
  local target_dir="$2"
  if [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
    backup_path "$target_dir"
    rm -f "$target_dir"
  fi
  mkdir -p "$target_dir"
  while IFS= read -r -d '' src_file; do
    local rel="${src_file#$src_dir/}"
    local target_file="$target_dir/$rel"
    copy_file_safely "$src_file" "$target_file"
  done < <(find "$src_dir" -type f -print0)
}

# ============================================================
# Helpers
# ============================================================
mask_secret() {
  local value="$1"
  local length=${#value}
  if [ "$length" -le 12 ]; then
    printf '%s' "$value"
    return
  fi
  printf '%s...%s' "${value:0:8}" "${value: -4}"
}

validate_env_var_name() {
  local name="$1"
  [[ "$name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || error "Invalid env var name: $name"
}

read_auth_entry() {
  local file="$1"
  [ -f "$file" ] || return 0
  node -e '
    const fs = require("fs");
    try {
      const data = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
      for (const [key, value] of Object.entries(data)) {
        if (typeof value === "string" && value.length > 0) {
          process.stdout.write(`${key}\t${value}`);
          break;
        }
      }
    } catch (error) {}
  ' "$file"
}

normalize_env_prefix() {
  local raw="$1"
  printf '%s' "$raw" \
    | tr '[:lower:]-./' '[:upper:]___' \
    | sed 's/[^A-Z0-9_]/_/g; s/__*/_/g; s/^_//; s/_$//'
}

collect_api_key_candidates() {
  local provider="$1"
  local normalized_provider=""
  local -a candidates=()

  if [ -n "$provider" ]; then
    normalized_provider=$(normalize_env_prefix "$provider")
    if [ -n "$normalized_provider" ]; then
      candidates+=("${normalized_provider}_API_KEY")
    fi
  fi

  candidates+=(
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "OPENROUTER_API_KEY"
    "GEMINI_API_KEY"
    "GOOGLE_API_KEY"
    "DEEPSEEK_API_KEY"
    "DASHSCOPE_API_KEY"
    "SILICONFLOW_API_KEY"
    "XAI_API_KEY"
    "GROQ_API_KEY"
    "MISTRAL_API_KEY"
    "COHERE_API_KEY"
    "TOGETHER_API_KEY"
    "FIREWORKS_API_KEY"
    "MOONSHOT_API_KEY"
    "ZHIPU_API_KEY"
  )

  printf '%s\n' "${candidates[@]}" | awk '!seen[$0]++'
}

detect_existing_env_auth() {
  local provider="$1"
  local candidate=""
  local value=""

  while IFS= read -r candidate; do
    [ -n "$candidate" ] || continue
    value="${!candidate:-}"
    if [ -n "$value" ]; then
      AUTH_ENV_VAR_NAME="$candidate"
      API_KEY="$value"
      PERSIST_AUTH=true
      info "No auth.json found; detected $candidate from environment and will persist it for Codex compatibility"
      return 0
    fi
  done < <(collect_api_key_candidates "$provider")

  return 1
}

# ============================================================
# Step 1: Check prerequisites
# ============================================================
check_deps() {
  command -v git >/dev/null || error "Git is required."
  command -v node >/dev/null || error "Node.js is required."
  if ! command -v codex >/dev/null; then
    warn "Codex CLI not found. Install: npm i -g @openai/codex"
  fi
}

# ============================================================
# Step 2: Detect existing configuration
# ============================================================
detect_existing() {
  echo ""
  if [ -f "$CODEX_HOME/config.toml" ]; then
    info "Existing config.toml found at $CODEX_HOME/config.toml"
    local cur_model cur_provider
    cur_model=$(grep '^model ' "$CODEX_HOME/config.toml" 2>/dev/null | head -1 | sed 's/.*= *"//;s/".*//' || true)
    cur_provider=$(grep '^model_provider ' "$CODEX_HOME/config.toml" 2>/dev/null | head -1 | sed 's/.*= *"//;s/".*//' || true)
    PROVIDER_NAME="$cur_provider"
    if [ -n "$cur_model" ]; then
      info "  Current model: $cur_model"
    fi
    if [ -n "$cur_provider" ]; then
      info "  Current provider: $cur_provider"
    fi
    SKIP_PROVIDER=true
    info "Detected existing provider/model configuration; keeping it without prompting"
  fi

  if [ -f "$CODEX_HOME/auth.json" ]; then
    local auth_entry existing_key_name existing_key_value
    auth_entry=$(read_auth_entry "$CODEX_HOME/auth.json")
    if [ -n "$auth_entry" ]; then
      IFS=$'\t' read -r existing_key_name existing_key_value <<< "$auth_entry"
      AUTH_ENV_VAR_NAME="$existing_key_name"
      info "Existing auth.json credential found: $AUTH_ENV_VAR_NAME=$(mask_secret "$existing_key_value")"
    else
      info "Existing auth.json found; leaving it untouched"
    fi
    SKIP_AUTH=true
    info "Detected existing authentication configuration; keeping it without prompting"
  elif [ "$SKIP_PROVIDER" = true ]; then
    SKIP_AUTH=true
    if ! detect_existing_env_auth "$PROVIDER_NAME"; then
      info "Existing Codex config detected; installer will not prompt for credentials or overwrite your current auth flow"
    fi
  fi
}

# ============================================================
# Step 3: Choose provider and model
# ============================================================
choose_provider() {
  if [ "$SKIP_PROVIDER" = true ]; then
    return
  fi

  echo ""
  bold "Select API provider:"
  echo ""
  for i in "${!PRESET_LABELS[@]}"; do
    echo "  $((i+1))) ${PRESET_LABELS[$i]}"
  done
  echo ""

  local choice
  read -rp "Enter choice [1-2] (default: 1): " choice
  choice="${choice:-1}"

  local idx=$((choice - 1))
  if [ "$idx" -lt 0 ] || [ "$idx" -ge "${#PRESET_NAMES[@]}" ]; then
    error "Invalid choice: $choice"
  fi

  PROVIDER_NAME="${PRESET_NAMES[$idx]}"
  PROVIDER_URL="${PRESET_URLS[$idx]}"
  MODEL="${PRESET_MODELS[$idx]}"

  if [ "$PROVIDER_NAME" = "custom" ]; then
    read -rp "Provider name: " PROVIDER_NAME
    read -rp "Base URL: " PROVIDER_URL
    read -rp "Model name: " MODEL
  else
    echo ""
    read -rp "Model name (default: $MODEL): " input_model
    MODEL="${input_model:-$MODEL}"
  fi

  info "Provider: $PROVIDER_NAME | URL: $PROVIDER_URL | Model: $MODEL"
}

# ============================================================
# Step 4: Configure API key (skipped if existing auth kept)
# ============================================================
configure_api_key() {
  if [ "$SKIP_AUTH" = true ]; then
    return
  fi

  echo ""
  read -rp "API key env var name (default: $AUTH_ENV_VAR_NAME): " input_env_name
  AUTH_ENV_VAR_NAME="${input_env_name:-$AUTH_ENV_VAR_NAME}"
  validate_env_var_name "$AUTH_ENV_VAR_NAME"

  local env_value="${!AUTH_ENV_VAR_NAME:-}"
  if [ -n "$env_value" ]; then
    API_KEY="$env_value"
    PERSIST_AUTH=true
    info "Detected $AUTH_ENV_VAR_NAME in current environment; will reuse it without prompting for the key again"
    return
  fi

  read -rsp "Enter API key for $AUTH_ENV_VAR_NAME (or press Enter to skip): " API_KEY
  echo ""
  if [ -z "$API_KEY" ]; then
    warn "No API key set. Make sure $AUTH_ENV_VAR_NAME is available in your environment before running Codex."
    SKIP_AUTH=true
    return
  fi

  PERSIST_AUTH=true
}

generate_fresh_config() {
  local template="$1"
  local target="$2"

  [ -f "$template" ] || error "Template config.toml not found at $template"

  if [ "$SKIP_PROVIDER" = true ]; then
    merge_scholar_config "$target" "$template"
  else
    if [ -f "$target" ]; then
      cp "$target" "${target}.bak"
      info "Backed up config.toml → config.toml.bak"
    fi
    sed -e "s|__MODEL__|$MODEL|g" \
        -e "s|__PROVIDER_NAME__|$PROVIDER_NAME|g" \
        -e "s|__PROVIDER_URL__|$PROVIDER_URL|g" \
        "$template" > "$target"
    info "Generated config.toml (model=$MODEL, provider=$PROVIDER_NAME)"
  fi
}

merge_scholar_config() {
  local target="$1"
  local template="$2"

  TARGET_PATH="$target" TEMPLATE_PATH="$template" python3 <<'PY'
import os
import pathlib
import re

def read(path: str) -> str:
    return pathlib.Path(path).read_text()

def extract_section_block(text: str, header: str) -> str:
    pattern = rf"(^\[{re.escape(header)}\]\n(?:.*\n)*?)(?=^\[|\Z)"
    m = re.search(pattern, text, flags=re.M)
    return m.group(1).rstrip() if m else ""

def extract_agent_sections(text: str):
    pattern = r"(^\[agents\.[^\]]+\]\n(?:.*\n)*?)(?=^\[|\Z)"
    return re.findall(pattern, text, flags=re.M)

target_path = os.environ['TARGET_PATH']
template_path = os.environ['TEMPLATE_PATH']
target = read(target_path)
template = read(template_path)
added = []

for section in ['features', 'mcp_servers.zotero', 'mcp_servers.zotero.env']:
    if f'[{section}]' not in target:
        block = extract_section_block(template, section)
        if block:
            target += '\n\n' + block + '\n'
            added.append(section)

for block in extract_agent_sections(template):
    header = re.search(r'^\[(agents\.[^\]]+)\]$', block, flags=re.M).group(1)
    if f'[{header}]' not in target:
        target += '\n\n' + block.rstrip() + '\n'
        added.append(header)

pathlib.Path(target_path).write_text(target.rstrip() + '\n')
print(','.join(added))
PY
}

generate_config() {
  local template="$SRC_DIR/config.toml"
  local target="$CODEX_HOME/config.toml"

  [ -f "$template" ] || error "Template config.toml not found at $template"

  if [ -f "$target" ]; then
    backup_path "$target"
    cp "$target" "${target}.bak"
    info "Backed up config.toml → config.toml.bak"
  fi

  if [ "$SKIP_PROVIDER" = true ]; then
    local added
    added=$(merge_scholar_config "$target" "$template")
    if [ -n "$added" ]; then
      info "Merged Scholar sections into existing config.toml: $added"
    else
      info "Config already had the required Scholar sections"
    fi
  else
    generate_fresh_config "$template" "$target"
  fi
}

# ============================================================
# Step 6: Write auth.json (only when installer captured a key)
# ============================================================
write_auth() {
  if [ "$PERSIST_AUTH" != true ]; then
    return
  fi

  local target="$CODEX_HOME/auth.json"
  if [ -f "$target" ]; then
    backup_path "$target"
    cp "$target" "${target}.bak"
    info "Backed up auth.json → auth.json.bak"
  fi

  node -e '
    const fs = require("fs");
    const envName = process.argv[1];
    const apiKey = process.argv[2];
    const target = process.argv[3];
    const payload = {};
    payload[envName] = apiKey;
    if (envName !== "OPENAI_API_KEY") {
      payload.OPENAI_API_KEY = apiKey;
    }
    fs.writeFileSync(target, JSON.stringify(payload, null, 2) + "\n");
  ' "$AUTH_ENV_VAR_NAME" "$API_KEY" "$target"
  chmod 600 "$target"

  if [ "$AUTH_ENV_VAR_NAME" = "OPENAI_API_KEY" ]; then
    info "Wrote auth.json (permissions: 600)"
  else
    info "Wrote auth.json with $AUTH_ENV_VAR_NAME and OPENAI_API_KEY for Codex compatibility (permissions: 600)"
  fi
}

copy_components() {
  if [ -d "$SRC_DIR/skills" ]; then
    copy_dir_safely "$SRC_DIR/skills" "$CODEX_HOME/skills"
  fi

  if [ -d "$SRC_DIR/agents" ]; then
    copy_dir_safely "$SRC_DIR/agents" "$CODEX_HOME/agents"
  fi

  if [ -f "$SRC_DIR/AGENTS.md" ]; then
    copy_file_safely "$SRC_DIR/AGENTS.md" "$CODEX_HOME/AGENTS.md"
  fi

  if [ -d "$SRC_DIR/scripts" ]; then
    copy_dir_safely "$SRC_DIR/scripts" "$CODEX_HOME/scripts"
  fi

  if [ -d "$SRC_DIR/utils" ]; then
    copy_dir_safely "$SRC_DIR/utils" "$CODEX_HOME/utils"
  fi

  info "Synced repo-managed Codex components"
}

configure_mcp() {
  if grep -q 'enabled = true' "$CODEX_HOME/config.toml" 2>/dev/null; then
    info "Zotero MCP already enabled"
    return
  fi

  echo ""
  read -rp "Enable Zotero MCP server? [y/N]: " enable_zotero
  if [ "$enable_zotero" = "y" ] || [ "$enable_zotero" = "Y" ]; then
    python3 - "$CODEX_HOME/config.toml" <<'PY'
import pathlib
import re
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text()
text = re.sub(r'(\[mcp_servers\.zotero\]\n(?:.*\n)*?enabled = )false', r'\1true', text, count=1)
path.write_text(text)
PY
    info "Zotero MCP enabled"
    if ! command -v zotero-mcp >/dev/null 2>&1; then
      warn "zotero-mcp not found. Install latest with: uv tool install --reinstall git+https://github.com/Galaxy-Dawn/zotero-mcp.git"
    fi
  fi
}

main() {
  echo ""
  echo "╔══════════════════════════════════════╗"
  echo "║   Claude Scholar Installer (Codex)   ║"
  echo "╚══════════════════════════════════════╝"
  echo ""

  check_deps

  info "Source: $SRC_DIR"
  info "Target: $CODEX_HOME"
  mkdir -p "$CODEX_HOME"

  detect_existing
  choose_provider
  configure_api_key
  generate_config
  write_auth
  copy_components
  configure_mcp

  echo ""
  echo "============================================================"
  info "Installation complete!"
  info "Updated files: $UPDATED_COUNT | Unchanged files skipped: $SKIPPED_COUNT | Backups created: $BACKUP_COUNT"
  if [ "$BACKUP_READY" -eq 1 ]; then
    info "Recover previous files from: $BACKUP_DIR"
  fi
  echo ""
  echo "  Config:  $CODEX_HOME/config.toml"
  echo "  Auth:    $CODEX_HOME/auth.json"
  echo "  Skills:  $CODEX_HOME/skills/"
  echo "  Agents:  $CODEX_HOME/agents/"
  echo ""
  info "Existing model/provider/API key settings are preserved when you choose the incremental update path."
  echo "  Run $(bold 'codex') to start."
  echo "============================================================"
}

main "$@"
SETUP_EOF

# Update README.md
sed -i 's/- Preserve your existing provider\/model choices unless you explicitly reconfigure them/- Silently preserve existing `config.toml` provider\/model and existing `auth.json` credentials, and auto-detect common `*_API_KEY` env vars when `auth.json` is absent/' README.md
sed -i 's/- Preserve existing API keys, auth files, permissions, and unrelated config fields/- For fresh installs, choose API provider (OpenAI or custom), model, and a custom API key env var name/' README.md
sed -i 's/- Merge Scholar-managed sections (features, agents, MCP, skills paths) into the existing config instead of overwriting the whole file/- Reuse an already-exported env var when available, then merge Scholar-specific sections (features, agents, MCP) into config/' README.md
sed -i 's/- Copy or refresh skills, agents, scripts, and utilities under `~\/.codex\/` with backups for overwritten managed files/- Copy skills, agents, scripts, and utils to `~\/.codex\/`/' README.md

# Update README.zh-CN.md
sed -i 's/- 保留你现有的 provider\/model 选择，除非你明确要求重配/- 静默保留已有 `config.toml` 中的 provider\/model，以及现有 `auth.json` 凭据；若缺少 `auth.json`，还会自动探测常见 `*_API_KEY` env/' README.zh-CN.md
sed -i 's/- 保留已有 API keys、auth 文件、权限配置和无关字段/- 对 fresh install，选择 API provider（OpenAI 或自定义）、模型，以及自定义 API key env var 名/' README.zh-CN.md
sed -i 's/- 将 Scholar 管理的部分（features、agents、MCP、skills 路径）增量合并到现有配置，而不是整体覆盖/- 若环境里已导出对应 env var，则直接复用，再把 Scholar 特有部分（features、agents、MCP）合并进配置/' README.zh-CN.md
sed -i 's/- 将 skills、agents、scripts、utils 刷新到 `~\/.codex\/`，并为被覆盖的受管文件创建备份/- 将 skills、agents、scripts、utils 复制到 `~\/.codex\/`/' README.zh-CN.md

echo "Patch applied successfully."
