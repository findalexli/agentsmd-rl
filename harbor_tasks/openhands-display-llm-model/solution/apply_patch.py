import os

REPO = '/workspace/OpenHands'
os.chdir(REPO)

# 1. Update ConversationInfo dataclass
with open('openhands/server/data_models/conversation_info.py', 'r') as f:
    content = f.read()

if 'llm_model:' not in content:
    content = content.rstrip()
    content = content.replace(
        'sandbox_id: str | None = None',
        'sandbox_id: str | None = None\n    llm_model: str | None = None'
    )
    with open('openhands/server/data_models/conversation_info.py', 'w') as f:
        f.write(content)
    print('Updated conversation_info.py')

# 2. Update manage_conversations.py
with open('openhands/server/routes/manage_conversations.py', 'r') as f:
    content = f.read()

if 'llm_model=app_conversation.llm_model' not in content:
    content = content.replace(
        'sandbox_id=app_conversation.sandbox_id,',
        'sandbox_id=app_conversation.sandbox_id,\n        llm_model=app_conversation.llm_model,'
    )
    with open('openhands/server/routes/manage_conversations.py', 'w') as f:
        f.write(content)
    print('Updated manage_conversations.py')

# 3. Update TypeScript types
with open('frontend/src/api/open-hands.types.ts', 'r') as f:
    content = f.read()

if 'llm_model?:' not in content:
    content = content.replace(
        'export interface Conversation {',
        'export interface Conversation {\n  llm_model?: string | null;'
    )
    with open('frontend/src/api/open-hands.types.ts', 'w') as f:
        f.write(content)
    print('Updated open-hands.types.ts')

# 4. Update ConversationCard
with open('frontend/src/components/features/conversation-panel/conversation-card/conversation-card.tsx', 'r') as f:
    content = f.read()

if 'llmModel?:' not in content:
    # Add to interface
    content = content.replace(
        'onContextMenuToggle?: (isOpen: boolean) => void;',
        'onContextMenuToggle?: (isOpen: boolean) => void;\n  llmModel?: string | null;'
    )
    # Add to destructuring
    content = content.replace(
        'onContextMenuToggle,\n}: ConversationCardProps',
        'onContextMenuToggle,\n  llmModel,\n}: ConversationCardProps'
    )
    # Add to footer specifically - be more specific to match only footer
    content = content.replace(
        '<ConversationCardFooter\n        selectedRepository={selectedRepository}',
        '<ConversationCardFooter\n        selectedRepository={selectedRepository}\n        llmModel={llmModel}'
    )
    with open('frontend/src/components/features/conversation-panel/conversation-card/conversation-card.tsx', 'w') as f:
        f.write(content)
    print('Updated conversation-card.tsx')

# 5. Update ConversationCardFooter
with open('frontend/src/components/features/conversation-panel/conversation-card/conversation-card-footer.tsx', 'r') as f:
    content = f.read()

if 'CircuitIcon' not in content:
    content = content.replace(
        'import { ConversationStatus } from "#/types/conversation-status";',
        'import { ConversationStatus } from "#/types/conversation-status";\nimport CircuitIcon from "#/icons/u-circuit.svg?react";'
    )
    content = content.replace(
        'conversationStatus?: ConversationStatus;\n}',
        'conversationStatus?: ConversationStatus;\n  llmModel?: string | null;\n}'
    )
    content = content.replace(
        'conversationStatus,\n}: ConversationCardFooterProps',
        'conversationStatus,\n  llmModel,\n}: ConversationCardFooterProps'
    )
    
    old_section = '''      {(createdAt ?? lastUpdatedAt) && (
        <p className="text-xs text-[#A3A3A3] flex-1 text-right">
          <time>
            {`${formatTimeDelta(lastUpdatedAt ?? createdAt)} ${t(I18nKey.CONVERSATION$AGO)}`}
          </time>
        </p>
      )}'''
    
    new_section = '''      <div className="flex items-center gap-2 flex-1 justify-end">
        {llmModel && (
          <span
            className="text-xs text-[#A3A3A3] max-w-[120px] flex items-center gap-1 overflow-hidden"
            title={llmModel}
            data-testid="conversation-card-llm-model"
          >
            <CircuitIcon width={12} height={12} className="shrink-0" />
            <span className="truncate">{llmModel}</span>
          </span>
        )}
        {(createdAt ?? lastUpdatedAt) && (
          <p className="text-xs text-[#A3A3A3] text-right">
            <time>
              {`${formatTimeDelta(lastUpdatedAt ?? createdAt)} ${t(I18nKey.CONVERSATION$AGO)}`}
            </time>
          </p>
        )}
      </div>'''
    
    if old_section in content:
        content = content.replace(old_section, new_section)
    
    with open('frontend/src/components/features/conversation-panel/conversation-card/conversation-card-footer.tsx', 'w') as f:
        f.write(content)
    print('Updated conversation-card-footer.tsx')

