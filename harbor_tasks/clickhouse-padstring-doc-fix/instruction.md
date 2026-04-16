# Fix Argument Descriptions for leftPad/rightPad Functions

## Symptom

When users call `leftPad` or `rightPad` with incorrect argument types, the error messages display misleading argument descriptions that do not match the actual expected types.

## Affected File

The file `src/Functions/padString.cpp` contains the argument descriptions that need correction.

## Arguments Requiring Description Fixes

The functions accept three arguments whose descriptions must match the following specifications:

1. **string** - Current description says `"Array"`; must be changed to `"String or FixedString"`
2. **length** - Current description says `"const UInt*"`; must be changed to `"UInt*"`
3. **pad_string** - Current description says `"Array"`; must be changed to `"String"`

## Required Changes

Update the argument description strings in the source file so that:
- The `"string"` argument description contains exactly `"String or FixedString"`
- The `"length"` argument description contains exactly `"UInt*"` (without the `"const "` prefix)
- The `"pad_string"` argument description contains exactly `"String"`

After the fix, the old incorrect description strings (`"Array"` for string and pad_string arguments, `"const UInt*"` for length) must no longer appear in the argument description contexts.
