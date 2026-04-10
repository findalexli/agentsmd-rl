import yaml

with open('/workspace/task/eval_manifest.yaml', 'r') as f:
    data = yaml.safe_load(f)

data['rubric'] = [
    {
        'rule': 'Update the chat.params hook output type to include maxOutputTokens: number | undefined',
        'source': {'path': 'packages/plugin/src/index.ts'}
    },
    {
        'rule': 'Compute maxOutputTokens before Plugin.trigger("chat.params") and add it to the params object',
        'source': {'path': 'packages/opencode/src/session/llm.ts'}
    },
    {
        'rule': 'Pass params.maxOutputTokens instead of the local maxOutputTokens variable to the streamText call',
        'source': {'path': 'packages/opencode/src/session/llm.ts'}
    }
]

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
