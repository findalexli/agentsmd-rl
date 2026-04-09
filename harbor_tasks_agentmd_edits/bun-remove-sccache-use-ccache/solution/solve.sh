#!/bin/bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied (SetupSccache no longer referenced)
if ! grep -q 'SetupSccache' CMakeLists.txt 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/.buildkite/Dockerfile b/.buildkite/Dockerfile
index 033aec633d6..2b5f9448345 100644
--- a/.buildkite/Dockerfile
+++ b/.buildkite/Dockerfile
@@ -26,7 +26,7 @@ RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git python3 python3-pip ninja-build \
    software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release unzip \
-   libxml2-dev ruby ruby-dev bison gawk perl make golang \
+   libxml2-dev ruby ruby-dev bison gawk perl make golang ccache \
    && add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get install -y gcc-13 g++-13 libgcc-13-dev libstdc++-13-dev \
@@ -35,7 +35,8 @@ RUN apt-get update && apt-get install -y --no-install-recommends \
    && wget https://apt.llvm.org/llvm.sh \
    && chmod +x llvm.sh \
    && ./llvm.sh ${LLVM_VERSION} all \
-   && rm llvm.sh
+   && rm llvm.sh \
+   && rm -rf /var/lib/apt/lists/*


 RUN --mount=type=tmpfs,target=/tmp \
@@ -48,14 +49,6 @@ RUN --mount=type=tmpfs,target=/tmp \
     wget -O /tmp/cmake.sh "$cmake_url" && \
     sh /tmp/cmake.sh --skip-license --prefix=/usr

-RUN --mount=type=tmpfs,target=/tmp \
-    sccache_version="0.12.0" && \
-    arch=$(uname -m) && \
-    sccache_url="https://github.com/mozilla/sccache/releases/download/v${sccache_version}/sccache-v${sccache_version}-${arch}-unknown-linux-musl.tar.gz" && \
-    wget -O /tmp/sccache.tar.gz "$sccache_url" && \
-    tar -xzf /tmp/sccache.tar.gz -C /tmp && \
-    install -m755 /tmp/sccache-v${sccache_version}-${arch}-unknown-linux-musl/sccache /usr/local/bin
-
 RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 130 \
    --slave /usr/bin/g++ g++ /usr/bin/g++-13 \
    --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-13 \
@@ -134,9 +127,7 @@ RUN ARCH=$(if [ "$TARGETARCH" = "arm64" ]; then echo "arm64"; else echo "amd64"
 RUN mkdir -p /var/cache/buildkite-agent /var/log/buildkite-agent /var/run/buildkite-agent /etc/buildkite-agent /var/lib/buildkite-agent/cache/bun

 # The following is necessary to configure buildkite to use a stable
-# checkout directory. sccache hashes absolute paths into its cache keys,
-# so if buildkite uses a different checkout path each time (which it does
-# by default), sccache will be useless.
+# checkout directory for ccache to be effective.
 RUN mkdir -p -m 755 /var/lib/buildkite-agent/hooks && \
     cat <<'EOF' > /var/lib/buildkite-agent/hooks/environment
 #!/bin/sh
diff --git a/CMakeLists.txt b/CMakeLists.txt
index 8fe9a83f3fa..f30ad577c1e 100644
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -47,15 +47,7 @@ include(SetupEsbuild)
 include(SetupZig)
 include(SetupRust)

-find_program(SCCACHE_PROGRAM sccache)
-if(SCCACHE_PROGRAM AND NOT DEFINED ENV{NO_SCCACHE})
-  include(SetupSccache)
-else()
-  find_program(CCACHE_PROGRAM ccache)
-  if(CCACHE_PROGRAM)
-    include(SetupCcache)
-  endif()
-endif()
+include(SetupCcache)

 # Generate dependency versions header
 include(GenerateDependencyVersions)
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 192ce5ad639..750eb17a625 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -23,7 +23,7 @@ Using your system's package manager, install Bun's dependencies:
 {% codetabs group="os" %}

 ```bash#macOS (Homebrew)
-$ brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache
+$ brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby
 ```

 ```bash#Ubuntu/Debian
@@ -65,43 +65,28 @@ $ brew install bun

 {% /codetabs %}

-### Optional: Install `sccache`
+### Optional: Install `ccache`

-sccache is used to cache compilation artifacts, significantly speeding up builds. It must be installed with S3 support:
+ccache is used to cache compilation artifacts, significantly speeding up builds:

 ```bash
 # For macOS
-$ brew install sccache
+$ brew install ccache

-# For Linux. Note that the version in your package manager may not have S3 support.
-$ cargo install sccache --features=s3
-```
-
-This will install `sccache` with S3 support. Our build scripts will automatically detect and use `sccache` with our shared S3 cache. **Note**: Not all versions of `sccache` are compiled with S3 support, hence we recommend installing it via `cargo`.
-
-#### Registering AWS Credentials for `sccache` (Core Developers Only)
-
-Core developers have write access to the shared S3 cache. To enable write access, you must log in with AWS credentials. The easiest way to do this is to use the [`aws` CLI](https://aws.amazon.com/cli/) and invoke [`aws configure` to provide your AWS security info](https://docs.aws.amazon.com/cli/latest/reference/configure/).
-
-The `cmake` scripts should automatically detect your AWS credentials from the environment or the `~/.aws/credentials` file.
-
-<details>
-    <summary>Logging in to the `aws` CLI</summary>
-
-    1. Install the AWS CLI by following [the official guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
-    2. Log in to your AWS account console. A team member should provide you with your credentials.
-    3. Click your name in the top right > Security credentials.
-    4. Scroll to "Access keys" and create a new access key.
-    5. Run `aws configure` in your terminal and provide the access key ID and secret access key when prompted.
-</details>
+# For Ubuntu/Debian
+$ sudo apt install ccache

-<details>
-    <summary>Common Issues You May Encounter</summary>
+# For Arch
+$ sudo pacman -S ccache

-    - To confirm that the cache is being used, you can use the `sccache --show-stats` command right after a build. This will expose very useful statistics, including cache hits/misses.
-    - If you have multiple AWS profiles configured, ensure that the correct profile is set in the `AWS_PROFILE` environment variable.
-    - `sccache` follows a server-client model. If you run into weird issues where `sccache` refuses to use S3, even though you have AWS credentials configured, try killing any running `sccache` servers with `sccache --stop-server` and then re-running the build.
-</details>
+# For Fedora
+$ sudo dnf install ccache

+# For openSUSE
+$ sudo zypper install ccache
+```
+
+Our build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.

 ## Install LLVM

diff --git a/cmake/tools/SetupCcache.cmake b/cmake/tools/SetupCcache.cmake
index fc1e64aa96c..3e1982ca70c 100644
--- a/cmake/tools/SetupCcache.cmake
+++ b/cmake/tools/SetupCcache.cmake
@@ -5,18 +5,12 @@ if(NOT ENABLE_CCACHE OR CACHE_STRATEGY STREQUAL "none")
   return()
 endif()

-if (CI AND NOT APPLE)
-  setenv(CCACHE_DISABLE 1)
-  return()
-endif()

 find_command(
   VARIABLE
     CCACHE_PROGRAM
   COMMAND
     ccache
-  REQUIRED
-    ${CI}
 )

 if(NOT CCACHE_PROGRAM)
diff --git a/cmake/tools/SetupSccache.cmake b/cmake/tools/SetupSccache.cmake
deleted file mode 100644
index cb4b5aa750a..00000000000
--- a/cmake/tools/SetupSccache.cmake
+++ /dev/null
@@ -1,123 +0,0 @@
-# Setup sccache as the C and C++ compiler launcher to speed up builds by caching
-if(CACHE_STRATEGY STREQUAL "none")
-  return()
-endif()
-
-set(SCCACHE_SHARED_CACHE_REGION "us-west-1")
-set(SCCACHE_SHARED_CACHE_BUCKET "bun-build-sccache-store")
-
-# Function to check if the system AWS credentials have access to the sccache S3 bucket.
-function(check_aws_credentials OUT_VAR)
-  # Install dependencies first
-  execute_process(
-    COMMAND ${BUN_EXECUTABLE} install --frozen-lockfile
-    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/scripts/build-cache
-    RESULT_VARIABLE INSTALL_EXIT_CODE
-    OUTPUT_VARIABLE INSTALL_OUTPUT
-    ERROR_VARIABLE INSTALL_ERROR
-  )
-
-  if(NOT INSTALL_EXIT_CODE EQUAL 0)
-    message(FATAL_ERROR "Failed to install dependencies in scripts/build-cache\n"
-      "Exit code: ${INSTALL_EXIT_CODE}\n"
-      "Output: ${INSTALL_OUTPUT}\n"
-      "Error: ${INSTALL_ERROR}")
-  endif()
-
-  # Check AWS credentials
-  execute_process(
-    COMMAND
-      ${BUN_EXECUTABLE}
-      run
-      have-access.ts
-      --bucket ${SCCACHE_SHARED_CACHE_BUCKET}
-      --region ${SCCACHE_SHARED_CACHE_REGION}
-    WORKING_DIRECTORY
-      ${CMAKE_SOURCE_DIR}/scripts/build-cache
-    RESULT_VARIABLE HAVE_ACCESS_EXIT_CODE
-  )
-
-  if(HAVE_ACCESS_EXIT_CODE EQUAL 0)
-    set(HAS_CREDENTIALS TRUE)
-  else()
-    set(HAS_CREDENTIALS FALSE)
-  endif()
-
-  set(${OUT_VAR} ${HAS_CREDENTIALS} PARENT_SCOPE)
-endfunction()
-
-# Configure sccache to use the local cache only.
-function(sccache_configure_local_filesystem)
-  unsetenv(SCCACHE_BUCKET)
-  unsetenv(SCCACHE_REGION)
-  setenv(SCCACHE_DIR "${CACHE_PATH}/sccache")
-endfunction()
-
-# Configure sccache to use the distributed cache (S3 + local).
-function(sccache_configure_distributed)
-  setenv(SCCACHE_BUCKET "${SCCACHE_SHARED_CACHE_BUCKET}")
-  setenv(SCCACHE_REGION "${SCCACHE_SHARED_CACHE_REGION}")
-  setenv(SCCACHE_DIR "${CACHE_PATH}/sccache")
-endfunction()
-
-function(sccache_configure_environment_ci)
-  if(CACHE_STRATEGY STREQUAL "auto" OR CACHE_STRATEGY STREQUAL "distributed")
-    check_aws_credentials(HAS_AWS_CREDENTIALS)
-    if(HAS_AWS_CREDENTIALS)
-      sccache_configure_distributed()
-      message(NOTICE "sccache: Using distributed cache strategy.")
-    else()
-      message(FATAL_ERROR "CI CACHE_STRATEGY is set to '${CACHE_STRATEGY}', but no valid AWS "
-        "credentials were found. Note that 'auto' requires AWS credentials to access the shared "
-        "cache in CI.")
-    endif()
-  elseif(CACHE_STRATEGY STREQUAL "local")
-    # We disallow this because we want our CI runs to always used the shared cache to accelerate
-    # builds.
-    # none, distributed and auto are all okay.
-    #
-    # If local is configured, it's as good as "none", so this is probably user error.
-    message(FATAL_ERROR "CI CACHE_STRATEGY is set to 'local', which is not allowed.")
-  endif()
-endfunction()
-
-function(sccache_configure_environment_developer)
-  # Local environments can use any strategy they like. S3 is set up in such a way so as to clean
-  # itself from old entries automatically.
-  if (CACHE_STRATEGY STREQUAL "auto" OR CACHE_STRATEGY STREQUAL "local")
-    # In the local environment, we prioritize using the local cache. This is because sccache takes
-    # into consideration the whole absolute path of the files being compiled, and it's very
-    # unlikely users will have the same absolute paths on their local machines.
-    sccache_configure_local_filesystem()
-    message(NOTICE "sccache: Using local cache strategy.")
-  elseif(CACHE_STRATEGY STREQUAL "distributed")
-    check_aws_credentials(HAS_AWS_CREDENTIALS)
-    if(HAS_AWS_CREDENTIALS)
-      sccache_configure_distributed()
-      message(NOTICE "sccache: Using distributed cache strategy.")
-    else()
-      message(FATAL_ERROR "CACHE_STRATEGY is set to 'distributed', but no valid AWS credentials "
-        "were found.")
-    endif()
-  endif()
-endfunction()
-
-find_command(VARIABLE SCCACHE_PROGRAM COMMAND sccache REQUIRED ${CI})
-if(NOT SCCACHE_PROGRAM)
-  message(WARNING "sccache not found. Your builds will be slower.")
-  return()
-endif()
-
-set(SCCACHE_ARGS CMAKE_C_COMPILER_LAUNCHER CMAKE_CXX_COMPILER_LAUNCHER)
-foreach(arg ${SCCACHE_ARGS})
-  setx(${arg} ${SCCACHE_PROGRAM})
-  list(APPEND CMAKE_ARGS -D${arg}=${${arg}})
-endforeach()
-
-setenv(SCCACHE_LOG "info")
-
-if (CI)
-  sccache_configure_environment_ci()
-else()
-  sccache_configure_environment_developer()
-endif()
diff --git a/docs/project/building-windows.mdx b/docs/project/building-windows.mdx
index 9a4a3ab2d77..a5541ac6ccd 100644
--- a/docs/project/building-windows.mdx
+++ b/docs/project/building-windows.mdx
@@ -49,7 +49,7 @@ After Visual Studio, you need the following:

 ```ps1 Scoop
 > irm https://get.scoop.sh | iex
-> scoop install sccache cmake git ninja llvm go ruby
+> scoop install ccache cmake git ninja llvm go ruby
 ```

 You can now run `bun run build` to build Bun. It will take a while.
diff --git a/docs/project/contributing.mdx b/docs/project/contributing.mdx
index 22616e74d1f..e13d6cb7954 100644
--- a/docs/project/contributing.mdx
+++ b/docs/project/contributing.mdx
@@ -20,7 +20,7 @@ Using your system's package manager, install Bun's dependencies:
 <CodeTabs selectionGroup="os" ">

 ```bash#macOS (Homebrew)
-$ brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache
+$ brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby
 ```

 ```bash#Ubuntu/Debian
@@ -62,43 +62,28 @@ $ brew install bun

 </CodeTabs>

-### Optional: Install `sccache`
+### Optional: Install `ccache`

-sccache is used to cache compilation artifacts, significantly speeding up builds. It must be installed with S3 support:
+ccache is used to cache compilation artifacts, significantly speeding up builds:

 ```bash
 # For macOS
-$ brew install sccache
+$ brew install ccache

-# For Linux. Note that the version in your package manager may not have S3 support.
-$ cargo install sccache --features=s3
-```
-
-This will install `sccache` with S3 support. Our build scripts will automatically detect and use `sccache` with our shared S3 cache. **Note**: Not all versions of `sccache` are compiled with S3 support, hence we recommend installing it via `cargo`.
-
-#### Registering AWS Credentials for `sccache` (Core Developers Only)
-
-Core developers have write access to the shared S3 cache. To enable write access, you must log in with AWS credentials. The easiest way to do this is to use the [`aws` CLI](https://aws.amazon.com/cli/) and invoke [`aws configure` to provide your AWS security info](https://docs.aws.amazon.com/cli/latest/reference/configure/).
-
-The `cmake` scripts should automatically detect your AWS credentials from the environment or the `~/.aws/credentials` file.
-
-<details>
-    <summary>Logging in to the `aws` CLI</summary>
-
-    1. Install the AWS CLI by following [the official guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
-    2. Log in to your AWS account console. A team member should provide you with your credentials.
-    3. Click your name in the top right > Security credentials.
-    4. Scroll to "Access keys" and create a new access key.
-    5. Run `aws configure` in your terminal and provide the access key ID and secret access key when prompted.
-</details>
+# For Ubuntu/Debian
+$ sudo apt install ccache

-<details>
-    <summary>Common Issues You May Encounter</summary>
+# For Arch
+$ sudo pacman -S ccache

-    - To confirm that the cache is being used, you can use the `sccache --show-stats` command right after a build. This will expose very useful statistics, including cache hits/misses.
-    - If you have multiple AWS profiles configured, ensure that the correct profile is set in the `AWS_PROFILE` environment variable.
-    - `sccache` follows a server-client model. If you run into weird issues where `sccache` refuses to use S3, even though you have AWS credentials configured, try killing any running `sccache` servers with `sccache --stop-server` and then re-running the build.
-</details>
+# For Fedora
+$ sudo dnf install ccache

+# For openSUSE
+$ sudo zypper install ccache
+```
+
+Our build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.

 ## Install LLVM

diff --git a/flake.nix b/flake.nix
index 513b432e4be..c30e79c5824 100644
--- a/flake.nix
+++ b/flake.nix
@@ -70,7 +70,7 @@
               ninja
               nodejs_22
               pkg-config
-              sccache
+              ccache
               zig_hook
             ]
             ++ lib.optionals stdenv.isDarwin [
diff --git a/scripts/bootstrap.ps1 b/scripts/bootstrap.ps1
index e104a3d504a..c0f5b77c304 100644
--- a/scripts/bootstrap.ps1
+++ b/scripts/bootstrap.ps1
@@ -137,7 +137,7 @@ function install_packages() {
     }

     if ($WithCache) {
-        scoop install sccache
+        scoop install ccache
     }

     if ($Go) {
@@ -148,7 +148,7 @@ function install_packages() {
     }

     if ($CI) {
-        # sccache is already installed
+        # ccache is already installed
     }

     if ($LastExitCode -ne 0) {
diff --git a/scripts/bootstrap.sh b/scripts/bootstrap.sh
index 7e447f09b71..74e05a94b0f 100644
--- a/scripts/bootstrap.sh
+++ b/scripts/bootstrap.sh
@@ -1,5 +1,5 @@
 #!/bin/sh
-# Version: 25
+# Version: 26

@@ -1086,7 +1086,7 @@ install_build_essentials() {
 	install_osxcross
 	install_gcc
 	install_rust
-	install_sccache
+	install_ccache
 	install_docker
 }

@@ -1206,35 +1206,24 @@ install_gcc() {
 	execute_sudo ln -sf $(which llvm-symbolizer-$llvm_v) /usr/bin/llvm-symbolizer
 }

-install_sccache() {
-	if [ "$os" != "linux" ]; then
-		error "Unsupported platform: $os"
-	fi
-
-	# Alright, look, this function is cobbled together but it's only as cobbled
-	# together as this whole script is.
-	#
-	# For some reason, move_to_bin doesn't work here due to permissions so I'm
-	# avoiding that function. It's also wrong with permissions and so on.
-	#
-	# Unfortunately, we cannot use install_packages since many package managers
-	# don't compile `sccache` with S3 support.
-	local opts=$-
-	set -ef
-
-	local sccache_http
-	sccache_http="https://github.com/mozilla/sccache/releases/download/v0.12.0/sccache-v0.12.0-$(uname -m)-unknown-linux-musl.tar.gz"
-
-	local file
-	file=$(download_file "$sccache_http")
-
-	local tmpdir
-	tmpdir=$(mktemp -d)
-
-	execute tar -xzf "$file" -C "$tmpdir"
-	execute_sudo install -m755 "$tmpdir/sccache-v0.12.0-$(uname -m)-unknown-linux-musl/sccache" "/usr/local/bin"
-
-	set +ef -"$opts"
+install_ccache() {
+	case "$pm" in
+	apt)
+		install_packages ccache
+		;;
+	brew)
+		install_packages ccache
+		;;
+	apk)
+		install_packages ccache
+		;;
+	dnf|yum)
+		install_packages ccache
+		;;
+	zypper)
+		install_packages ccache
+		;;
+	esac
 }

 install_rust() {
@@ -1457,9 +1446,7 @@ create_buildkite_user() {
 	done

 	# The following is necessary to configure buildkite to use a stable
-	# checkout directory. sccache hashes absolute paths into its cache keys,
-	# so if buildkite uses a different checkout path each time (which it does
-	# by default), sccache will be useless.
+	# checkout directory for ccache to be effective.
 	local opts=$-
 	set -ef

diff --git a/scripts/build-cache/bun.lock b/scripts/build-cache/bun.lock
deleted file mode 100644
index b822c814837..00000000000
--- a/scripts/build-cache/bun.lock
+++ /dev/null
@@ -1,249 +0,0 @@
-{
-  "lockfileVersion": 1,
-  "configVersion": 1,
-  "workspaces": {
-    "": {
-      "dependencies": {
-        "@aws-sdk/client-s3": "^3.928.0",
-        "@aws-sdk/property-provider": "^3.374.0",
-      },
-    },
-  },
-  "packages": {
-    "@aws-crypto/crc32": ["@aws-crypto/crc32@5.2.0", "", { "dependencies": { "@aws-crypto/util": "^5.2.0", "@aws-sdk/types": "^3.222.0", "tslib": "^2.6.2" } }, "sha512-nLbCWqQNgUiwwtFsen1AdzAtvuLRsQS8rYgMuxCrdKf9kOssamGLuPwyTY9wyYblNr9+1XM8v6zoDTPPSIeANg=="],
-    "@aws-crypto/crc32c": ["@aws-crypto/crc32c@5.2.0", "", { "dependencies": { "@aws-crypto/util": "^5.2.0", "@aws-sdk/types": "^3.222.0", "tslib": "^2.6.2" } }, "sha512-+iWb8qaHLYKrNvGRbiYRHSdKRWhto5XlZUEBwDjYNf+ly5SVYG6zEoYIdxvf5R3zyeP16w4PLBn3rH1xc74Rag=="],
-    "@aws-crypto/sha1-browser": ["@aws-crypto/sha1-browser@5.2.0", "", { "dependencies": { "@aws-crypto/supports-web-crypto": "^5.2.0", "@aws-crypto/util": "^5.2.0", "@aws-sdk/types": "^3.222.0",
diff --git a/scripts/build-cache/have-access.ts b/scripts/build-cache/have-access.ts
deleted file mode 100644
index 3c87188a63d..00000000000
--- a/scripts/build-cache/have-access.ts
+++ /dev/null
@@ -1,82 +0,0 @@
-import {
-  GetObjectCommand,
-  HeadBucketCommand,
-  PutObjectCommand,
-  S3Client,
-} from "@aws-sdk/client-s3";
-import {
-  fromEnv,
-  fromInstanceMetadata,
-  fromContainerMetadata,
-  fromHttp,
-  chain,
-} from "@aws-sdk/property-provider";
-
-const region = process.argv.includes("--region")
-  ? process.argv[process.argv.indexOf("--region") + 1]
-  : "us-west-1";
-const bucket = process.argv.includes("--bucket")
-  ? process.argv[process.argv.indexOf("--bucket") + 1]
-  : "bun-build-sccache-store";
-
-const s3 = new S3Client({
-  region,
-  credentials: chain([
-    fromEnv(),
-    fromHttp(),
-    fromInstanceMetadata(),
-    fromContainerMetadata(),
-  ]),
-});
-
-async function canAccessS3() {
-  try {
-    await s3.send(
-      new HeadBucketCommand({
-        Bucket: bucket,
-      }),
-    );
-    return true;
-  } catch (e) {
-    return false;
-  }
-}
-
-async function putReadDeleteCheck() {
-  try {
-    const key = `test/test-object-${Date.now()}.txt`;
-    const body = "Hello, world!";
-    await s3.send(
-      new PutObjectCommand({
-        Bucket: bucket,
-        Key: key,
-        Body: body,
-      }),
-    );
-    return true;
-  } catch (e) {
-    return false;
-  }
-}
-
-async function main() {
-  const hasAccess = await canAccessS3();
-  if (!hasAccess) {
-    console.log("No access to S3 bucket");
-    process.exit(1);
-  }
-
-  const canWrite = await putReadDeleteCheck();
-  if (!canWrite) {
-    console.log("Cannot write to S3 bucket");
-    process.exit(1);
-  }
-
-  console.log("S3 access confirmed");
-  process.exit(0);
-}
-
-main();
diff --git a/scripts/build-cache/package.json b/scripts/build-cache/package.json
deleted file mode 100644
index 510d55b8e63..00000000000
--- a/scripts/build-cache/package.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "dependencies": {
-    "@aws-sdk/client-s3": "^3.928.0",
-    "@aws-sdk/property-provider": "^3.374.0",
-  }
-}
diff --git a/shell.nix b/shell.nix
index 513b432e4be..c30e79c5824 100644
--- a/shell.nix
+++ b/shell.nix
@@ -70,7 +70,7 @@
               ninja
               nodejs_22
               pkg-config
-              sccache
+              ccache
             ]
             ++ lib.optionals stdenv.isDarwin [
PATCH

echo "Patch applied successfully."
