#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied (ParsedRunCommand is the new type introduced by the fix)
if grep -q 'pub(crate) enum ParsedRunCommand' crates/uv/src/commands/project/run.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv/src/commands/mod.rs b/crates/uv/src/commands/mod.rs
index 69189a18369d2..163c0178d2be3 100644
--- a/crates/uv/src/commands/mod.rs
+++ b/crates/uv/src/commands/mod.rs
@@ -36,7 +36,7 @@ pub(crate) use project::format::format;
 pub(crate) use project::init::{InitKind, InitProjectKind, init};
 pub(crate) use project::lock::lock;
 pub(crate) use project::remove::remove;
-pub(crate) use project::run::{RunCommand, run};
+pub(crate) use project::run::{ParsedRunCommand, RunCommand, run};
 pub(crate) use project::sync::sync;
 pub(crate) use project::tree::tree;
 pub(crate) use project::version::{project_version, self_version};
diff --git a/crates/uv/src/commands/project/run.rs b/crates/uv/src/commands/project/run.rs
index 654fc2f77bf7e..84e9ae41e9585 100644
--- a/crates/uv/src/commands/project/run.rs
+++ b/crates/uv/src/commands/project/run.rs
@@ -16,7 +16,7 @@ use tracing::{debug, trace, warn};
 use url::Url;

 use uv_cache::Cache;
