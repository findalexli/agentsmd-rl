#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q '<dynamic_person_properties>' ee/hogai/chat_agent/taxonomy/prompts.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Add dynamic_person_properties section to PROPERTY_TYPES_PROMPT ---
python3 -c "
import re
path = 'ee/hogai/chat_agent/taxonomy/prompts.py'
with open(path) as f:
    src = f.read()

insert = '''
<dynamic_person_properties>
Some person properties follow dynamic naming patterns with IDs. These will NOT appear in tool results because they are dynamically generated per survey, feature flag, or product tour.
If a user's question involves these features, construct the property name using the pattern:

- \\\$survey_dismissed/{survey_id} / \\\$survey_responded/{survey_id} — Boolean, tracks whether a person dismissed or responded to a specific survey
- \\\$feature_enrollment/{flag_key} — Boolean, whether a person opted into a specific early access feature
- \\\$feature/{flag_key} — the feature flag value for a specific flag (this is an event property, not a person property)
- \\\$feature_interaction/{feature_key} — Boolean, whether a person interacted with a specific feature
- \\\$product_tour_dismissed/{tour_id} / \\\$product_tour_shown/{tour_id} / \\\$product_tour_completed/{tour_id} — Boolean, tracks product tour lifecycle for a specific tour
</dynamic_person_properties>'''

src = src.replace('</group>\n</entity>', '</group>\n' + insert + '\n</entity>')
with open(path, 'w') as f:
    f.write(src)
"

# --- 2. Add hint constants and modify execute_taxonomy_query in core.py ---
python3 -c "
path = 'ee/hogai/tools/read_taxonomy/core.py'
with open(path) as f:
    src = f.read()

# Add hint constants before execute_taxonomy_query
hints = '''
DYNAMIC_PERSON_PROPERTIES_HINT = \"\"\"
NOTE: Some person properties follow dynamic naming patterns and will NOT appear in the list above.
If the user's question involves surveys, feature flags, early access features, or product tours, construct the property name using these patterns:
- \\\$survey_dismissed/{survey_id}, \\\$survey_responded/{survey_id} — Boolean, survey dismiss/response tracking
- \\\$feature_enrollment/{flag_key} — Boolean, early access feature enrollment
- \\\$feature_interaction/{feature_key} — Boolean, feature interaction tracking
- \\\$product_tour_dismissed/{tour_id}, \\\$product_tour_shown/{tour_id}, \\\$product_tour_completed/{tour_id} — Boolean, product tour lifecycle
\"\"\".strip()

DYNAMIC_EVENT_PROPERTIES_HINT = \"\"\"
NOTE: Some event properties follow dynamic naming patterns and will NOT appear in the list above.
If the user's question involves feature flags, construct the property name using this pattern:
- \\\$feature/{flag_key} — the feature flag value for a specific flag
\"\"\".strip()

'''

src = src.replace(
    'def execute_taxonomy_query(',
    hints + 'def execute_taxonomy_query('
)

# Modify event property results to append hint
src = src.replace(
    '''case ReadEventProperties():
            return toolkit.retrieve_event_or_action_properties(query.event_name)''',
    '''case ReadEventProperties():
            result = toolkit.retrieve_event_or_action_properties(query.event_name)
            return f\"{result}\\n\\n{DYNAMIC_EVENT_PROPERTIES_HINT}\"'''
)

# Modify action property results to append hint
src = src.replace(
    '''case ReadActionProperties():
            return toolkit.retrieve_event_or_action_properties(query.action_id)''',
    '''case ReadActionProperties():
            result = toolkit.retrieve_event_or_action_properties(query.action_id)
            return f\"{result}\\n\\n{DYNAMIC_EVENT_PROPERTIES_HINT}\"'''
)

# Modify entity property results to conditionally append person hint
src = src.replace(
    '''case ReadEntityProperties():
            return toolkit.retrieve_entity_properties(query.entity)''',
    '''case ReadEntityProperties():
            result = toolkit.retrieve_entity_properties(query.entity)
            if query.entity == \"person\":
                return f\"{result}\\n\\n{DYNAMIC_PERSON_PROPERTIES_HINT}\"
            return result'''
)

with open(path, 'w') as f:
    f.write(src)
"

# --- 3. Update omit filter in event_taxonomy_query_runner.py ---
python3 -c "
path = 'posthog/hogql_queries/ai/event_taxonomy_query_runner.py'
with open(path) as f:
    src = f.read()

# Replace old omit list with expanded version
old_block = '''            r\"\\\\\$feature\\/\",
            # flatten-properties-plugin
            \"__\",
            # other metadata
            \"phjs\",
            \"survey_dismissed\",
            \"survey_responded\",
            \"partial_filter_chosen\",
            \"changed_action\",
            \"window-id\",
            \"changed_event\",
            \"partial_filter\",
            \"distinct_id\",'''

new_block = '''            r\"\\\\\$feature\\/\",
            r\"\\\\\$feature_enrollment\\/\",
            r\"\\\\\$feature_interaction\\/\",
            # product tours
            r\"\\\\\$product_tour\",
            # flatten-properties-plugin
            \"__\",
            # surveys
            \"survey_dismiss\",
            \"survey_responded\",
            # other metadata
            \"phjs\",
            \"partial_filter_chosen\",
            \"changed_action\",
            \"window-id\",
            \"changed_event\",
            \"partial_filter\",'''

