import { describe, it, expect } from 'vitest';
import { webSearchTool } from '../src/tools';
import { converTool } from '../src/openaiResponsesModel';

describe('scaffold: web search externalWebAccess option', () => {
  it('webSearchTool preserves explicit false external web access', () => {
    const t = webSearchTool({ externalWebAccess: false } as any);
    const providerData = (t as any).providerData;
    expect(providerData).toBeDefined();
    expect(providerData.external_web_access).toBe(false);
  });

  it('webSearchTool preserves explicit true external web access', () => {
    const t = webSearchTool({ externalWebAccess: true } as any);
    const providerData = (t as any).providerData;
    expect(providerData).toBeDefined();
    expect(providerData.external_web_access).toBe(true);
  });

  it('webSearchTool omits external_web_access when option not provided', () => {
    const t = webSearchTool({});
    const providerData = (t as any).providerData;
    expect(providerData).toBeDefined();
    expect('external_web_access' in providerData).toBe(false);
  });

  it('converTool forwards external_web_access=false on web_search', () => {
    const result = converTool({
      type: 'hosted_tool',
      providerData: {
        type: 'web_search',
        search_context_size: 'medium',
        external_web_access: false,
      },
    } as any);
    expect((result.tool as any).type).toBe('web_search');
    expect((result.tool as any).external_web_access).toBe(false);
  });

  it('converTool forwards external_web_access=true on web_search', () => {
    const result = converTool({
      type: 'hosted_tool',
      providerData: {
        type: 'web_search',
        search_context_size: 'medium',
        external_web_access: true,
      },
    } as any);
    expect((result.tool as any).type).toBe('web_search');
    expect((result.tool as any).external_web_access).toBe(true);
  });

  it('converTool omits external_web_access when not present in providerData', () => {
    const result = converTool({
      type: 'hosted_tool',
      providerData: {
        type: 'web_search',
        search_context_size: 'medium',
      },
    } as any);
    expect((result.tool as any).type).toBe('web_search');
    expect('external_web_access' in (result.tool as any)).toBe(false);
  });
});