# 6. Update ConversationPanel
with open('frontend/src/components/features/conversation-panel/conversation-panel.tsx', 'r') as f:
    content = f.read()

if 'llmModel={project.llm_model}' not in content:
    content = content.replace(
        'onContextMenuToggle={(isOpen) =>\n              setOpenContextMenuId(isOpen ? project.conversation_id : null)\n            }\n          />',
        'onContextMenuToggle={(isOpen) =>\n              setOpenContextMenuId(isOpen ? project.conversation_id : null)\n            }\n            llmModel={project.llm_model}\n          />'
    )
    with open('frontend/src/components/features/conversation-panel/conversation-panel.tsx', 'w') as f:
        f.write(content)
    print('Updated conversation-panel.tsx')

# 7. Update conversation-name.tsx
with open('frontend/src/components/features/conversation/conversation-name.tsx', 'r') as f:
    content = f.read()

if 'conversation.llm_model' not in content:
    content = content.replace(
        'import { ConversationVersionBadge } from "../conversation-panel/conversation-card/conversation-version-badge";',
        'import { ConversationVersionBadge } from "../conversation-panel/conversation-card/conversation-version-badge";\nimport CircuitIcon from "#/icons/u-circuit.svg?react";'
    )
    old_block = '''        {titleMode !== "edit" && (
          <ConversationVersionBadge
            version={conversation.conversation_version}
          />
        )}

        {titleMode !== "edit" && ('''
    
    new_block = '''        {titleMode !== "edit" && (
          <ConversationVersionBadge
            version={conversation.conversation_version}
          />
        )}

        {titleMode !== "edit" && conversation.llm_model && (
          <span
            className="text-xs text-[#A3A3A3] max-w-[150px] flex items-center gap-1 overflow-hidden"
            title={conversation.llm_model}
            data-testid="conversation-name-llm-model"
          >
            <CircuitIcon width={12} height={12} className="shrink-0" />
            <span className="truncate">{conversation.llm_model}</span>
          </span>
        )}

        {titleMode !== "edit" && ('''
    
    if old_block in content:
        content = content.replace(old_block, new_block)
    
    with open('frontend/src/components/features/conversation/conversation-name.tsx', 'w') as f:
        f.write(content)
    print('Updated conversation-name.tsx')

# 8. Update recent-conversation.tsx
with open('frontend/src/components/features/home/recent-conversations/recent-conversation.tsx', 'r') as f:
    content = f.read()

if 'conversation.llm_model' not in content:
    content = content.replace(
        'import RepoForkedIcon from "#/icons/repo-forked.svg?react";',
        'import RepoForkedIcon from "#/icons/repo-forked.svg?react";\nimport CircuitIcon from "#/icons/u-circuit.svg?react";'
    )
    old_block = '{(conversation.created_at || conversation.last_updated_at) && ('
    new_block = '''{conversation.llm_model && (
          <span
            className="max-w-[120px] flex items-center gap-1 overflow-hidden"
            title={conversation.llm_model}
            data-testid="recent-conversation-llm-model"
          >
            <CircuitIcon width={12} height={12} className="shrink-0" />
            <span className="truncate">{conversation.llm_model}</span>
          </span>
        )}
        {(conversation.created_at || conversation.last_updated_at) && ('''
    content = content.replace(old_block, new_block)
    with open('frontend/src/components/features/home/recent-conversations/recent-conversation.tsx', 'w') as f:
        f.write(content)
    print('Updated recent-conversation.tsx')

print('\nAll patches applied successfully!')
