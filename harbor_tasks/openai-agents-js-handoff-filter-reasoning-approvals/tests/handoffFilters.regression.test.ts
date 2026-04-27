import { describe, test, expect } from 'vitest';
import { removeAllTools } from '../../src/extensions';
import {
  RunMessageOutputItem,
  RunReasoningItem,
  RunToolApprovalItem,
} from '../../src/items';
import type { AgentInputItem } from '../../src/types';
import type * as protocol from '../../src/types/protocol';
import { TEST_AGENT, fakeModelMessage } from '../stubs';

const reasoningItem: protocol.ReasoningItem = {
  type: 'reasoning',
  content: [{ type: 'input_text', text: 'thinking' }],
};

const hostedMcpApprovalRequest: protocol.HostedToolCallItem = {
  type: 'hosted_tool_call',
  id: 'approval-1',
  name: 'lookup_account',
  status: 'in_progress',
  providerData: {
    type: 'mcp_approval_request',
    id: 'approval-1',
    server_label: 'crm',
    name: 'lookup_account',
    arguments: '{}',
  },
};

describe('removeAllTools regression: reasoning + approval placeholders', () => {
  test('drops RunReasoningItem from preHandoffItems and newItems', () => {
    const message = new RunMessageOutputItem(
      fakeModelMessage('keep'),
      TEST_AGENT,
    );
    const reasoningRunItem = new RunReasoningItem(reasoningItem, TEST_AGENT);

    const result = removeAllTools({
      inputHistory: [],
      preHandoffItems: [message, reasoningRunItem],
      newItems: [reasoningRunItem],
    });

    expect(result.preHandoffItems).toStrictEqual([message]);
    expect(result.newItems).toStrictEqual([]);
  });

  test('drops RunToolApprovalItem placeholders from run collections', () => {
    const message = new RunMessageOutputItem(
      fakeModelMessage('keep'),
      TEST_AGENT,
    );
    const approvalRunItem = new RunToolApprovalItem(
      hostedMcpApprovalRequest,
      TEST_AGENT,
    );

    const result = removeAllTools({
      inputHistory: [],
      preHandoffItems: [message, approvalRunItem],
      newItems: [approvalRunItem, message],
    });

    expect(result.preHandoffItems).toStrictEqual([message]);
    expect(result.newItems).toStrictEqual([message]);
  });

  test('filters reasoning entries out of inputHistory arrays', () => {
    const userMessage = {
      type: 'message',
      role: 'user',
      content: [{ type: 'input_text', text: 'hello' }],
    } as AgentInputItem;
    const history: AgentInputItem[] = [userMessage, reasoningItem];

    const result = removeAllTools({
      inputHistory: history,
      preHandoffItems: [],
      newItems: [],
    });

    expect(result.inputHistory).toStrictEqual([userMessage]);
    expect(history).toHaveLength(2);
  });

  test('keeps non-tool, non-reasoning, non-approval items intact', () => {
    const message = new RunMessageOutputItem(
      fakeModelMessage('preserve me'),
      TEST_AGENT,
    );
    const userMessage = {
      type: 'message',
      role: 'user',
      content: [{ type: 'input_text', text: 'hi' }],
    } as AgentInputItem;

    const result = removeAllTools({
      inputHistory: [userMessage],
      preHandoffItems: [message],
      newItems: [message],
    });

    expect(result.inputHistory).toStrictEqual([userMessage]);
    expect(result.preHandoffItems).toStrictEqual([message]);
    expect(result.newItems).toStrictEqual([message]);
  });
});
