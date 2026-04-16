#!/bin/bash
set -e

cd /workspace/playwright

# Check if already patched
if grep -q "network" packages/playwright/src/mcp/terminal/command.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Create the route.ts tool file
cat > packages/playwright/src/mcp/browser/tools/route.ts << 'ROUTE_EOF'
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { z } from 'playwright-core/lib/mcpBundle';
import { defineTool } from './tool';

import type * as playwright from 'playwright-core';
import type { RouteEntry } from '../context';

const route = defineTool({
  capability: 'core',

  schema: {
    name: 'browser_route',
    title: 'Mock network requests',
    description: 'Set up a route to mock network requests matching a URL pattern',
    inputSchema: z.object({
      pattern: z.string().describe('URL pattern to match (e.g., "**/api/users", "**/*.{png,jpg}")'),
      status: z.number().optional().describe('HTTP status code to return (default: 200)'),
      body: z.string().optional().describe('Response body (text or JSON string)'),
      contentType: z.string().optional().describe('Content-Type header (e.g., "application/json", "text/html")'),
      headers: z.array(z.string()).optional().describe('Headers to add in "Name: Value" format'),
      removeHeaders: z.string().optional().describe('Comma-separated list of header names to remove from request'),
    }),
    type: 'action',
  },

  handle: async (context, params, response) => {
    const addHeaders = params.headers ? Object.fromEntries(params.headers.map(h => {
      const colonIndex = h.indexOf(':');
      return [h.substring(0, colonIndex).trim(), h.substring(colonIndex + 1).trim()];
    })) : undefined;
    const removeHeaders = params.removeHeaders ? params.removeHeaders.split(',').map(h => h.trim()) : undefined;

    const handler = async (route: playwright.Route) => {
      // If we have a body or status, fulfill with mock response
      if (params.body !== undefined || params.status !== undefined) {
        await route.fulfill({
          status: params.status ?? 200,
          contentType: params.contentType,
          body: params.body,
        });
        return;
      }

      // Otherwise, modify headers and continue
      const headers = { ...route.request().headers() };
      if (addHeaders) {
        for (const [key, value] of Object.entries(addHeaders))
          headers[key] = value as string;
      }
      if (removeHeaders) {
        for (const header of removeHeaders)
          delete headers[header.toLowerCase()];
      }
      await route.continue({ headers });
    };

    const entry: RouteEntry = {
      pattern: params.pattern,
      status: params.status,
      body: params.body,
      contentType: params.contentType,
      addHeaders,
      removeHeaders,
      handler,
    };

    await context.addRoute(entry);
    response.addTextResult(`Route added for pattern: ${params.pattern}`);
    response.addCode(`await page.context().route('${params.pattern}', async route => { /* route handler */ });`);
  },
});

const routeList = defineTool({
  capability: 'core',

  schema: {
    name: 'browser_route_list',
    title: 'List network routes',
    description: 'List all active network routes',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (context, params, response) => {
    const routes = context.routes();
    if (routes.length === 0) {
      response.addTextResult('No active routes');
      return;
    }

    const lines: string[] = [];
    for (let i = 0; i < routes.length; i++) {
      const route = routes[i];
      const details: string[] = [];
      if (route.status !== undefined)
        details.push(`status=${route.status}`);
      if (route.body !== undefined)
        details.push(`body=${route.body.length > 50 ? route.body.substring(0, 50) + '...' : route.body}`);
      if (route.contentType)
        details.push(`contentType=${route.contentType}`);
      if (route.addHeaders)
        details.push(`addHeaders=${JSON.stringify(route.addHeaders)}`);
      if (route.removeHeaders)
        details.push(`removeHeaders=${route.removeHeaders.join(',')}`);

      const detailsStr = details.length ? ` (${details.join(', ')})` : '';
      lines.push(`${i + 1}. ${route.pattern}${detailsStr}`);
    }
    response.addTextResult(lines.join('\n'));
  },
});

const unroute = defineTool({
  capability: 'core',

  schema: {
    name: 'browser_unroute',
    title: 'Remove network routes',
    description: 'Remove network routes matching a pattern (or all routes if no pattern specified)',
    inputSchema: z.object({
      pattern: z.string().optional().describe('URL pattern to unroute (omit to remove all routes)'),
    }),
    type: 'action',
  },

  handle: async (context, params, response) => {
    const removed = await context.removeRoute(params.pattern);
    if (params.pattern)
      response.addTextResult(`Removed ${removed} route(s) for pattern: ${params.pattern}`);
    else
      response.addTextResult(`Removed all ${removed} route(s)`);
  },
});

export default [
  route,
  routeList,
  unroute,
];
ROUTE_EOF

# Patch context.ts - add RouteEntry type and route methods
sed -i '/type ContextOptions = {/,/^};$/{
/^};$/a\
\
export type RouteEntry = {\
  pattern: string;\
  status?: number;\
  body?: string;\
  contentType?: string;\
  addHeaders?: Record<string, string>;\
  removeHeaders?: string[];\
  handler: (route: playwright.Route) => Promise<void>;\
};
}' packages/playwright/src/mcp/browser/context.ts

# Add _routes array to Context class
sed -i '/private _clientInfo: ClientInfo;/a\  private _routes: RouteEntry[] = [];' packages/playwright/src/mcp/browser/context.ts

