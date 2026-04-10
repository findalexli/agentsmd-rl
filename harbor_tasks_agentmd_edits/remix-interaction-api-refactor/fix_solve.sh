#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'export interface Interaction' packages/interaction/src/lib/interaction.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
from pathlib import Path
import re

PKG = Path("packages/interaction")

# ── 1. Update src/index.ts — remove capture/listenWith, add Interaction/ContainerOptions ──
p = PKG / "src/index.ts"
p.write_text("""\
export {
  type ContainerOptions,
  type Dispatched,
  type EventListeners,
  type EventsContainer,
  type Interaction,
  type InteractionSetup,
  type TypedEventTarget,
  createContainer,
  defineInteraction,
  on,
} from './lib/interaction.ts'
""")
print("Updated src/index.ts")

# ── 2. Update src/lib/interaction.ts — core refactor ──
p = PKG / "src/lib/interaction.ts"
src = p.read_text()

# 2a. Add Interaction interface after EventListeners type
interaction_interface = '''
/**
 * Context object provided to interaction setup functions via `this`.
 */
export interface Interaction {
  /**
   * The target element this interaction is being set up on.
   */
  readonly target: EventTarget
  /**
   * The abort signal that will dispose this interaction when aborted.
   */
  readonly signal: AbortSignal
  /**
   * Error handler from the parent container.
   */
  readonly raise: (error: unknown) => void
  /**
   * Create a container on a target with listeners. Automatically passes
   * through signal and onError from the parent container.
   */
  on<target extends EventTarget>(target: target, listeners: EventListeners<target>): void
}
'''

# Insert after EventListeners type definition
src = src.replace(
    "export type InteractionSetup = (target: EventTarget, signal: AbortSignal) => void",
    interaction_interface + "\n/**\n * A function that sets up an interaction on a target.\n */\nexport type InteractionSetup = (this: Interaction) => void"
)

# 2b. Update EventListeners doc comment for descriptor pattern
src = src.replace(
    " *     capture((event) => {}),",
    " *     { capture: true, listener(event) {} },"
)

# 2c. Add ContainerOptions type before createContainer
container_options = '''/**
 * Options for creating an event container.
 */
export type ContainerOptions = {
  /**
   * An optional abort signal to dispose the container when the signal is aborted
   */
  signal?: AbortSignal
  /**
   * An optional error handler called when a listener throws an error
   */
  onError?: (error: unknown) => void
}

'''

src = src.replace(
    "/**\n * ### Description\n *\n * Creates an event container",
    container_options + "/**\n * ### Description\n *\n * Creates an event container"
)

# 2d. Add error handling example to createContainer jsdoc
src = src.replace(
    " */\nexport function createContainer<target extends EventTarget>(",
    """ *
 * ### With error handling:
 *
 * ```ts
 * let container = createContainer(button, {
 *   onError(error) {
 *     console.error('Listener error:', error)
 *   },
 * })
 * ```
 */
export function createContainer<target extends EventTarget>("""
)

# 2e. Change createContainer signature from signal to options
src = src.replace(
    """  /**
   * An optional abort signal to dispose the container when the signal is aborted
   *
   * @example
   * ```ts
   * let controller = new AbortController()
   * let container = createContainer(target, controller.signal)
   * // will remove all listeners and dispose the container
   * controller.abort()
   * ```
   */
  signal?: AbortSignal,""",
    """  /**
   * Optional configuration for the container
   *
   * @example
   * ```ts
   * let controller = new AbortController()
   * let container = createContainer(target, {
   *   signal: controller.signal,
   *   onError(error) {
   *     console.error(error)
   *   },
   * })
   * // will remove all listeners and dispose the container
   * controller.abort()
   * ```
   */
  options?: ContainerOptions,"""
)

# 2f. Destructure options in createContainer body
src = src.replace(
    "): EventsContainer<target> {\n  let controller = new AbortController()\n\n  if (signal) {",
    "): EventsContainer<target> {\n  let controller = new AbortController()\n  let { signal, onError = defaultOnError } = options ?? {}\n\n  if (signal) {"
)

# 2g. Update binding creation to pass onError and destructure descriptor
src = src.replace(
    """          bindings[type] = descriptors.map((d) =>
              createBinding(target, type, d.listener, d.options, controller.signal),
            )""",
    """          bindings[type] = descriptors.map((d) => {
              let { listener, ...options } = d
              return createBinding(target, type, listener, options, controller.signal, onError)
            })"""
)

