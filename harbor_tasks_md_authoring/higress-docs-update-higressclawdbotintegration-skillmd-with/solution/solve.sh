#!/usr/bin/env bash
set -euo pipefail

cd /workspace/higress

# Idempotency guard
if grep -qF "**Important:** API key changes take effect immediately via hot-reload. No contai" ".claude/skills/higress-clawdbot-integration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/higress-clawdbot-integration/SKILL.md b/.claude/skills/higress-clawdbot-integration/SKILL.md
@@ -97,6 +97,23 @@ clawdbot models auth login --provider higress
 
 This will configure Clawdbot to use Higress AI Gateway as a model provider.
 
+### Step 6: Manage API Keys (optional)
+
+After deployment, you can manage API keys without redeploying:
+
+```bash
+# View configured API keys
+./get-ai-gateway.sh config list
+
+# Add or update an API key (hot-reload, no restart needed)
+./get-ai-gateway.sh config add --provider <provider> --key <api-key>
+
+# Remove an API key (hot-reload, no restart needed)
+./get-ai-gateway.sh config remove --provider <provider>
+```
+
+**Note:** Changes take effect immediately via hot-reload. No container restart required.
+
 ## CLI Parameters Reference
 
 ### Basic Options
@@ -148,6 +165,45 @@ $DATA_FOLDER/logs/access.log
 
 These logs can be used with the **agent-session-monitor** skill for token tracking and conversation analysis.
 
+## Managing API Keys
+
+After deployment, use the `config` subcommand to manage LLM provider API keys:
+
+```bash
+# List all configured API keys
+./get-ai-gateway.sh config list
+
+# Add or update an API key
+./get-ai-gateway.sh config add --provider deepseek --key sk-xxx
+
+# Remove an API key
+./get-ai-gateway.sh config remove --provider deepseek
+```
+
+**Important:** API key changes take effect immediately via hot-reload. No container restart is required.
+
+**Supported providers:**
+- `dashscope` (or `qwen`) - Aliyun Dashscope (Qwen)
+- `deepseek` - DeepSeek
+- `moonshot` (or `kimi`) - Moonshot (Kimi)
+- `zhipuai` (or `zhipu`) - Zhipu AI
+- `openai` - OpenAI
+- `openrouter` - OpenRouter
+- `claude` - Claude
+- `gemini` - Google Gemini
+- `groq` - Groq
+- `doubao` - Doubao
+- `baichuan` - Baichuan AI
+- `yi` - 01.AI (Yi)
+- `stepfun` - Stepfun
+- `minimax` - Minimax
+- `cohere` - Cohere
+- `mistral` - Mistral AI
+- `github` - Github Models
+- `fireworks` - Fireworks AI
+- `togetherai` (or `together`) - Together AI
+- `grok` - Grok
+
 ## Managing Routing Rules
 
 After deployment, use the `route` subcommand to manage auto-routing rules:
@@ -270,7 +326,40 @@ curl 'http://localhost:8080/v1/chat/completions' \
 - deep thinking What's the best architecture for this system?
 ```
 
-### Example 4: Full Integration with Clawdbot
+### Example 4: Manage API Keys
+
+**User:** 帮我查看当前配置的API keys，并添加一个DeepSeek的key
+
+**Steps:**
+1. List current API keys:
+   ```bash
+   ./get-ai-gateway.sh config list
+   ```
+
+2. Add DeepSeek API key:
+   ```bash
+   ./get-ai-gateway.sh config add --provider deepseek --key sk-xxx
+   ```
+
+**Response:**
+```
+当前配置的API keys:
+
+  Aliyun Dashscope (Qwen): sk-ab***ef12
+  OpenAI:                  sk-cd***gh34
+
+Adding API key for DeepSeek...
+Updating AI Gateway configuration...
+
+✅ API key updated successfully!
+
+Provider: DeepSeek
+Key: sk-xx***yy56
+
+Configuration has been hot-reloaded (no restart needed).
+```
+
+### Example 5: Full Integration with Clawdbot
 
 **User:** 完整配置Higress和Clawdbot的集成
 
PATCH

echo "Gold patch applied."
