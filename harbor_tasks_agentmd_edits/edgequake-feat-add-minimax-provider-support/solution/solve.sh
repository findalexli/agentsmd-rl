#!/usr/bin/env bash
set -euo pipefail

cd /workspace/edgequake

# Idempotent: skip if already applied
if grep -q '"minimax" => "MiniMax-M2.7"' edgequake/crates/edgequake-api/src/safety_limits.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.env.example b/.env.example
index 7156489c..8fb3b1b6 100644
--- a/.env.example
+++ b/.env.example
@@ -65,7 +65,19 @@ OLLAMA_HOST=http://localhost:11434
 #   - Embedding: embeddinggemma (768 dimensions)

 # -----------------------------------------------------------------------------
-# Option 3: LM Studio (Local, OpenAI-compatible API)
+# Option 3: MiniMax (Cloud-hosted, OpenAI-compatible API)
+# -----------------------------------------------------------------------------
+# MINIMAX_API_KEY=your-minimax-api-key-here
+# MINIMAX_BASE_URL=https://api.minimax.io/v1  # Optional: default is https://api.minimax.io/v1
+# For China mainland, use: https://api.minimaxi.com/v1
+
+# Default MiniMax Models (set in models.toml):
+#   - Chat/LLM: MiniMax-M2.7 (204K context, latest flagship model)
+#   - Fast: MiniMax-M2.7-highspeed (204K context, low-latency)
+#   - Legacy: MiniMax-M2.5, MiniMax-M2.5-highspeed
+
+# -----------------------------------------------------------------------------
+# Option 4: LM Studio (Local, OpenAI-compatible API)
 # -----------------------------------------------------------------------------
 # LMSTUDIO_HOST=http://localhost:1234
 # LMSTUDIO_MODEL=gemma2-9b-it                # Chat model
diff --git a/README.md b/README.md
index 9bafaa41..49f98834 100644
--- a/README.md
+++ b/README.md
@@ -225,7 +225,7 @@ curl -X POST http://localhost:8080/api/v1/query \
 │  Backend (Rust - 11 Crates)                                                 │
 │  ┌──────────────────────────────────────────────────────────────────────┐   │
 │  │  edgequake-core          │  Orchestration & Pipeline                 │   │
-│  │  edgequake-llm           │  OpenAI, Ollama, LM Studio, Mock          │   │
+│  │  edgequake-llm           │  OpenAI, Anthropic, MiniMax, Ollama, etc.  │   │
 │  │  edgequake-storage       │  PostgreSQL AGE, Memory adapters          │   │
 │  │  edgequake-api           │  REST API server                          │   │
 │  │  edgequake-pipeline      │  Document ingestion pipeline              │   │
@@ -242,9 +242,10 @@ curl -X POST http://localhost:8080/api/v1/query \
 │  ┌─────────────────────────────┐   ┌──────────────────────────────────┐     │
 │  │   LLM Providers             │   │   Storage Backends               │     │
 │  │  • OpenAI (gpt-4.1-nano)    │   │  • PostgreSQL 15+ (AGE + vector) │     │
-│  │  • Ollama (gemma3:12b)      │   │  • In-Memory (dev/testing)       │     │
-│  │  • LM Studio (local models) │   │  • Graph: Property graph model   │     │
-│  │  • Mock (testing, free)     │   │  • Vector: pgvector embeddings   │     │
+│  │  • Anthropic (Claude)       │   │  • In-Memory (dev/testing)       │     │
+│  │  • MiniMax (MiniMax-M2.7)   │   │  • Graph: Property graph model   │     │
+│  │  • Ollama (gemma3:12b)      │   │  • Vector: pgvector embeddings   │     │
+│  │  • LM Studio, xAI, Gemini  │   │                                  │     │
 │  │  Auto-detection via env     │   │                                  │     │
 │  └─────────────────────────────┘   └──────────────────────────────────┘     │
 └─────────────────────────────────────────────────────────────────────────────┘