# 2h. Update diff loop to destructure descriptor
src = src.replace(
    """          for (let i = 0; i < min; i++) {
            let d = descriptors[i]
            let b = existing[i]
            if (optionsChanged(d.options, b.options)) {
              b.rebind(d.listener, d.options)
            } else {
              b.setListener(d.listener)
            }""",
    """          for (let i = 0; i < min; i++) {
            let d = descriptors[i]
            let b = existing[i]
            let { listener, ...options } = d
            if (optionsChanged(options, b.options)) {
              b.rebind(listener, options)
            } else {
              b.setListener(listener)
            }"""
)

# 2i. Update growth loop to destructure and pass onError
src = src.replace(
    """            for (let i = existing.length; i < descriptors.length; i++) {
              let d = descriptors[i]
              existing.push(createBinding(target, type, d.listener, d.options, controller.signal))""",
    """            for (let i = existing.length; i < descriptors.length; i++) {
              let d = descriptors[i]
              let { listener, ...options } = d
              existing.push(
                createBinding(target, type, listener, options, controller.signal, onError),
              )"""
)

# 2j. Simplify the on() function — remove signal overload
# Find and replace the entire on function
on_old = '''export function on<target extends EventTarget>(
  target: target,
  signal: AbortSignal,
  listeners: EventListeners<target>,
): () => void
export function on<target extends EventTarget>(
  target: target,
  listeners: EventListeners<target>,
): () => void
export function on(
  target: EventTarget,
  signalOrListeners: AbortSignal | EventListeners,
  listeners?: EventListeners,
): () => void {
  if (!(signalOrListeners instanceof AbortSignal)) {
    let container = createContainer(target)
    container.set(signalOrListeners)
    return container.dispose
  } else if (listeners) {
    let container = createContainer(target, signalOrListeners)
    container.set(listeners)
    return container.dispose
  }
  throw new Error('Invalid arguments')
}'''

on_new = '''export function on<target extends EventTarget>(
  target: target,
  listeners: EventListeners<target>,
): () => void {
  let container = createContainer(target)
  container.set(listeners)
  return container.dispose
}'''

src = src.replace(on_old, on_new)

# 2k. Update on() jsdoc to remove signal overload examples
src = src.replace(
    "Add event listeners with async reentry protection and semantic Interactions.\n *\n * ### Basic usage:\n *\n * ```ts",
    "Add event listeners with async reentry protection and semantic Interactions. Shorthand for `createContainer` without options.\n *\n * ```ts"
)
src = src.replace(
    """ * on(button, {
 *   click(event, signal) {""",
    """ * let dispose = on(button, {
 *   click(event, signal) {"""
)

# Remove the signal overload example from on() jsdoc
signal_example = """ *
 * ### With abort signal to dispose the container:
 *
 * ```ts
 * let controller = new AbortController()
 * on(button, controller.signal, {
 *   click(event, signal) {
 *     console.log('clicked')
 *   },
 * })
 * // will remove all listeners and dispose the container
 * controller.abort()
 * ```
 *
 * ### With array of listeners on a type:
 *
 * ```ts
 * on(button, {
 *   click: [
 *     (event, signal) => {
 *       if (someCondition) {
 *         event.stopImmediatePropagation()
 *       }
 *       console.log('called')
 *     },
 *     (event, signal) => {
 *       console.log('not called')
 *     },
 *   ],
 * })
 * ```"""
if signal_example in src:
    src = src.replace(signal_example, " *\n * // later\n * dispose()")

# Update interaction jsdoc examples
src = src.replace(
    """ * function KeydownEnter(target, signal) {
 *   on(target, signal, {""",
    """ * function KeydownEnter(this: Interaction) {
 *   this.on(this.target, {"""
)
src = src.replace(
    """ *         target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))""",
    """ *         this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))"""
)

# 2l. Remove capture and listenWith functions
src = src.replace(
    """export function listenWith<L>(options: AddEventListenerOptions, listener: L): Descriptor<L> {
  return { options, listener }
}

export function capture<L>(listener: L): Descriptor<L> {
  return listenWith({ capture: true }, listener)
}

""", ""
)

