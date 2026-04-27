FROM eclipse-temurin:21.0.5_11-jdk

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        unzip \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# pytest is part of the test harness, not the agent's responsibility. Pre-install
# pinned versions so test.sh can run offline. --break-system-packages because the
# base image follows PEP 668 (externally managed); we do not need a venv inside
# this image.
RUN pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4

# Pinned dependency jars from Maven Central. selenium-api 4.41.0 mirrors
# the API surface used by the json package at the base commit (4.41.0-SNAPSHOT).
# jspecify 1.0.0 supplies the @Nullable / @NullMarked annotations.
ENV LIBS=/workspace/libs
RUN mkdir -p $LIBS \
 && curl -fsSL -o $LIBS/selenium-api-4.41.0.jar \
      https://repo1.maven.org/maven2/org/seleniumhq/selenium/selenium-api/4.41.0/selenium-api-4.41.0.jar \
 && curl -fsSL -o $LIBS/jspecify-1.0.0.jar \
      https://repo1.maven.org/maven2/org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar

# Clone Selenium at the base commit (parent of merge commit for PR 17038).
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git /workspace/selenium \
 && cd /workspace/selenium \
 && git checkout 079453e88d36562132f1052cf921eba913c77b1b

WORKDIR /workspace/selenium

RUN mkdir -p /logs/verifier