# Add route methods after ensureBrowserContext method
sed -i '/this._closeBrowserContextPromise = undefined;/a\
\
  routes(): RouteEntry[] {\
    return this._routes;\
  }\
\
  async addRoute(entry: RouteEntry): Promise<void> {\
    const { browserContext } = await this._ensureBrowserContext();\
    await browserContext.route(entry.pattern, entry.handler);\
    this._routes.push(entry);\
  }\
\
  async removeRoute(pattern?: string): Promise<number> {\
    if (!this._browserContextPromise)\
      return 0;\
    const { browserContext } = await this._browserContextPromise;\
    let removed = 0;\
    if (pattern) {\
      const toRemove = this._routes.filter(r => r.pattern === pattern);\
      for (const route of toRemove)\
        await browserContext.unroute(route.pattern, route.handler);\
      this._routes = this._routes.filter(r => r.pattern !== pattern);\
      removed = toRemove.length;\
    } else {\
      for (const route of this._routes)\
        await browserContext.unroute(route.pattern, route.handler);\
      removed = this._routes.length;\
      this._routes = [];\
    }\
    return removed;\
  }
' packages/playwright/src/mcp/browser/context.ts

# Register route tools in tools.ts
sed -i "/import pdf from '.\/tools\/pdf';/a\import route from '.\/tools\/route';" packages/playwright/src/mcp/browser/tools.ts
sed -i '/...pdf,/a\  ...route,' packages/playwright/src/mcp/browser/tools.ts

# Add 'network' category to command.ts
sed -i "s/export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'devtools' | 'session' | 'config' | 'install';/export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'network' | 'devtools' | 'session' | 'config' | 'install';/" packages/playwright/src/mcp/terminal/command.ts

# Add network commands to commands.ts - insert before sessionStorageClear
sed -i '/const sessionStorageClear = declareCommand({/,/^});$/{/^});$/a\
\
\/\/ Network\
\
const routeMock = declareCommand({\
  name: '\''route'\'',\
  description: '\''Mock network requests matching a URL pattern'\'',\
  category: '\''network'\'',\
  args: z.object({\
    pattern: z.string().describe('\''URL pattern to match (e.g., "**\/*\/api\/users")'\''),\
  }),\
  options: z.object({\
    status: z.number().optional().describe('\''HTTP status code (default: 200)'\''),\
    body: z.string().optional().describe('\''Response body (text or JSON string)'\''),\
    ['\''content-type'\'']: z.string().optional().describe('\''Content-Type header'\''),\
    header: z.union([z.string(), z.array(z.string())]).optional().transform(v => v ? (Array.isArray(v) ? v : [v]) : undefined).describe('\''Header to add in "Name: Value" format (repeatable)'\''),\
    ['\''remove-header'\'']: z.string().optional().describe('\''Comma-separated header names to remove'\''),\
  }),\
  toolName: '\''browser_route'\'',\
  toolParams: ({ pattern, status, body, ['\''content-type'\'']: contentType, header: headers, ['\''remove-header'\'']: removeHeaders }) => ({\
    pattern,\
    status,\
    body,\
    contentType,\
    headers,\
    removeHeaders,\
  }),\
});\
\
const routeList = declareCommand({\
  name: '\''route-list'\'',\
  description: '\''List all active network routes'\'',\
  category: '\''network'\'',\
  args: z.object({}),\
  toolName: '\''browser_route_list'\'',\
  toolParams: () => ({}),\
});\
\
const unroute = declareCommand({\
  name: '\''unroute'\'',\
  description: '\''Remove routes matching a pattern (or all routes)'\'',\
  category: '\''network'\'',\
  args: z.object({\
    pattern: z.string().optional().describe('\''URL pattern to unroute (omit to remove all)'\''),\
  }),\
  toolName: '\''browser_unroute'\'',\
  toolParams: ({ pattern }) => ({ pattern }),\
});
}' packages/playwright/src/mcp/terminal/commands.ts

# Add network commands to commandsArray - insert before config
sed -i '/sessionStorageClear,$/a\
\
  \/\/ network category\
  routeMock,\
  routeList,\
  unroute,' packages/playwright/src/mcp/terminal/commands.ts

# Add network category to helpGenerator.ts
sed -i "/{ name: 'storage', title: 'Storage' },/a\  { name: 'network', title: 'Network' }," packages/playwright/src/mcp/terminal/helpGenerator.ts

# Update SKILL.md with documentation changes
cat > .claude/skills/playwright-mcp-dev/SKILL.md << 'SKILL_EOF'
---
name: playwright-mcp-dev
description: Explains how to add and debug playwright MCP tools and CLI commands.
---

# MCP

## Adding MCP Tools
- Create a new tool in `packages/playwright/src/mcp/browser/tools/your-tool.ts`
- Register the tool in `packages/playwright/src/mcp/browser/tools.ts`
- Add ToolCapability in `packages/playwright/src/mcp/config.d.ts`
- Place new tests in `tests/mcp/mcp-<category>.spec.ts`

## Building
- Assume watch is running at all times, run lint to see type errors

## Testing
- Run tests as `npm run ctest-mcp <category>`
- Do not run test --debug

# CLI

## Adding commands
- CLI commands are based on MCP tools. Implement the corresponding MCP tool as per `Adding MCP Tools` section above, if needed.
- Add new CLI category for tool if needed:
  - Add Category in `packages/playwright/src/mcp/terminal/command.ts`
  - Update doc generator `packages/playwright/src/mcp/terminal/helpGenerator.ts`
- Register command in `packages/playwright/src/mcp/terminal/commands.ts`
- Update skill file at `packages/playwright/src/skill/SKILL.md` and references if necessary
  in `packages/playwright/src/skill/references/`
- Place new tests in `tests/mcp/cli-<category>.spec.ts`

## Building
- Assume watch is running at all times, run lint to see type errors

## Testing
- Run tests as `npm run ctest-mcp cli-<category>`
- Do not run test --debug

# Lint
- run `npm run flint` to lint everything before commit
SKILL_EOF

echo "Gold patch applied successfully"