diff --git a/docs/operations/configuration.md b/docs/operations/configuration.md
index b8b80fc4..57130ce5 100644
--- a/docs/operations/configuration.md
+++ b/docs/operations/configuration.md
@@ -116,6 +116,13 @@ DATABASE_URL="postgresql://edgequake:pass@pgbouncer:6432/edgequake"
 | `OPENROUTER_API_KEY`  | String | None                        | OpenRouter API key (required) |
 | `OPENROUTER_BASE_URL` | String | `https://openrouter.ai/api` | API endpoint                  |

+#### MiniMax
+
+| Variable            | Type   | Default                      | Description                                          |
+| ------------------- | ------ | ---------------------------- | ---------------------------------------------------- |
+| `MINIMAX_API_KEY`   | String | None                         | MiniMax API key (required)                           |
+| `MINIMAX_BASE_URL`  | String | `https://api.minimax.io/v1`  | API endpoint (use `https://api.minimaxi.com/v1` for China) |
+
 #### Azure OpenAI

 | Variable                   | Type   | Default              | Description                 |
@@ -201,6 +208,7 @@ image_per_unit = 0.0
 | `gemini`     | Google Gemini models    | `GEMINI_API_KEY`       |
 | `xai`        | xAI Grok models         | `XAI_API_KEY`          |
 | `openrouter` | OpenRouter aggregator   | `OPENROUTER_API_KEY`   |
+| `minimax`    | MiniMax AI models       | `MINIMAX_API_KEY`      |
 | `azure`      | Azure OpenAI            | `AZURE_OPENAI_API_KEY` |
 | `ollama`     | Ollama local models     | None (local)           |
 | `lm_studio`  | LM Studio local         | None (local)           |
diff --git a/edgequake/crates/edgequake-api/src/provider_types.rs b/edgequake/crates/edgequake-api/src/provider_types.rs
index 7939865b..b4954e3b 100644
--- a/edgequake/crates/edgequake-api/src/provider_types.rs
+++ b/edgequake/crates/edgequake-api/src/provider_types.rs
@@ -299,6 +299,27 @@ impl AvailableProvidersResponse {
                     embedding_dimension: 768,
                 },
             },
+            ProviderInfo {
+                id: "minimax".to_string(),
+                name: "MiniMax".to_string(),
+                description: "MiniMax AI (MiniMax-M2.7) - Latest flagship model with enhanced reasoning and coding"
+                    .to_string(),
+                available: std::env::var("MINIMAX_API_KEY").is_ok(),
+                config_requirements: {
+                    let api_key_set = std::env::var("MINIMAX_API_KEY").is_ok();
+                    vec![ConfigRequirement {
+                        env_var: "MINIMAX_API_KEY".to_string(),
+                        required: true,
+                        description: "MiniMax API key".to_string(),
+                        satisfied: api_key_set,
+                    }]
+                },
+                default_models: DefaultModels {
+                    chat_model: "MiniMax-M2.7".to_string(),
+                    embedding_model: "".to_string(),
+                    embedding_dimension: 0,
+                },
+            },
             ProviderInfo {
                 id: "azure".to_string(),
                 name: "Azure OpenAI".to_string(),
diff --git a/edgequake/crates/edgequake-api/src/safety_limits.rs b/edgequake/crates/edgequake-api/src/safety_limits.rs
index b55c76bc..aef03599 100644
--- a/edgequake/crates/edgequake-api/src/safety_limits.rs
+++ b/edgequake/crates/edgequake-api/src/safety_limits.rs
@@ -355,6 +355,7 @@ pub fn default_model_for_provider(provider_name: &str) -> &'static str {
         "openrouter" => "openai/gpt-4o-mini",
         "ollama" => "gemma3:12b",
         "lmstudio" | "lm-studio" | "lm_studio" => "gemma-3n-e4b-it",
+        "minimax" => "MiniMax-M2.7",
         "mock" => "mock-model",
         _ => "gpt-4.1-nano",
     }
diff --git a/edgequake/models.toml b/edgequake/models.toml
index 22e4d519..28d360e9 100644
--- a/edgequake/models.toml
+++ b/edgequake/models.toml
@@ -25,6 +25,7 @@
 #   - Anthropic: claude-sonnet-4-5-20250929 (LLM)
 #   - Gemini: gemini-2.5-flash (LLM), gemini-embedding-001 (embedding)
 #   - xAI: grok-4-1-fast (LLM)