# 2m. Add defaultOnError + InteractionHandle class before the descriptor internals
handle_code = '''function defaultOnError(error: unknown) {
  throw error
}

class InteractionHandle implements Interaction {
  readonly target: EventTarget
  readonly signal: AbortSignal
  readonly raise: (error: unknown) => void

  constructor(target: EventTarget, signal: AbortSignal, onError: (error: unknown) => void) {
    this.target = target
    this.signal = signal
    this.raise = onError
  }

  on<target extends EventTarget>(target: target, listeners: EventListeners<target>): void {
    let container = createContainer(target, {
      signal: this.signal,
      onError: this.raise,
    })
    container.set(listeners)
  }
}

'''

src = src.replace(
    "type ListenerOrDescriptor<Listener> = Listener | Descriptor<Listener>",
    handle_code + "type ListenerOrDescriptor<Listener> = Listener | Descriptor<Listener>"
)

# 2n. Update Descriptor interface to extend AddEventListenerOptions
src = src.replace(
    """interface Descriptor<L> {
  options: AddEventListenerOptions
  listener: L
}""",
    """interface Descriptor<L> extends AddEventListenerOptions {
  listener: L
}"""
)

# 2o. Update normalizeDescriptors to not use nested options
src = src.replace(
    """    return raw.map((item) =>
      isDescriptor<Listener>(item) ? item : { listener: item, options: {} },
    )""",
    "    return raw.map((item) => (isDescriptor<Listener>(item) ? item : { listener: item }))"
)
src = src.replace(
    "  return [isDescriptor<Listener>(raw) ? raw : { listener: raw, options: {} }]",
    "  return [isDescriptor<Listener>(raw) ? raw : { listener: raw }]"
)

# 2p. Update isDescriptor to check for listener only
src = src.replace(
    "  return typeof value === 'object' && value !== null && 'options' in value && 'listener' in value",
    "  return typeof value === 'object' && value !== null && 'listener' in value"
)

# 2q. Add onError parameter to createBinding
src = src.replace(
    """  listener: ListenerFor<target, k>,
  options: AddEventListenerOptions,
  containerSignal: AbortSignal,
): Binding<ListenerFor<target, k>> {""",
    """  listener: ListenerFor<target, k>,
  options: AddEventListenerOptions,
  containerSignal: AbortSignal,
  onError: (error: unknown) => void,
): Binding<ListenerFor<target, k>> {"""
)

# 2r. Wrap listener call in try/catch with onError
src = src.replace(
    """  let wrappedListener = (event: Event) => {
    abort()
    // TODO: figure out if we can remove this cast
    listener(event as any, reentry.signal)
  }""",
    """  let wrappedListener = (event: Event) => {
    abort()
    try {
      // TODO: figure out if we can remove this cast
      let result = listener(event as any, reentry.signal)
      if (result instanceof Promise) {
        result.catch(onError)
      }
    } catch (error) {
      onError(error)
    }
  }"""
)

# 2s. Update interaction binding to use InteractionHandle
src = src.replace(
    """    if (count === 0) {
      interaction(target, containerSignal)
    }""",
    """    if (count === 0) {
      let interactionContext = new InteractionHandle(target, containerSignal, onError)
      interaction.call(interactionContext)
    }"""
)

p.write_text(src)
print("Updated src/lib/interaction.ts")

# ── 3. Update interaction implementations ──

# 3a. form.ts
p = PKG / "src/lib/interactions/form.ts"
src = p.read_text()
src = src.replace(
    "import { defineInteraction } from '../interaction.ts'",
    "import { defineInteraction, type Interaction } from '../interaction.ts'"
)
src = src.replace(
    "function FormReset(target: EventTarget, signal: AbortSignal) {\n  if (!(target instanceof HTMLElement)) return\n",
    "function FormReset(this: Interaction) {\n  if (!(this.target instanceof HTMLElement)) return\n\n  let target = this.target\n"
)
src = src.replace(
    "    form.addEventListener('reset', () => target.dispatchEvent(new Event(formReset)), { signal })",
    "    this.on(form, {\n      reset() {\n        target.dispatchEvent(new Event(formReset))\n      },\n    })"
)
p.write_text(src)
print("Updated interactions/form.ts")

# 3b. keys.ts
p = PKG / "src/lib/interactions/keys.ts"
src = p.read_text()
src = src.replace(
    "import { defineInteraction, on } from '../interaction.ts'",
    "import { defineInteraction, type Interaction } from '../interaction.ts'"
)

