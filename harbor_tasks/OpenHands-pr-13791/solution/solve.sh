#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for PR #13791: fix(slack): immediately display 'No Repository' option
# Idempotency check: look for distinctive line from the patch
if grep -q "no_repository:" enterprise/integrations/slack/slack_manager.py 2>/dev/null; then
    echo "Patch already applied (idempotency check passed)"
    exit 0
fi

patch -p1 <<'PATCH'
diff --git a/enterprise/integrations/slack/slack_manager.py b/enterprise/integrations/slack/slack_manager.py
index 9d7924bfdf58..65698791b7b4 100644
--- a/enterprise/integrations/slack/slack_manager.py
+++ b/enterprise/integrations/slack/slack_manager.py
@@ -239,12 +239,14 @@ async def _search_repositories(
     def _generate_repo_selection_form(
         self, message_ts: str, thread_ts: str | None
     ) -> list[dict[str, Any]]:
-        """Generate a repo selection form using external_select for dynamic loading.
+        """Generate a repo selection form with immediate "No Repository" button and search dropdown.

-        This uses Slack's external_select element which allows:
-        - Type-ahead search for repositories
-        - Dynamic loading of options from an external endpoint
-        - Support for users with many repositories (no 100 option limit)
+        This form provides two options side-by-side:
+        1. A "No Repository" button - immediately clickable without any loading
+        2. An external_select dropdown - for searching repositories dynamically
+
+        This design ensures "No Repository" is always immediately available while
+        still providing full dynamic search capability for repositories.

         Args:
             message_ts: The message timestamp for tracking
@@ -266,12 +268,22 @@ def _generate_repo_selection_form(
                 'type': 'section',
                 'text': {
                     'type': 'mrkdwn',
-                    'text': 'Type to search your repositories:',
+                    'text': 'Select a repository or continue without one:',
                 },
             },
             {
                 'type': 'actions',
                 'elements': [
+                    {
+                        'type': 'button',
+                        'action_id': f'no_repository:{message_ts}:{thread_ts}',
+                        'text': {
+                            'type': 'plain_text',
+                            'text': 'No Repository',
+                            'emoji': True,
+                        },
+                        'value': '-',
+                    },
                     {
                         'type': 'external_select',
                         'action_id': f'repository_select:{message_ts}:{thread_ts}',
@@ -279,8 +291,8 @@ def _generate_repo_selection_form(
                             'type': 'plain_text',
                             'text': 'Search repositories...',
                         },
-                        'min_query_length': 0,  # Load initial options immediately
-                    }
+                        'min_query_length': 0,
+                    },
                 ],
             },
         ]
