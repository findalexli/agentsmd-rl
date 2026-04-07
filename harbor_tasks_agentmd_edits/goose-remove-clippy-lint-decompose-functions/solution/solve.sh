#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied
if [ -f clippy.toml ] && grep -q 'too-many-lines-threshold' clippy.toml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'GOLDCLOSE_PATCH_XYZ'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index daa7fd470b96..3d975ebdc6c9 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -56,7 +56,7 @@
 **Rust checks:**
 - `cargo fmt --check` - Code formatting (rustfmt)
 - `cargo test --jobs 2` - All tests
-- `./scripts/clippy-lint.sh` - Linting (clippy)
+- `cargo clippy --all-targets -- -D warnings` - Linting (clippy)
 - `just check-openapi-schema` - OpenAPI schema validation
 
 **Desktop app checks:**
@@ -76,7 +76,7 @@
 
 Do not comment on:
 - **Style/formatting** - CI handles this (rustfmt, prettier)
-- **Clippy warnings** - CI handles this (clippy-lint.sh)
+- **Clippy warnings** - CI handles this (clippy)
 - **Test failures** - CI handles this (full test suite)
 - **Missing dependencies** - CI handles this (npm ci will fail)
 - **Minor naming suggestions** - unless truly confusing
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 0e70cb6b676f..ad6a1d2d1719 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -95,7 +95,10 @@ jobs:
           # play nicely with hermit-managed rust
           hermit uninstall rustup
           export CARGO_INCREMENTAL=0
-          ./scripts/clippy-lint.sh
+          cargo clippy --all-targets -- -D warnings
+
+      - name: Check for banned TLS crates
+        run: ./scripts/check-no-native-tls.sh
 
   openapi-schema-check:
     name: Check OpenAPI Schema is Up-to-Date
diff --git a/.github/workflows/goose-issue-solver.yml b/.github/workflows/goose-issue-solver.yml
index 879a6cf1190e..e6619564e8d1 100644
--- a/.github/workflows/goose-issue-solver.yml
+++ b/.github/workflows/goose-issue-solver.yml
@@ -95,7 +95,7 @@ env:
       - [ ] cargo check
       - [ ] cargo test (affected crates)
       - [ ] cargo fmt
-      - [ ] ./scripts/clippy-lint.sh
+      - [ ] cargo clippy --all-targets -- -D warnings
       - [ ] Fix failures, retry up to 3 times
 
       ## Phase 6: Confirm (MANDATORY)
diff --git a/AGENTS.md b/AGENTS.md
index 75a4c5f0c478..bcc2be8ed9cb 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -28,8 +28,7 @@ just record-mcp-tests        # record MCP
 ### Lint/Format
 ```bash
 cargo fmt
-./scripts/clippy-lint.sh
-cargo clippy --fix
+cargo clippy --all-targets -- -D warnings
 ```
 
 ### UI
@@ -63,7 +62,7 @@ ui/desktop/           # Electron app
 # 3. cargo fmt
 # 4. cargo build
 # 5. cargo test -p <crate>
-# 6. ./scripts/clippy-lint.sh
+# 6. cargo clippy --all-targets -- -D warnings
 # 7. [if server] just generate-openapi
 ```
 
@@ -92,7 +91,7 @@ Logging: Clean up existing logs, don't add more unless for errors or security ev
 Never: Edit ui/desktop/openapi.json manually
 Never: Edit Cargo.toml use cargo add
 Never: Skip cargo fmt
-Never: Merge without ./scripts/clippy-lint.sh
+Never: Merge without running clippy
 Never: Comment self-evident operations (`// Initialize`, `// Return result`), getters/setters, constructors, or standard Rust idioms
 
 ## Entry Points
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index d301e83874bb..2139a6abdd77 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -103,7 +103,7 @@ When making changes to the Rust code, test them on the CLI or run checks, tests,
 cargo check  # verify changes compile
 cargo test  # run tests with changes
 cargo fmt   # format code