# Add WindowEventMap and DocumentEventMap
window_doc_maps = """
  interface WindowEventMap {
    [escape]: KeyboardEvent
    [enter]: KeyboardEvent
    [space]: KeyboardEvent
    [backspace]: KeyboardEvent
    [del]: KeyboardEvent
    [arrowLeft]: KeyboardEvent
    [arrowRight]: KeyboardEvent
    [arrowUp]: KeyboardEvent
    [arrowDown]: KeyboardEvent
    [home]: KeyboardEvent
    [end]: KeyboardEvent
    [pageUp]: KeyboardEvent
    [pageDown]: KeyboardEvent
    [tab]: KeyboardEvent
  }

  interface DocumentEventMap {
    [escape]: KeyboardEvent
    [enter]: KeyboardEvent
    [space]: KeyboardEvent
    [backspace]: KeyboardEvent
    [del]: KeyboardEvent
    [arrowLeft]: KeyboardEvent
    [arrowRight]: KeyboardEvent
    [arrowUp]: KeyboardEvent
    [arrowDown]: KeyboardEvent
    [home]: KeyboardEvent
    [end]: KeyboardEvent
    [pageUp]: KeyboardEvent
    [pageDown]: KeyboardEvent
    [tab]: KeyboardEvent
  }"""
src = src.replace(
    "    [tab]: KeyboardEvent\n  }\n}",
    "    [tab]: KeyboardEvent\n  }" + window_doc_maps + "\n}"
)

src = src.replace(
    "function Keys(target: EventTarget, signal: AbortSignal) {\n  if (!(target instanceof HTMLElement || target instanceof Document || target instanceof Window))\n    return\n\n  on(target, signal, {",
    "function Keys(this: Interaction) {\n  if (\n    !(\n      this.target instanceof HTMLElement ||\n      this.target instanceof Document ||\n      this.target instanceof Window\n    )\n  )\n    return\n\n  let target = this.target\n  this.on(this.target, {"
)
p.write_text(src)
print("Updated interactions/keys.ts")

# 3c. popover.ts
p = PKG / "src/lib/interactions/popover.ts"
src = p.read_text()
src = src.replace(
    "import { defineInteraction, on } from '../interaction'",
    "import { defineInteraction, type Interaction } from '../interaction'"
)
src = src.replace(
    "function Popover(target: EventTarget, signal: AbortSignal) {\n  if (!(target instanceof HTMLElement)) return\n\n  let popoverId",
    "function Popover(this: Interaction) {\n  if (!(this.target instanceof HTMLElement)) return\n\n  let target = this.target\n  let popoverId"
)
src = src.replace(
    "  on(popover, signal, {",
    "  this.on(popover, {"
)
p.write_text(src)
print("Updated interactions/popover.ts")

# 3d. press.ts
p = PKG / "src/lib/interactions/press.ts"
src = p.read_text()
src = src.replace(
    "import { defineInteraction, on } from '../interaction.ts'",
    "import { defineInteraction, type Interaction } from '../interaction.ts'"
)
src = src.replace(
    "function Press(target: EventTarget, signal: AbortSignal) {\n  if (!(target instanceof HTMLElement)) return\n\n  let isPointerDown",
    "function Press(this: Interaction) {\n  if (!(this.target instanceof HTMLElement)) return\n\n  let target = this.target\n  let isPointerDown"
)
src = src.replace(
    "  on(target, signal, {",
    "  this.on(this.target, {"
)
src = src.replace(
    "  on(target.ownerDocument, signal, {",
    "  this.on(target.ownerDocument, {"
)
p.write_text(src)
print("Updated interactions/press.ts")

# ── 4. Update tsconfig.json ──
p = PKG / "tsconfig.json"
src = p.read_text()
src = src.replace('"lib": ["ES2020", "DOM", "DOM.Iterable"]', '"lib": ["ES2024", "DOM", "DOM.Iterable"]')
p.write_text(src)
print("Updated tsconfig.json")

# ── 5. Update test file ──
p = PKG / "src/lib/interaction.test.ts"
src = p.read_text()

# Update imports
src = src.replace(
    """import {
  capture,
  createContainer,
  defineInteraction,
  listenWith,
  on,
  TypedEventTarget,
  type Dispatched,
  type EventListeners,
} from './interaction.ts'""",
    """import {
  createContainer,
  defineInteraction,
  on,
  TypedEventTarget,
  type Dispatched,
  type EventListeners,
  type Interaction,
} from './interaction.ts'"""
)

