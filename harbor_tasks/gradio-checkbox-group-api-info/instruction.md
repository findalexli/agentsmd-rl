# Fix: AttributeError in ColoredCheckboxGroup.api_info()

## Problem

Calling `api_info()` on a `ColoredCheckboxGroup` component raises an `AttributeError`. The method tries to access `self.choices` but the `ColoredCheckboxGroup` class does not store choices as a direct instance attribute -- it stores them in `self.props["choices"]` instead.

## Root Cause

The `api_info()` method in `gradio/components/custom_html_components/colored_checkbox_group.py` references `self.choices` to build the enum list for the API schema. However, unlike the standard `CheckboxGroup`, the `ColoredCheckboxGroup.__init__` stores its choices in the `self.props` dictionary rather than as a direct attribute. This means `self.choices` raises an `AttributeError` at runtime.

## Expected Fix

Update the `api_info()` method to read choices from the correct location where `__init__` actually stores them.

## Files to Investigate

- `gradio/components/custom_html_components/colored_checkbox_group.py` -- the `api_info()` method
