FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install JDK 17 from Eclipse Adoptium
RUN curl -sL "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz" | tar -xz -C /opt && \
    ln -s /opt/jdk-17.0.13+11 /opt/jdk && \
    echo 'export PATH=/opt/jdk/bin:$PATH' >> /etc/profile

ENV JAVA_HOME=/opt/jdk
ENV PATH="/opt/jdk/bin:$PATH"

# Install Gradle 8.14.3
RUN curl -sL "https://services.gradle.org/distributions/gradle-8.14.3-bin.zip" -o /tmp/gradle.zip && \
    unzip -q /tmp/gradle.zip -d /opt && \
    ln -s /opt/gradle-8.14.3/bin/gradle /usr/local/bin/gradle && \
    rm /tmp/gradle.zip

WORKDIR /workspace

RUN git clone --depth=1 --filter=blob:none https://github.com/continuedev/continue.git

WORKDIR /workspace/continue

RUN git fetch origin 7f3254013710ef44867d35fa8718b7b6df40c507 && \
    git checkout 7f3254013710ef44867d35fa8718b7b6df40c507

RUN mkdir -p /logs/verifier

CMD ["python3", "-m", "http.server", "8080"]