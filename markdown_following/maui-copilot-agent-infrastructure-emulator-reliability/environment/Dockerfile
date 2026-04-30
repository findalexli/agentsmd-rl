FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install git, curl, and PowerShell (needed to test .ps1 scripts)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates gnupg && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    chmod a+r /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends powershell && \
    rm -rf /var/lib/apt/lists/*

# dotnet/maui is huge — shallow clone at base commit
RUN git init /workspace/maui && \
    cd /workspace/maui && \
    git remote add origin https://github.com/dotnet/maui.git && \
    git fetch --depth=1 origin c1e543e1f116911ffb934e60c79bb501ea1814e3 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
