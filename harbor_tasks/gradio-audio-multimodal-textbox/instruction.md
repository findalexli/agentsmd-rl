# Fix: Audio input in MultimodalTextbox not functional

## Problem

After the Svelte 5 migration, audio recording in the `MultimodalTextbox` component is broken. When a user clicks the microphone button to record audio, the timer gets stuck at 0:00 and the stop button does not work. The audio playback component is also non-functional.

## Root Cause

In Svelte 5, plain `let` variable declarations are not reactive -- the DOM does not update when their values change. The variables controlling recording state (`is_recording`, `seconds`, `has_started`, etc.) and playback state (`playing`, `duration`, `currentTime`, `waveform_ready`) in the audio components were declared with plain `let` instead of `$state()`.

Additionally, the stop button logic does not correctly differentiate between stopping a recording vs. clearing when recording has not started yet, and the `startMic()` call has no error handling.

## Expected Behavior

- The microphone button should start recording and the timer should count up
- The stop button should stop the recording when recording is active, or clear when not
- Audio playback controls should work correctly after recording
- Microphone errors should be caught and handled gracefully

## Files to Investigate

- `js/audio/shared/MinimalAudioRecorder.svelte` -- recording state variables and stop button logic
- `js/audio/shared/MinimalAudioPlayer.svelte` -- playback state variables
