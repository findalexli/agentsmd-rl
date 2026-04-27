FROM eclipse-temurin:17.0.13_11-jdk-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN mkdir -p selenium && cd selenium \
    && git init -q \
    && git remote add origin https://github.com/SeleniumHQ/selenium.git \
    && git config core.sparseCheckout true \
    && printf 'java/src/org/openqa/selenium/Keys.java\n' > .git/info/sparse-checkout \
    && git fetch --depth 1 origin 99a25472c4da3b39a9f049e1ac07086e3bf508f5 \
    && git checkout FETCH_HEAD \
    && rm -rf .git

RUN mkdir -p /opt/keys_stubs/org/jspecify/annotations \
    && printf 'package org.jspecify.annotations;\nimport java.lang.annotation.*;\n@Retention(RetentionPolicy.RUNTIME)\n@Target({ElementType.TYPE_USE, ElementType.METHOD, ElementType.PARAMETER, ElementType.FIELD, ElementType.LOCAL_VARIABLE})\npublic @interface Nullable {}\n' > /opt/keys_stubs/org/jspecify/annotations/Nullable.java

RUN mkdir -p /logs/verifier
