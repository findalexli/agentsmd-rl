#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check: if distinctive line from patch exists, skip
if grep -q "rustup_sha256s\[amd64\]=\"4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10\"" scripts/docker/install_os_dependencies.sh 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/.github/workflows/additional-ci-image-checks.yml b/.github/workflows/additional-ci-image-checks.yml
index 6a33cea2..e39fcbd4 100644
--- a/.github/workflows/additional-ci-image-checks.yml
+++ b/.github/workflows/additional-ci-image-checks.yml
@@ -116,8 +116,10 @@ jobs:
       (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')

   # Check that after earlier cache push, breeze command will build quickly
+  # This build is a bit slow from in-the scratch builds, so we should run it only in
+  # regular PRs
   check-that-image-builds-quickly:
-    timeout-minutes: 17
+    timeout-minutes: 25
     name: Check that image builds quickly
     runs-on: ${{ fromJSON(inputs.runners) }}
     env:
@@ -141,4 +143,6 @@ jobs:
       - name: "Install Breeze"
         uses: ./.github/actions/breeze
       - name: "Check that image builds quickly"
-        run: breeze shell --max-time 900 --platform "${PLATFORM}"
+        # Synchronize to be a little bit shorter than above timeout-minutes to make sure that
+        # if the build takes too long the job will fail with logs. 22 minutes * 60 s = 1320 seconds
+        run: breeze shell --max-time 1320 --platform "${PLATFORM}"
diff --git a/Dockerfile b/Dockerfile
index 6c5f6ebb..c7177a1d 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -122,6 +122,8 @@ fi
 AIRFLOW_PYTHON_VERSION=${AIRFLOW_PYTHON_VERSION:-3.10.18}
 PYTHON_LTO=${PYTHON_LTO:-true}
 GOLANG_MAJOR_MINOR_VERSION=${GOLANG_MAJOR_MINOR_VERSION:-1.24.4}
+RUSTUP_DEFAULT_TOOLCHAIN=${RUSTUP_DEFAULT_TOOLCHAIN:-stable}
+RUSTUP_VERSION=${RUSTUP_VERSION:-1.29.0}
 COSIGN_VERSION=${COSIGN_VERSION:-3.0.5}

 if [[ "${1}" == "runtime" ]]; then
@@ -493,6 +495,33 @@ function install_golang() {
     rm -rf /usr/local/go && tar -C /usr/local -xzf go"${GOLANG_MAJOR_MINOR_VERSION}".linux.tar.gz
 }

+function install_rustup() {
+    local arch
+    arch="$(dpkg --print-architecture)"
+    declare -A rustup_targets=(
+        [amd64]="x86_64-unknown-linux-gnu"
+        [arm64]="aarch64-unknown-linux-gnu"
+    )
+    declare -A rustup_sha256s=(
+        # https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/{target}/rustup-init.sha256
+        [amd64]="4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10"
+        [arm64]="9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792"
+    )
+    local target="${rustup_targets[${arch}]}"
+    local rustup_sha256="${rustup_sha256s[${arch}]}"
+    if [[ -z "${target}" ]]; then
+        echo "Unsupported architecture for rustup: ${arch}"
+        exit 1
+    fi
+    curl --proto '=https' --tlsv1.2 -sSf \
+        "https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/${target}/rustup-init" \
+        -o /tmp/rustup-init
+    echo "${rustup_sha256}  /tmp/rustup-init" | sha256sum --check
+    chmod +x /tmp/rustup-init
+    /tmp/rustup-init -y --default-toolchain "${RUSTUP_DEFAULT_TOOLCHAIN}"
+    rm -f /tmp/rustup-init
+}
+
 function apt_clean() {
     apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
     rm -rf /var/lib/apt/lists/* /var/log/*
@@ -508,6 +537,7 @@ else
     install_debian_dev_dependencies
     install_python
     install_additional_dev_dependencies
+    install_rustup
     if [[ "${INSTALLATION_TYPE}" == "CI" ]]; then
         install_golang
     fi
@@ -1843,6 +1873,10 @@ ENV DEV_APT_DEPS=${DEV_APT_DEPS} \

 ARG PYTHON_LTO

+ENV RUSTUP_HOME="/usr/local/rustup"
+ENV CARGO_HOME="/usr/local/cargo"
+ENV PATH="${CARGO_HOME}/bin:${PATH}"
+
 COPY --from=scripts install_os_dependencies.sh /scripts/docker/
 RUN PYTHON_LTO=${PYTHON_LTO} bash /scripts/docker/install_os_dependencies.sh dev

diff --git a/Dockerfile.ci b/Dockerfile.ci
index 2b1c38f3..298323d2 100644
--- a/Dockerfile.ci
+++ b/Dockerfile.ci
@@ -62,6 +62,8 @@ fi
 AIRFLOW_PYTHON_VERSION=${AIRFLOW_PYTHON_VERSION:-3.10.18}
 PYTHON_LTO=${PYTHON_LTO:-true}
 GOLANG_MAJOR_MINOR_VERSION=${GOLANG_MAJOR_MINOR_VERSION:-1.24.4}
+RUSTUP_DEFAULT_TOOLCHAIN=${RUSTUP_DEFAULT_TOOLCHAIN:-stable}
+RUSTUP_VERSION=${RUSTUP_VERSION:-1.29.0}
 COSIGN_VERSION=${COSIGN_VERSION:-3.0.5}

 if [[ "${1}" == "runtime" ]]; then
@@ -433,6 +435,33 @@ function install_golang() {
     rm -rf /usr/local/go && tar -C /usr/local -xzf go"${GOLANG_MAJOR_MINOR_VERSION}".linux.tar.gz
 }

+function install_rustup() {
+    local arch
+    arch="$(dpkg --print-architecture)"
+    declare -A rustup_targets=(
+        [amd64]="x86_64-unknown-linux-gnu"
+        [arm64]="aarch64-unknown-linux-gnu"
+    )
+    declare -A rustup_sha256s=(
+        # https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/{target}/rustup-init.sha256
+        [amd64]="4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10"
+        [arm64]="9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792"
+    )
+    local target="${rustup_targets[${arch}]}"
+    local rustup_sha256="${rustup_sha256s[${arch}]}"
+    if [[ -z "${target}" ]]; then
+        echo "Unsupported architecture for rustup: ${arch}"
+        exit 1
+    fi
+    curl --proto '=https' --tlsv1.2 -sSf \
+        "https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/${target}/rustup-init" \
+        -o /tmp/rustup-init
+    echo "${rustup_sha256}  /tmp/rustup-init" | sha256sum --check
+    chmod +x /tmp/rustup-init
+    /tmp/rustup-init -y --default-toolchain "${RUSTUP_DEFAULT_TOOLCHAIN}"
+    rm -f /tmp/rustup-init
+}
+
 function apt_clean() {
     apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
     rm -rf /var/lib/apt/lists/* /var/log/*
@@ -448,6 +477,7 @@ else
     install_debian_dev_dependencies
     install_python
     install_additional_dev_dependencies
+    install_rustup
     if [[ "${INSTALLATION_TYPE}" == "CI" ]]; then
         install_golang
     fi
@@ -1646,6 +1676,9 @@ ENV DEV_APT_COMMAND=${DEV_APT_COMMAND} \
 ARG AIRFLOW_PYTHON_VERSION="3.12.13"
 ENV AIRFLOW_PYTHON_VERSION=${AIRFLOW_PYTHON_VERSION}
 ENV GOLANG_MAJOR_MINOR_VERSION="1.26.1"
+ENV RUSTUP_HOME="/usr/local/rustup"
+ENV CARGO_HOME="/usr/local/cargo"
+ENV PATH="${CARGO_HOME}/bin:${PATH}"

 ARG PYTHON_LTO

@@ -1805,7 +1838,7 @@ ENV AIRFLOW_PIP_VERSION=${AIRFLOW_PIP_VERSION} \
     AIRFLOW_PREK_VERSION=${AIRFLOW_PREK_VERSION}

 # The PATH is needed for python to find installed and cargo to build the wheels
-ENV PATH="/usr/python/bin:/root/.local/bin:/root/.cargo/bin:${PATH}"
+ENV PATH="/usr/python/bin:/root/.local/bin:${PATH}"
 # Useful for creating a cache id based on the underlying architecture, preventing the use of cached python packages from
 # an incorrect architecture.
 ARG TARGETARCH
diff --git a/scripts/docker/install_os_dependencies.sh b/scripts/docker/install_os_dependencies.sh
index 95b1679a..f351d4fb 100644
--- a/scripts/docker/install_os_dependencies.sh
+++ b/scripts/docker/install_os_dependencies.sh
@@ -28,6 +28,8 @@ fi
 AIRFLOW_PYTHON_VERSION=${AIRFLOW_PYTHON_VERSION:-3.10.18}
 PYTHON_LTO=${PYTHON_LTO:-true}
 GOLANG_MAJOR_MINOR_VERSION=${GOLANG_MAJOR_MINOR_VERSION:-1.24.4}
+RUSTUP_DEFAULT_TOOLCHAIN=${RUSTUP_DEFAULT_TOOLCHAIN:-stable}
+RUSTUP_VERSION=${RUSTUP_VERSION:-1.29.0}
 COSIGN_VERSION=${COSIGN_VERSION:-3.0.5}

 if [[ "${1}" == "runtime" ]]; then
@@ -399,6 +401,33 @@ function install_golang() {
     rm -rf /usr/local/go && tar -C /usr/local -xzf go"${GOLANG_MAJOR_MINOR_VERSION}".linux.tar.gz
 }

+function install_rustup() {
+    local arch
+    arch="$(dpkg --print-architecture)"
+    declare -A rustup_targets=(
+        [amd64]="x86_64-unknown-linux-gnu"
+        [arm64]="aarch64-unknown-linux-gnu"
+    )
+    declare -A rustup_sha256s=(
+        # https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/{target}/rustup-init.sha256
+        [amd64]="4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10"
+        [arm64]="9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792"
+    )
+    local target="${rustup_targets[${arch}]}"
+    local rustup_sha256="${rustup_sha256s[${arch}]}"
+    if [[ -z "${target}" ]]; then
+        echo "Unsupported architecture for rustup: ${arch}"
+        exit 1
+    fi
+    curl --proto '=https' --tlsv1.2 -sSf \
+        "https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/${target}/rustup-init" \
+        -o /tmp/rustup-init
+    echo "${rustup_sha256}  /tmp/rustup-init" | sha256sum --check
+    chmod +x /tmp/rustup-init
+    /tmp/rustup-init -y --default-toolchain "${RUSTUP_DEFAULT_TOOLCHAIN}"
+    rm -f /tmp/rustup-init
+}
+
 function apt_clean() {
     apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
     rm -rf /var/lib/apt/lists/* /var/log/*
@@ -414,6 +443,7 @@ else
     install_debian_dev_dependencies
     install_python
     install_additional_dev_dependencies
+    install_rustup
     if [[ "${INSTALLATION_TYPE}" == "CI" ]]; then
         install_golang
     fi
PATCH

echo "Patch applied successfully"
