# Fix Slack "No Repository" Selection Delay

## Problem

In `enterprise/integrations/slack/slack_manager.py`, the Slack integration's repository selection form has a usability issue: users who don't want to select a repository must wait for a network request to complete before they can interact with the form, because "No Repository" is bundled with the dynamically loaded options.

Currently:
- `_generate_repo_selection_form` creates a form with only an `external_select` dropdown and the prompt `"Type to search your repositories:"`. All options require a network request.
- `_build_repo_options` prepends a "No Repository" entry as the first option and limits repositories to 99 (reserving one slot within Slack's 100-option limit).
- `receive_form_interaction` directly accesses `selected_option` from the dropdown payload, which only exists for `external_select` interactions.

## Requirements

1. **Immediate "No Repository" button**: The form should include a Slack button element (`'type': 'button'`) that is immediately clickable without any network request. It should have:
   - An `action_id` starting with `no_repository:`
   - A `'value'` of `'-'`

   The button and the existing `external_select` dropdown should be in the same actions block.

2. **Retained search dropdown**: The `external_select` dropdown should remain for repository search, with `action_id` starting with `repository_select:`.

3. **Updated instruction text**: The form should display `"Select a repository or continue without one:"`.

4. **Repository-only options**: `_build_repo_options` should return only repository entries (no prepended "No Repository" option). Since the dropdown no longer needs to reserve a slot for "No Repository", it should support up to 100 repositories instead of the current 99.

5. **Unified action parsing**: A new helper method should be added to parse both button and dropdown action payloads. It should identify action types by checking the `action_id` prefix for `no_repository:` and `repository_select:`, and return `None` for unrecognized actions.

6. **Graceful interaction handling**: `receive_form_interaction` should use the new parsing helper. When it returns `None`, log a warning and return early. The `'-'` value should be treated as no repository selected.

## Verification

```bash
cd /workspace/openhands
python -m pytest enterprise/tests/unit/test_slack_integration.py -v
```
