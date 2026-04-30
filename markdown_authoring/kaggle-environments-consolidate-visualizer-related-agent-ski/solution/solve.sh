#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kaggle-environments

# Idempotency guard
if grep -qF "Follow the `create-visualizer` skill to build a web-based replay visualizer for " ".agents/skills/create-environment/SKILL.md" && grep -qF ".agents/skills/create-open-spiel-visualizer/SKILL.md" ".agents/skills/create-open-spiel-visualizer/SKILL.md" && grep -qF "**Observation string is empty (OpenSpiel):** Some games use `information_state_s" ".agents/skills/create-visualizer/SKILL.md" && grep -qF "5. **Two typefaces.** Use **Inter** (sans-serif) for all UI text -- player names" ".agents/skills/create-visualizer/visualizer-style-guide.md" && grep -qF "All three approaches can optionally include a **visualizer** (see `create-visual" ".agents/skills/onboard-open-spiel-game/SKILL.md" && grep -qF "- **create-visualizer** -- step-by-step guide for building a web visualizer for " "AGENTS.md" && grep -qF "- `create-visualizer` -- building a web visualizer for any game (regular or Open" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-environment/SKILL.md b/.agents/skills/create-environment/SKILL.md
@@ -235,6 +235,10 @@ Run tests with:
 uv sync && uv run pytest tests/envs/<name>/test_<name>.py -v
 ```
 
+## Step 6: Add a visualizer (optional)
+
+Follow the `create-visualizer` skill to build a web-based replay visualizer for this environment.
+
 ## Checklist
 
 - [ ] `<name>.json` spec is valid JSON with all required top-level keys
diff --git a/.agents/skills/create-open-spiel-visualizer/SKILL.md b/.agents/skills/create-open-spiel-visualizer/SKILL.md
@@ -1,689 +0,0 @@
-# Create a Visualizer for a New OpenSpiel Game
-
-Build a standalone web visualizer (hybrid DOM + canvas) for an OpenSpiel game that does **not** already have a harness, proxy, or visualizer in kaggle-environments. The game must already exist in OpenSpiel's game registry. No proxy, transformer, or custom game implementation is needed -- the visualizer parses the raw OpenSpiel observation string directly.
-
-**When to use this skill:** You have an OpenSpiel game name (e.g., `"quoridor"`, `"amazons"`) and want to create a complete visualizer so humans can watch replays. The game doesn't need any special observation formatting -- you work with whatever string OpenSpiel's `observation_string()` returns.
-
-**Related skills:**
-- `onboard-open-spiel-game` -- if you also need a proxy, custom game, tests, or full onboarding
-- `create-visualizer` -- for non-OpenSpiel environments
-
-## Prerequisites
-
-### OpenSpiel source code
-
-The OpenSpiel repository should be cloned locally (typically at `../open_spiel` relative to the kaggle-environments root). This is **required** -- you need to read the game's C++ source to understand:
-- The observation string format (`ObservationString` method)
-- Game parameters and defaults
-- Game type (perfect vs imperfect information, sequential vs simultaneous)
-- Action encoding
-
-Find the game source at `open_spiel/games/<game_name>/` (or `open_spiel/games/<game_name>.h` / `open_spiel/games/<game_name>.cc` for single-file games).
-
-### Python virtual environment
-
-Create a venv for running Python commands. Do NOT install packages globally.
-
-```bash
-python3 -m venv .venv
-.venv/bin/pip install -e ".[dev]"
-```
-
-This installs `kaggle-environments` with all dependencies (including `pyspiel`) in an isolated environment. All subsequent Python commands should use `.venv/bin/python`.
-
-### Verify the game exists
-
-```bash
-.venv/bin/python -c "import pyspiel; print('$GAME_NAME' in [g.short_name for g in pyspiel.registered_games().values()])"
-```
-
-Or simply check that the source directory exists in the OpenSpiel repo: `ls ../open_spiel/open_spiel/games/$GAME_NAME/`
-
-## Step 1: Study the game from OpenSpiel source
-
-Read the game's `.h` file in the OpenSpiel repo to understand:
-
-1. **Observation string format** -- search for `ObservationString`, `ToString`, `OwnBoardString`, etc. The header comments typically show example output with character-by-character explanations.
-
-2. **Game parameters** -- look for default constants and the `GameParameters` section. Note which params affect board size, game length, etc.
-
-3. **Game type** -- check for:
-   - `Information::PERFECT_INFORMATION` vs `IMPERFECT_INFORMATION`
-   - `Dynamics::SEQUENTIAL` vs `SIMULTANEOUS`
-   - Number of players
-
-4. **Action encoding** -- understand `NumDistinctActions()` and how actions are serialized.
-
-**Why this matters:**
-- **Imperfect information games** (e.g., Battleship, poker): each player gets a DIFFERENT `observationString`. The renderer must handle per-player observations via `step[0].observation.observationString` and `step[1].observation.observationString` separately. You'll likely want to show multiple boards.
-- **Perfect information games** (e.g., Breakthrough, Pentago): all players see the same board. A single `getObservationString(step)` that returns the first non-empty observation is sufficient.
-
-### Choose appropriate parameters
-
-Default parameters may create games that are too large for a good visualizer experience. For example, Battleship defaults to 10x10 with 5 ships and 50 shots. Choose smaller parameters that keep the game visually clear:
-
-```
-# Too large:
-"battleship"
-
-# Better for visualizer:
-"battleship(board_width=5,board_height=5,ship_sizes=[2;3],ship_values=[1;1],num_shots=10,allow_repeated_shots=false)"
-```
-
-Note: list parameters in OpenSpiel use semicolons inside square brackets: `ship_sizes=[2;3;4]`.
-
-## Step 2: Register the game in GAMES_LIST
-
-Edit `kaggle_environments/envs/open_spiel_env/open_spiel_env.py` and add the game string to `GAMES_LIST` (around line 850). Keep alphabetical order.
-
-```python
-GAMES_LIST = [
-    # ...existing games...
-    "<game_name>",                           # simple
-    "<game_name>(board_size=5,param=val)",   # with parameters
-]
-```
-
-The environment will be registered as `open_spiel_<game_name>` and accessible via `make("open_spiel_<game_name>")`.
-
-## Step 3: Generate test-replay.json
-
-**Important:** The built-in `"random"` agent requires `includeLegalActions: True` to function. Without it, the agent cannot determine legal moves and will immediately produce an invalid action, ending the game in 2-3 steps.
-
-```bash
-.venv/bin/python -c "
-from kaggle_environments import make
-import json
-env = make('open_spiel_$GAME_NAME', debug=True, configuration={'includeLegalActions': True})
-env.run(['random', 'random'])
-replay = env.toJSON()
-with open('test-replay.json', 'w') as f:
-    json.dump(replay, f, indent=2)
-print(f'Generated replay with {len(replay[\"steps\"])} steps')
-print(f'Statuses: {replay[\"statuses\"]}')
-print(f'Rewards: {replay[\"rewards\"]}')
-"
-```
-
-Verify the replay has a reasonable number of steps (not 2-3, which indicates the random agent failed). Inspect a few observation strings to confirm they match the format you studied in Step 1:
-
-```bash
-.venv/bin/python -c "
-import json
-with open('test-replay.json') as f:
-    replay = json.load(f)
-# Show a mid-game observation
-mid = len(replay['steps']) // 2
-print(replay['steps'][mid][0]['observation'].get('observationString', '(none)'))
-"
-```
-
-Move this file to the replay directory after creating the project structure.
-
-## Step 4: Create the visualizer directory
-
-Path: `kaggle_environments/envs/open_spiel_env/games/<game_name>/visualizer/default/`
-
-Also create an empty `kaggle_environments/envs/open_spiel_env/games/<game_name>/__init__.py`.
-
-### File tree
-
-```
-games/<game_name>/
-  __init__.py                            (empty)
-  visualizer/default/
-    package.json
-    vite.config.ts
-    tsconfig.json
-    index.html
-    replays/test-replay.json             (from Step 3)
-    src/
-      main.ts
-      renderer.ts
-      style.css
-```
-
-### package.json
-
-```json
-{
-  "name": "@kaggle-environments/open-spiel-<game_name>-visualizer",
-  "private": true,
-  "version": "0.0.0",
-  "type": "module",
-  "scripts": {
-    "dev": "vite",
-    "dev-with-replay": "cross-env VITE_REPLAY_FILE=./replays/test-replay.json vite",
-    "build": "tsc && vite build",
-    "preview": "vite preview"
-  },
-  "devDependencies": {
-    "cross-env": "^10.1.0",
-    "typescript": "^5.0.0",
-    "vite": "^5.0.0"
-  },
-  "dependencies": {
-    "@kaggle-environments/core": "workspace:*"
-  }
-}
-```
-
-### vite.config.ts
-
-```typescript
-import { defineConfig, mergeConfig } from 'vite';
-import baseConfig from '../../../../../../../web/vite.config.base';
-
-export default mergeConfig(
-  baseConfig,
-  defineConfig({
-    publicDir: 'replays',
-  })
-);
-```
-
-Note: OpenSpiel visualizers are 7 levels deep from the repo root (`kaggle_environments/envs/open_spiel_env/games/<name>/visualizer/default/`), so the relative path to `web/` is `../../../../../../../`.
-
-### tsconfig.json
-
-```json
-{
-  "extends": "../../../../../../../web/tsconfig.base.json",
-  "include": ["src"],
-  "compilerOptions": {
-    "allowJs": true
-  }
-}
-```
-
-### index.html
-
-```html
-<!DOCTYPE html>
-<html lang="en">
-  <head>
-    <meta charset="UTF-8" />
-    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
-    <title><Game Name> Visualizer</title>
-    <link rel="preconnect" href="https://fonts.googleapis.com" />
-    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
-    <link href="https://fonts.googleapis.com/css2?family=Mynerve&display=swap" rel="stylesheet" />
-  </head>
-  <body>
-    <div id="app"></div>
-    <script type="module" src="/src/main.ts"></script>
-  </body>
-</html>
-```
-
-### src/style.css
-
-```css
-@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
-
-html, body, #app {
-  width: 100%;
-  height: 100%;
-  margin: 0;
-  padding: 0;
-  overflow: hidden;
-}
-
-.renderer-container {
-  display: flex;
-  flex-direction: column;
-  align-items: center;
-  width: 100%;
-  height: 100%;
-  min-height: 0;
-  background-color: #f5f1e2;
-  overflow: hidden;
-  font-family: 'Inter', sans-serif;
-  box-sizing: border-box;
-  padding: 12px;
-  color: #050001;
-  container-type: inline-size;
-}
-
-.renderer-container canvas {
-  position: relative;
-  flex-grow: 1;
-  width: 100%;
-  max-width: 512px;
-  min-height: 0;
-}
-
-.sketched-border {
-  border: 1px dashed #3c3b37;
-}
-
-.header {
-  display: flex;
-  justify-content: center;
-  align-items: center;
-  width: 100%;
-  padding: 8px 0;
-  font-size: 1.1rem;
-  font-weight: 600;
-  flex-shrink: 0;
-  gap: 16px;
-}
-
-.status-container {
-  display: flex;
-  align-items: center;
-  justify-content: center;
-  padding: 5px 16px;
-  background-color: white;
-  font-size: 0.9rem;
-  font-weight: 600;
-  min-height: 18px;
-  min-width: 200px;
-  margin-top: 8px;
-  flex-shrink: 0;
-}
-```
-
-### src/main.ts
-
-```typescript
-import { createReplayVisualizer, ReplayAdapter } from '@kaggle-environments/core';
-import { renderer } from './renderer';
-import './style.css';
-
-const app = document.getElementById('app');
-if (!app) {
-  throw new Error('Could not find app element');
-}
-
-if (import.meta.env?.DEV && import.meta.hot) {
-  import.meta.hot.accept();
-}
-
-createReplayVisualizer(
-  app,
-  new ReplayAdapter({
-    gameName: 'open_spiel_<game_name>',
-    renderer: renderer as any,
-    ui: 'side-panel',
-  })
-);
-```
-
-## Visual style guide
-
-All OpenSpiel visualizers should match a **paper-and-ink** aesthetic. The goal is a warm, tactile, stationery-like look -- as if the game were drawn on paper with hand-sketched borders.
-
-### Aesthetic principles
-
-1. **Warm paper-like background.** Use a warm parchment background (`#f5f1e2`) instead of dark or saturated colors. The canvas should have a transparent background so the page color shows through from the DOM layer beneath.
-
-2. **Light color scheme.** Use near-black text (`#050001`) on the paper background. Avoid dark backgrounds, white-on-dark text, and neon/diffused glows.
-
-3. **Sketched borders.** Use dashed borders (`1px dashed #3c3b37`) on containers instead of solid CSS borders or diffused `box-shadow`. This gives a hand-drawn, woodblock-print quality.
-
-4. **High-resolution text.** Prefer **DOM elements** for all text, labels, and status displays rather than canvas text. Canvas `fillText` cannot use web fonts reliably. Use canvas only for the game board/grid itself. Wrap the canvas in a flex container alongside DOM-based status elements.
-
-5. **Two typefaces.** Use **Inter** (sans-serif) for all UI text -- player names, scores, labels, controls. Use **Mynerve** (cursive) as an optional accent font for annotations, commentary, and decorative text. Load Inter via CSS `@import` in `style.css` and Mynerve via `<link>` in `index.html`.
-
-6. **Hard offset shadows.** For modals and popover panels, use hard black offset shadows (e.g., `box-shadow: -0.75rem 0.75rem`) rather than soft diffused drop-shadows. This matches the woodblock/stamp aesthetic.
-
-7. **Responsive sizing.** Use CSS container queries (`@container (max-width: 680px)`) for responsive layout adjustments. Set `container-type: inline-size` on the main wrapper. The **680px** breakpoint is the mobile threshold. Use `rem`-based font sizes (`0.8rem`, `1rem`, `1.1rem`).
-
-### Color palette
-
-| Element | Color / Treatment | Notes |
-|---------|------------------|-------|
-| Page background | `#f5f1e2` | Warm parchment, never dark or saturated |
-| Primary text | `#050001` | Near-black, used on all body text |
-| Secondary text | `#444343` | Softer dark for table values and metadata |
-| Container background | `white` | Player cards, score tables, panels |
-| Active player highlight | `#bdeeff` | Light blue background on the active player card |
-| Borders | `1px dashed #3c3b37` | Sketched look on containers |
-| Buttons / controls bg | `#f1f1f1` | Light gray for interactive elements |
-| Button shadow | `box-shadow: -0.125rem 0.125rem 0 #000` | Hard black offset, not diffused |
-| Canvas background | Transparent | Page background shows through from DOM layer |
-| Board grid lines | `1px dashed #3c3b37` or `1px solid #3c3b37` | Sketched look for grid lines on canvas |
-| Board labels | `#000000` (Inter font) | Column/row labels around the board |
-
-### Rendering approach
-
-Use a **hybrid DOM + canvas** architecture:
-
-- **Canvas**: game board grid, pieces, move highlights, board decorations. Keep the canvas background transparent so the page background shows through.
-- **DOM**: player names, score tables, turn indicators, game-over modals, annotations. Use `border: 1px dashed #3c3b37` on containers.
-
-Cap the canvas at a maximum width (e.g., `max-width: 512px`) and use `aspect-ratio: 1` for square boards.
-
-```
-+------------------------------------------+
-|  [DOM] Header: player cards with         |
-|  dashed borders                          |
-+------------------------------------------+
-|                                          |
-|  [Canvas] Game board (transparent bg)    |
-|  on warm parchment background            |
-|                                          |
-+------------------------------------------+
-|  [DOM] Status / score with dashed        |
-|  borders, annotations in Mynerve font   |
-+------------------------------------------+
-```
-
-### Sketched border container pattern
-
-Use white containers with a dashed border for a hand-drawn look:
-
-```typescript
-const statusContainer = document.createElement('div');
-Object.assign(statusContainer.style, {
-  padding: '5px 12px',
-  backgroundColor: 'white',
-  border: '1px dashed #3c3b37',
-  textAlign: 'center',
-  minWidth: '200px',
-  marginTop: '10px',
-  fontFamily: "'Inter', sans-serif",
-});
-```
-
-### Active player indication
-
-Use background color change and scale transform on player containers:
-
-```css
-.player {
-  background-color: white;
-  transition: scale 300ms;
-}
-
-.player.active {
-  background-color: #bdeeff;
-  scale: 1.1;
-}
-```
-
-### Game-over presentation
-
-Use a modal overlay with staggered reveal animations:
-
-```css
-.game-over-modal {
-  background-color: #f5f1e2;
-  color: #050001;
-}
-```
-
-Display results in a table with dashed borders. Use CSS `@starting-style` and `transition` for staggered element reveals.
-
-## Step 5: Write the renderer
-
-The renderer is the core of the visualizer. It is called on every step change and renders into the parent element using a mix of DOM elements and canvas.
-
-### Renderer architecture
-
-```typescript
-import type { RendererOptions } from '@kaggle-environments/core';
-
-// 1. Define a typed interface for the parsed game state
-interface GameState {
-  // Game-specific fields parsed from the observation string
-}
-
-// 2. Parse the observation string into your typed state
-function parseObservation(obsString: string): GameState | null {
-  // Parse the OpenSpiel observation string format
-  // (the format you studied from the C++ source in Step 1)
-}
-
-// 3. Helpers to extract data from raw step arrays
-//    For PERFECT information games, use a single helper that finds the first obs:
-function getObservationString(step: any): string {
-  if (!step || !Array.isArray(step)) return '';
-  for (const player of step) {
-    const obs = player?.observation?.observationString;
-    if (obs) return obs;
-  }
-  return '';
-}
-
-//    For IMPERFECT information games, extract per-player observations:
-function getPlayerObservationString(step: any, playerIdx: number): string {
-  if (!step || !Array.isArray(step)) return '';
-  return step[playerIdx]?.observation?.observationString ?? '';
-}
-
-// 4. Helper to check if the game is over
-function isTerminal(step: any): boolean {
-  if (!step || !Array.isArray(step)) return false;
-  return step.some((p: any) => p?.status === 'DONE' || p?.observation?.isTerminal);
-}
-
-// 5. Helper to get current player
-function getCurrentPlayer(step: any): number {
-  if (!step || !Array.isArray(step)) return 0;
-  for (const player of step) {
-    const cp = player?.observation?.currentPlayer;
-    if (cp !== undefined && cp >= 0) return cp;
-  }
-  return 0;
-}
-
-// 6. Helper to get rewards
-function getRewards(step: any): [number, number] {
-  if (!step || !Array.isArray(step)) return [0, 0];
-  return [step[0]?.reward ?? 0, step[1]?.reward ?? 0];
-}
-
-// 7. Main renderer function
-export function renderer(options: RendererOptions) {
-  const { step, replay, parent } = options;
-  const steps = replay.steps as any[];
-  // ... rendering logic
-}
-```
-
-### Replay data shape
-
-Each step in `replay.steps` is an array of player observations:
-
-```
-replay.steps[stepIndex][playerIndex].observation.observationString  -- the OpenSpiel state string
-replay.steps[stepIndex][playerIndex].observation.currentPlayer      -- whose turn it is
-replay.steps[stepIndex][playerIndex].observation.isTerminal         -- game over flag
-replay.steps[stepIndex][playerIndex].action.submission              -- action taken (-1 = not acting)
-replay.steps[stepIndex][playerIndex].reward                        -- cumulative reward
-replay.steps[stepIndex][playerIndex].status                        -- "ACTIVE" or "DONE"
-```
-
-**Key detail for imperfect information games:** `step[0].observation.observationString` and `step[1].observation.observationString` contain DIFFERENT strings -- each player's private view. Parse both and render them (e.g., side-by-side boards for Battleship).
-
-### Visual design requirements
-
-Every visualizer MUST clearly communicate these four things:
-
-#### 1. Current actor (whose turn it is)
-
-- Show a **DOM header** at the top with the current player's name
-- Highlight the active player's card with a `#bdeeff` light blue background and `scale: 1.1` (see style guide)
-- On game over, show the result in a parchment-colored modal with a dashed-border table
-
-#### 2. Move taken (what just happened)
-
-- Compare the current step's state with the previous step's state to detect what changed
-- Highlight the move visually: glowing ring on placed piece, gold overlay on moved-from/moved-to squares, dashed outline on played pit, etc.
-- Show a brief textual description of the move when appropriate (e.g., "P1 fires B3: HIT!")
-
-#### 3. Move implications (what the move caused)
-
-- Show **deltas/diffs** when state values change: `+N` / `-N` badges near changed elements
-- Mark captured/removed pieces distinctly (red X, faded outline, "CAPTURED" label)
-- Highlight score changes with colored `+N` indicators near the score display
-- For games with complex mechanics (e.g., sowing seeds, rotating quadrants), visually indicate the affected region
-
-#### 4. Current score / game progress
-
-- Show scores in the header or a DOM stats element using player-colored text
-- Show piece counts, stones remaining, boxes claimed, hit/miss ratios, etc.
-- At game over, display the final result prominently in the status container
-
-### Handling game phases
-
-Some games have distinct phases (e.g., Battleship has ship placement then war). Detect the phase from the observation state and adjust the display accordingly:
-- Show phase name in the header or status container
-- Adapt what stats are shown (e.g., no shot stats during placement)
-- Potentially change the visual emphasis
-
-### Renderer template (hybrid DOM + canvas)
-
-```typescript
-export function renderer(options: RendererOptions) {
-  const { step, replay, parent } = options;
-  const steps = replay.steps as any[];
-
-  // Re-create DOM structure each call (simple, reliable)
-  parent.innerHTML = `
-    <div class="renderer-container">
-      <div class="header"></div>
-      <canvas></canvas>
-      <div class="status-container sketched-border"></div>
-    </div>
-  `;
-  const container = parent.querySelector('.renderer-container') as HTMLDivElement;
-  const header = parent.querySelector('.header') as HTMLDivElement;
-  const canvas = parent.querySelector('canvas') as HTMLCanvasElement;
-  const statusContainer = parent.querySelector('.status-container') as HTMLDivElement;
-  if (!canvas || !replay) return;
-
-  // Size canvas to fill its flex area
-  canvas.width = 0;
-  canvas.height = 0;
-  const { width, height } = canvas.getBoundingClientRect();
-  canvas.width = width;
-  canvas.height = height;
-
-  const c = canvas.getContext('2d');
-  if (!c) return;
-
-  // Parse current state
-  const currentStep = steps[step];
-  const obsString = getObservationString(currentStep);
-  const state = parseObservation(obsString);
-
-  // Parse previous state for diff visualization
-  let prevState: GameState | null = null;
-  if (step > 0) {
-    prevState = parseObservation(getObservationString(steps[step - 1]));
-  }
-
-  if (!state) {
-    statusContainer.textContent = 'Waiting for game data...';
-    return;
-  }
-
-  const terminal = isTerminal(currentStep);
-  const cp = getCurrentPlayer(currentStep);
-
-  // --- 1. Build header (DOM) ---
-  // Player names in sketched-border cards, active player highlighted
-  const p1Active = !terminal && cp === 0;
-  const p2Active = !terminal && cp === 1;
-  header.innerHTML = `
-    <span class="sketched-border" style="padding: 4px 12px; background-color: ${p1Active ? '#bdeeff' : 'white'}; font-weight: 700;">Player 1</span>
-    <span style="color: #444343;">vs</span>
-    <span class="sketched-border" style="padding: 4px 12px; background-color: ${p2Active ? '#bdeeff' : 'white'}; font-weight: 700;">Player 2</span>
-  `;
-
-  // --- 2. Draw game board on canvas ---
-  // Canvas is transparent -- page background shows through from the DOM layer
-  c.clearRect(0, 0, width, height);
-  // ... draw board, pieces, move highlights ...
-
-  // --- 3. Update status container (DOM) ---
-  if (terminal) {
-    const rewards = getRewards(currentStep);
-    let msg = 'Game Over -- Draw';
-    if (rewards[0] > rewards[1]) msg = 'Game Over -- Player 1 wins!';
-    else if (rewards[1] > rewards[0]) msg = 'Game Over -- Player 2 wins!';
-    statusContainer.textContent = msg;
-    statusContainer.style.fontWeight = '700';
-  } else {
-    statusContainer.textContent = `Player ${cp + 1}'s turn`;
-  }
-}
-```
-
-### Layout guidelines
-
-- **Header** (DOM): player names and title at the top, flexbox centered with gap
-- **Canvas**: game board centered in the remaining flex space, scaled responsively
-- **Status container** (DOM): white container with dashed border at the bottom with game state text
-- Use `Math.min()` to cap board size and ensure it doesn't overflow
-- Keep margins around the board for labels (draw labels on canvas or use positioned DOM elements)
-- For multi-board games (imperfect info): arrange boards in a 2x2 or side-by-side grid on the canvas
-
-## Step 6: Build and verify
-
-```bash
-# From repo root
-pnpm install
-
-# Build (catches TypeScript errors)
-pnpm build   # select your game from the picker
-
-# Run dev server with replay
-pnpm dev-with-replay   # select your game from the picker
-
-# Or run dev server directly for this specific game
-cd kaggle_environments/envs/open_spiel_env/games/<game_name>/visualizer/default
-pnpm dev-with-replay
-```
-
-**Common build errors:**
-- Unused variables/parameters: remove them
-- Missing type imports: ensure `import type { RendererOptions } from '@kaggle-environments/core'`
-
-### Verification checklist
-
-- [ ] Game string added to `GAMES_LIST` in `open_spiel_env.py`
-- [ ] `games/<game_name>/__init__.py` exists (empty is fine)
-- [ ] `test-replay.json` has a full game (not just 2-3 steps from invalid actions)
-- [ ] `pnpm install` succeeds from repo root
-- [ ] `pnpm build` passes with no TypeScript errors
-- [ ] `pnpm dev-with-replay` launches and the game appears in the picker
-- [ ] Stepping through the replay shows the board updating correctly
-- [ ] Current player is clearly indicated with color
-- [ ] Last move is highlighted (glow, ring, overlay, etc.)
-- [ ] Move diffs are shown (deltas, captures, removed pieces)
-- [ ] Score / game progress is visible in the header or status container
-- [ ] Game over state displays the result clearly
-- [ ] Board scales responsively (try resizing the window)
-- [ ] Text uses Inter font (loaded via Google Fonts import in style.css)
-- [ ] Status/turn info is in a DOM container with dashed border (not canvas text)
-- [ ] Active player card has `#bdeeff` background highlight
-- [ ] `pnpm format` passes (run from repo root)
-
-## Reference implementations
-
-Study these completed visualizers for acceptable code patterns:
-
-- OpenSpiel Chess
-- ConnectX
-
-## Troubleshooting
-
-**Replay has only 2-3 steps / "INVALID ACTION DETECTED":** The built-in `"random"` agent needs `includeLegalActions: True` in the configuration to function. Without it, the agent cannot determine which actions are legal. Generate the replay with:
-```python
-env = make('open_spiel_$GAME_NAME', debug=True, configuration={'includeLegalActions': True})
-```
-
-**"Game not found" when running `make()`:** Ensure the game string is in `GAMES_LIST` and spelled correctly. Verify with:
-```bash
-.venv/bin/python -c "import pyspiel; print(pyspiel.load_game('$GAME_NAME'))"
-```
-
-**Observation string is empty:** Some games use `information_state_string()` instead of `observation_string()`. The framework handles this automatically -- check the game type in the OpenSpiel source for `provides_observation_string` vs `provides_information_state_string`.
-
-**Canvas is blank:** Check the browser console for errors. Common issues: incorrect CSS (canvas has 0 height), parse function returning null because the observation string format doesn't match expectations. Print the raw observation string to debug.
-
-**Game requires list parameters:** OpenSpiel uses semicolons inside square brackets for lists: `ship_sizes=[2;3;4]`, `ship_values=[1.0;1.0;1.0]`. These go directly in the game string in `GAMES_LIST`.
diff --git a/.agents/skills/create-visualizer/SKILL.md b/.agents/skills/create-visualizer/SKILL.md
@@ -1,25 +1,40 @@
 # Create / Update a Visualizer
 