-use uv_cli::ExternalCommand;
+use uv_cli::{ExternalCommand, GlobalArgs};
 use uv_client::BaseClientBuilder;
 use uv_configuration::{
     Concurrency, Constraints, DependencyGroups, DryRun, EditableMode, EnvFile, ExtrasSpecification,
@@ -37,8 +37,8 @@ use uv_python::{
 use uv_redacted::DisplaySafeUrl;
 use uv_requirements::{RequirementsSource, RequirementsSpecification};
 use uv_resolver::{Installable, Lock, Preference};
-use uv_scripts::Pep723Item;
-use uv_settings::PythonInstallMirrors;
+use uv_scripts::{Pep723Error, Pep723Item, Pep723Metadata, Pep723Script};
+use uv_settings::{EnvironmentOptions, FilesystemOptions, PythonInstallMirrors};
 use uv_shell::runnable::WindowsRunnable;
 use uv_static::EnvVars;
 use uv_warnings::warn_user;
@@ -73,7 +73,9 @@ use crate::commands::project::{
 use crate::commands::reporters::PythonDownloadReporter;
 use crate::commands::{ExitStatus, diagnostics, project};
 use crate::printer::Printer;
-use crate::settings::{FrozenSource, LockCheck, ResolverInstallerSettings, ResolverSettings};
+use crate::settings::{
+    FrozenSource, GlobalSettings, LockCheck, ResolverInstallerSettings, ResolverSettings,
+};

 /// Run a command.
 #[expect(clippy::fn_params_excessive_bools)]
@@ -81,7 +83,6 @@ pub(crate) async fn run(
     project_dir: &Path,
     script: Option<Pep723Item>,
     command: Option<RunCommand>,
-    downloaded_script: Option<&tempfile::NamedTempFile>,
     requirements: Vec<RequirementsSource>,
     show_resolution: bool,
     lock_check: LockCheck,
@@ -1271,7 +1272,7 @@ hint: If you are running a script with `{}` in the shebang, you may need to incl
     };

     debug!("Running `{command}`");
-    let mut process = command.as_command(interpreter, downloaded_script);
+    let mut process = command.as_command(interpreter);

     // Construct the `PATH` environment variable.
     let new_path = std::env::join_paths(
@@ -1423,15 +1424,272 @@ pub(crate) enum RunCommand {
     PythonStdin(Vec<u8>, Vec<OsString>),
     /// Execute a `pythonw` script provided via `stdin`.
     PythonGuiStdin(Vec<u8>, Vec<OsString>),
-    /// Execute a Python script provided via a remote URL.
-    PythonRemote(DisplaySafeUrl, Vec<OsString>),
+    /// Execute a Python script downloaded from a remote URL.
+    PythonRemote(tempfile::NamedTempFile, Vec<OsString>),
     /// Execute an external command.
     External(OsString, Vec<OsString>),
     /// Execute an empty command (in practice, `python` with no arguments).
     Empty,
 }

+/// A parsed `uv run` target before any remote script has been downloaded.
+#[derive(Debug)]
+pub(crate) enum ParsedRunCommand {
+    /// A target that is already fully resolved and ready to execute.
+    Ready(RunCommand),
+    /// A remote target that must be downloaded before it can be inspected or executed.
+    PendingRemote(PendingRemoteRunCommand),
+}
+
+/// The information needed to fetch and execute a remote `uv run` target.
+#[derive(Debug)]
+pub(crate) struct PendingRemoteRunCommand {
+    /// The remote URL to download.
+    url: DisplaySafeUrl,
+    /// The arguments to forward after the downloaded script path.
+    args: Vec<OsString>,
+}
+
+impl PendingRemoteRunCommand {
+    /// Download the remote script and return the URL, temporary file, and forwarded arguments.
+    async fn download(
+        self,
+        client_builder: &BaseClientBuilder<'_>,
+    ) -> anyhow::Result<(DisplaySafeUrl, tempfile::NamedTempFile, Vec<OsString>)> {
+        let url = self.url.clone();
+        let downloaded_script =
+            ParsedRunCommand::download_remote_script(&self.url, client_builder).await?;
+        Ok((url, downloaded_script, self.args))
+    }
+}
+
+impl ParsedRunCommand {
+    /// Return the local script directory used for target workspace discovery, if any.
+    pub(crate) fn script_dir(&self) -> Option<&Path> {
+        match self {
+            Self::Ready(run_command) => run_command.script_dir(),
+            Self::PendingRemote(..) => None,
+        }
+    }
+
+    /// Resolve the parsed target into a [`RunCommand`] and any associated PEP 723 metadata.
+    pub(crate) async fn resolve(
+        self,
+        global_args: &GlobalArgs,
+        filesystem: Option<&FilesystemOptions>,
+        environment: &EnvironmentOptions,
+    ) -> anyhow::Result<(Option<Pep723Item>, RunCommand)> {
+        match self {
+            Self::Ready(run_command) => {
+                let script = run_command.read_pep723_item().await?;
+                Ok((script, run_command))
+            }
+            Self::PendingRemote(remote_command) => {
+                let settings = GlobalSettings::resolve(global_args, filesystem, environment);
+                let client_builder = BaseClientBuilder::new(
+                    settings.network_settings.connectivity,
+                    settings.network_settings.system_certs,
+                    settings.network_settings.allow_insecure_host,
+                    settings.preview,
+                    settings.network_settings.read_timeout,
+                    settings.network_settings.connect_timeout,
+                    settings.network_settings.retries,
+                )
+                .http_proxy(settings.network_settings.http_proxy)
+                .https_proxy(settings.network_settings.https_proxy)
+                .no_proxy(settings.network_settings.no_proxy);
+
+                let (url, downloaded_script, args) =
+                    remote_command.download(&client_builder).await?;
+                let script = match Pep723Metadata::read(&downloaded_script).await {
+                    Ok(Some(metadata)) => Some(Pep723Item::Remote(metadata, url)),
+                    Ok(None) => None,
+                    Err(Pep723Error::Io(err)) if err.kind() == std::io::ErrorKind::NotFound => None,
+                    Err(err) => return Err(err.into()),
+                };
+
+                Ok((script, RunCommand::PythonRemote(downloaded_script, args)))
+            }
+        }
+    }
+
+    /// Determine the [`ParsedRunCommand`] for a given set of arguments.
+    pub(crate) fn from_args(
+        command: &ExternalCommand,
+        module: bool,
+        script: bool,
+        gui_script: bool,
+    ) -> anyhow::Result<Self> {
+        let (target, args) = command.split();
+        let Some(target) = target else {
+            return Ok(Self::Ready(RunCommand::Empty));
+        };
+
+        if target.eq_ignore_ascii_case("-") {
+            let mut buf = Vec::with_capacity(1024);
+            std::io::stdin().read_to_end(&mut buf)?;
+
+            return if module {
+                Err(anyhow!("Cannot run a Python module from stdin"))
+            } else if gui_script {
+                Ok(Self::Ready(RunCommand::PythonGuiStdin(buf, args.to_vec())))
+            } else {
+                Ok(Self::Ready(RunCommand::PythonStdin(buf, args.to_vec())))
+            };
+        }
+
+        let target_path = PathBuf::from(target);
+
+        // Determine whether the user provided a remote script.
+        if target_path.starts_with("http://") || target_path.starts_with("https://") {
+            // Only continue if we are absolutely certain no local file exists.
+            //
+            // We don't do this check on Windows since the file path would
+            // be invalid anyway, and thus couldn't refer to a local file.
+            if !cfg!(unix) || matches!(target_path.try_exists(), Ok(false)) {
+                let url = DisplaySafeUrl::parse(&target.to_string_lossy())?;
+                return Ok(Self::PendingRemote(PendingRemoteRunCommand {
+                    url,
+                    args: args.to_vec(),
+                }));
+            }
+        }
+
+        if module {
+            return Ok(Self::Ready(RunCommand::PythonModule(
+                target.clone(),
+                args.to_vec(),
+            )));
+        } else if gui_script {
+            return Ok(Self::Ready(RunCommand::PythonGuiScript(
+                target.clone().into(),
+                args.to_vec(),
+            )));
+        } else if script {
+            return Ok(Self::Ready(RunCommand::PythonScript(
+                target.clone().into(),
+                args.to_vec(),
+            )));
+        }
+
+        let metadata = target_path.metadata();
+        let is_file = metadata.as_ref().is_ok_and(std::fs::Metadata::is_file);
+        let is_dir = metadata.as_ref().is_ok_and(std::fs::Metadata::is_dir);
+
+        if target.eq_ignore_ascii_case("python") {
+            Ok(Self::Ready(RunCommand::Python(args.to_vec())))
+        } else if target_path
+            .extension()
+            .is_some_and(|ext| ext.eq_ignore_ascii_case("py") || ext.eq_ignore_ascii_case("pyc"))
+            && is_file
+        {
+            Ok(Self::Ready(RunCommand::PythonScript(
+                target_path,
+                args.to_vec(),
+            )))
+        } else if target_path
+            .extension()
+            .is_some_and(|ext| ext.eq_ignore_ascii_case("pyw"))
+            && is_file
+        {
+            Ok(Self::Ready(RunCommand::PythonGuiScript(
+                target_path,
+                args.to_vec(),
+            )))
+        } else if is_dir && target_path.join("__main__.py").is_file() {
+            Ok(Self::Ready(RunCommand::PythonPackage(
+                target.clone(),
+                target_path,
+                args.to_vec(),
+            )))
+        } else if is_file && is_python_zipapp(&target_path) {
+            Ok(Self::Ready(RunCommand::PythonZipapp(
+                target_path,
+                args.to_vec(),
+            )))
+        } else {
+            Ok(Self::Ready(RunCommand::External(
+                target.clone(),
+                args.iter().map(std::clone::Clone::clone).collect(),
+            )))
+        }
+    }
+
+    /// Download a remote script target into a temporary file ready for execution.
+    async fn download_remote_script(
+        mut url: &DisplaySafeUrl,
+        client_builder: &BaseClientBuilder<'_>,
+    ) -> anyhow::Result<tempfile::NamedTempFile> {
+        let client = client_builder.build();
+        let mut response = client
+            .for_host(url)
+            .get(Url::from(url.clone()))
+            .send()
+            .await?;
+
+        let gist_url;
+        // If it's a Gist URL, use the GitHub API to get the raw URL.
+        if response.url().host_str() == Some("gist.github.com") {
+            gist_url =
+                resolve_gist_url(DisplaySafeUrl::ref_cast(response.url()), client_builder).await?;
+            url = &gist_url;
+
+            response = client
+                .for_host(url)
+                .get(Url::from(url.clone()))
+                .send()
+                .await?;
+        }
+
+        let file_stem = url
+            .path_segments()
+            .and_then(Iterator::last)
+            .and_then(|segment| segment.strip_suffix(".py"))
+            .unwrap_or("script");
+        let file = tempfile::Builder::new()
+            .prefix(file_stem)
+            .suffix(".py")
+            .tempfile()?;
+
+        // Stream the response to the file.
+        let mut writer = file.as_file();
+        let mut reader = response.bytes_stream();
+        while let Some(chunk) = reader.next().await {
+            use std::io::Write;
+            writer.write_all(&chunk?)?;
+        }
+
+        Ok(file)
+    }
+}
+
 impl RunCommand {
+    /// Read any inline PEP 723 metadata associated with this command target.
+    async fn read_pep723_item(&self) -> Result<Option<Pep723Item>, Pep723Error> {
+        match self {
+            Self::PythonScript(script, _) | Self::PythonGuiScript(script, _) => {
+                match Pep723Script::read(script).await {
+                    Ok(Some(script)) => Ok(Some(Pep723Item::Script(script))),
+                    Ok(None) => Ok(None),
+                    Err(Pep723Error::Io(err)) if err.kind() == std::io::ErrorKind::NotFound => {
+                        Ok(None)
+                    }
+                    Err(err) => Err(err),
+                }
+            }
+            Self::PythonStdin(contents, _) | Self::PythonGuiStdin(contents, _) => {
+                Pep723Metadata::parse(contents).map(|metadata| metadata.map(Pep723Item::Stdin))
+            }
+            Self::Python(_)
+            | Self::PythonPackage(..)
+            | Self::PythonZipapp(..)
+            | Self::PythonModule(..)
+            | Self::PythonRemote(..)
+            | Self::External(..)
+            | Self::Empty => Ok(None),
+        }
+    }
+
     /// Return the name of the target executable, for display purposes.
     fn display_executable(&self) -> Cow<'_, str> {
         match self {
@@ -1464,11 +1722,7 @@ impl RunCommand {
     }

     /// Convert a [`RunCommand`] into a [`Command`].
-    fn as_command(
-        &self,
-        interpreter: &Interpreter,
-        downloaded_script: Option<&tempfile::NamedTempFile>,
-    ) -> Command {
+    fn as_command(&self, interpreter: &Interpreter) -> Command {
         match self {
             Self::Python(args) => {
                 let mut process = Command::new(interpreter.sys_executable());
@@ -1498,9 +1752,9 @@ impl RunCommand {
                 process.args(args);
                 process
             }
-            Self::PythonRemote(.., args) => {
+            Self::PythonRemote(downloaded_script, args) => {
                 let mut process = Command::new(interpreter.sys_executable());
-                process.arg(downloaded_script.unwrap().path());
+                process.arg(downloaded_script.path());
                 process.args(args);
                 process
             }
@@ -1731,135 +1985,6 @@ async fn resolve_gist_url(
     Ok(url)
 }

-impl RunCommand {
-    /// Determine the [`RunCommand`] for a given set of arguments.
-    pub(crate) fn from_args(
-        command: &ExternalCommand,
-        module: bool,
-        script: bool,
-        gui_script: bool,
-    ) -> anyhow::Result<Self> {
-        let (target, args) = command.split();
-        let Some(target) = target else {
-            return Ok(Self::Empty);
-        };
-
-        if target.eq_ignore_ascii_case("-") {
-            let mut buf = Vec::with_capacity(1024);
-            std::io::stdin().read_to_end(&mut buf)?;
-
-            return if module {
-                Err(anyhow!("Cannot run a Python module from stdin"))
-            } else if gui_script {
-                Ok(Self::PythonGuiStdin(buf, args.to_vec()))
-            } else {
-                Ok(Self::PythonStdin(buf, args.to_vec()))
-            };
-        }
-
-        let target_path = PathBuf::from(target);
-
-        // Determine whether the user provided a remote script.
-        if target_path.starts_with("http://") || target_path.starts_with("https://") {
-            // Only continue if we are absolutely certain no local file exists.
-            //
-            // We don't do this check on Windows since the file path would
-            // be invalid anyway, and thus couldn't refer to a local file.
-            if !cfg!(unix) || matches!(target_path.try_exists(), Ok(false)) {
-                let url = DisplaySafeUrl::parse(&target.to_string_lossy())?;
-                return Ok(Self::PythonRemote(url, args.to_vec()));
-            }
-        }
-
-        if module {
-            return Ok(Self::PythonModule(target.clone(), args.to_vec()));
-        } else if gui_script {
-            return Ok(Self::PythonGuiScript(target.clone().into(), args.to_vec()));
-        } else if script {
-            return Ok(Self::PythonScript(target.clone().into(), args.to_vec()));
-        }
-
-        let metadata = target_path.metadata();
-        let is_file = metadata.as_ref().is_ok_and(std::fs::Metadata::is_file);
-        let is_dir = metadata.as_ref().is_ok_and(std::fs::Metadata::is_dir);
-
-        if target.eq_ignore_ascii_case("python") {
-            Ok(Self::Python(args.to_vec()))
-        } else if target_path
-            .extension()
-            .is_some_and(|ext| ext.eq_ignore_ascii_case("py") || ext.eq_ignore_ascii_case("pyc"))
-            && is_file
-        {
-            Ok(Self::PythonScript(target_path, args.to_vec()))
-        } else if target_path
-            .extension()
-            .is_some_and(|ext| ext.eq_ignore_ascii_case("pyw"))
-            && is_file
-        {
-            Ok(Self::PythonGuiScript(target_path, args.to_vec()))
-        } else if is_dir && target_path.join("__main__.py").is_file() {
-            Ok(Self::PythonPackage(
-                target.clone(),
-                target_path,
-                args.to_vec(),
-            ))
-        } else if is_file && is_python_zipapp(&target_path) {
-            Ok(Self::PythonZipapp(target_path, args.to_vec()))
-        } else {
-            Ok(Self::External(
-                target.clone(),
-                args.iter().map(std::clone::Clone::clone).collect(),
-            ))
-        }
-    }
-
-    pub(crate) async fn download_remote_script(
-        mut url: &DisplaySafeUrl,
-        client_builder: &BaseClientBuilder<'_>,
-    ) -> anyhow::Result<tempfile::NamedTempFile> {
-        let client = client_builder.build();
-        let mut response = client
-            .for_host(url)
-            .get(Url::from(url.clone()))
-            .send()
-            .await?;
-
-        let gist_url;
-        // If it's a Gist URL, use the GitHub API to get the raw URL.
-        if response.url().host_str() == Some("gist.github.com") {
-            gist_url =
-                resolve_gist_url(DisplaySafeUrl::ref_cast(response.url()), client_builder).await?;
-            url = &gist_url;
-
-            response = client
-                .for_host(url)
-                .get(Url::from(url.clone()))
-                .send()
-                .await?;
-        }
-
-        let file_stem = url
-            .path_segments()
-            .and_then(Iterator::last)
-            .and_then(|segment| segment.strip_suffix(".py"))
-            .unwrap_or("script");
-        let file = tempfile::Builder::new()
-            .prefix(file_stem)
-            .suffix(".py")
-            .tempfile()?;
-
-        // Stream the response to the file.
-        let mut writer = file.as_file();
-        let mut reader = response.bytes_stream();
-        while let Some(chunk) = reader.next().await {
-            use std::io::Write;
-            writer.write_all(&chunk?)?;
-        }
-
-        Ok(file)
-    }
-}
-
 /// Returns `true` if the target is a ZIP archive containing a `__main__.py` file.
 fn is_python_zipapp(target: &Path) -> bool {
     if let Ok(file) = fs_err::File::open(target) {
diff --git a/crates/uv/src/lib.rs b/crates/uv/src/lib.rs
index 9f066aef3dbfd..b0f7870d89611 100644
--- a/crates/uv/src/lib.rs
+++ b/crates/uv/src/lib.rs
@@ -45,13 +45,13 @@ use uv_pypi_types::{ParsedDirectoryUrl, ParsedUrl};
 use uv_python::PythonRequest;
 use uv_requirements::{GroupsSpecification, RequirementsSource};
 use uv_requirements_txt::RequirementsTxtRequirement;
-use uv_scripts::{Pep723Error, Pep723Item, Pep723Metadata, Pep723Script};
+use uv_scripts::{Pep723Error, Pep723Item, Pep723Script};
 use uv_settings::{Combine, EnvironmentOptions, FilesystemOptions, Options};
 use uv_static::EnvVars;
 use uv_warnings::{warn_user, warn_user_once};
 use uv_workspace::{DiscoveryOptions, Workspace, WorkspaceCache};

-use crate::commands::{ExitStatus, RunCommand, ScriptPath, ToolRunCommand};
+use crate::commands::{ExitStatus, ParsedRunCommand, RunCommand, ScriptPath, ToolRunCommand};
 use crate::printer::Printer;
 use crate::settings::{
     CacheSettings, GlobalSettings, PipCheckSettings, PipCompileSettings, PipFreezeSettings,
@@ -88,7 +88,7 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
     }

     // Parse the external command, if necessary.
-    let run_command = if let Commands::Project(command) = &*cli.command
+    let parsed_run_command = if let Commands::Project(command) = &*cli.command
         && let ProjectCommand::Run(uv_cli::RunArgs {
             command: Some(ref command),
             module,
@@ -97,7 +97,9 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
             ..
         }) = **command
     {
-        Some(RunCommand::from_args(command, module, script, gui_script)?)
+        Some(ParsedRunCommand::from_args(
+            command, module, script, gui_script,
+        )?)
     } else {
         None
     };
@@ -127,7 +129,7 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
         } else {
             Cow::Owned(path)
         }
-    } else if let Some(run_command) = &run_command
+    } else if let Some(run_command) = &parsed_run_command
         && early_preview.is_enabled(PreviewFeature::TargetWorkspaceDiscovery)
         && let Some(dir) = run_command.script_dir()
     {
@@ -254,56 +256,24 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
         project.combine(user).combine(system)
     };

-    let mut downloaded_script = None;
     // If the target is a remote script, download it.
     // If the target is a PEP 723 script, parse it.
-    let script = if let Commands::Project(command) = &*cli.command {
+    let (run_script, run_command) = if let Some(parsed_run_command) = parsed_run_command {
+        let (script, run_command) = parsed_run_command
+            .resolve(
+                &cli.top_level.global_args,
+                filesystem.as_ref(),
+                &environment,
+            )
+            .await?;
+        (script, Some(run_command))
+    } else {
+        (None, None)
+    };
+    let script = if let Some(run_script) = run_script {
+        Some(run_script)
+    } else if let Commands::Project(command) = &*cli.command {
         match &**command {
-            ProjectCommand::Run(uv_cli::RunArgs { .. }) => match run_command.as_ref() {
-                Some(
-                    RunCommand::PythonScript(script, _) | RunCommand::PythonGuiScript(script, _),
-                ) => match Pep723Script::read(&script).await {
-                    Ok(Some(script)) => Some(Pep723Item::Script(script)),
-                    Ok(None) => None,
-                    Err(Pep723Error::Io(err)) if err.kind() == std::io::ErrorKind::NotFound => None,
-                    Err(err) => return Err(err.into()),
-                },
-                Some(RunCommand::PythonRemote(url, _)) => {
-                    let settings = GlobalSettings::resolve(
-                        &cli.top_level.global_args,
-                        filesystem.as_ref(),
-                        &environment,
-                    );
-                    let client_builder = BaseClientBuilder::new(
-                        settings.network_settings.connectivity,
-                        settings.network_settings.system_certs,
-                        settings.network_settings.allow_insecure_host,
-                        settings.preview,
-                        settings.network_settings.read_timeout,
-                        settings.network_settings.connect_timeout,
-                        settings.network_settings.retries,
-                    )
-                    .http_proxy(settings.network_settings.http_proxy)
-                    .https_proxy(settings.network_settings.https_proxy)
-                    .no_proxy(settings.network_settings.no_proxy);
-
-                    downloaded_script =
-                        Some(RunCommand::download_remote_script(url, &client_builder).await?);
-
-                    match Pep723Metadata::read(downloaded_script.as_ref().unwrap()).await {
-                        Ok(Some(metadata)) => Some(Pep723Item::Remote(metadata, url.clone())),
-                        Ok(None) => None,
-                        Err(Pep723Error::Io(err)) if err.kind() == std::io::ErrorKind::NotFound => {
-                            None
-                        }
-                        Err(err) => return Err(err.into()),
-                    }
-                }
-                Some(
-                    RunCommand::PythonStdin(contents, _) | RunCommand::PythonGuiStdin(contents, _),
-                ) => Pep723Metadata::parse(contents)?.map(Pep723Item::Stdin),
-                _ => None,
-            },
             // For `uv add --script` and `uv lock --script`, we'll create a PEP 723 tag if it
             // doesn't already exist.
             ProjectCommand::Add(uv_cli::AddArgs {
@@ -313,7 +283,7 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
             | ProjectCommand::Lock(uv_cli::LockArgs {
                 script: Some(script),
                 ..
-            }) => match Pep723Script::read(&script).await {
+            }) => match Pep723Script::read(script).await {
                 Ok(Some(script)) => Some(Pep723Item::Script(script)),
                 Ok(None) => None,
                 Err(err) => return Err(err.into()),
@@ -334,7 +304,7 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
             | ProjectCommand::Export(uv_cli::ExportArgs {
                 script: Some(script),
                 ..
-            }) => match Pep723Script::read(&script).await {
+            }) => match Pep723Script::read(script).await {
                 Ok(Some(script)) => Some(Pep723Item::Script(script)),
                 Ok(None) => {
                     bail!(
@@ -1345,7 +1315,6 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
                 project,
                 &project_dir,
                 run_command,
-                downloaded_script.as_ref(),
                 script,
                 globals,
                 cli.top_level.no_config,
@@ -2017,7 +1986,6 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
     project_command: Box<ProjectCommand>,
     project_dir: &Path,
     command: Option<RunCommand>,
-    downloaded_script: Option<&tempfile::NamedTempFile>,
     script: Option<Pep723Item>,
     globals: GlobalSettings,
     // TODO(zanieb): Determine a better story for passing `no_config` in here
@@ -2138,7 +2106,6 @@ async fn run_project(
                 project_dir,
                 script,
                 command,
-                downloaded_script,
                 requirements,
                 args.show_resolution || globals.verbose > 0,
                 args.lock_check,

PATCH

echo "Patch applied successfully."
