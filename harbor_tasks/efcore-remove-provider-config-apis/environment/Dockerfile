FROM mcr.microsoft.com/dotnet/nightly/sdk:11.0.100-preview.3

ENV DEBIAN_FRONTEND=noninteractive \
    DOTNET_NOLOGO=1 \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    NUGET_XMLDOC_MODE=skip

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

WORKDIR /workspace

ARG REPO_URL=https://github.com/dotnet/efcore.git
ARG BASE_COMMIT=79c8ce77076dd5cb24e96971a6ef5dd587777104

RUN git clone --filter=blob:none ${REPO_URL} efcore && \
    cd efcore && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/efcore

# Replace global.json with one pointing at the SDK we have installed.
# rollForward: latestMajor allows the available preview-3 SDK to satisfy a request for preview-1.
RUN printf '%s\n' \
    '{' \
    '  "sdk": {' \
    '    "version": "11.0.100-preview.3.26207.106",' \
    '    "allowPrerelease": true,' \
    '    "rollForward": "latestMajor"' \
    '  },' \
    '  "msbuild-sdks": {' \
    '    "Microsoft.DotNet.Arcade.Sdk": "11.0.0-beta.26151.104",' \
    '    "Microsoft.DotNet.Helix.Sdk": "11.0.0-beta.26151.104",' \
    '    "Microsoft.Build.NoTargets": "3.7.134"' \
    '  }' \
    '}' > global.json

# Pre-restore + build EFCore.Tests at base. This warms the NuGet cache and
# builds dependent projects, so subsequent incremental builds are fast.
RUN dotnet restore test/EFCore.Tests/EFCore.Tests.csproj && \
    dotnet build test/EFCore.Tests/EFCore.Tests.csproj -v minimal

RUN mkdir -p /logs/verifier
