# Write a CLAUDE.md

Source: [realtime-ai/realtime-ai#38](https://github.com/realtime-ai/realtime-ai/pull/38)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Major additions to documentation:
- Updated project overview with gRPC and WebSocket architecture support
- Added Quick Start Guide for new developers
- Documented all 8 examples including new ones (grpc-assis, translation-demo, simultaneous-interpretation, tracing-demo)
- Added comprehensive ASR (Automatic Speech Recognition) system documentation
- Added TTS (Text-to-Speech) provider system documentation
- Documented TranslateElement for real-time translation
- Added gRPC architecture section with use cases and comparison to WebRTC
- Documented GitHub Actions CI/CD workflows
- Added Advanced Deployment Architectures section (ConversationRelay v2)
- Expanded Key Packages section with pkg/asr, pkg/tts, pkg/proto, pkg/utils
- Added comprehensive Examples and Demos section
- Enhanced Testing section with integration tests and CI/CD info
- Added Documentation Resources section with all available docs
- Updated Element Categories with WhisperSTTElement, UniversalTTSElement, TranslateElement
- Updated Connection System with GRPCConnection and WSConnection
- Added Azure environment variables documentation

Expanded from ~200 lines to 694 lines (500+ new lines of documentation) Reflects current state of codebase including all recent major features

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
