# Selenium Java — Deduplicate Unicode PUA mappings in `Keys`

The `Keys` enum in
`java/src/org/openqa/selenium/Keys.java` is the public registry of pressable
non-text keys, each mapped to a single Unicode Private Use Area (PUA) code
point in the range `0xE000`–`0xF8FF`. Two of its constants currently violate
the "one canonical key per PUA value" rule that the rest of the enum follows.

## What is wrong

1. `OPTION` is declared with `'\uE052'`, the same code point already used by
   `RIGHT_ALT`. On macOS, the platform-friendly name for this modifier is
   `OPTION`, but the W3C WebDriver specification — and every other binding —
   treats Option as the **same key as Alt**, whose Unicode value in this enum
   is `0xE00A` (the value of `Keys.ALT`). The current declaration therefore
   does two unwanted things at once:

   - It collides with `RIGHT_ALT` rather than aliasing `ALT`, so
     `Keys.OPTION.charAt(0)` returns `0xE052` (the right-Alt code) instead of
     `0xE00A` (the Alt code).
   - It introduces a duplicate PUA value that makes
     `Keys.getKeyFromUnicode(char)` order-dependent for `0xE052`.

   Constants that are intentional aliases of another `Keys` value already
   exist in this file (for example, `LEFT_SHIFT(Keys.SHIFT)`,
   `LEFT_CONTROL(Keys.CONTROL)`, `LEFT_ALT(Keys.ALT)`, `COMMAND(Keys.META)`,
   `ARROW_LEFT(Keys.LEFT)`, …). These use the existing
   `Keys(Keys other)` constructor in this file, which copies the target
   constant's char without introducing a new code. `OPTION` should be defined
   the same way.

2. `FN` is declared with its own unstandardized PUA value and a `TODO`
   comment. The `Fn` key is **not part of the W3C WebDriver specification**
   and has no standardized Unicode mapping; its behavior is not guaranteed
   across drivers/platforms. Because Selenium's policy is to mark public
   functionality as `@Deprecated` (with a Javadoc message explaining the
   situation) before any potential removal, `FN` must continue to exist as a
   public enum constant, but it must be deprecated rather than retained as a
   first-class mapping.

## What you must do

Edit only `java/src/org/openqa/selenium/Keys.java`:

- Make `OPTION` a true alias of `ALT` so that:
  - `Keys.OPTION.charAt(0) == Keys.ALT.charAt(0)` (i.e. equals `0xE00A`).
  - `Keys.OPTION.toString().equals(Keys.ALT.toString())`.
  - `Keys.OPTION.getCodePoint() == Keys.ALT.getCodePoint()`.
  - `Keys.OPTION` is still a public enum constant (do **not** delete it —
    that would break API compatibility).

- Deprecate `FN` so that:
  - The reflective check `Keys.class.getField("FN").isAnnotationPresent(Deprecated.class)`
    returns `true`.
  - `Keys.FN` is still a public enum constant (do **not** delete it — that
    would break API compatibility).
  - The Javadoc on `FN` explains *why* it is deprecated (no W3C
    standardization, behavior not guaranteed). The Javadoc convention used
    elsewhere in the project applies (brief description, `@deprecated` tag).
  - `Keys.FN.charAt(0)` continues to equal `Keys.RIGHT_CONTROL.charAt(0)`
    (= `0xE051`). Use the same alias-style construction the rest of the
    enum uses for related keys.

- Do **not** change the Unicode values of any other constants. In particular:
  - `Keys.ALT.charAt(0)` must remain `0xE00A`.
  - `Keys.RIGHT_ALT.charAt(0)` must remain `0xE052`.
  - `Keys.RIGHT_CONTROL.charAt(0)` must remain `0xE051`.

- The class-level Javadoc (lines 23–40) currently says that `OPTION` and `FN`
  are "symbolic and reserved for possible future mapping." Update that
  paragraph so it reflects the new reality (e.g. that `OPTION` is a symbolic
  alias for an existing key). Do not restate what the code does — explain
  the project intent.

## Constraints

- Confine the edit to `java/src/org/openqa/selenium/Keys.java`. No other
  file should be touched.
- Maintain API/ABI compatibility: do not remove or rename any existing
  enum constant, do not change any constructor signatures.
- Keep the diff small and reversible — do not reformat unrelated code.
- Comments should explain *why* a choice is made, not *what* the line
  does (well-named identifiers already convey "what").
