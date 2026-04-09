#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'clientPort' packages/react-devtools-core/src/standalone.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Reset files to original state
git checkout -- packages/react-devtools-core/src/backend.js \
    packages/react-devtools-core/src/standalone.js \
    packages/react-devtools/app.html \
    packages/react-devtools/preload.js

python3 << 'PYTHON'
import re

# ============================================================
# backend.js
# ============================================================
with open('packages/react-devtools-core/src/backend.js', 'r') as f:
    content = f.read()

# 1. Add path?: string to ConnectOptions type (after nativeStyleEditorValidAttributes)
content = content.replace(
    'nativeStyleEditorValidAttributes?: $ReadOnlyArray<string>,\n   port',
    'nativeStyleEditorValidAttributes?: $ReadOnlyArray<string>,\n  path?: string,\n   port'
)

# 2. Add path = '' to destructuring (after nativeStyleEditorValidAttributes)
content = content.replace(
    'nativeStyleEditorValidAttributes,\n    useHttps = false,',
    'nativeStyleEditorValidAttributes,\n    path = \'\',\n    useHttps = false,'
)

# 3. Add prefixedPath after protocol
content = content.replace(
    "const protocol = useHttps ? 'wss' : 'ws';\n  let retryTimeoutID",
    "const protocol = useHttps ? 'wss' : 'ws';\n  const prefixedPath = path !== '' && !path.startsWith('/') ? '/' + path : path;\n  let retryTimeoutID"
)

# 4. Update uri
content = content.replace(
    "const uri = protocol + '://' + host + ':' + port;",
    "const uri = protocol + '://' + host + ':' + port + prefixedPath;"
)

with open('packages/react-devtools-core/src/backend.js', 'w') as f:
    f.write(content)

print('backend.js updated')

# ============================================================
# standalone.js
# ============================================================
with open('packages/react-devtools-core/src/standalone.js', 'r') as f:
    content = f.read()

# 1. Add ClientOptions type after LoggerOptions
old_logger = '''type LoggerOptions = {
  surface?: ?string,
};'''
new_logger = '''type LoggerOptions = {
  surface?: ?string,
};

type ClientOptions = {
  host?: string,
  port?: number,
  useHttps?: boolean,
};'''
content = content.replace(old_logger, new_logger)

# 2. Add parameters to startServer
old_params = '''function startServer(
  port: number = 8097,
  host: string = 'localhost',
  httpsOptions?: ServerOptions,
  loggerOptions?: LoggerOptions,
): {close(): void} {'''
new_params = '''function startServer(
  port: number = 8097,
  host: string = 'localhost',
  httpsOptions?: ServerOptions,
  loggerOptions?: LoggerOptions,
  path?: string,
  clientOptions?: ClientOptions,
): {close(): void} {'''
content = content.replace(old_params, new_params)

# 3. Update first retry handler (server.on error)
old_retry1 = '''server.on('error', (event: $FlowFixMe) => {
    onError(event);
    log.error('Failed to start the DevTools server', event);
    startServerTimeoutID = setTimeout(() => startServer(port), 1000);
  });'''
new_retry1 = '''server.on('error', (event: $FlowFixMe) => {
    onError(event);
    log.error('Failed to start the DevTools server', event);
    startServerTimeoutID = setTimeout(
      () =>
        startServer(
          port,
          host,
          httpsOptions,
          loggerOptions,
          path,
          clientOptions,
        ),
      1000,
    );
  });'''
content = content.replace(old_retry1, new_retry1)

# 4. Add client override variables before response.end
old_response = '''    const componentFiltersString = JSON.stringify(getSavedComponentFilters());

    response.end('''
new_response = '''    const componentFiltersString = JSON.stringify(getSavedComponentFilters());

    // Client overrides: when connecting through a reverse proxy, the client
    // may need to connect to a different host/port/protocol than the server.
    const clientHost = clientOptions?.host ?? host;
    const clientPort = clientOptions?.port ?? port;
    const clientUseHttps = clientOptions?.useHttps ?? useHttps;

    response.end('''
content = content.replace(old_response, new_response)

# 5. Update the connectToDevTools template
# The template spans multiple lines, so we need a more complex replacement
# Original: `ReactDevToolsBackend.connectToDevTools({port: ${port}, host: '${host}', useHttps: ${
#           useHttps ? 'true' : 'false'
#         }});
#         `,
old_template = '''`ReactDevToolsBackend.connectToDevTools({port: ${port}, host: '${host}', useHttps: ${
          useHttps ? 'true' : 'false'
        }});
        `,'''
