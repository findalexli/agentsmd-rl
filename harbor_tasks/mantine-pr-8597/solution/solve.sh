#!/bin/bash
set -e
cd /workspace/repo

python3 << 'PYTHON_SCRIPT'
import re

# 1. Combobox.types.ts - add the new prop to ComboboxLikeProps interface
with open('packages/@mantine/core/src/components/Combobox/Combobox.types.ts', 'r') as f:
    content = f.read()

# Find the line with selectFirstOptionOnChange and add the new prop after it
old_text = '''  /** If set, the first option is selected when value changes, `false` by default */
  selectFirstOptionOnChange?: boolean;

  /** Called when option is submitted from dropdown with mouse click or `Enter` key */
  onOptionSubmit?: (value: string) => void;'''

new_text = '''  /** If set, the first option is selected when value changes, `false` by default */
  selectFirstOptionOnChange?: boolean;

  /** If set, the first option is selected when dropdown opens, `false` by default */
  selectFirstOptionOnDropdownOpen?: boolean;

  /** Called when option is submitted from dropdown with mouse click or `Enter` key */
  onOptionSubmit?: (value: string) => void;'''

content = content.replace(old_text, new_text)

with open('packages/@mantine/core/src/components/Combobox/Combobox.types.ts', 'w') as f:
    f.write(content)

# 2. Select.tsx - add prop destructuring
with open('packages/@mantine/core/src/components/Select/Select.tsx', 'r') as f:
    content = f.read()

# Add prop to destructuring
content = content.replace(
    'selectFirstOptionOnChange,\n    onOptionSubmit,',
    'selectFirstOptionOnChange,\n    selectFirstOptionOnDropdownOpen,\n    onOptionSubmit,'
)

# Update onDropdownOpen handler
old_handler = '''    onDropdownOpen: () => {
      onDropdownOpen?.();
      combobox.updateSelectedOptionIndex('active', { scrollIntoView: true });
    },'''

new_handler = '''    onDropdownOpen: () => {
      onDropdownOpen?.();
      if (selectFirstOptionOnDropdownOpen) {
        combobox.selectFirstOption();
      } else {
        combobox.updateSelectedOptionIndex('active', { scrollIntoView: true });
      }
    },'''

content = content.replace(old_handler, new_handler)

with open('packages/@mantine/core/src/components/Select/Select.tsx', 'w') as f:
    f.write(content)

# 3. Autocomplete.tsx - add prop destructuring and new handler
with open('packages/@mantine/core/src/components/Autocomplete/Autocomplete.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'selectFirstOptionOnChange,\n    onOptionSubmit,',
    'selectFirstOptionOnChange,\n    selectFirstOptionOnDropdownOpen,\n    onOptionSubmit,'
)

old_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen,'''

new_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen: () => {
      onDropdownOpen?.();
      if (selectFirstOptionOnDropdownOpen) {
        combobox.selectFirstOption();
      }
    },'''

content = content.replace(old_handler, new_handler)

with open('packages/@mantine/core/src/components/Autocomplete/Autocomplete.tsx', 'w') as f:
    f.write(content)

# 4. MultiSelect.tsx - add prop destructuring and new handler
with open('packages/@mantine/core/src/components/MultiSelect/MultiSelect.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'selectFirstOptionOnChange,\n    onOptionSubmit,',
    'selectFirstOptionOnChange,\n    selectFirstOptionOnDropdownOpen,\n    onOptionSubmit,'
)

old_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen,'''

new_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen: () => {
      onDropdownOpen?.();
      if (selectFirstOptionOnDropdownOpen) {
        combobox.selectFirstOption();
      }
    },'''

content = content.replace(old_handler, new_handler)

with open('packages/@mantine/core/src/components/MultiSelect/MultiSelect.tsx', 'w') as f:
    f.write(content)

# 5. TagsInput.tsx - add prop destructuring and new handler
with open('packages/@mantine/core/src/components/TagsInput/TagsInput.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'selectFirstOptionOnChange,\n    onOptionSubmit,',
    'selectFirstOptionOnChange,\n    selectFirstOptionOnDropdownOpen,\n    onOptionSubmit,'
)

old_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen,'''

new_handler = '''  const combobox = useCombobox({
    opened: dropdownOpened,
    defaultOpened: defaultDropdownOpened,
    onDropdownOpen: () => {
      onDropdownOpen?.();
      if (selectFirstOptionOnDropdownOpen) {
        combobox.selectFirstOption();
      }
    },'''

content = content.replace(old_handler, new_handler)

with open('packages/@mantine/core/src/components/TagsInput/TagsInput.tsx', 'w') as f:
    f.write(content)

print("Patch applied successfully")
PYTHON_SCRIPT

# Idempotency check - look for distinctive new code
grep -q "selectFirstOptionOnDropdownOpen" packages/@mantine/core/src/components/Combobox/Combobox.types.ts