+#   - MiniMax: MiniMax-M2.7 (LLM)
 #   - OpenRouter: openai/gpt-4o-mini (LLM)
 #   - Ollama: gemma3:12b (LLM), embeddinggemma (embedding)
 #   - LM Studio: gemma-3n-e4b-it (LLM), text-embedding-nomic-embed-text-v1.5 (embedding)
@@ -1542,6 +1543,119 @@ output_per_1k = 0.0
 embedding_per_1k = 0.00015
 image_per_unit = 0.0

+# =============================================================================
+# MINIMAX PROVIDER
+# =============================================================================
+# MiniMax AI models via OpenAI-compatible API
+# Requires: MINIMAX_API_KEY environment variable
+# Pricing verified: March 2025 (platform.minimax.io)
+
+[[providers]]
+name = "minimax"
+display_name = "MiniMax"
+type = "openaicompatible"
+api_base = "https://api.minimax.io/v1"
+api_key_env = "MINIMAX_API_KEY"
+enabled = true
+priority = 18
+description = "MiniMax AI - Peak performance models with 204K context and competitive pricing"
+
+[[providers.models]]
+name = "MiniMax-M2.7"
+display_name = "MiniMax M2.7"
+model_type = "llm"
+description = "Latest flagship model with enhanced reasoning and coding"
+deprecated = false
+tags = ["recommended", "reasoning", "cost-effective"]
+
+[providers.models.capabilities]
+context_length = 204800
+max_output_tokens = 192000
+supports_vision = false
+supports_function_calling = true
+supports_json_mode = true
+supports_streaming = true
+supports_system_message = true
+embedding_dimension = 0
+
+[providers.models.cost]
+input_per_1k = 0.0003
+output_per_1k = 0.0012
+embedding_per_1k = 0.0
+image_per_unit = 0.0
+
+[[providers.models]]
+name = "MiniMax-M2.7-highspeed"
+display_name = "MiniMax M2.7 High Speed"
+model_type = "llm"
+description = "High-speed version of M2.7 for low-latency scenarios"
+deprecated = false
+tags = ["fast", "cost-effective"]
+
+[providers.models.capabilities]
+context_length = 204800
+max_output_tokens = 192000
+supports_vision = false
+supports_function_calling = true
+supports_json_mode = true
+supports_streaming = true
+supports_system_message = true
+embedding_dimension = 0
+
+[providers.models.cost]
+input_per_1k = 0.0006
+output_per_1k = 0.0024
+embedding_per_1k = 0.0
+image_per_unit = 0.0
+
+[[providers.models]]
+name = "MiniMax-M2.5"
+display_name = "MiniMax M2.5"
+model_type = "llm"
+description = "Peak Performance. Ultimate Value. Master the Complex"
+deprecated = false
+tags = ["reasoning", "cost-effective"]
+
+[providers.models.capabilities]
+context_length = 204800
+max_output_tokens = 192000
+supports_vision = false
+supports_function_calling = true
+supports_json_mode = true
+supports_streaming = true
+supports_system_message = true
+embedding_dimension = 0
+
+[providers.models.cost]
+input_per_1k = 0.0003
+output_per_1k = 0.0012
+embedding_per_1k = 0.0
+image_per_unit = 0.0
+
+[[providers.models]]
+name = "MiniMax-M2.5-highspeed"
+display_name = "MiniMax M2.5 High Speed"
+model_type = "llm"
+description = "Same performance, faster and more agile"
+deprecated = false
+tags = ["fast", "cost-effective"]
+
+[providers.models.capabilities]
+context_length = 204800
+max_output_tokens = 192000
+supports_vision = false
+supports_function_calling = true
+supports_json_mode = true
+supports_streaming = true
+supports_system_message = true
+embedding_dimension = 0
+
+[providers.models.cost]
+input_per_1k = 0.0006
+output_per_1k = 0.0024
+embedding_per_1k = 0.0
+image_per_unit = 0.0
+
 # =============================================================================
 # MOCK PROVIDER
 # =============================================================================