@@ -288,8 +300,11 @@ def _generate_repo_selection_form(
     def _build_repo_options(self, repos: list[Repository]) -> list[dict[str, Any]]:
         """Build Slack options list from repositories.

-        Always includes a "No Repository" option at the top, followed by up to 99
-        repositories (Slack has a 100 option limit for external_select).
+        Returns up to 100 repositories formatted as Slack options
+        (Slack has a 100 option limit for external_select).
+
+        Note: "No Repository" is handled by a separate button in the form,
+        so it's not included in the dropdown options.

         Args:
             repos: List of Repository objects
@@ -297,13 +312,7 @@ def _build_repo_options(self, repos: list[Repository]) -> list[dict[str, Any]]:
         Returns:
             List of Slack option objects
         """
-        options: list[dict[str, Any]] = [
-            {
-                'text': {'type': 'plain_text', 'text': 'No Repository'},
-                'value': '-',
-            }
-        ]
-        options.extend(
+        return [
             {
                 'text': {
                     'type': 'plain_text',
@@ -311,9 +320,8 @@ def _build_repo_options(self, repos: list[Repository]) -> list[dict[str, Any]]:
                 },
                 'value': repo.full_name,
             }
-            for repo in repos[:99]  # Leave room for "No Repository" option
-        )
-        return options
+            for repo in repos[:100]
+        ]

     async def search_repos_for_slack(
         self, user_auth: UserAuth, query: str, per_page: int = 20
@@ -363,33 +371,69 @@ async def receive_message(self, message: Message):
                 SlackError(SlackErrorCode.UNEXPECTED_ERROR),
             )

+    def _parse_form_action(self, action: dict) -> tuple[str, str | None, str] | None:
+        """Parse action payload and extract message_ts, thread_ts, and selected value.
+
+        This handles the different payload structures for button clicks vs dropdown
+        selections in the repository selection form.
+
+        Args:
+            action: The action object from the Slack payload
+
+        Returns:
+            Tuple of (message_ts, thread_ts, selected_value) if action is recognized,
+            None if the action_id is unknown.
+        """
+        action_id = action['action_id']
+
+        if action_id.startswith('no_repository:'):
+            # Button click - value is in 'value' field
+            attribs = action_id.split('no_repository:')[-1]
+            selected_value = action.get('value', '-')
+        elif action_id.startswith('repository_select:'):
+            # Dropdown selection - value is in 'selected_option'
+            attribs = action_id.split('repository_select:')[-1]
+            selected_value = action['selected_option']['value']
+        else:
+            return None
+
+        message_ts, thread_ts = attribs.split(':')
+        thread_ts = None if thread_ts == 'None' else thread_ts
+
+        return message_ts, thread_ts, selected_value
+
     async def receive_form_interaction(self, slack_payload: dict):
-        """Process a Slack form interaction (repository selection).
+        """Process a Slack form interaction (repository selection or button click).

-        This handles the block_actions payload when a user selects a repository
-        from the dropdown form. It retrieves the original user message from Redis
-        and delegates to receive_message for processing.
+        This handles the block_actions payload when a user interacts with the
+        repository selection form. It can handle:
+        - "No Repository" button click: proceeds with conversation without a repo
+        - Repository selection from dropdown: proceeds with the selected repo

         Args:
             slack_payload: The raw Slack interaction payload
         """
         # Extract fields from the Slack interaction payload
-        selected_repository = slack_payload['actions'][0]['selected_option']['value']
-        if selected_repository == '-':
-            selected_repository = None
-
+        action = slack_payload['actions'][0]
         slack_user_id = slack_payload['user']['id']
         channel_id = slack_payload['container']['channel_id']
         team_id = slack_payload['team']['id']

-        # Get original message_ts and thread_ts from action_id
-        attribs = slack_payload['actions'][0]['action_id'].split('repository_select:')[
-            -1
-        ]
-        message_ts, thread_ts = attribs.split(':')
-        thread_ts = None if thread_ts == 'None' else thread_ts
+        # Parse the action to extract message_ts, thread_ts, and selected value
+        parsed = self._parse_form_action(action)
+        if parsed is None:
+            logger.warning(
+                'slack_unknown_action_id',
+                extra={
+                    'action_id': action['action_id'],
+                    'slack_user_id': slack_user_id,
+                },
+            )
+            return

-        # Build partial payload for error handling during Redis retrieval
+        message_ts, thread_ts, selected_value = parsed
+
+        # Build partial payload for error handling
         payload = {
             'team_id': team_id,
             'channel_id': channel_id,
@@ -398,6 +442,9 @@ async def receive_form_interaction(self, slack_payload: dict):
             'thread_ts': thread_ts,
         }

+        # Convert "-" (No Repository) to None
+        selected_repository = None if selected_value == '-' else selected_value
+
         # Retrieve the original user message from Redis
         try:
             user_msg = await self._retrieve_user_msg_for_form(message_ts, thread_ts)
diff --git a/enterprise/server/routes/integration/slack.py b/enterprise/server/routes/integration/slack.py
index 94d8054de1e4..3fba892c5d97 100644
--- a/enterprise/server/routes/integration/slack.py
+++ b/enterprise/server/routes/integration/slack.py
@@ -335,6 +335,9 @@ async def on_options_load(request: Request, background_tasks: BackgroundTasks):
     2. Searches for repositories matching the user's query
     3. Returns up to 100 options for the dropdown

+    Note: "No Repository" is handled by a separate button in the form, so it's
+    not included in the dropdown options. Error cases return an empty list.
+
     Configuration: Set the Options Load URL in Slack App settings to:
     https://your-domain/slack/on-options-load
     """
diff --git a/enterprise/tests/unit/test_slack_integration.py b/enterprise/tests/unit/test_slack_integration.py
index 6ca52cc5e45a..147e812b395f 100644
--- a/enterprise/tests/unit/test_slack_integration.py
+++ b/enterprise/tests/unit/test_slack_integration.py
@@ -135,14 +135,19 @@ async def test_timeout_during_verification_shows_selector(

     @patch('integrations.slack.slack_manager.sio')
     @patch.object(SlackManager, 'send_message', new_callable=AsyncMock)
-    async def test_no_repo_mentioned_shows_external_selector(
+    async def test_no_repo_mentioned_shows_button_and_dropdown(
         self,
         mock_send_message,
         mock_sio,
         slack_manager,
         slack_new_conversation_view,
     ):
-        """Test that when no repo is mentioned, external_select repo selector is shown."""
+        """Test that when no repo is mentioned, a button and dropdown are shown.
+
+        The form shows:
+        1. A "No Repository" button - immediately clickable without loading
+        2. An external_select dropdown - for searching repositories dynamically
+        """
         # Setup Redis mock
         mock_redis = AsyncMock()
         mock_sio.manager.redis = mock_redis
@@ -162,17 +167,75 @@ async def test_no_repo_mentioned_shows_external_selector(
         mock_send_message.assert_called_once()
         call_args = mock_send_message.call_args

-        # Should be the repo selection form with external_select
+        # Should be the repo selection form with button + external_select
         message = call_args[0][0]
         assert isinstance(message, dict)
         assert message.get('text') == 'Choose a Repository:'
-        # Verify it's using external_select
+
         blocks = message.get('blocks', [])
         actions_block = next((b for b in blocks if b.get('type') == 'actions'), None)
         assert actions_block is not None
         elements = actions_block.get('elements', [])
-        assert len(elements) > 0
-        assert elements[0].get('type') == 'external_select'
+
+        # Should have 2 elements: button and external_select
+        assert len(elements) == 2
+
+        # First element: "No Repository" button (immediately available)
+        assert elements[0].get('type') == 'button'
+        assert elements[0].get('action_id').startswith('no_repository:')
+        assert elements[0].get('value') == '-'
+
+        # Second element: external_select for searching repos
+        assert elements[1].get('type') == 'external_select'
+        assert elements[1].get('action_id').startswith('repository_select:')
+
+    @pytest.mark.asyncio
+    @patch('integrations.slack.slack_manager.sio')
+    async def test_no_repository_button_click_processes_correctly(
+        self,
+        mock_sio,
+        slack_manager,
+    ):
+        """Test that clicking 'No Repository' button correctly processes the interaction.
+
+        This verifies the button click path through receive_form_interaction, ensuring
+        the no_repository: action_id is correctly parsed and processed.
+        """
+        # Setup: Mock Redis to return a stored user message
+        mock_redis = AsyncMock()
+        mock_sio.manager.redis = mock_redis
+        stored_msg = json.dumps({'text': 'Hello, help me with code', 'user': 'U123'})
+        mock_redis.get = AsyncMock(return_value=stored_msg)
+
+        # Simulate button click payload (what Slack sends when button is clicked)
+        button_payload = {
+            'type': 'block_actions',
+            'actions': [
+                {
+                    'action_id': 'no_repository:1234567890.123456:None',
+                    'type': 'button',
+                    'value': '-',
+                }
+            ],
+            'user': {'id': 'U123'},
+            'container': {'channel_id': 'C123'},
+            'team': {'id': 'T123'},
+        }
+
+        # Mock receive_message to capture what's passed to it
+        with patch.object(
+            slack_manager, 'receive_message', new_callable=AsyncMock
+        ) as mock_receive:
+            await slack_manager.receive_form_interaction(button_payload)
+
+            # Verify receive_message was called
+            mock_receive.assert_called_once()
+
+            # Verify the message payload has selected_repo as None
+            call_args = mock_receive.call_args[0][0]
+            assert call_args.message['selected_repo'] is None
+            assert call_args.message['message_ts'] == '1234567890.123456'
+            assert call_args.message['thread_ts'] is None

     @patch('integrations.slack.slack_manager.sio')
     @patch('integrations.slack.slack_manager.ProviderHandler')
@@ -223,8 +286,8 @@ async def test_verified_repo_starts_job(
 class TestBuildRepoOptions:
     """Test the _build_repo_options helper method.

-    Note: _build_repo_options always includes the "No Repository" option at the top.
-    This is by design for the external_select dropdown.
+    Note: _build_repo_options returns only actual repositories. The "No Repository"
+    option is now handled by a separate button in the form, not the dropdown.
     """

     def test_build_options_with_repos(self, slack_manager):
@@ -247,21 +310,20 @@ def test_build_options_with_repos(self, slack_manager):

         options = slack_manager._build_repo_options(repos)

-        # Should have 3 options: "No Repository" + 2 repos
-        assert len(options) == 3
-        assert options[0]['value'] == '-'
-        assert options[0]['text']['text'] == 'No Repository'
-        assert options[1]['value'] == 'owner/repo1'
-        assert options[2]['value'] == 'owner/repo2'
+        # Should have 2 options (repos only - "No Repository" is now a button)
+        assert len(options) == 2
+        assert options[0]['value'] == 'owner/repo1'
+        assert options[1]['value'] == 'owner/repo2'

     def test_build_options_empty_repos(self, slack_manager):
-        """Test building options with empty repo list still includes No Repository."""
+        """Test building options with empty repo list returns empty list.
+
+        Note: "No Repository" is now handled by a separate button in the form.
+        """
         options = slack_manager._build_repo_options([])

-        # Should have 1 option: just "No Repository"
-        assert len(options) == 1
-        assert options[0]['value'] == '-'
-        assert options[0]['text']['text'] == 'No Repository'
+        # Should have 0 options (empty list)
+        assert len(options) == 0

     def test_build_options_truncates_long_names(self, slack_manager):
         """Test that repo names longer than 75 chars are truncated."""
@@ -278,12 +340,12 @@ def test_build_options_truncates_long_names(self, slack_manager):

         options = slack_manager._build_repo_options(repos)

-        # First option is "No Repository", second is the repo
-        assert len(options) == 2
+        # Should have 1 option (the repo only - "No Repository" is a button)
+        assert len(options) == 1
         # Text should be truncated to 75 chars
-        assert len(options[1]['text']['text']) == 75
+        assert len(options[0]['text']['text']) == 75
         # But value should have full name
-        assert options[1]['value'] == long_name
+        assert options[0]['value'] == long_name


 class TestSearchRepositories:
@@ -413,23 +475,23 @@ async def test_search_and_build_options_integration(
         options = slack_manager._build_repo_options(search_results)

         # Verify: Options are correctly built from search results
-        assert len(options) == 4  # "No Repository" + 3 repos
-
-        # First option should be "No Repository"
-        assert options[0]['value'] == '-'
-        assert options[0]['text']['text'] == 'No Repository'
+        # Note: "No Repository" is now a button, not in the dropdown
+        assert len(options) == 3  # 3 repos only

-        # Remaining options should be the repos in order
-        assert options[1]['value'] == 'myorg/react-dashboard'
-        assert options[1]['text']['text'] == 'myorg/react-dashboard'
-        assert options[2]['value'] == 'myorg/python-api'
-        assert options[3]['value'] == 'myorg/docs-site'
+        # Options should be the repos in order
+        assert options[0]['value'] == 'myorg/react-dashboard'
+        assert options[0]['text']['text'] == 'myorg/react-dashboard'
+        assert options[1]['value'] == 'myorg/python-api'
+        assert options[2]['value'] == 'myorg/docs-site'

     @patch('integrations.slack.slack_manager.ProviderHandler')
-    async def test_search_with_empty_results_builds_no_repo_only_option(
+    async def test_search_with_empty_results_builds_empty_options(
         self, mock_provider_handler_class, slack_manager, mock_user_auth
     ):
-        """Test that when search returns no results, only 'No Repository' option is shown."""
+        """Test that when search returns no results, empty options list is returned.
+
+        Note: "No Repository" is now handled by a separate button in the form.
+        """
         # Setup: No matching repos
         mock_provider_handler = MagicMock()
         mock_provider_handler.search_repositories = AsyncMock(return_value=[])
@@ -447,10 +509,8 @@ async def test_search_with_empty_results_builds_no_repo_only_option(
         )
         options = slack_manager._build_repo_options(search_results)

-        # Verify: Only "No Repository" option
-        assert len(options) == 1
-        assert options[0]['value'] == '-'
-        assert options[0]['text']['text'] == 'No Repository'
+        # Verify: Empty options list (button handles "No Repository")
+        assert len(options) == 0


 class TestUserMsgStorage:
@@ -669,7 +729,10 @@ def background_tasks(self):
     async def test_on_options_load_disabled_returns_empty_options(
         self, mock_request, background_tasks
     ):
-        """Test that when webhooks are disabled, empty options are returned."""
+        """Test that when webhooks are disabled, empty options are returned.
+
+        Note: 'No Repository' is handled by a separate button in the form.
+        """
         from server.routes.integration.slack import on_options_load

         response = await on_options_load(mock_request, background_tasks)
@@ -683,7 +746,10 @@ async def test_on_options_load_disabled_returns_empty_options(
     async def test_on_options_load_no_payload_returns_empty_options(
         self, mock_request, background_tasks
     ):
-        """Test that when no payload is in request, empty options are returned."""
+        """Test that when no payload is in request, empty options are returned.
+
+        Note: 'No Repository' is handled by a separate button in the form.
+        """
         from server.routes.integration.slack import on_options_load

         mock_request.body = AsyncMock(return_value=b'')
@@ -731,7 +797,10 @@ async def test_on_options_load_invalid_signature_raises_403(
     async def test_on_options_load_wrong_payload_type_returns_empty_options(
         self, mock_signature_verifier, mock_request, background_tasks
     ):
-        """Test that non-block_suggestion payload returns empty options."""
+        """Test that non-block_suggestion payload returns empty options.
+
+        Note: 'No Repository' is handled by a separate button in the form.
+        """
         from server.routes.integration.slack import on_options_load

         payload = {
@@ -764,7 +833,10 @@ async def test_on_options_load_unauthenticated_user_returns_empty_options(
         background_tasks,
         valid_block_suggestion_payload,
     ):
-        """Test that unauthenticated users get empty options and linking message is queued."""
+        """Test that unauthenticated users get empty options and linking message is queued.
+
+        Note: 'No Repository' is handled by a separate button in the form.
+        """
         from server.routes.integration.slack import on_options_load

         payload_str = json.dumps(valid_block_suggestion_payload)
@@ -817,9 +889,8 @@ async def test_on_options_load_successful_search_with_repos(
             return_value=(mock_slack_user, mock_user_auth)
         )

-        # Expected options from search_repos_for_slack
+        # Expected options from search_repos_for_slack (no "No Repository" - that's a button)
         expected_options = [
-            {'text': {'type': 'plain_text', 'text': 'No Repository'}, 'value': '-'},
             {
                 'text': {'type': 'plain_text', 'text': 'owner/repo1'},
                 'value': 'owner/repo1',
@@ -878,11 +949,8 @@ async def test_on_options_load_empty_query_search(
         mock_slack_manager.authenticate_user = AsyncMock(
             return_value=(mock_slack_user, mock_user_auth)
         )
-        mock_slack_manager.search_repos_for_slack = AsyncMock(
-            return_value=[
-                {'text': {'type': 'plain_text', 'text': 'No Repository'}, 'value': '-'}
-            ]
-        )
+        # Empty search returns empty list (no repos found, and "No Repository" is a button)
+        mock_slack_manager.search_repos_for_slack = AsyncMock(return_value=[])

         response = await on_options_load(mock_request, background_tasks)

@@ -907,7 +975,10 @@ async def test_on_options_load_search_exception_returns_empty_options(
         mock_slack_user,
         mock_user_auth,
     ):
-        """Test that when search raises an exception, empty options are returned gracefully."""
+        """Test that when search raises an exception, empty options are returned gracefully.
+
+        Note: 'No Repository' is handled by a separate button in the form.
+        """
         from server.routes.integration.slack import on_options_load

         payload_str = json.dumps(valid_block_suggestion_payload)
PATCH

echo "Patch applied successfully"