-Each visualizer lives at `kaggle_environments/envs/<name>/visualizer/default/` as a Vite + TypeScript project within the pnpm workspace.
+Build a web visualizer for any Kaggle game environment -- regular or OpenSpiel. Each visualizer is a Vite + TypeScript project within the pnpm workspace.
 
-## Step 1: Create the project structure
+**Related skills:**
+- `create-environment` -- if you need to build the Python backend for a custom game first
+- `onboard-open-spiel-game` -- if you need to register or configure an OpenSpiel game first
 
-Create `kaggle_environments/envs/<name>/visualizer/default/` with:
+## Step 1: Determine your variant
+
+| Variant | Directory | Relative path to `web/` | `gameName` |
+|---------|-----------|------------------------|------------|
+| Regular env | `kaggle_environments/envs/<name>/visualizer/default/` | `../../../../../` (5 levels) | `"<name>"` |
+| OpenSpiel env | `kaggle_environments/envs/open_spiel_env/games/<name>/visualizer/default/` | `../../../../../../../` (7 levels) | `"open_spiel_<name>"` |
+
+Both variants use the same boilerplate, shared workspace dependency, and renderer interface. The only differences are the directory depth (which affects relative paths to base configs) and the replay data shape.
+
+## Step 2: Create the project structure
+
+Create the visualizer directory with these files:
 
 ```
 visualizer/default/
 ├── package.json
 ├── vite.config.ts
 ├── tsconfig.json
 ├── index.html
+├── replays/test-replay.json    (for dev -- see "Generate a test replay" below)
 └── src/
     ├── main.ts
-    └── renderer.ts
+    ├── renderer.ts
+    └── style.css
 ```
 
 This directory is automatically part of the pnpm workspace (via root `pnpm-workspace.yaml` pattern `kaggle_environments/envs/*/visualizer/*`).
 