diff --git a/edgequake_webui/src/components/models/model-card.tsx b/edgequake_webui/src/components/models/model-card.tsx
index 852ec674..c9824902 100644
--- a/edgequake_webui/src/components/models/model-card.tsx
+++ b/edgequake_webui/src/components/models/model-card.tsx
@@ -67,6 +67,8 @@ function getProviderIcon(providerId: string, className?: string) {
       return <Sparkles className={cn(iconClass, 'text-orange-600')} />;
     case 'azure':
       return <Cloud className={cn(iconClass, 'text-blue-500')} />;
+    case 'minimax':
+      return <Sparkles className={cn(iconClass, 'text-teal-600')} />;
     case 'mock':
       return <FlaskConical className={cn(iconClass, 'text-gray-500')} />;
     default:
diff --git a/edgequake_webui/src/components/models/model-selector.tsx b/edgequake_webui/src/components/models/model-selector.tsx
index cf233b00..2c2cbd20 100644
--- a/edgequake_webui/src/components/models/model-selector.tsx
+++ b/edgequake_webui/src/components/models/model-selector.tsx
@@ -119,6 +119,8 @@ function getProviderIcon(providerId: string, className?: string) {
       return <Globe className={cn(iconClass, 'text-indigo-600')} />;
     case 'azure':
       return <Cloud className={cn(iconClass, 'text-sky-600')} />;
+    case 'minimax':
+      return <Sparkles className={cn(iconClass, 'text-teal-600')} />;
     case 'mock':
       return <FlaskConical className={cn(iconClass, 'text-gray-500')} />;
     default:
diff --git a/edgequake_webui/src/components/settings/provider-status-card.tsx b/edgequake_webui/src/components/settings/provider-status-card.tsx
index ebff1ee9..aa433e19 100644
--- a/edgequake_webui/src/components/settings/provider-status-card.tsx
+++ b/edgequake_webui/src/components/settings/provider-status-card.tsx
@@ -78,6 +78,7 @@ export function ProviderStatusCard() {
       'xai': 'xAI',
       'openrouter': 'OpenRouter',
       'azure': 'Azure OpenAI',
+      'minimax': 'MiniMax',
       'mock': 'Mock (Development)',
     };
     return names[name.toLowerCase()] || name;
@@ -143,6 +144,12 @@ export EDGEQUAKE_LLM_MODEL="openai/gpt-4o-mini"`,
 export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
 export EDGEQUAKE_LLM_PROVIDER="azure"`,
       },
+      'minimax': {
+        label: 'MiniMax Configuration',
+        code: `export MINIMAX_API_KEY="..."
+export EDGEQUAKE_LLM_PROVIDER="minimax"
+export EDGEQUAKE_LLM_MODEL="MiniMax-M2.7"`,
+      },
     };
     return configs[providerName.toLowerCase()] || { label: 'Configuration', code: '' };
   };
diff --git a/edgequake_webui/src/hooks/use-providers.ts b/edgequake_webui/src/hooks/use-providers.ts
index e3b4274e..cf4ebe14 100644
--- a/edgequake_webui/src/hooks/use-providers.ts
+++ b/edgequake_webui/src/hooks/use-providers.ts
@@ -129,6 +129,7 @@ export function getProviderDisplayName(providerId: string): string {
     xai: "xAI",
     openrouter: "OpenRouter",
     azure: "Azure OpenAI",
+    minimax: "MiniMax",
     mock: "Mock (Dev)",
   };
   return names[providerId.toLowerCase()] || providerId;
@@ -147,6 +148,7 @@ export function getProviderIconClass(providerId: string): string {
     xai: "text-slate-700",
     openrouter: "text-indigo-600",
     azure: "text-sky-600",
+    minimax: "text-teal-600",
     mock: "text-gray-500",
   };
   return icons[providerId.toLowerCase()] || "text-gray-500";

PATCH

echo "Patch applied successfully."