-./scripts/clippy-lint.sh # run the linter
+cargo clippy --all-targets -- -D warnings # run the linter
 ```
 
 ### Node
diff --git a/HOWTOAI.md b/HOWTOAI.md
index 32efe2cb71d1..16706abd46fb 100644
--- a/HOWTOAI.md
+++ b/HOWTOAI.md
@@ -142,7 +142,7 @@ If you're new to Rust, configure your AI tool to help you learn:
 This is a Rust project using cargo workspaces.
 - Follow existing error handling patterns using anyhow::Result
 - Use async/await for I/O operations
-- Follow the project's clippy lints (see clippy-baselines/)
+- Follow the project's clippy lints (see clippy.toml)
 - Run cargo fmt before committing
 ```
 
@@ -240,7 +240,7 @@ cargo build -p goose-mcp
 cargo test -p goose-mcp
 
 # Run clippy
-./scripts/clippy-lint.sh
+cargo clippy --all-targets -- -D warnings
 ```
 
 ### Example 2: Fixing a Rust Compiler Error
@@ -314,4 +314,4 @@ cargo build -p goose-cli -p goose
 
 # Run tests
 cargo test -p goose-cli
-```
\ No newline at end of file
+```
diff --git a/Justfile b/Justfile
index 04d84aa79144..f50ef4c4adfd 100644
--- a/Justfile
+++ b/Justfile
@@ -10,7 +10,9 @@ check-everything:
     @echo "  → Formatting Rust code..."
     cargo fmt --all
     @echo "  → Running clippy linting..."
-    ./scripts/clippy-lint.sh
+    cargo clippy --all-targets -- -D warnings
+    @echo "  → Checking for banned TLS crates..."
+    ./scripts/check-no-native-tls.sh
     @echo "  → Checking UI code formatting..."
     cd ui/desktop && npm run lint:check
     @echo "  → Validating OpenAPI schema..."
diff --git a/clippy-baselines/too_many_lines.txt b/clippy-baselines/too_many_lines.txt
deleted file mode 100644
index 8c6867aaef47..000000000000
--- a/clippy-baselines/too_many_lines.txt
+++ /dev/null
@@ -1,26 +0,0 @@
-crates/goose-cli/src/commands/configure.rs::configure_provider_dialog
-crates/goose-cli/src/commands/configure.rs::configure_tool_permissions_dialog
-crates/goose-cli/src/commands/project.rs::handle_project_default
-crates/goose-cli/src/commands/project.rs::handle_projects_interactive
-crates/goose-cli/src/session/builder.rs::build_session
-crates/goose-cli/src/session/export.rs::tool_response_to_markdown
-crates/goose-cli/src/session/mod.rs::process_agent_response
-crates/goose-mcp/src/computercontroller/mod.rs::new
-crates/goose-mcp/src/computercontroller/pdf_tool.rs::pdf_tool
-crates/goose-mcp/src/memory/mod.rs::new
-crates/goose-server/src/openapi.rs::convert_typed_schema
-crates/goose-server/src/openapi.rs::convert_typed_schema
-crates/goose/src/agents/agent.rs::create_recipe
-crates/goose/src/agents/agent.rs::dispatch_tool_call
-crates/goose/src/agents/agent.rs::reply
-crates/goose/src/agents/agent.rs::reply_internal
-crates/goose/src/providers/claude_code.rs::execute_command
-crates/goose/src/providers/codex.rs::execute_command
-crates/goose/src/providers/formats/anthropic.rs::format_messages
-crates/goose/src/providers/formats/anthropic.rs::response_to_streaming_message
-crates/goose/src/providers/formats/databricks.rs::format_messages
-crates/goose/src/providers/formats/google.rs::format_messages
-crates/goose/src/providers/formats/openai.rs::format_messages
-crates/goose/src/providers/formats/openai.rs::response_to_streaming_message
-crates/goose/src/providers/snowflake.rs::post
-crates/goose/src/security/mod.rs::analyze_tool_requests
diff --git a/clippy.toml b/clippy.toml
new file mode 100644
index 000000000000..f5522e6783eb
--- /dev/null
+++ b/clippy.toml
@@ -0,0 +1 @@
+too-many-lines-threshold = 200
diff --git a/crates/goose-cli/src/session/builder.rs b/crates/goose-cli/src/session/builder.rs
index 7599ce37e8b2..edda60e3e109 100644
--- a/crates/goose-cli/src/session/builder.rs
+++ b/crates/goose-cli/src/session/builder.rs
@@ -337,36 +337,26 @@ async fn load_extensions(
     agent_ptr
 }
 
-pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
-    goose::posthog::set_session_context("cli", session_config.resume);
-
-    let config = Config::global();
-    let agent: Agent = Agent::new();
-
-    if session_config.container.is_some() {
-        agent.set_container(session_config.container.clone()).await;
-    }
-
-    let session_manager = agent.config.session_manager.clone();
-
-    let (saved_provider, saved_model_config) = if session_config.resume {
-        if let Some(ref session_id) = session_config.session_id {
-            match session_manager.get_session(session_id, false).await {
-                Ok(session_data) => (session_data.provider_name, session_data.model_config),
-                Err(_) => (None, None),
-            }
-        } else {
-            (None, None)
-        }
-    } else {
-        (None, None)
-    };
+struct ResolvedProviderConfig {
+    provider_name: String,
+    model_name: String,
+    model_config: goose::model::ModelConfig,
+}
 
-    let recipe = session_config.recipe.as_ref();
-    let recipe_settings = recipe.and_then(|r| r.settings.as_ref());
+fn resolve_provider_and_model(
+    session_config: &SessionBuilderConfig,
+    config: &Config,
+    saved_provider: Option<String>,
+    saved_model_config: Option<goose::model::ModelConfig>,
+) -> ResolvedProviderConfig {
+    let recipe_settings = session_config
+        .recipe
+        .as_ref()
+        .and_then(|r| r.settings.as_ref());
 
     let provider_name = session_config
         .provider
+        .clone()
         .or(saved_provider)
         .or_else(|| recipe_settings.and_then(|s| s.goose_provider.clone()))
         .or_else(|| config.get_goose_provider().ok())
@@ -374,6 +364,7 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
 
     let model_name = session_config
         .model
+        .clone()
         .or_else(|| saved_model_config.as_ref().map(|mc| mc.model_name.clone()))
         .or_else(|| recipe_settings.and_then(|s| s.goose_model.clone()))
         .or_else(|| config.get_goose_model().ok())
@@ -399,41 +390,18 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
             .with_temperature(temperature)
     };
 
-    agent
-        .apply_recipe_components(
-            recipe.and_then(|r| r.sub_recipes.clone()),
-            recipe.and_then(|r| r.response.clone()),
-            true,
-        )
-        .await;
-
-    let new_provider = match create(&provider_name, model_config).await {
-        Ok(provider) => provider,
-        Err(e) => {
-            output::render_error(&format!(
-                "Error {}.\n\
-                Please check your system keychain and run 'goose configure' again.\n\
-                If your system is unable to use the keyring, please try setting secret key(s) via environment variables.\n\
-                For more info, see: https://block.github.io/goose/docs/troubleshooting/#keychainkeyring-errors",
-                e
-            ));
-            process::exit(1);
-        }
-    };
-    let provider_for_display = Arc::clone(&new_provider);
-
-    if let Some(lead_worker) = new_provider.as_lead_worker() {
-        let (lead_model, worker_model) = lead_worker.get_model_info();
-        tracing::info!(
-            "🤖 Lead/Worker Mode Enabled: Lead model (first 3 turns): {}, Worker model (turn 4+): {}, Auto-fallback on failures: Enabled",
-            lead_model,
-            worker_model
-        );
-    } else {
-        tracing::info!("🤖 Using model: {}", model_name);
+    ResolvedProviderConfig {
+        provider_name,
+        model_name,
+        model_config,
     }
+}
 
-    let session_id: String = if session_config.no_session {
+async fn resolve_session_id(
+    session_config: &SessionBuilderConfig,
+    session_manager: &goose::session::session_manager::SessionManager,
+) -> String {
+    if session_config.no_session {
         let working_dir = std::env::current_dir().expect("Could not get working directory");
         let session = session_manager
             .create_session(working_dir, "CLI Session".to_string(), SessionType::Hidden)
@@ -441,13 +409,13 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
             .expect("Could not create session");
         session.id
     } else if session_config.resume {
-        if let Some(session_id) = session_config.session_id {
-            match session_manager.get_session(&session_id, false).await {
-                Ok(_) => session_id,
+        if let Some(ref session_id) = session_config.session_id {
+            match session_manager.get_session(session_id, false).await {
+                Ok(_) => session_id.clone(),
                 Err(_) => {
                     output::render_error(&format!(
                         "Cannot resume session {} - no such session exists",
-                        style(&session_id).cyan()
+                        style(session_id).cyan()
                     ));
                     process::exit(1);
                 }
@@ -462,66 +430,73 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
             }
         }
     } else {
-        session_config.session_id.unwrap()
-    };
+        session_config.session_id.clone().unwrap()
+    }
+}
 
-    agent
-        .update_provider(new_provider, &session_id)
+async fn handle_resumed_session_workdir(agent: &Agent, session_id: &str, interactive: bool) {
+    let session = agent
+        .config
+        .session_manager
+        .get_session(session_id, false)
         .await
         .unwrap_or_else(|e| {
-            output::render_error(&format!("Failed to initialize agent: {}", e));
+            output::render_error(&format!("Failed to read session metadata: {}", e));
             process::exit(1);
         });
 
-    if session_config.resume {
-        let session = agent
-            .config
-            .session_manager
-            .get_session(&session_id, false)
-            .await
-            .unwrap_or_else(|e| {
-                output::render_error(&format!("Failed to read session metadata: {}", e));
-                process::exit(1);
-            });
-
-        let current_workdir =
-            std::env::current_dir().expect("Failed to get current working directory");
-        if current_workdir != session.working_dir {
-            if session_config.interactive {
-                let change_workdir = cliclack::confirm(format!("{} The original working directory of this session was set to {}. Your current directory is {}. Do you want to switch back to the original working directory?", style("WARNING:").yellow(), style(session.working_dir.display()).cyan(), style(current_workdir.display()).cyan()))
-                        .initial_value(true)
-                        .interact().expect("Failed to get user input");
-
-                if change_workdir {
-                    if !session.working_dir.exists() {
-                        output::render_error(&format!(
-                            "Cannot switch to original working directory - {} no longer exists",
-                            style(session.working_dir.display()).cyan()
-                        ));
-                    } else if let Err(e) = std::env::set_current_dir(&session.working_dir) {
-                        output::render_error(&format!(
-                            "Failed to switch to original working directory: {}",
-                            e
-                        ));
-                    }
-                }
-            } else {
-                eprintln!(
-                    "{}",
-                    style(format!(
-                        "Warning: Working directory differs from session (current: {}, session: {}). Staying in current directory.",
-                        current_workdir.display(),
-                        session.working_dir.display()
-                    ))
-                    .yellow()
-                );
+    let current_workdir = std::env::current_dir().expect("Failed to get current working directory");
+    if current_workdir == session.working_dir {
+        return;
+    }
+
+    if interactive {
+        let change_workdir = cliclack::confirm(format!(
+            "{} The original working directory of this session was set to {}. \
+             Your current directory is {}. \
+             Do you want to switch back to the original working directory?",
+            style("WARNING:").yellow(),
+            style(session.working_dir.display()).cyan(),
+            style(current_workdir.display()).cyan(),
+        ))
+        .initial_value(true)
+        .interact()
+        .expect("Failed to get user input");
+
+        if change_workdir {
+            if !session.working_dir.exists() {
+                output::render_error(&format!(
+                    "Cannot switch to original working directory - {} no longer exists",
+                    style(session.working_dir.display()).cyan()
+                ));
+            } else if let Err(e) = std::env::set_current_dir(&session.working_dir) {
+                output::render_error(&format!(
+                    "Failed to switch to original working directory: {}",
+                    e
+                ));
             }
         }
+    } else {
+        eprintln!(
+            "{}",
+            style(format!(
+                "Warning: Working directory differs from session (current: {}, session: {}). \
+                 Staying in current directory.",
+                current_workdir.display(),
+                session.working_dir.display()
+            ))
+            .yellow()
+        );
     }
+}
 
-    // Setup extensions for the agent
-    // Extensions need to be added after the session is created because we change directory when resuming a session
-
+async fn resolve_and_load_extensions(
+    agent: Agent,
+    session_config: &SessionBuilderConfig,
+    recipe: Option<&Recipe>,
+    session_id: &str,
+    provider_for_debug: Arc<dyn goose::providers::base::Provider>,
+) -> Arc<Agent> {
     for warning in goose::config::get_warnings() {
         eprintln!("{}", style(format!("Warning: {}", warning)).yellow());
     }
@@ -530,7 +505,7 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
         agent
             .config
             .session_manager
-            .get_session(&session_id, false)
+            .get_session(session_id, false)
             .await
             .ok()
             .and_then(|s| EnabledExtensionsState::from_extension_data(&s.extension_data))
@@ -542,7 +517,7 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
         resolve_extensions_for_new_session(recipe.and_then(|r| r.extensions.as_deref()), None)
     };
 
-    let cli_flag_extensions_to_load = parse_cli_flag_extensions(
+    let cli_flag_extensions = parse_cli_flag_extensions(
         &session_config.extensions,
         &session_config.streamable_http_extensions,
         &session_config.builtins,
@@ -552,18 +527,136 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
         .iter()
         .map(|cfg| (cfg.name(), cfg.clone()))
         .collect();
-    extensions_to_load.extend(cli_flag_extensions_to_load);
+    extensions_to_load.extend(cli_flag_extensions);
 
-    let agent_ptr = load_extensions(
+    load_extensions(
         agent,
         extensions_to_load,
-        Arc::clone(&provider_for_display),
+        provider_for_debug,
         session_config.interactive,
+        session_id,
+    )
+    .await
+}
+
+async fn configure_session_prompts(
+    session: &CliSession,
+    config: &Config,
+    session_config: &SessionBuilderConfig,
+    session_id: &str,
+) {
+    if let Err(e) = session.agent.persist_extension_state(session_id).await {
+        tracing::warn!("Failed to save extension state: {}", e);
+    }
+
+    session
+        .agent
+        .extend_system_prompt(super::prompt::get_cli_prompt())
+        .await;
+
+    if let Some(ref additional_prompt) = session_config.additional_system_prompt {
+        session
+            .agent
+            .extend_system_prompt(additional_prompt.clone())
+            .await;
+    }
+
+    let system_prompt_file: Option<String> = config.get_param("GOOSE_SYSTEM_PROMPT_FILE_PATH").ok();
+    if let Some(ref path) = system_prompt_file {
+        let override_prompt =
+            std::fs::read_to_string(path).expect("Failed to read system prompt file");
+        session.agent.override_system_prompt(override_prompt).await;
+    }
+}
+
+pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
+    goose::posthog::set_session_context("cli", session_config.resume);
+
+    let config = Config::global();
+    let agent: Agent = Agent::new();
+
+    if session_config.container.is_some() {
+        agent.set_container(session_config.container.clone()).await;
+    }
+
+    let session_manager = agent.config.session_manager.clone();
+
+    let (saved_provider, saved_model_config) = if session_config.resume {
+        if let Some(ref session_id) = session_config.session_id {
+            match session_manager.get_session(session_id, false).await {
+                Ok(session_data) => (session_data.provider_name, session_data.model_config),
+                Err(_) => (None, None),
+            }
+        } else {
+            (None, None)
+        }
+    } else {
+        (None, None)
+    };
+
+    let resolved =
+        resolve_provider_and_model(&session_config, config, saved_provider, saved_model_config);
+
+    let recipe = session_config.recipe.as_ref();
+
+    agent
+        .apply_recipe_components(
+            recipe.and_then(|r| r.sub_recipes.clone()),
+            recipe.and_then(|r| r.response.clone()),
+            true,
+        )
+        .await;
+
+    let new_provider = match create(&resolved.provider_name, resolved.model_config).await {
+        Ok(provider) => provider,
+        Err(e) => {
+            output::render_error(&format!(
+                "Error {}.\n\
+                Please check your system keychain and run 'goose configure' again.\n\
+                If your system is unable to use the keyring, please try setting secret key(s) via environment variables.\n\
+                For more info, see: https://block.github.io/goose/docs/troubleshooting/#keychainkeyring-errors",
+                e
+            ));
+            process::exit(1);
+        }
+    };
+    let provider_for_display = Arc::clone(&new_provider);
+
+    if let Some(lead_worker) = new_provider.as_lead_worker() {
+        let (lead_model, worker_model) = lead_worker.get_model_info();
+        tracing::info!(
+            "🤖 Lead/Worker Mode Enabled: Lead model (first 3 turns): {}, Worker model (turn 4+): {}, Auto-fallback on failures: Enabled",
+            lead_model,
+            worker_model
+        );
+    } else {
+        tracing::info!("🤖 Using model: {}", resolved.model_name);
+    }
+
+    let session_id = resolve_session_id(&session_config, &session_manager).await;
+
+    agent
+        .update_provider(new_provider, &session_id)
+        .await
+        .unwrap_or_else(|e| {
+            output::render_error(&format!("Failed to initialize agent: {}", e));
+            process::exit(1);
+        });
+
+    if session_config.resume {
+        handle_resumed_session_workdir(&agent, &session_id, session_config.interactive).await;
+    }
+
+    // Extensions are loaded after session creation because we may change directory when resuming
+    let agent_ptr = resolve_and_load_extensions(
+        agent,
+        &session_config,
+        recipe,
         &session_id,
+        Arc::clone(&provider_for_display),
     )
     .await;
 
-    // Determine editor mode
     let edit_mode = config
         .get_param::<String>("EDIT_MODE")
         .ok()
@@ -590,38 +683,13 @@ pub async fn build_session(session_config: SessionBuilderConfig) -> CliSession {
     )
     .await;
 
-    if let Err(e) = session
-        .agent
-        .persist_extension_state(&session_id.clone())
-        .await
-    {
-        tracing::warn!("Failed to save extension state: {}", e);
-    }
-
-    // Add CLI-specific system prompt extension
-    session
-        .agent
-        .extend_system_prompt(super::prompt::get_cli_prompt())
-        .await;
-
-    if let Some(additional_prompt) = session_config.additional_system_prompt {
-        session.agent.extend_system_prompt(additional_prompt).await;
-    }
-
-    // Only override system prompt if a system override exists
-    let system_prompt_file: Option<String> = config.get_param("GOOSE_SYSTEM_PROMPT_FILE_PATH").ok();
-    if let Some(ref path) = system_prompt_file {
-        let override_prompt =
-            std::fs::read_to_string(path).expect("Failed to read system prompt file");
-        session.agent.override_system_prompt(override_prompt).await;
-    }
+    configure_session_prompts(&session, config, &session_config, &session_id).await;
 
-    // Display session information unless in quiet mode
     if !session_config.quiet {
         output::display_session_info(
             session_config.resume,
-            &provider_name,
-            &model_name,
+            &resolved.provider_name,
+            &resolved.model_name,
             &Some(session_id),
             Some(&provider_for_display),
         );
diff --git a/scripts/clippy-baseline.sh b/scripts/clippy-baseline.sh
deleted file mode 100755
index 7d30f3c98ade..000000000000
--- a/scripts/clippy-baseline.sh
+++ /dev/null
@@ -1,161 +0,0 @@
-#!/bin/bash
-
-# Baseline clippy rules - only fail on NEW violations
-#
-# Format: "rule_name|violation_parser"
-#
-# Violation parsers (run clippy on your rule to see which fits):
-#   function_name - When spans show: "fn my_function(..."
-#   type_name     - When spans show: "struct MyStruct" or "enum MyEnum"
-#   file_only     - When spans show file-level issues
-#
-# Note: If your rule doesn't fit these parsers, you may need to add a new parser
-# to the parse_violation() function below
-#
-# To add new rules:
-# 1. Add rule below: "clippy::your_rule|violation_parser"
-# 2. Generate baseline: ./scripts/clippy-baseline.sh generate clippy::your_rule
-
-BASELINE_RULES=(
-    "clippy::too_many_lines|function_name"
-)
-
-parse_violation() {
-    local rule_code="$1"
-    local violation_parser="$2"
-
-    case "$violation_parser" in
-        "function_name")
-            jq -r 'select(.message.code.code == "'"$rule_code"'") |
-                   .message.spans[0] as $span |
-                   ($span.text | map(.text) | map(select(test("\\bfn\\b"))) | first // "") as $line |
-                   if $line == "" then empty else "\($span.file_name)::\($line | capture("fn\\s+(?<name>[a-z_][a-z0-9_]*)") | .name)" end'
-            ;;
-        "type_name")
-            jq -r 'select(.message.code.code == "'"$rule_code"'") |
-                   "\(.message.spans[0].file_name)::\(.message.spans[0].text[0].text | split(" ")[1] | split(" ")[0])"'
-            ;;
-        "file_only")
-            jq -r 'select(.message.code.code == "'"$rule_code"'") |
-                   "\(.message.spans[0].file_name)"'
-            ;;
-        *)
-            echo "Unknown violation parser: $violation_parser" >&2
-            exit 1
-            ;;
-    esac
-}
-
-get_baseline_file() {
-    local rule_name="$1"
-    local safe_name=$(echo "$rule_name" | sed 's/clippy:://' | sed 's/:/-/g')
-    echo "clippy-baselines/${safe_name}.txt"
-}
-
-
-generate_baseline() {
-    local rule_name="$1"
-
-    [[ -z "$rule_name" ]] && { echo "Missing rule name"; return 1; }
-
-    local violation_parser=""
-    for rule in "${BASELINE_RULES[@]}"; do
-        [[ "${rule%|*}" == "$rule_name" ]] && { violation_parser="${rule#*|}"; break; }
-    done
-
-    [[ -z "$violation_parser" ]] && { echo "Unknown rule: $rule_name"; return 1; }
-
-    local baseline_file=$(get_baseline_file "$rule_name")
-
-    cargo clippy --jobs 2 --message-format=json -- -W "$rule_name" | \
-        parse_violation "$rule_name" "$violation_parser" | \
-        sort > "$baseline_file"
-
-    echo "✅ Generated baseline for $rule_name ($(wc -l < "$baseline_file") violations)"
-}
-
-
-# Check a single rule from pre-generated JSON (optimized version)
-check_rule_from_json() {
-    local temp_json="$1"
-    local rule_name="$2"
-    local violation_parser="$3"
-    local baseline_file="$4"
-
-    echo "  → Checking $rule_name"
-
-    if [[ ! -f "$baseline_file" ]]; then
-        echo "  ❌ $rule_name: baseline file not found"
-        return 1
-    fi
-
-    local temp_parsed=$(mktemp)
-    cat "$temp_json" | parse_violation "$rule_name" "$violation_parser" | sort > "$temp_parsed"
-
-    local new_violations_file=$(mktemp)
-    diff <(sort "$baseline_file") <(sort "$temp_parsed") | grep "^>" | cut -c3- > "$new_violations_file"
-
-    if [[ -s "$new_violations_file" ]]; then
-        echo "  ❌ $rule_name: NEW violations found:"
-
-        while IFS= read -r violation; do
-            # Extract all violations for this rule and find the matching one
-            cat "$temp_json" | jq -c 'select(.message.code.code == "'"$rule_name"'")' 2>/dev/null | while read -r json_line; do
-                parsed_id=$(echo "$json_line" | parse_violation "$rule_name" "$violation_parser")
-                if [[ "$parsed_id" == "$violation" ]]; then
-                    echo "$json_line" | jq -r '.message.rendered' | sed 's/^/    /'
-                fi
-            done
-        done < "$new_violations_file"
-
-        rm "$temp_parsed" "$new_violations_file"
-        return 1
-    fi
-
-    rm "$new_violations_file"
-
-    echo "  ✅ $rule_name: ok"
-    rm "$temp_parsed"
-    return 0
-}
-
-check_all_baseline_rules() {
-    echo "🔍 Checking baseline clippy rules..."
-
-    local clippy_flags=""
-    for rule in "${BASELINE_RULES[@]}"; do
-        local rule_name="${rule%|*}"
-        clippy_flags="$clippy_flags -W $rule_name"
-    done
-
-    local temp_json=$(mktemp)
-    cargo clippy --jobs 2 --message-format=json -- $clippy_flags | tee "$temp_json"
-
-    local failed_rules=()
-
-    # Check each rule against its baseline
-    for rule in "${BASELINE_RULES[@]}"; do
-        local rule_name="${rule%|*}"
-        local violation_parser="${rule#*|}"
-        local baseline_file=$(get_baseline_file "$rule_name")
-
-        if ! check_rule_from_json "$temp_json" "$rule_name" "$violation_parser" "$baseline_file"; then
-            failed_rules+=("$rule_name")
-        fi
-    done
-
-    rm "$temp_json"
-
-    if [[ ${#failed_rules[@]} -gt 0 ]]; then
-        echo ""
-        echo "❌ Failed baseline checks for: ${failed_rules[*]}"
-        exit 1
-    else
-        echo ""
-        echo "✅ All baseline clippy checks passed!"
-    fi
-}
-
-if [[ "$1" == "generate" ]]; then
-    generate_baseline "$2"
-fi
diff --git a/scripts/clippy-lint.sh b/scripts/clippy-lint.sh
deleted file mode 100755
index 6414c94294c9..000000000000
--- a/scripts/clippy-lint.sh
+++ /dev/null
@@ -1,42 +0,0 @@
-#!/bin/bash
-
-# Combined lint script
-# Runs standard clippy (strict) + baseline clippy rules
-
-set -e
-
-SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
-
-# Source the baseline functions
-source "$SCRIPT_DIR/clippy-baseline.sh"
-
-echo "🔍 Running all clippy checks..."
-
-FIX_MODE=0
-[[ "$1" == "--fix" ]] && FIX_MODE=1
-
-run_clippy() {
-  if [[ "$FIX_MODE" -eq 1 ]]; then
-    cargo fmt
-    cargo clippy --all-targets --jobs 2 \
-      --fix --allow-dirty --allow-staged \
-      -- -D warnings
-  else
-    cargo clippy --all-targets --jobs 2 -- -D warnings
-  fi
-}
-
-if [[ "$FIX_MODE" -eq 1 ]]; then
-  echo "🛠  Applying fixes..."
-else
-  echo "🔍 Running clippy..."
-fi
-
-run_clippy
-echo ""
-check_all_baseline_rules
-echo ""
-echo "🔒 Checking for banned TLS crates..."
-"$SCRIPT_DIR/check-no-native-tls.sh"
-echo ""
-echo "✅ Done"

GOLDCLOSE_PATCH_XYZ

echo "Patch applied successfully."
