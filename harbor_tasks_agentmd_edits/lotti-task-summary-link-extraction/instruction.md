# Add Links Section to AI Task Summaries

## Problem

AI-generated task summaries in Lotti currently do not extract or display links found within task entries. Users frequently paste URLs (GitHub issues, Linear tickets, documentation links, Stack Overflow answers) in their task logs, but these get buried in the raw text. When reviewing a task summary, there's no consolidated view of all referenced URLs.

## Expected Behavior

1. **Prompt update**: The task summary prompt (`preconfigured_prompts.dart`) should instruct the AI to append a **Links** section at the end of each summary. The AI should scan all log entries for URLs, extract unique ones, generate succinct titles for each, and format them as clickable Markdown links. If no URLs are found, the section should be omitted entirely.

2. **Clickable links in UI**: All AI summary display widgets should make Markdown links tappable, opening them in an external browser via `url_launcher`. This applies to the expandable summary, the base summary widget, and the modal view. Links should be visually styled with the theme's primary color.

3. **Documentation**: After implementing the code changes, update the relevant feature documentation to describe this new Automatic Link Extraction behavior. The project's `AGENTS.md` requires feature README files to be updated alongside code changes.

## Files to Look At

- `lib/features/ai/util/preconfigured_prompts.dart` — where the task summary prompt is defined
- `lib/features/ai/ui/expandable_ai_response_summary.dart` — expandable task summary widget
- `lib/features/ai/ui/ai_response_summary.dart` — base summary widget for non-task responses
- `lib/features/ai/ui/ai_response_summary_modal.dart` — full-screen modal summary view
- `lib/themes/theme.dart` — theme configuration including GptMarkdown styling
- `lib/features/ai/README.md` — feature documentation that should reflect the new behavior
