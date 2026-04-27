# Restore notification sound and browser tab flash on agent state changes

You are working in the **All-Hands-AI/OpenHands** repository (the React + Vite
frontend lives under `frontend/`). The notification sound and browser-tab
title flashing features were accidentally removed in a previous refactor.
The `enable_sound_notifications` setting toggle still exists in the
Application Settings UI but currently does nothing, because the underlying
notification machinery was deleted.

Your task is to restore that machinery: re-implement a small browser-tab
title flasher utility and a React hook that triggers it when the agent
reaches a state that requires user attention. Then wire the hook into the
existing `AgentStatus` component.

The audio asset (`frontend/src/assets/notification.mp3`) is already provided
in the working tree; you do not need to recreate the binary file. You DO
need to make sure your hook imports it.

---

## What is broken

There is no in-app notification when the agent finishes work, awaits input,
or asks for confirmation. Specifically:

1. There is no module under `frontend/src/utils/` that flashes the document
   title between the original title and an "agent ready"-style message.
2. There is no hook under `frontend/src/hooks/` that observes agent-state
   transitions and triggers tab flashing or a notification sound.
3. The `AgentStatus` component does not invoke any such hook, so nothing
   ever fires.

The user setting `settings.enable_sound_notifications` (already exposed by
the existing `useSettings` hook in
`frontend/src/hooks/query/use-settings.ts`) must control whether the sound
plays.

---

## What you must implement

### 1. `frontend/src/utils/browser-tab.ts`

Export a single object named **`browserTab`** with two methods:

- `startNotification(message: string): void`
- `stopNotification(): void`

Behavior contract (these are the observable rules a unit test will check):

- Calling `startNotification(message)` records `document.title` at the time
  of the call as a baseline, then sets up a recurring task that **toggles
  `document.title` between the baseline and `message` exactly every 1000
  milliseconds**. The first tick (after 1000ms) must show `message`; the
  next tick must show the baseline; and so on.
- If, while the flasher is active, `document.title` is changed externally
  to a value that is **neither** the current baseline **nor** the
  notification message (for example, the user renames the conversation),
  the flasher must update its baseline to that new title. After the
  baseline is updated, ticks must continue to toggle between the **new**
  baseline and the message; calling `stopNotification()` must restore
  `document.title` to the new baseline (not the original one).
- Calling `stopNotification()` clears the recurring task and restores
  `document.title` to the most recently observed baseline.
- Calling `startNotification` while a flasher is already running must not
  leak intervals — start fresh.
- The module must be safe to import in a non-browser environment (SSR /
  Vitest's jsdom is fine, but `window` / `document` may legitimately be
  absent in some runtimes; guard appropriately so importing doesn't throw).
- Use `window.setInterval` / `window.clearInterval` (the test uses
  `vi.useFakeTimers()` and `vi.advanceTimersByTime(1000)` to drive ticks).

### 2. `frontend/src/hooks/use-agent-notification.ts`

Export a **named** function `useAgentNotification(curAgentState: AgentState)`
that returns nothing.

The agent state enum is `AgentState` from `#/types/agent-state`. The
mapping from `AgentState` to i18n key is `AGENT_STATUS_MAP` from
`#/utils/status`. The settings hook is `useSettings` from
`#/hooks/query/use-settings`; the relevant boolean is
`settings.enable_sound_notifications`.

Notification trigger states (the only states that should cause anything to
fire):

- `AgentState.AWAITING_USER_INPUT`
- `AgentState.FINISHED`
- `AgentState.AWAITING_USER_CONFIRMATION`

Behavior contract:

- The hook must **only fire on a state transition** into a notification
  state. Re-rendering with the same `curAgentState` value must not retrigger
  the sound or restart the tab flash.
- States outside the trigger list (e.g. `RUNNING`, `LOADING`) must not
  cause `browserTab.startNotification` to be called and must not cause the
  audio to play.
- When the hook fires:
  - If `settings.enable_sound_notifications` is `true`, play
    `frontend/src/assets/notification.mp3`. Reset the audio's
    `currentTime` to `0` immediately before each play (so consecutive
    notifications restart the clip rather than queuing). Set the audio
    `volume` to `0.5`. Use the standard browser `Audio` constructor —
    `new Audio(notificationSoundUrl)`. Swallow autoplay rejection
    (`.catch(() => {})`) silently — browsers may block autoplay and that
    must not propagate.
  - If `document.hasFocus()` is `false`, look up the i18n key
    `AGENT_STATUS_MAP[curAgentState]` and pass the translated string
    (using `t(...)` from `react-i18next`) as the `message` argument to
    `browserTab.startNotification(message)`. If the key is missing
    fall back to the raw `curAgentState` string. Translation keys must
    come from `AGENT_STATUS_MAP` — do **not** dynamically construct
    `t(...)` keys via template literals.
  - If `document.hasFocus()` is `true`, do **not** flash the tab — but
    still play the sound (the completion chime UX pattern: audible when
    focused, both audible and visual when not).
- When `enable_sound_notifications` is `false`, the audio must not play.
- Subscribe to the `window` `"focus"` event. When the window gains focus,
  call `browserTab.stopNotification()`. Unsubscribe on cleanup.
- The audio object should be created lazily inside a `useEffect` (not at
  module load and not during render) so that import is SSR-safe and
  React 18 strict-mode-safe.

Imports the hook must use:

```ts
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { AgentState } from "#/types/agent-state";
import { browserTab } from "#/utils/browser-tab";
import { useSettings } from "#/hooks/query/use-settings";
import { AGENT_STATUS_MAP } from "#/utils/status";
import notificationSound from "#/assets/notification.mp3";
```

(Vite resolves `*.mp3` imports to a URL string, which is what `new Audio()`
expects.)

### 3. Wire the hook into `AgentStatus`

In `frontend/src/components/features/controls/agent-status.tsx`, after the
existing call to `useAgentState()` that destructures `curAgentState`, call
`useAgentNotification(curAgentState)` so the hook actually runs while the
component is mounted. Add the corresponding import.

---

## How your work is checked

Vitest unit tests exercise the contract above. They use `vi.useFakeTimers()`
and `vi.advanceTimersByTime(1000)` to drive intervals; they stub `Audio`
and spy on `browserTab.startNotification` / `browserTab.stopNotification`;
they mock `useSettings` to flip `enable_sound_notifications`; and they
flip `document.hasFocus()` to test focused vs unfocused behavior. Your
implementation must make those tests pass.

The asset file `frontend/src/assets/notification.mp3` is preinstalled — do
not delete it. `npm install` has already been run; you do not have network
access at test time.