src = src.replace(old_block, new_block)
with open(path, 'w') as f:
    f.write(src)
"

# --- 4. Update SKILL.md to reference new docs ---
python3 -c "
path = 'products/posthog_ai/skills/query-examples/SKILL.md'
with open(path) as f:
    src = f.read()

# Add dynamic properties reference in Data Schema section
src = src.replace(
    '- [Skipped events in the read-data-schema tool](./references/taxonomy-skipped-events.md)',
    '- [Skipped events in the read-data-schema tool](./references/taxonomy-skipped-events.md)\n- [Dynamic person and event properties](./references/taxonomy-dynamic-properties.md) — patterns like \`\$survey_dismissed/{id}\`, \`\$feature/{key}\` that don'\''t appear in tool results'
)

# Add new query examples
src = src.replace(
    '- [Team taxonomy (top events by count, paginated)](./references/example-team-taxonomy.md)',
    '- [Team taxonomy (top events by count, paginated)](./references/example-team-taxonomy.md)\n- [Event taxonomy (properties of an event, with sample values)](./references/example-event-taxonomy.md)\n- [Person property taxonomy (sample values for person properties)](./references/example-person-property-taxonomy.md)'
)

with open(path, 'w') as f:
    f.write(src)
"

# --- 5. Create new reference docs ---

cat > products/posthog_ai/skills/query-examples/references/taxonomy-dynamic-properties.md <<'DYNPROPS'
# Dynamic person and event properties

Some properties follow dynamic naming patterns with IDs or keys.
These are **not returned** by the `read-data-schema` tool because they are generated per survey, feature flag, or product tour.
If a user's question involves these features, construct the property name using the patterns below.

## Person properties

Pattern | Type | Description
`$survey_dismissed/{survey_id}` | Boolean | Whether a person dismissed a specific survey
`$survey_responded/{survey_id}` | Boolean | Whether a person responded to a specific survey
`$feature_enrollment/{flag_key}` | Boolean | Whether a person opted into an early access feature
`$feature_interaction/{feature_key}` | Boolean | Whether a person interacted with a specific feature
`$product_tour_dismissed/{tour_id}` | Boolean | Whether a person dismissed a product tour
`$product_tour_shown/{tour_id}` | Boolean | Whether a person was shown a product tour
`$product_tour_completed/{tour_id}` | Boolean | Whether a person completed a product tour

## Event properties

Pattern | Type | Description
`$feature/{flag_key}` | String | The feature flag value for a specific flag

## Querying dynamic properties with SQL

Because these properties are not discoverable via the `read-data-schema` tool, you must know the ID or key.
Use these queries to find the IDs, then construct the property name.

### Find survey IDs

```sql
SELECT id, name, description, type
FROM system.surveys
WHERE NOT archived
ORDER BY created_at DESC
LIMIT 20
```

Then query person properties like `$survey_dismissed/{id}` or `$survey_responded/{id}`.

### Find feature flag keys

```sql
SELECT id, key, name, rollout_percentage
FROM system.feature_flags
WHERE NOT deleted
ORDER BY created_at DESC
LIMIT 20
```

Then query event properties like `$feature/{key}` or person properties like `$feature_enrollment/{key}`.

### Find early access features

```sql
SELECT id, name, feature_flag_id
FROM system.early_access_features
WHERE NOT deleted
ORDER BY created_at DESC
LIMIT 20
```

Then look up the flag key and query `$feature_enrollment/{flag_key}`.

## Event taxonomy omit list

The `read-data-schema` tool's event property results automatically filter out these dynamic patterns
(and other noisy properties) to keep results clean:

Pattern | Reason
`$feature/{flag_key}` | Feature flag values — one per flag, high cardinality
`$feature_enrollment/{flag_key}` | Early access enrollment — dynamic per flag
`$feature_interaction/{feature_key}` | Feature interaction tracking — dynamic per feature
`$product_tour_*` | Product tour lifecycle — dynamic per tour
`survey_dismiss*`, `survey_responded*` | Survey tracking — dynamic per survey
`$set`, `$set_once` | Person property setting, not analytics properties
`$ip` | Privacy-related
`__*` | Flatten-properties-plugin artifacts
`phjs*` | Internal SDK metadata
DYNPROPS

cat > products/posthog_ai/skills/query-examples/references/example-event-taxonomy.md.j2 <<'EVTTAX'
# Event taxonomy (properties of an event, with sample values)

All properties for a given event, with up to 5 sample values each:

```sql
{{ render_hogql_example({"kind": "EventTaxonomyQuery", "event": "$pageview"}) }}
```

Specific properties only (faster, skips the omit filter):

```sql
{{ render_hogql_example({"kind": "EventTaxonomyQuery", "event": "$pageview", "properties": ["$browser", "$os"]}) }}
```
EVTTAX

cat > products/posthog_ai/skills/query-examples/references/example-person-property-taxonomy.md.j2 <<'PERSTAX'
# Person property taxonomy (sample values for person properties)

Sample values for specific person properties:

```sql
{{ render_hogql_example({"kind": "ActorsPropertyTaxonomyQuery", "properties": ["email", "$initial_browser"]}) }}
```
PERSTAX

echo "Patch applied successfully."
