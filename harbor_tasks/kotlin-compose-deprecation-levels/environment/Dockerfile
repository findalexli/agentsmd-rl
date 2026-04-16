FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    openjdk-21-jdk \
    patch \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler for behavioral tests
RUN curl -L -o /tmp/kotlin-compiler.zip https://github.com/JetBrains/kotlin/releases/download/v2.0.21/kotlin-compiler-2.0.21.zip && \
    unzip -q /tmp/kotlin-compiler.zip -d /opt && \
    rm /tmp/kotlin-compiler.zip && \
    ln -sf /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    ln -sf /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Create workspace and logs directories
RUN mkdir -p /workspace/kotlin /logs/verifier

# Clone kotlin repo at base commit (blobless clone for speed with full tree structure)
# We need the full structure for Gradle to work, but can skip blob content
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git sparse-checkout init && \
    git sparse-checkout set \
        libraries/tools/kotlin-compose-compiler/ \
        libraries/tools/kotlin-gradle-plugin-integration-tests/ \
        libraries/tools/kotlin-gradle-plugin/ \
        libraries/tools/kotlin-gradle-plugin-api/ \
        plugins/compose/ \
        gradle/ \
        buildSrc/ \
        repo/gradle-settings-conventions/ \
        repo/gradle-build-conventions/ \
        build.gradle.kts \
        settings.gradle.kts \
        gradle.properties \
        .gitignore && \
    git fetch --depth 1 origin f94fe0faca67ca5a57db9421948cab80af1686b7 && \
    git checkout f94fe0faca67ca5a57db9421948cab80af1686b7

WORKDIR /workspace/kotlin

# Install Python dependencies for testing
RUN pip install pytest

# Create missing directories required by Gradle configuration
# The sparse checkout doesn't include these, but Gradle expects them to exist
RUN mkdir -p native/swift/sir-printer && \
    mkdir -p native/swift/sir && \
    mkdir -p native/swift/objc-bridge && \
    mkdir -p native/objc-visual-export && \
    mkdir -p compiler/util && \
    mkdir -p compiler/config && \
    mkdir -p "compiler/config.jvm" && \
    mkdir -p "compiler/config:configuration-keys-generator" && \
    mkdir -p "kotlin-util-io" && \
    mkdir -p "kotlin-util-klib" && \
    mkdir -p "kotlin-util-klib-metadata" && \
    mkdir -p "kotlin-util-klib-abi" && \
    mkdir -p daemon-common && \
    mkdir -p kotlin-daemon && \
    mkdir -p kotlin-daemon-client && \
    mkdir -p kotlin-daemon-tests && \
    mkdir -p kotlin-preloader && \
    mkdir -p kotlin-runner && \
    mkdir -p "compiler/arguments.common" && \
    mkdir -p "compiler/arguments" && \
    mkdir -p "compiler/container" && \
    mkdir -p "compiler/resolution.common" && \
    mkdir -p "compiler/resolution.common.jvm" && \
    mkdir -p "compiler/resolution" && \
    mkdir -p "compiler/serialization" && \
    mkdir -p "compiler/psi:psi-api" && \
    mkdir -p "compiler/psi:psi-impl" && \
    mkdir -p "compiler/psi:psi-utils" && \
    mkdir -p "compiler/psi:psi-frontend-utils" && \
    mkdir -p "compiler/psi:parser" && \
    mkdir -p "compiler/multiplatform-parsing" && \
    mkdir -p "compiler/frontend" && \
    mkdir -p "compiler/frontend.common" && \
    mkdir -p "compiler/frontend.common-psi" && \
    mkdir -p "compiler/frontend.java" && \
    mkdir -p "compiler/frontend:cfg" && \
    mkdir -p "kotlin-compiler-runner-unshaded" && \
    mkdir -p "kotlin-compiler-runner" && \
    mkdir -p "compiler/ir.tree" && \
    mkdir -p "compiler/ir.tree:tree-generator" && \
    mkdir -p "compiler/ir.psi2ir" && \
    mkdir -p "compiler/ir.objcinterop" && \
    mkdir -p "compiler/ir.backend.common" && \
    mkdir -p "compiler/ir.backend.native" && \
    mkdir -p "compiler/ir.actualization" && \
    mkdir -p "compiler/ir.serialization.common" && \
    mkdir -p "compiler/ir.serialization.jvm" && \
    mkdir -p "compiler/ir.serialization.js" && \
    mkdir -p "compiler/ir.serialization.native" && \
    mkdir -p "compiler/ir.serialization.jklib"

# Pre-download Gradle wrapper to avoid network issues during tests
RUN ./gradlew --version || true