new_template = '''`ReactDevToolsBackend.connectToDevTools({port: ${clientPort}, host: '${clientHost}', useHttps: ${
          clientUseHttps ? 'true' : 'false'
        }${path != null ? `, path: '${path}'` : ''}});
        `,'''
content = content.replace(old_template, new_template)

# 6. Update second retry handler (httpServer.on error)
old_retry2 = '''httpServer.on('error', (event: $FlowFixMe) => {
    onError(event);
    statusListener('Failed to start the server.', 'error');
    startServerTimeoutID = setTimeout(() => startServer(port), 1000);
  });'''
new_retry2 = '''httpServer.on('error', (event: $FlowFixMe) => {
    onError(event);
    statusListener('Failed to start the server.', 'error');
    startServerTimeoutID = setTimeout(
      () =>
        startServer(
          port,
          host,
          httpsOptions,
          loggerOptions,
          path,
          clientOptions,
        ),
      1000,
    );
  });'''
content = content.replace(old_retry2, new_retry2)

with open('packages/react-devtools-core/src/standalone.js', 'w') as f:
    f.write(content)

print('standalone.js updated')

# ============================================================
# app.html
# ============================================================
with open('packages/react-devtools/app.html', 'r') as f:
    content = f.read()

# 1. Update readEnv destructuring
content = content.replace(
    "const {options, useHttps, host, protocol, port} = readEnv();",
    "const {options, useHttps, host, protocol, port, path, clientHost, clientPort, clientUseHttps} = readEnv();"
)

# 2. Update server variables
old_vars = '''const localIp = ip.address();
      const defaultPort = (port === 443 && useHttps) || (port === 80 && !useHttps);
      const server = defaultPort ? `${protocol}://${host}` : `${protocol}://${host}:${port}`;
      const serverIp = defaultPort ? `${protocol}://${localIp}` : `${protocol}://${localIp}:${port}`;'''
new_vars = '''const localIp = ip.address();

      // Effective values for display URLs: client overrides take precedence over server values.
      const effectiveHost = clientHost != null ? clientHost : host;
      const effectivePort = clientPort != null ? clientPort : port;
      const effectiveUseHttps = clientUseHttps != null ? clientUseHttps : useHttps;
      const effectiveProtocol = effectiveUseHttps ? 'https' : 'http';
      const defaultPort = (effectivePort === 443 && effectiveUseHttps) || (effectivePort === 80 && !effectiveUseHttps);
      const pathStr = path != null ? path : '';
      const server = defaultPort ? `${effectiveProtocol}://${effectiveHost}${pathStr}` : `${effectiveProtocol}://${effectiveHost}:${effectivePort}${pathStr}`;
      const serverIp = defaultPort ? `${effectiveProtocol}://${localIp}${pathStr}` : `${effectiveProtocol}://${localIp}:${effectivePort}${pathStr}`;'''
content = content.replace(old_vars, new_vars)

# 3. Update startServer call
content = content.replace(
    ".startServer(port, host, options);",
    ".startServer(port, host, options, undefined, path, {host: clientHost, port: clientPort, useHttps: clientUseHttps});"
)

with open('packages/react-devtools/app.html', 'w') as f:
    f.write(content)

print('app.html updated')

# ============================================================
# preload.js
# ============================================================
with open('packages/react-devtools/preload.js', 'r') as f:
    content = f.read()

old_return = '''return {options, useHttps, host, protocol, port};'''
new_return = '''const path = process.env.REACT_DEVTOOLS_PATH || undefined;
    const clientHost = process.env.REACT_DEVTOOLS_CLIENT_HOST || undefined;
    const clientPort = process.env.REACT_DEVTOOLS_CLIENT_PORT
      ? +process.env.REACT_DEVTOOLS_CLIENT_PORT
      : undefined;
    const clientUseHttps =
      process.env.REACT_DEVTOOLS_CLIENT_USE_HTTPS === 'true' ? true : undefined;
    return {
      options,
      useHttps,
      host,
      protocol,
      port,
      path,
      clientHost,
      clientPort,
      clientUseHttps,
    };'''
content = content.replace(old_return, new_return)

with open('packages/react-devtools/preload.js', 'w') as f:
    f.write(content)

print('preload.js updated')

PYTHON

echo "All files updated successfully."
