# Task: Display LLM Model on Conversation Cards and Header

## Problem

Users cannot see which LLM model was used for each conversation. The backend already stores the LLM model information in `AppConversation.llm_model`, but this information is not displayed anywhere in the UI.

## Goal

Display the LLM model name on conversation cards in the sidebar panel and in the conversation header when viewing a conversation. The display should include a circuit icon and handle long model names gracefully with truncation and tooltips.

## Files to Modify

### Backend
1. **openhands/server/data_models/conversation_info.py**
   - Add `llm_model: str | None = None` field to the `ConversationInfo` dataclass

2. **openhands/server/routes/manage_conversations.py**
   - Update the `_to_conversation_info` function to include `llm_model=app_conversation.llm_model`

### Frontend
1. **frontend/src/api/open-hands.types.ts**
   - Add `llm_model?: string | null;` to the `Conversation` interface

2. **frontend/src/components/features/conversation-panel/conversation-card/conversation-card.tsx**
   - Add `llmModel?: string | null` to props interface
   - Pass `llmModel` prop to `ConversationCardFooter`

3. **frontend/src/components/features/conversation-panel/conversation-card/conversation-card-footer.tsx**
   - Import `CircuitIcon` from `#/icons/u-circuit.svg?react`
   - Add `llmModel?: string | null` to props interface
   - Display the LLM model when provided with:
     - Circuit icon (`<CircuitIcon width={12} height={12} className="shrink-0" />`)
     - Truncated text with `max-w-[120px]` and `truncate` class
     - `title` attribute for tooltip showing full model name
     - `data-testid="conversation-card-llm-model"` for testing

4. **frontend/src/components/features/conversation-panel/conversation-panel.tsx**
   - Pass `llmModel={project.llm_model}` to `ConversationCard`

5. **frontend/src/components/features/conversation/conversation-name.tsx**
   - Import `CircuitIcon`
   - Display `conversation.llm_model` when available and not in edit mode
   - Use similar styling as ConversationCardFooter
   - Add `data-testid="conversation-name-llm-model"`

6. **frontend/src/components/features/home/recent-conversations/recent-conversation.tsx**
   - Import `CircuitIcon`
   - Display `conversation.llm_model` when available
   - Use similar styling as other components
   - Add `data-testid="recent-conversation-llm-model"`

## Requirements

1. The LLM model should only be displayed when it exists (not null/undefined)
2. Long model names should be truncated with `max-w-[120px]` and show full name on hover via `title` attribute
3. The CircuitIcon should be 12x12 pixels with `shrink-0` class to prevent shrinking
4. Text should use the `truncate` Tailwind class for proper truncation
5. Components should conditionally render the LLM model display only when the value is provided
6. For ConversationName, the LLM model should not be shown when in edit mode (`titleMode !== "edit"`)

## Reference

The CircuitIcon import path is `#/icons/u-circuit.svg?react`. This is an existing icon in the codebase.

The styling should match the existing patterns in each file, using Tailwind classes like:
- `text-xs text-[#A3A3A3]` for text styling
- `flex items-center gap-1` for layout
- `overflow-hidden` for container

## Testing

Your implementation will be tested by:
1. Checking that the ConversationInfo dataclass has the llm_model field
2. Verifying the _to_conversation_info function populates the field
3. Checking TypeScript types include llm_model
4. Verifying each component conditionally renders the LLM model with CircuitIcon
5. Confirming proper data-testid attributes are present
6. Checking TypeScript compilation passes