-## Step 2: Write the boilerplate files
+For OpenSpiel games, also create an empty `games/<name>/__init__.py` if one doesn't exist.
 
 ### `package.json`
 
@@ -31,6 +46,7 @@ This directory is automatically part of the pnpm workspace (via root `pnpm-works
   "type": "module",
   "scripts": {
     "dev": "vite",
+    "dev-with-replay": "cross-env VITE_REPLAY_FILE=./replays/test-replay.json vite",
     "build": "tsc && vite build",
     "preview": "vite preview"
   },
@@ -51,9 +67,15 @@ Add any game-specific dependencies (e.g., `three` for 3D, `pixi.js` for 2D sprit
 
 ```typescript
 import { defineConfig, mergeConfig } from "vite";
+// Adjust path depth: 5 levels for regular envs, 7 for OpenSpiel
 import baseConfig from "../../../../../web/vite.config.base";
 
-export default mergeConfig(baseConfig, defineConfig({}));
+export default mergeConfig(
+  baseConfig,
+  defineConfig({
+    publicDir: "replays",
+  })
+);
 ```
 
 The base config (at `web/vite.config.base.ts`) provides: tsconfigPaths, TypeScript checker, cssInjectedByJs plugin, dev server on port 5173, relative base path for builds, and CORS.
@@ -70,7 +92,7 @@ The base config (at `web/vite.config.base.ts`) provides: tsconfigPaths, TypeScri
 }
 ```
 
-The base config (at `web/tsconfig.base.json`) provides: ESNext target/module, strict mode, JSX react-jsx, and the `@kaggle-environments/core` path alias.
+Adjust the `extends` path to match your variant's depth.
 
 ### `index.html`
 
@@ -81,6 +103,9 @@ The base config (at `web/tsconfig.base.json`) provides: ESNext target/module, st
     <meta charset="UTF-8" />
     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
     <title><Name> Visualizer</title>
+    <link rel="preconnect" href="https://fonts.googleapis.com" />
+    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
+    <link href="https://fonts.googleapis.com/css2?family=Mynerve&display=swap" rel="stylesheet" />
   </head>
   <body>
     <div id="app"></div>
@@ -91,26 +116,34 @@ The base config (at `web/tsconfig.base.json`) provides: ESNext target/module, st
 
 The `<div id="app">` is required -- `createReplayVisualizer` mounts to it.
 
-## Step 3: Write the entry point (`src/main.ts`)
+### `src/style.css`
+
+See [visualizer-style-guide.md](visualizer-style-guide.md) for the standard CSS and the full visual design system.
+
+### `src/main.ts`
 
 ```typescript
 import { createReplayVisualizer, ReplayAdapter } from "@kaggle-environments/core";
 import { renderer } from "./renderer";
+import "./style.css";
 
 const app = document.getElementById("app");
-if (app) {
-  if (import.meta.env?.DEV && import.meta.hot) {
-    import.meta.hot.accept();
-  }
-  createReplayVisualizer(
-    app,
-    new ReplayAdapter({
-      gameName: "<name>",
-      renderer: renderer,
-      ui: "inline",
-    })
-  );
+if (!app) {
+  throw new Error("Could not find app element");
 }
+
+if (import.meta.env?.DEV && import.meta.hot) {
+  import.meta.hot.accept();
+}
+
+createReplayVisualizer(
+  app,
+  new ReplayAdapter({
+    gameName: "<name>",           // must match the registered env name
+    renderer: renderer as any,
+    ui: "side-panel",             // "side-panel" (with reasoning logs) or "inline"
+  })
+);
 ```
 
 ### ReplayAdapter options
@@ -125,47 +158,141 @@ if (app) {
 | `layout` | string | `"side-by-side"` or `"stacked"` |
 | `initialSpeed` | number | Playback speed multiplier |
 
-## Step 4: Write the renderer (`src/renderer.ts`)
+### Generate a test replay
 
-The renderer function is called on every step change. It receives a `RendererOptions` object and should draw into the provided `parent` element.
+For regular environments:
+
+```bash
+uv run python -c "
+from kaggle_environments import make
+import json
+env = make('<name>', debug=True)
+env.run(['agent1', 'agent2'])
+with open('test-replay.json', 'w') as f:
+    json.dump(env.toJSON(), f, indent=2)
+print(f'Generated replay with {len(env.toJSON()[\"steps\"])} steps')
+"
+```
+
+For OpenSpiel environments (the `"random"` agent needs `includeLegalActions`):
+
+```bash
+uv run python -c "
+from kaggle_environments import make
+import json
+env = make('open_spiel_<name>', debug=True, configuration={'includeLegalActions': True})
+env.run(['random', 'random'])
+replay = env.toJSON()
+with open('test-replay.json', 'w') as f:
+    json.dump(replay, f, indent=2)
+print(f'Generated replay with {len(replay[\"steps\"])} steps')
+print(f'Statuses: {replay[\"statuses\"]}')
+"
+```
+
+Verify the replay has a reasonable number of steps (not 2-3, which indicates the agent failed).
+
+## Step 3: Understand the replay data shape
+
+The renderer function receives a `RendererOptions` object. The shape of `replay.steps` differs between regular and OpenSpiel environments.
+
+### Regular environments
+
+Steps are transformed through the core adapter into `BaseGameStep` objects:
 
 ```typescript
-import type { RendererOptions } from "@kaggle-environments/core";
+interface BaseGameStep {
+  step: number;
+  players: BaseGamePlayer[];
+}
 
-export function renderer(options: RendererOptions) {
-  const { replay, parent, step, setStep, setPlaying } = options;
-  const currentStep = replay.steps[step];
-  const config = replay.configuration;
+interface BaseGamePlayer {
+  id: number;
+  name: string;
+  thumbnail: string;
+  isTurn: boolean;
+  actionDisplayText?: string;
+  thoughts?: string;
+}
+```
 
-  // Create DOM elements on first call, update on subsequent calls.
-  // The parent element persists across calls -- reuse elements.
+Access via `replay.steps[step].players[i]`. For raw env data, you can write a custom transformer (see "Optional: Add a transformer" below).
 
-  let canvas = parent.querySelector("canvas") as HTMLCanvasElement | null;
-  if (!canvas) {
-    canvas = document.createElement("canvas");
-    parent.appendChild(canvas);
-  }
+### OpenSpiel environments
 
-  const ctx = canvas.getContext("2d");
-  if (!ctx) return;
+Steps are raw arrays from the unified interpreter:
 
-  // Size the canvas to fit the container
-  const width = parent.clientWidth || 400;
-  const height = parent.clientHeight || 400;
-  canvas.width = width;
-  canvas.height = height;
+```typescript
+// Each step is an array of player observations:
+replay.steps[stepIndex][playerIndex].observation.observationString  // game state (JSON if proxy exists)
+replay.steps[stepIndex][playerIndex].observation.currentPlayer      // whose turn it is
+replay.steps[stepIndex][playerIndex].observation.isTerminal         // game over flag
+replay.steps[stepIndex][playerIndex].action.submission              // action taken (-1 = not acting)
+replay.steps[stepIndex][playerIndex].reward                        // cumulative reward
+replay.steps[stepIndex][playerIndex].status                        // "ACTIVE" or "DONE"
+```
+
+#### Games with a proxy (default)
 
-  // Clear and draw for the current step
-  ctx.clearRect(0, 0, width, height);
+If the game has a proxy (see `onboard-open-spiel-game` skill -- this is the default), the `observationString` is **JSON**. The renderer just parses it:
 
-  // Access step data:
-  // currentStep.players[i].id, .name, .isTurn, .actionDisplayText
-  // For raw env data, use replay.steps (array of raw step arrays from env.toJSON())
+```typescript
+function getObservation(step: any, playerIdx: number): any | null {
+  const raw = step?.[playerIdx]?.observation?.observationString;
+  if (!raw) return null;
+  try { return JSON.parse(raw); } catch { return null; }
+}
+
+// Usage in renderer:
+const obs = getObservation(currentStep, 0);
+// obs.board, obs.current_player, obs.is_terminal, obs.winner, obs.scores, obs.last_action, etc.
+```
+
+The proxy's `state_dict()` method determines what fields are available. See `onboard-open-spiel-game` for the standard fields: `board`, `current_player`, `is_terminal`, `winner`, `scores`, `last_action`, `phase`.
+
+For **perfect information** games, both players get the same observation. For **imperfect information** games, each player gets a different JSON object containing only their private view -- parse both and render them (e.g., side-by-side boards).
+
+#### Games without a proxy (raw text observations)
+
+Some games may not have a proxy (e.g., games added to `GAMES_LIST` only). In this case, `observationString` is the raw text from OpenSpiel's `ObservationString()` or `InformationStateString()`. You'll need to parse it manually:
 
-  // ... your rendering logic ...
+```typescript
+function getObservationString(step: any, playerIdx: number = 0): string {
+  return step?.[playerIdx]?.observation?.observationString ?? '';
 }
 ```
 
+Study the game's C++ source at `open_spiel/games/<game_name>/` (`.h`/`.cc` files) to understand the format of `ObservationString` and `ToString`.
+
+#### Common OpenSpiel step helpers
+
+These helpers work regardless of whether the game has a proxy:
+
+```typescript
+function isTerminal(step: any): boolean {
+  if (!step || !Array.isArray(step)) return false;
+  return step.some((p: any) => p?.status === 'DONE' || p?.observation?.isTerminal);
+}
+
+function getCurrentPlayer(step: any): number {
+  if (!step || !Array.isArray(step)) return 0;
+  for (const player of step) {
+    const cp = player?.observation?.currentPlayer;
+    if (cp !== undefined && cp >= 0) return cp;
+  }
+  return 0;
+}
+
+function getRewards(step: any): [number, number] {
+  if (!step || !Array.isArray(step)) return [0, 0];
+  return [step[0]?.reward ?? 0, step[1]?.reward ?? 0];
+}
+```
+
+## Step 4: Write the renderer (`src/renderer.ts`)
+
+The renderer function is called on every step change. It receives a `RendererOptions` object and should draw into the provided `parent` element.
+
 ### RendererOptions fields
 
 | Field | Type | Description |
@@ -178,45 +305,121 @@ export function renderer(options: RendererOptions) {
 | `registerPlaybackHandlers` | function | Register custom play/pause/step handlers |
 | `agents` | any[] | Agent metadata |
 
-### Replay data shape
+### Visual design requirements
+
+Every visualizer MUST clearly communicate these four things:
+
+1. **Current actor (whose turn it is):** Show player names in the header, highlight the active player's card with `#bdeeff` background and `scale: 1.1`.
+
+2. **Move taken (what just happened):** Compare current and previous step states to detect what changed. Highlight the move visually (glowing ring, gold overlay, dashed outline, etc.).
+
+3. **Move implications (what the move caused):** Show deltas/diffs when state values change (`+N` / `-N` badges). Mark captured/removed pieces distinctly. Highlight score changes.
+
+4. **Current score / game progress:** Show scores, piece counts, progress indicators. At game over, display the final result prominently.
 
-The `replay` object matches the environment's `toJSON()` output transformed through the core adapter:
+### Renderer template
 
 ```typescript
-interface ReplayData {
-  name: string;           // environment name
-  version: string;
-  steps: BaseGameStep[];  // transformed steps (or raw if no transformer)
-  configuration: Record<string, any>;
-}
+import type { RendererOptions } from "@kaggle-environments/core";
 
-interface BaseGameStep {
-  step: number;
-  players: BaseGamePlayer[];
-}
+export function renderer(options: RendererOptions) {
+  const { step, replay, parent } = options;
+  const steps = replay.steps as any[];
+
+  // Re-create DOM structure each call (simple, reliable)
+  parent.innerHTML = `
+    <div class="renderer-container">
+      <div class="header"></div>
+      <canvas></canvas>
+      <div class="status-container sketched-border"></div>
+    </div>
+  `;
+  const header = parent.querySelector('.header') as HTMLDivElement;
+  const canvas = parent.querySelector('canvas') as HTMLCanvasElement;
+  const statusContainer = parent.querySelector('.status-container') as HTMLDivElement;
+  if (!canvas || !replay) return;
+
+  // Size canvas to fill its flex area
+  canvas.width = 0;
+  canvas.height = 0;
+  const { width, height } = canvas.getBoundingClientRect();
+  canvas.width = width;
+  canvas.height = height;
 
-interface BaseGamePlayer {
-  id: number;
-  name: string;
-  thumbnail: string;
-  isTurn: boolean;
-  actionDisplayText?: string;
-  thoughts?: string;
+  const c = canvas.getContext('2d');
+  if (!c) return;
+
+  const currentStep = steps[step];
+
+  // --- Parse game state (game-specific) ---
+  // For regular envs: currentStep.players[i]
+  // For OpenSpiel (with proxy): JSON.parse(currentStep[0].observation.observationString)
+  // For OpenSpiel (no proxy): parse raw text from currentStep[0].observation.observationString
+
+  // --- 1. Build header (DOM) ---
+  // Player names in sketched-border cards, active player highlighted
+  header.innerHTML = `
+    <span class="sketched-border" style="padding: 4px 12px; background-color: white; font-weight: 700;">Player 1</span>
+    <span style="color: #444343;">vs</span>
+    <span class="sketched-border" style="padding: 4px 12px; background-color: white; font-weight: 700;">Player 2</span>
+  `;
+
+  // --- 2. Draw game board on canvas ---
+  c.clearRect(0, 0, width, height);
+  // ... draw board, pieces, move highlights ...
+
+  // --- 3. Update status container (DOM) ---
+  statusContainer.textContent = 'Game status here';
 }
 ```
 
-If you need raw step data (direct access to observations, actions, rewards as defined in the spec), you can write a custom transformer or access the raw steps before transformation.
-
 ### Rendering tips
 
-- **Reuse DOM elements:** The renderer is called on every step change. Don't recreate the entire DOM each time -- create on first call, update on subsequent calls.
+- **Reuse DOM elements:** The renderer is called on every step change. The example above recreates innerHTML for simplicity, but for performance-sensitive games, create on first call and update on subsequent calls.
 - **Canvas vs DOM:** Canvas works well for game boards. Plain DOM/HTML works for text-heavy games.
 - **React alternative:** Pass `GameRenderer` (a React component) to `ReplayAdapter` instead of `renderer` for React-based visualizers. The component receives the same data as props.
 - **Responsive sizing:** Use `parent.clientWidth` / `parent.clientHeight` to size your rendering area.
 
-## Step 5: Integrate with the environment
+### Follow the style guide
+
+See [visualizer-style-guide.md](visualizer-style-guide.md) for the complete visual design system -- colors, fonts, layout patterns, and CSS.
+
+## Step 5 (optional): Add a transformer
+
+If your game needs data preprocessing (e.g., parsing observation strings into structured step objects), add a transformer in `web/core/src/transformers/`.
+
+1. Create `web/core/src/transformers/<name>/`:
+   - `<name>ReplayTypes.ts` -- TypeScript types for raw and transformed steps
+   - `<name>Transformer.ts` -- transform function and step label/description helpers
+
+2. Register it in `web/core/src/transformers.ts`:
+   ```typescript
+   import { myGameTransformer, getMyGameStepLabel, getMyGameStepDescription } from './transformers/<name>/<name>Transformer';
+   import { MyGameStep } from './transformers/<name>/<name>ReplayTypes';
+
+   // In processEpisodeData switch:
+   case 'open_spiel_<name>':
+     transformedSteps = myGameTransformer(environment);
+     break;
+
+   // In getGameStepLabel switch:
+   case 'open_spiel_<name>':
+     return getMyGameStepLabel(gameStep as MyGameStep);
+
+   // In getGameStepDescription switch:
+   case 'open_spiel_<name>':
+     return getMyGameStepDescription(gameStep as MyGameStep);
+   ```
 
-In `<name>.py`, ensure `html_renderer()` reads the built visualizer output:
+3. Then use the transformed data in your renderer instead of parsing raw observations.
+
+**Reference transformers:** `web/core/src/transformers/chess/`, `web/core/src/transformers/connect_four/`, `web/core/src/transformers/go/`.
+
+A transformer is not required -- games with a proxy already get structured JSON observations, and simpler games can parse observation strings directly in the renderer.
+
+## Step 6: Integrate with the environment
+
+In the environment's Python module, ensure `html_renderer()` reads the built visualizer output:
 
 ```python
 def html_renderer():
@@ -227,7 +430,9 @@ def html_renderer():
     return ""
 ```
 
-## Step 6: Develop and build
+For OpenSpiel games, this is handled by the shared framework -- no per-game Python change is needed.
+
+## Step 7: Build and verify
 
 ```bash
 # Install dependencies (from repo root)
@@ -236,6 +441,9 @@ pnpm install
 # Run dev server with hot reload (interactive game picker)
 pnpm dev
 
+# Run dev server with a specific replay file
+pnpm dev-with-replay   # select your game from the picker
+
 # Build for production (interactive picker)
 pnpm build
 
@@ -249,22 +457,38 @@ pnpm test:e2e
 pnpm format
 ```
 
-During development, `pnpm dev` runs the `find-games.js` script which prompts you to select a game, then starts a Vite dev server with hot module replacement.
-
 ## Checklist
 
 - [ ] `package.json` has `@kaggle-environments/core` as `workspace:*` dependency
-- [ ] `vite.config.ts` extends `web/vite.config.base`
-- [ ] `tsconfig.json` extends `web/tsconfig.base.json`
+- [ ] `vite.config.ts` extends `web/vite.config.base` with correct relative path depth
+- [ ] `tsconfig.json` extends `web/tsconfig.base.json` with correct relative path depth
 - [ ] `index.html` has `<div id="app"></div>`
 - [ ] `src/main.ts` uses `createReplayVisualizer` + `ReplayAdapter`
+- [ ] `src/style.css` follows the [visualizer-style-guide.md](visualizer-style-guide.md)
 - [ ] Renderer handles first call (create elements) and subsequent calls (update)
-- [ ] `html_renderer()` in the Python env reads `dist/index.html`
+- [ ] Current actor, move taken, move implications, and score are all visible
+- [ ] `html_renderer()` in the Python env reads `dist/index.html` (regular envs only)
+- [ ] `test-replay.json` has a full game (not 2-3 steps from agent failure)
 - [ ] `pnpm build` produces output in `dist/`
 - [ ] `pnpm format` passes
+- [ ] If transformer: registered in `web/core/src/transformers.ts` switch statements
 
 ## Reference implementations
 
 - `kaggle_environments/envs/rps/visualizer/default/` -- simple canvas-based renderer
 - `kaggle_environments/envs/werewolf/visualizer/default/` -- more complex with custom transformer
+- `kaggle_environments/envs/open_spiel_env/games/connect_four/visualizer/default/` -- OpenSpiel visualizer
 - `web/core/src/index.ts` -- all exports from `@kaggle-environments/core`
+
+## Troubleshooting
+
+**Replay has only 2-3 steps / "INVALID ACTION DETECTED":** The OpenSpiel `"random"` agent needs `includeLegalActions: True` in the configuration. Generate the replay with:
+```python
+env = make('open_spiel_<name>', debug=True, configuration={'includeLegalActions': True})
+```
+
+**Canvas is blank:** Check the browser console for errors. Common issues: incorrect CSS (canvas has 0 height), parse function returning null because the observation string format doesn't match expectations. Print the raw observation string to debug.
+
+**Observation string is empty (OpenSpiel):** Some games use `information_state_string()` instead of `observation_string()`. The framework handles this automatically -- check the game type in the OpenSpiel source for `provides_observation_string` vs `provides_information_state_string`.
+
+**Game requires list parameters (OpenSpiel):** OpenSpiel uses semicolons inside square brackets for lists: `ship_sizes=[2;3;4]`, `ship_values=[1.0;1.0;1.0]`. These go directly in the game string in `GAMES_LIST`.
diff --git a/.agents/skills/create-visualizer/visualizer-style-guide.md b/.agents/skills/create-visualizer/visualizer-style-guide.md
@@ -0,0 +1,181 @@
+# Visualizer Style Guide
+
+All Kaggle environment visualizers should match a **paper-and-ink** aesthetic. The goal is a warm, tactile, stationery-like look -- as if the game were drawn on paper with hand-sketched borders.
+
+## Aesthetic principles
+
+1. **Warm paper-like background.** Use a warm parchment background (`#f5f1e2`) instead of dark or saturated colors. The canvas should have a transparent background so the page color shows through from the DOM layer beneath.
+
+2. **Light color scheme.** Use near-black text (`#050001`) on the paper background. Avoid dark backgrounds, white-on-dark text, and neon/diffused glows.
+
+3. **Sketched borders.** Use dashed borders (`1px dashed #3c3b37`) on containers instead of solid CSS borders or diffused `box-shadow`. This gives a hand-drawn, woodblock-print quality.
+
+4. **High-resolution text.** Prefer **DOM elements** for all text, labels, and status displays rather than canvas text. Canvas `fillText` cannot use web fonts reliably. Use canvas only for the game board/grid itself. Wrap the canvas in a flex container alongside DOM-based status elements.
+
+5. **Two typefaces.** Use **Inter** (sans-serif) for all UI text -- player names, scores, labels, controls. Use **Mynerve** (cursive) as an optional accent font for annotations, commentary, and decorative text. Load Inter via CSS `@import` in `style.css` and Mynerve via `<link>` in `index.html`.
+
+6. **Hard offset shadows.** For modals and popover panels, use hard black offset shadows (e.g., `box-shadow: -0.75rem 0.75rem`) rather than soft diffused drop-shadows. This matches the woodblock/stamp aesthetic.
+
+7. **Responsive sizing.** Use CSS container queries (`@container (max-width: 680px)`) for responsive layout adjustments. Set `container-type: inline-size` on the main wrapper. The **680px** breakpoint is the mobile threshold. Use `rem`-based font sizes (`0.8rem`, `1rem`, `1.1rem`).
+
+## Color palette
+
+| Element | Color / Treatment | Notes |
+|---------|------------------|-------|
+| Page background | `#f5f1e2` | Warm parchment, never dark or saturated |
+| Primary text | `#050001` | Near-black, used on all body text |
+| Secondary text | `#444343` | Softer dark for table values and metadata |
+| Container background | `white` | Player cards, score tables, panels |
+| Active player highlight | `#bdeeff` | Light blue background on the active player card |
+| Borders | `1px dashed #3c3b37` | Sketched look on containers |
+| Buttons / controls bg | `#f1f1f1` | Light gray for interactive elements |
+| Button shadow | `box-shadow: -0.125rem 0.125rem 0 #000` | Hard black offset, not diffused |
+| Canvas background | Transparent | Page background shows through from DOM layer |
+| Board grid lines | `1px dashed #3c3b37` or `1px solid #3c3b37` | Sketched look for grid lines on canvas |
+| Board labels | `#000000` (Inter font) | Column/row labels around the board |
+
+## Rendering approach
+
+Use a **hybrid DOM + canvas** architecture:
+
+- **Canvas**: game board grid, pieces, move highlights, board decorations. Keep the canvas background transparent so the page background shows through.
+- **DOM**: player names, score tables, turn indicators, game-over modals, annotations. Use `border: 1px dashed #3c3b37` on containers.
+
+Cap the canvas at a maximum width (e.g., `max-width: 512px`) and use `aspect-ratio: 1` for square boards.
+
+```
++------------------------------------------+
+|  [DOM] Header: player cards with         |
+|  dashed borders                          |
++------------------------------------------+
+|                                          |
+|  [Canvas] Game board (transparent bg)    |
+|  on warm parchment background            |
+|                                          |
++------------------------------------------+
+|  [DOM] Status / score with dashed        |
+|  borders, annotations in Mynerve font   |
++------------------------------------------+
+```
+
+## Sketched border container pattern
+
+Use white containers with a dashed border for a hand-drawn look:
+
+```typescript
+const statusContainer = document.createElement('div');
+Object.assign(statusContainer.style, {
+  padding: '5px 12px',
+  backgroundColor: 'white',
+  border: '1px dashed #3c3b37',
+  textAlign: 'center',
+  minWidth: '200px',
+  marginTop: '10px',
+  fontFamily: "'Inter', sans-serif",
+});
+```
+
+## Active player indication
+
+Use background color change and scale transform on player containers:
+
+```css
+.player {
+  background-color: white;
+  transition: scale 300ms;
+}
+
+.player.active {
+  background-color: #bdeeff;
+  scale: 1.1;
+}
+```
+
+## Game-over presentation
+
+Use a modal overlay with staggered reveal animations:
+
+```css
+.game-over-modal {
+  background-color: #f5f1e2;
+  color: #050001;
+}
+```
+
+Display results in a table with dashed borders. Use CSS `@starting-style` and `transition` for staggered element reveals.
+
+## Standard CSS (`style.css`)
+
+```css
+@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
+
+html, body, #app {
+  width: 100%;
+  height: 100%;
+  margin: 0;
+  padding: 0;
+  overflow: hidden;
+}
+
+.renderer-container {
+  display: flex;
+  flex-direction: column;
+  align-items: center;
+  width: 100%;
+  height: 100%;
+  min-height: 0;
+  background-color: #f5f1e2;
+  overflow: hidden;
+  font-family: 'Inter', sans-serif;
+  box-sizing: border-box;
+  padding: 12px;
+  color: #050001;
+  container-type: inline-size;
+}
+
+.renderer-container canvas {
+  position: relative;
+  flex-grow: 1;
+  width: 100%;
+  max-width: 512px;
+  min-height: 0;
+}
+
+.sketched-border {
+  border: 1px dashed #3c3b37;
+}
+
+.header {
+  display: flex;
+  justify-content: center;
+  align-items: center;
+  width: 100%;
+  padding: 8px 0;
+  font-size: 1.1rem;
+  font-weight: 600;
+  flex-shrink: 0;
+  gap: 16px;
+}
+
+.status-container {
+  display: flex;
+  align-items: center;
+  justify-content: center;
+  padding: 5px 16px;
+  background-color: white;
+  font-size: 0.9rem;
+  font-weight: 600;
+  min-height: 18px;
+  min-width: 200px;
+  margin-top: 8px;
+  flex-shrink: 0;
+}
+```
+
+## Standard `index.html` font links
+
+```html
+<link rel="preconnect" href="https://fonts.googleapis.com" />
+<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
+<link href="https://fonts.googleapis.com/css2?family=Mynerve&display=swap" rel="stylesheet" />
+```
diff --git a/.agents/skills/onboard-open-spiel-game/SKILL.md b/.agents/skills/onboard-open-spiel-game/SKILL.md
@@ -2,6 +2,9 @@
 
 The OpenSpiel integration (`kaggle_environments/envs/open_spiel_env/`) provides a unified framework that wraps games from Google's [OpenSpiel library](https://github.com/google-deepmind/open_spiel) into Kaggle environments. A shared interpreter handles all games -- you do NOT write a per-game interpreter. Instead, you configure the game and optionally add a proxy, visualizer, or custom game implementation.
 
+**Related skills:**
+- `create-visualizer` -- for adding a web visualizer (covers both regular and OpenSpiel games)
+
 ## Determine the approach
 
 Before starting, determine which pattern fits your game:
@@ -12,7 +15,7 @@ Before starting, determine which pattern fits your game:
 | Game exists in OpenSpiel but you want better observation format (e.g., JSON instead of OpenSpiel strings) | **Add proxy** | `games/<name>/<name>_proxy.py` |
 | Game does NOT exist in OpenSpiel and needs a custom Python implementation | **Add custom game** | `games/<name>/<name>_game.py` |
 
-All three approaches can optionally include a **visualizer** and/or **support files** (openings, presets).
+All three approaches can optionally include a **visualizer** (see `create-visualizer` skill) and/or **support files** (openings, presets).
 
 ## Step 1: Add to GAMES_LIST
 
diff --git a/AGENTS.md b/AGENTS.md
@@ -3,10 +3,9 @@
 This document provides guidance for AI coding agents working with the `kaggle-environments` repository. It covers project structure, commands, code style, and architecture.
 
 For detailed how-to guides, see the skills in `.agents/skills/`:
-- **create-environment** -- step-by-step guide for building a new game environment or updating an existing one
-- **create-visualizer** -- step-by-step guide for building a web visualizer or updating an existing one
-- **onboard-open-spiel-game** -- step-by-step guide for adding an OpenSpiel game
-- **create-open-spiel-visualizer** -- step-by-step guide for building a visualizer for a new OpenSpiel game (no harness/proxy needed)
+- **create-environment** -- step-by-step guide for building a new game environment (Python backend)
+- **create-visualizer** -- step-by-step guide for building a web visualizer for any game (regular or OpenSpiel)
+- **onboard-open-spiel-game** -- step-by-step guide for adding an OpenSpiel game (Python backend)
 
 ## Project Overview
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -5,7 +5,6 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 See [AGENTS.md](AGENTS.md) for project overview, architecture, commands, and code style.
 
 See `.agents/skills/` for detailed how-to guides:
-- `create-environment` -- building a game environment
-- `create-visualizer` -- building a web visualizer
-- `onboard-open-spiel-game` -- adding an OpenSpiel game
-- `create-open-spiel-visualizer` -- building a visualizer for a new OpenSpiel game
+- `create-environment` -- building a game environment (Python backend)
+- `create-visualizer` -- building a web visualizer for any game (regular or OpenSpiel)
+- `onboard-open-spiel-game` -- adding an OpenSpiel game (Python backend)
PATCH

echo "Gold patch applied."
