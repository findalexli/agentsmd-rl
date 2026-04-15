# Fix: Audio input in MultimodalTextbox not functional

## Problem

After the Svelte 5 migration, audio recording in the `MultimodalTextbox` component is broken. When a user clicks the microphone button to record audio, the following symptoms occur:

1. **Timer does not update** - The recording timer stays stuck at 0:00 and does not increment as recording continues. The recording state variables appear to not trigger UI updates when modified.
2. **Stop button is unresponsive or behaves incorrectly** - When clicked, it should stop the recording when recording is active, or clear the component when recording has not yet started; currently this distinction is not handled properly
3. **Playback controls do not reflect state** - After recording, the audio player does not correctly display or respond to playback state changes. The waveform and timeline fail to update during playback.
4. **Microphone errors are not handled** - If microphone access fails (e.g., user denies permission), the error is unhandled and the component does not gracefully recover

## Files to Investigate

- `js/audio/shared/MinimalAudioRecorder.svelte` - Investigate the recording state variables (`record`, `seconds`, `is_recording`, `has_started`, `mic_devices`, `selected_device_id`, `show_device_selection`) and their declaration pattern. Also check the stop button onclick handler and the `startMic()` call for error handling.
- `js/audio/shared/MinimalAudioPlayer.svelte` - Investigate the playback state variables (`playing`, `duration`, `currentTime`, `waveform_ready`) and their declaration pattern.

## Expected Behavior

- The microphone button should start recording and the timer should count up during recording (the `seconds` variable should increment and the UI should update)
- The stop button should stop the recording when recording is active (`is_recording` is true), or clear the component (via `onclear?.()`) when recording has not yet started
- Audio playback controls should correctly reflect and respond to state changes (`playing`, `duration`, `currentTime`, `waveform_ready`)
- Microphone access errors should be caught and handled gracefully (e.g., log error and clear component)
- All state variables should use Svelte 5 reactivity patterns appropriate for the Svelte 5 runtime