# Update container.set with listenWith
src = src.replace(
    "      container.set({ test: listenWith({ capture: true }, listener2) })",
    "      container.set({ test: { capture: true, listener: listener2 } })"
)

# Update describe names and test for descriptors
src = src.replace(
    "    describe('listenWith', () => {\n      it('provides options with listenWith', () => {",
    "    describe('descriptors', () => {\n      it('provides options with descriptors', () => {"
)
src = src.replace(
    "          test: listenWith({ once: true }, listener),",
    "          test: { once: true, listener },"
)

# Remove describe('capture') opening and merge into descriptors
src = src.replace(
    """      })
    })

    describe('capture', () => {
      it('captures events', () => {""",
    """      })

      it('captures events', () => {"""
)

# Update capture test
src = src.replace(
    """        createContainer(document.body).set({
          click: capture((event) => {
            event.stopPropagation()
            captured = true
          }),
        })""",
    """        createContainer(document.body).set({
          click: {
            capture: true,
            listener(event) {
              event.stopPropagation()
              captured = true
            },
          },
        })"""
)

# Add error handling tests after capture test's closing
error_tests = '''
    describe('error handling', () => {
      it('calls onError when a listener throws synchronously', () => {
        let target = new EventTarget()
        let mock = vi.fn()
        let error = new Error('test')
        let container = createContainer(target, { onError: mock })
        container.set({
          test: () => {
            throw error
          },
        })
        target.dispatchEvent(new Event('test'))
        expect(mock).toHaveBeenCalledWith(error)
      })
    })

    it('calls onError when a listener throws asynchronously', async () => {
      let target = new EventTarget()
      let mock = vi.fn()
      let error = new Error('test')
      createContainer(target, { onError: mock }).set({
        async test() {
          // ensure the error is thrown asynchronously (next microtask)
          await Promise.resolve()
          throw error
        },
      })
      target.dispatchEvent(new Event('test'))
      // let the listener's awaited microtask run and reject
      await Promise.resolve()
      // run the container's result.catch(onError) handler
      await Promise.resolve()
      expect(mock).toHaveBeenCalledWith(error)
    })

'''

# Insert error handling tests before the types describe
src = src.replace(
    "    describe('types', () => {",
    error_tests + "    describe('types', () => {"
)

# Remove the signal overload type test
src = src.replace(
    """
      it('accepts optional abort signal', () => {
        let button = document.createElement('button')
        let controller = new AbortController()
        on(button, controller.signal, {
          pointerdown: (event) => {
            type T = Assert<Equal<typeof event, Dispatched<PointerEvent, HTMLButtonElement>>>
          },
          // @ts-expect-error - unknown event type
          test: () => {},
        })
      })""",
    ""
)

# Update defineInteraction tests to use this context
src = src.replace(
    """      function Test(target: EventTarget, signal: AbortSignal) {
        on(target, signal, {
          [hostType]: () => {
            target.dispatchEvent(new Event(myType))
          },
        })
      }""",
    """      function Test(this: Interaction) {
        this.on(this.target, {
          [hostType]: () => {
            this.target.dispatchEvent(new Event(myType))
          },
        })
      }""",
)

# There are two such patterns (one in describe, one outside)
src = src.replace(
    """    function Test(target: EventTarget, signal: AbortSignal) {
      on(target, signal, {
        [hostType]: () => {
          target.dispatchEvent(new Event(myType))
        },
      })
    }""",
    """    function Test(this: Interaction) {
      this.on(this.target, {
        [hostType]: () => {
          this.target.dispatchEvent(new Event(myType))
        },
      })
    }""",
)

p.write_text(src)
print("Updated interaction.test.ts")

# ── 6. Update README.md ──
p = PKG / "README.md"
src = p.read_text()

# Update imports — remove capture, listenWith
src = src.replace(
    "import { on, capture, listenWith } from '@remix-run/interaction'",
    "import { on } from '@remix-run/interaction'"
)
src = src.replace(
    "import { on, listenWith, capture } from '@remix-run/interaction'",
    "import { on } from '@remix-run/interaction'"
)

# Update array listeners example
src = src.replace(
    """    capture((event) => {
      // capture phase
    }),
    listenWith({ once: true }, (event) => {
      console.log('only once')
    }),""",
    """    {
      capture: true,
      listener(event) {
        // capture phase
      },
    },
    {
      once: true,
      listener(event) {
        console.log('only once')
      },
    },"""
)

