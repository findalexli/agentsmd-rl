#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q 'pub enum StdioOrFd' ext/process/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/ext/io/lib.rs b/ext/io/lib.rs
index 8a49d09dae523e..184cc08bdef9a5 100644
--- a/ext/io/lib.rs
+++ b/ext/io/lib.rs
@@ -262,31 +262,50 @@ deno_core::extension!(deno_io,
       ));
       assert_eq!(rid, 0, "stdin must have ResourceId 0");

-      let rid = t.add(FileResource::new(
-        Rc::new(match stdio.stdout.pipe {
-          StdioPipeInner::Inherit => StdFileResourceInner::new(
+      let (stdout_inner, child_stdout) = match stdio.stdout.pipe {
+        StdioPipeInner::Inherit => (
+          StdFileResourceInner::new(
             StdFileResourceKind::Stdout,
             STDOUT_HANDLE.try_clone().unwrap(),
             None,
           ),
-          StdioPipeInner::File(pipe) => StdFileResourceInner::file(pipe, None),
-        }),
+          STDOUT_HANDLE.try_clone().unwrap(),
+        ),
+        StdioPipeInner::File(pipe) => {
+          let child_handle = pipe.try_clone().unwrap();
+          (StdFileResourceInner::file(pipe, None), child_handle)
+        }
+      };
+      let rid = t.add(FileResource::new(
+        Rc::new(stdout_inner),
         "stdout".to_string(),
       ));
       assert_eq!(rid, 1, "stdout must have ResourceId 1");

-      let rid = t.add(FileResource::new(
-        Rc::new(match stdio.stderr.pipe {
-          StdioPipeInner::Inherit => StdFileResourceInner::new(
+      let (stderr_inner, child_stderr) = match stdio.stderr.pipe {
+        StdioPipeInner::Inherit => (
+          StdFileResourceInner::new(
             StdFileResourceKind::Stderr,
             STDERR_HANDLE.try_clone().unwrap(),
             None,
           ),
-          StdioPipeInner::File(pipe) => StdFileResourceInner::file(pipe, None),
-        }),
+          STDERR_HANDLE.try_clone().unwrap(),
+        ),
+        StdioPipeInner::File(pipe) => {
+          let child_handle = pipe.try_clone().unwrap();
+          (StdFileResourceInner::file(pipe, None), child_handle)
+        }
+      };
+      let rid = t.add(FileResource::new(
+        Rc::new(stderr_inner),
         "stderr".to_string(),
       ));
       assert_eq!(rid, 2, "stderr must have ResourceId 2");
+
+      state.put(ChildProcessStdio {
+        stdout: child_stdout,
+        stderr: child_stderr,
+      });
     }
   },
 );
@@ -339,6 +358,18 @@ pub struct Stdio {
   pub stderr: StdioPipe,
 }

+/// Holds the effective stdout/stderr handles for child process inheritance.
+///
+/// When the runtime redirects stdout/stderr (e.g. during `deno test` for
+/// output capture), child processes spawned with `stdio: "inherit"` need
+/// to inherit the redirected handles, not the original OS stdout/stderr.
+/// This struct is stored in `OpState` during IO extension init and read
+/// by the process extension when spawning children.
+pub struct ChildProcessStdio {
+  pub stdout: StdFile,
+  pub stderr: StdFile,
+}
+
 #[derive(Debug)]
 pub struct WriteOnlyResource<S> {
   stream: AsyncRefCell<S>,
diff --git a/ext/node/polyfills/internal/child_process.ts b/ext/node/polyfills/internal/child_process.ts
index a6e1e140fe2ae8..8e661dea78bbb5 100644
--- a/ext/node/polyfills/internal/child_process.ts
+++ b/ext/node/polyfills/internal/child_process.ts
@@ -748,7 +748,7 @@ function toDenoStdio(
     return "inherit";
   }
   if (typeof pipe === "number") {
-    /* Assume it's a rid returned by fs APIs */
+    /* Real OS file descriptor, e.g. from fs.openSync() */
     return pipe;
   }

diff --git a/ext/process/lib.rs b/ext/process/lib.rs
index 57e7bbf98fac0e..24348d686e1ac6 100644
--- a/ext/process/lib.rs
+++ b/ext/process/lib.rs
@@ -7,6 +7,8 @@ use std::collections::HashMap;
 use std::ffi::OsString;
 use std::io::Write;
 #[cfg(unix)]
+use std::os::unix::io::FromRawFd;
+#[cfg(unix)]
 use std::os::unix::prelude::ExitStatusExt;
 #[cfg(unix)]
 use std::os::unix::process::CommandExt;
@@ -31,11 +33,11 @@ use deno_core::convert::Uint8Array;
 use deno_core::op2;
 use deno_core::serde_json;
 use deno_error::JsErrorBox;
+use deno_io::ChildProcessStdio;
 use deno_io::ChildStderrResource;
 use deno_io::ChildStdinResource;
 use deno_io::ChildStdoutResource;
 use deno_io::IntoRawIoHandle;
-use deno_io::fs::FileResource;
 use deno_os::SignalError;
 use deno_permissions::PathQueryDescriptor;
 use deno_permissions::PermissionsContainer;
@@ -79,12 +81,12 @@ impl Stdio {
 }

 #[derive(Copy, Clone, Eq, PartialEq)]
-pub enum StdioOrRid {
+pub enum StdioOrFd {
   Stdio(Stdio),
-  Rid(ResourceId),
+  Fd(i32),
 }

-impl<'de> Deserialize<'de> for StdioOrRid {
+impl<'de> Deserialize<'de> for StdioOrFd {
   fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
   where
     D: serde::Deserializer<'de>,
@@ -93,47 +95,72 @@ impl<'de> Deserialize<'de> for StdioOrRid {
     let value = Value::deserialize(deserializer)?;
     match value {
       Value::String(val) => match val.as_str() {
-        "inherit" => Ok(StdioOrRid::Stdio(Stdio::Inherit)),
-        "piped" => Ok(StdioOrRid::Stdio(Stdio::Piped)),
-        "null" => Ok(StdioOrRid::Stdio(Stdio::Null)),
+        "inherit" => Ok(StdioOrFd::Stdio(Stdio::Inherit)),
+        "piped" => Ok(StdioOrFd::Stdio(Stdio::Piped)),
+        "null" => Ok(StdioOrFd::Stdio(Stdio::Null)),
         "ipc_for_internal_use" => {
-          Ok(StdioOrRid::Stdio(Stdio::IpcForInternalUse))
+          Ok(StdioOrFd::Stdio(Stdio::IpcForInternalUse))
         }
         val => Err(serde::de::Error::unknown_variant(
           val,
           &["inherit", "piped", "null"],
         )),
       },
-      Value::Number(val) => match val.as_u64() {
-        Some(val) if val <= ResourceId::MAX as u64 => {
-          Ok(StdioOrRid::Rid(val as ResourceId))
+      Value::Number(val) => match val.as_i64() {
+        Some(val) if val >= 0 && val <= i32::MAX as i64 => {
+          Ok(StdioOrFd::Fd(val as i32))
         }
-        _ => Err(serde::de::Error::custom("Expected a positive integer")),
+        _ => Err(serde::de::Error::custom(
+          "Expected a non-negative integer file descriptor",
+        )),
       },
       _ => Err(serde::de::Error::custom(
-        r#"Expected a resource id, "inherit", "piped", or "null""#,
+        r#"Expected a file descriptor, "inherit", "piped", or "null""#,
       )),
     }
   }
 }

-impl StdioOrRid {
-  pub fn as_stdio(
-    &self,
-    state: &mut OpState,
-  ) -> Result<StdStdio, ProcessError> {
+impl StdioOrFd {
+  pub fn as_stdio(&self) -> Result<StdStdio, ProcessError> {
     match &self {
-      StdioOrRid::Stdio(val) => Ok(val.as_stdio()),
-      StdioOrRid::Rid(rid) => {
-        Ok(FileResource::with_file(state, *rid, |file| {
-          file.as_stdio().map_err(deno_error::JsErrorBox::from_err)
-        })?)
+      StdioOrFd::Stdio(val) => Ok(val.as_stdio()),
+      StdioOrFd::Fd(fd) => {
+        #[cfg(unix)]
+        {
+          // Safety: we dup the fd so the original remains open for the caller
+          let new_fd = unsafe { libc::dup(*fd) };
+          if new_fd < 0 {
+            return Err(ProcessError::Io(std::io::Error::last_os_error()));
+          }
+          // Safety: new_fd is a valid, freshly duplicated file descriptor
+          Ok(unsafe {
+            StdStdio::from(std::os::unix::io::OwnedFd::from_raw_fd(new_fd))
+          })
+        }
+        #[cfg(windows)]
+        {
+          // SAFETY: *fd is a valid CRT file descriptor obtained from fs.openSync
+          let handle = unsafe { libc::get_osfhandle(*fd as _) };
+          if handle == -1 {
+            return Err(ProcessError::Io(std::io::Error::last_os_error()));
+          }
+          // SAFETY: handle is a valid OS handle returned by get_osfhandle (checked above)
+          let borrowed = unsafe {
+            std::os::windows::io::BorrowedHandle::borrow_raw(
+              handle as std::os::windows::io::RawHandle,
+            )
+          };
+          let owned =
+            borrowed.try_clone_to_owned().map_err(ProcessError::Io)?;
+          Ok(StdStdio::from(owned))
+        }
       }
     }
   }

   pub fn is_ipc(&self) -> bool {
-    matches!(self, StdioOrRid::Stdio(Stdio::IpcForInternalUse))
+    matches!(self, StdioOrFd::Stdio(Stdio::IpcForInternalUse))
   }
 }

@@ -248,7 +275,7 @@ pub struct SpawnArgs {

   input: Option<JsBuffer>,

-  extra_stdio: Vec<Stdio>,
+  extra_stdio: Vec<StdioOrFd>,
   detached: bool,
   needs_npm_process_state: bool,
   #[cfg(unix)]
@@ -349,9 +376,9 @@ pub enum ProcessError {
 #[derive(Deserialize)]
 #[serde(rename_all = "camelCase")]
 pub struct ChildStdio {
-  stdin: StdioOrRid,
-  stdout: StdioOrRid,
-  stderr: StdioOrRid,
+  stdin: StdioOrFd,
+  stdout: StdioOrFd,
+  stderr: StdioOrFd,
 }

 #[derive(ToV8)]
@@ -515,16 +542,22 @@ fn create_command(
   } else if args.input.is_some() {
     command.stdin(StdStdio::piped());
   } else {
-    command.stdin(args.stdio.stdin.as_stdio(state)?);
+    command.stdin(args.stdio.stdin.as_stdio()?);
   }

   command.stdout(match args.stdio.stdout {
-    StdioOrRid::Stdio(Stdio::Inherit) => StdioOrRid::Rid(1).as_stdio(state)?,
-    value => value.as_stdio(state)?,
+    StdioOrFd::Stdio(Stdio::Inherit) => {
+      let cs = state.borrow::<ChildProcessStdio>();
+      StdStdio::from(cs.stdout.try_clone().map_err(ProcessError::Io)?)
+    }
+    value => value.as_stdio()?,
   });
   command.stderr(match args.stdio.stderr {
-    StdioOrRid::Stdio(Stdio::Inherit) => StdioOrRid::Rid(2).as_stdio(state)?,
-    value => value.as_stdio(state)?,
+    StdioOrFd::Stdio(Stdio::Inherit) => {
+      let cs = state.borrow::<ChildProcessStdio>();
+      StdStdio::from(cs.stderr.try_clone().map_err(ProcessError::Io)?)
+    }
+    value => value.as_stdio()?,
   });

   #[cfg(unix)]
@@ -578,27 +611,34 @@ fn create_command(
     for (i, stdio) in args.extra_stdio.into_iter().enumerate() {
       // index 0 in `extra_stdio` actually refers to fd 3
       // because we handle stdin,stdout,stderr specially
-      let fd = (i + 3) as i32;
-      // TODO(nathanwhit): handle inherited, but this relies on the parent process having
-      // fds open already. since we don't generally support dealing with raw fds,
-      // we can't properly support this
-      if matches!(stdio, Stdio::Piped) {
-        let (fd1, fd2) = deno_io::bi_pipe_pair_raw()?;
-        fds_to_dup.push((fd2, fd));
-        fds_to_close.push(fd2);
-        let rid = state.resource_table.add(
-          match deno_io::BiPipeResource::from_raw_handle(fd1) {
-            Ok(v) => v,
-            Err(e) => {
-              log::warn!("Failed to open bidirectional pipe for fd {fd}: {e}");
-              extra_pipe_rids.push(None);
-              continue;
-            }
-          },
-        );
-        extra_pipe_rids.push(Some(rid));
-      } else {
-        extra_pipe_rids.push(None);
+      let target_fd = (i + 3) as i32;
+      match stdio {
+        StdioOrFd::Stdio(Stdio::Piped) => {
+          let (fd1, fd2) = deno_io::bi_pipe_pair_raw()?;
+          fds_to_dup.push((fd2, target_fd));
+          fds_to_close.push(fd2);
+          let rid = state.resource_table.add(
+            match deno_io::BiPipeResource::from_raw_handle(fd1) {
+              Ok(v) => v,
+              Err(e) => {
+                log::warn!(
+                  "Failed to open bidirectional pipe for fd {target_fd}: {e}"
+                );
+                extra_pipe_rids.push(None);
+                continue;
+              }
+            },
+          );
+          extra_pipe_rids.push(Some(rid));
+        }
+        StdioOrFd::Fd(fd) => {
+          // Dup the caller's fd onto the target fd slot in the child
+          fds_to_dup.push((fd, target_fd));
+          extra_pipe_rids.push(None);
+        }
+        _ => {
+          extra_pipe_rids.push(None);
+        }
       }
     }

@@ -670,29 +710,40 @@ fn create_command(
     for (i, stdio) in args.extra_stdio.into_iter().enumerate() {
       // index 0 in `extra_stdio` actually refers to fd 3
       // because we handle stdin,stdout,stderr specially
-      let fd = (i + 3) as i32;
-      // TODO(nathanwhit): handle inherited, but this relies on the parent process having
-      // fds open already. since we don't generally support dealing with raw fds,
-      // we can't properly support this
-      if matches!(stdio, Stdio::Piped) {
-        let (fd1, fd2) = deno_io::bi_pipe_pair_raw()?;
-        handles_to_close.push(fd2);
-        let rid = state.resource_table.add(
-          match deno_io::BiPipeResource::from_raw_handle(fd1) {
-            Ok(v) => v,
-            Err(e) => {
-              log::warn!("Failed to open bidirectional pipe for fd {fd}: {e}");
-              extra_pipe_rids.push(None);
-              continue;
-            }
-          },
-        );
-        command.extra_handle(Some(fd2));
-        extra_pipe_rids.push(Some(rid));
-      } else {
-        // no handle, push an empty handle so we need get the right fds for following handles
-        command.extra_handle(None);
-        extra_pipe_rids.push(None);
+      let target_fd = (i + 3) as i32;
+      match stdio {
+        StdioOrFd::Stdio(Stdio::Piped) => {
+          let (fd1, fd2) = deno_io::bi_pipe_pair_raw()?;
+          handles_to_close.push(fd2);
+          let rid = state.resource_table.add(
+            match deno_io::BiPipeResource::from_raw_handle(fd1) {
+              Ok(v) => v,
+              Err(e) => {
+                log::warn!(
+                  "Failed to open bidirectional pipe for fd {target_fd}: {e}"
+                );
+                extra_pipe_rids.push(None);
+                continue;
+              }
+            },
+          );
+          command.extra_handle(Some(fd2));
+          extra_pipe_rids.push(Some(rid));
+        }
+        StdioOrFd::Fd(fd) => {
+          // SAFETY: fd is a valid CRT file descriptor passed from the JS stdio array
+          let handle = unsafe { libc::get_osfhandle(fd as _) };
+          if handle == -1 {
+            return Err(ProcessError::Io(std::io::Error::last_os_error()));
+          }
+          command.extra_handle(Some(handle as _));
+          extra_pipe_rids.push(None);
+        }
+        _ => {
+          // no handle, push an empty handle so we get the right fds for following handles
+          command.extra_handle(None);
+          extra_pipe_rids.push(None);
+        }
       }
     }

@@ -1116,8 +1167,8 @@ fn op_spawn_sync(
   state: &mut OpState,
   #[serde] args: SpawnArgs,
 ) -> Result<SpawnOutput, ProcessError> {
-  let stdout = matches!(args.stdio.stdout, StdioOrRid::Stdio(Stdio::Piped));
-  let stderr = matches!(args.stdio.stderr, StdioOrRid::Stdio(Stdio::Piped));
+  let stdout = matches!(args.stdio.stdout, StdioOrFd::Stdio(Stdio::Piped));
+  let stderr = matches!(args.stdio.stderr, StdioOrFd::Stdio(Stdio::Piped));
   let input = args.input.clone();
   let (mut command, _, _, _) =
     create_command(state, args, "Deno.Command().outputSync()")?;
@@ -1219,11 +1270,11 @@ mod deprecated {
     cwd: Option<String>,
     env: Vec<(String, String)>,
     #[from_v8(serde)]
-    stdin: StdioOrRid,
+    stdin: StdioOrFd,
     #[from_v8(serde)]
-    stdout: StdioOrRid,
+    stdout: StdioOrFd,
     #[from_v8(serde)]
-    stderr: StdioOrRid,
+    stderr: StdioOrFd,
   }

   struct ChildResource {
@@ -1296,21 +1347,21 @@ mod deprecated {
     }

     // TODO: make this work with other resources, eg. sockets
-    c.stdin(run_args.stdin.as_stdio(state)?);
-    c.stdout(
-      match run_args.stdout {
-        StdioOrRid::Stdio(Stdio::Inherit) => StdioOrRid::Rid(1),
-        value => value,
+    c.stdin(run_args.stdin.as_stdio()?);
+    c.stdout(match run_args.stdout {
+      StdioOrFd::Stdio(Stdio::Inherit) => {
+        let cs = state.borrow::<ChildProcessStdio>();
+        StdStdio::from(cs.stdout.try_clone().map_err(ProcessError::Io)?)
       }
-      .as_stdio(state)?,
-    );
-    c.stderr(
-      match run_args.stderr {
-        StdioOrRid::Stdio(Stdio::Inherit) => StdioOrRid::Rid(2),
-        value => value,
+      value => value.as_stdio()?,
+    });
+    c.stderr(match run_args.stderr {
+      StdioOrFd::Stdio(Stdio::Inherit) => {
+        let cs = state.borrow::<ChildProcessStdio>();
+        StdStdio::from(cs.stderr.try_clone().map_err(ProcessError::Io)?)
       }
-      .as_stdio(state)?,
-    );
+      value => value.as_stdio()?,
+    });

     // We want to kill child when it's closed
     c.kill_on_drop(true);
diff --git a/tests/unit_node/child_process_test.ts b/tests/unit_node/child_process_test.ts
index 094e490549d841..5b5a45b82fbcf4 100644
--- a/tests/unit_node/child_process_test.ts
+++ b/tests/unit_node/child_process_test.ts
@@ -1365,3 +1365,32 @@ Deno.test(function spawnSyncReturnsPid() {
   assertEquals(typeof ret.pid, "number");
   assert(ret.pid > 0);
 });
+
+Deno.test({
+  name: "spawnWithNumericFdInStdioArray",
+  ignore: Deno.build.os === "windows",
+  async fn() {
+    const fs = await import("node:fs");
+    const tmpFile = Deno.makeTempFileSync();
+    try {
+      const fd = fs.openSync(tmpFile, "w");
+      const child = spawn("/bin/sh", [
+        "-c",
+        "echo hello from child >&3",
+      ], {
+        stdio: ["ignore", "pipe", "pipe", fd],
+      });
+      const { promise, resolve } = Promise.withResolvers<number>();
+      child.on("close", (code: number) => {
+        resolve(code);
+      });
+      const code = await promise;
+      fs.closeSync(fd);
+      assertEquals(code, 0);
+      const content = Deno.readTextFileSync(tmpFile);
+      assertEquals(content, "hello from child\n");
+    } finally {
+      Deno.removeSync(tmpFile);
+    }
+  },
+});

PATCH

echo "Patch applied successfully."
