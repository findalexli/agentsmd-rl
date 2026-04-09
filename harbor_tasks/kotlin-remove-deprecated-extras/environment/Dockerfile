FROM eclipse-temurin:17-jdk-jammy

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip git curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
ENV KOTLIN_VERSION=2.0.21
RUN curl -sL "https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VERSION}/kotlin-compiler-${KOTLIN_VERSION}.zip" -o /tmp/kotlinc.zip && \
    unzip -q /tmp/kotlinc.zip -d /opt/ && \
    rm /tmp/kotlinc.zip && \
    ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin

# Download test dependencies (JUnit 4 + hamcrest + kotlin-test)
RUN mkdir -p /workspace/lib && \
    curl -sL "https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar" -o /workspace/lib/junit.jar && \
    curl -sL "https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar" -o /workspace/lib/hamcrest.jar && \
    cp /opt/kotlinc/lib/kotlin-stdlib.jar /workspace/lib/ && \
    cp /opt/kotlinc/lib/kotlin-test.jar /workspace/lib/ && \
    curl -sL "https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-test-junit/${KOTLIN_VERSION}/kotlin-test-junit-${KOTLIN_VERSION}.jar" -o /workspace/lib/kotlin-test-junit.jar && \
    curl -sL "https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-stdlib/${KOTLIN_VERSION}/kotlin-stdlib-${KOTLIN_VERSION}.jar" -o /workspace/lib/kotlin-stdlib.jar && \
    curl -sL "https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-test/${KOTLIN_VERSION}/kotlin-test-${KOTLIN_VERSION}.jar" -o /workspace/lib/kotlin-test.jar

# Download source files from the kotlin-tooling-core module
ENV BASE_COMMIT=95085a77af52e78028044f0ea5404803232ad697
ENV BASE_URL=https://raw.githubusercontent.com/JetBrains/kotlin/${BASE_COMMIT}

RUN mkdir -p /workspace/kotlin/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core && \
    mkdir -p /workspace/kotlin/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core && \
    mkdir -p /workspace/kotlin/build && \
    mkdir -p /logs/verifier

# Download main source files
RUN for f in Extras.kt ExtrasImpl.kt ExtrasProperty.kt ExtrasUtils.kt HasExtras.kt Interner.kt KotlinToolingVersion.kt UnsafeApi.kt closure.kt typeUtils.kt; do \
        curl -sL "${BASE_URL}/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/$f" \
            -o "/workspace/kotlin/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/$f"; \
    done

# Download test source files
RUN for f in ClosureTest.kt ExtrasIdFromStringTest.kt ExtrasPropertyTest.kt ExtrasSerializableTest.kt ExtrasTest.kt InternerTest.kt KotlinToolingVersionTest.kt TypeTest.kt; do \
        curl -sL "${BASE_URL}/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/$f" \
            -o "/workspace/kotlin/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/$f"; \
    done

# Initialize git repo for patch application
RUN cd /workspace/kotlin && \
    git init && \
    git config user.email "bot@example.com" && \
    git config user.name "Bot" && \
    git add -A && \
    git commit -m "Base commit: 95085a77af52e78028044f0ea5404803232ad697"

WORKDIR /workspace/kotlin

ENV LIB_DIR=/workspace/lib
ENV BUILD_DIR=/workspace/kotlin/build
ENV MAIN_SRC=/workspace/kotlin/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core
ENV TEST_SRC=/workspace/kotlin/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core