# Update event listener options example
src = src.replace(
    """on(button, {
  click: capture((event) => {
    console.log('capture phase')
  }),
  focus: listenWith({ once: true }, (event) => {
    console.log('focused once')
  }),
})""",
    """on(button, {
  click: {
    capture: true,
    listener(event) {
      console.log('capture phase')
    },
  },
  focus: {
    once: true,
    listener(event) {
      console.log('focused once')
    },
  },
})"""
)

# Update createContainer docs
src = src.replace(
    "Use `createContainer(target, signal?)` when",
    "Use `createContainer` when"
)

# Update disposing listeners section — remove signal overload, add container signal example
src = src.replace(
    """// Using an external AbortSignal
let controller = new AbortController()
on(button, controller.signal, { click: () => {} })
controller.abort() // removes all listeners added via that call

// Containers
let container = createContainer(window)
container.set({ resize: () => {} })
container.dispose()""",
    """// Containers
let container = createContainer(window)
container.set({ resize: () => {} })
container.dispose()

// Use a signal
let eventsController = new AbortController()
let container = createContainer(window, {
  signal: eventsController.signal,
})
container.set({ resize: () => {} })
eventsController.abort()"""
)

# Update custom interactions example
src = src.replace(
    "import { defineInteraction, on } from '@remix-run/interaction'",
    "import { defineInteraction, on, type Interaction } from '@remix-run/interaction'"
)
src = src.replace(
    """function KeydownEnter(target: EventTarget, signal: AbortSignal) {
  if (!(target instanceof HTMLElement)) return

  on(target, signal, {
    keydown(event) {
      if (event.key === 'Enter') {
        target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))""",
    """function KeydownEnter(this: Interaction) {
  if (!(this.target instanceof HTMLElement)) return

  this.on(this.target, {
    keydown(event) {
      if (event.key === 'Enter') {
        this.target.dispatchEvent(new KeyboardEvent(keydownEnter, { key: 'Enter' }))"""
)

p.write_text(src)
print("Updated README.md")

# ── 7. Update CHANGELOG.md ──
p = PKG / "CHANGELOG.md"
src = p.read_text()

changelog_entry = """## Unreleased

- BREAKING CHANGE: Interaction API refactor - interactions now use `this` context with `this.on()`, `this.target`, `this.signal`, and `this.raise`

  Interactions are now functions that receive an `Interaction` context via `this`:

  ```ts
  // Before
  function MyInteraction(target: EventTarget, signal: AbortSignal) {
    createContainer(target, { signal }).set({ ... })
  }

  // After
  function MyInteraction(this: Interaction) {
    this.on(this.target, { ... })
    // or for different targets
    this.on(this.target.ownerDocument, { ... })
  }
  ```

  The `Interaction` context provides:

  - `this.target` - The target element
  - `this.signal` - Abort signal for cleanup
  - `this.raise` - Error handler (renamed from `onError`)
  - `this.on(target, listeners)` - Create a container with automatic signal/error propagation

- BREAKING CHANGE: Simplify descriptor API - descriptors now extend `AddEventListenerOptions` directly

  Removed `capture()` and `listenWith()` helper functions. Consumers now provide options inline using descriptor objects:

  ```tsx
  // removed
  capture((event) => {})
  listenWith({ once: true }, (event) => {})

  // new API
  {
    capture: true,
    listener(event) {}
  }
  {
    once: true,
    listener(event) {}
  }
  ```

- BREAKING CHANGE: Remove `on` signal overload, just use containers directly

  ```tsx
  // removed
  on(target, signal, listeners)

  // on is just a shortcut now
  let dispose = on(target, listeners)
  dispose()

  // use containers for signal cleanup
  let container = createContainer(target, { signal })
  ```

- Added `onError` handler so containers can handle listener errors in one place (avoids Remix Component needing to wrap EventListener interfaces to raise to `<Catch>`)

  ```tsx
  createContainer(target, {
    onError(error) {
      // handle error
    },
  })
  ```

"""

src = src.replace("## v0.1.0", changelog_entry + "## v0.1.0")
p.write_text(src)
print("Updated CHANGELOG.md")

print("\nAll changes applied successfully.")
PYEOF

echo "Patch applied successfully."
