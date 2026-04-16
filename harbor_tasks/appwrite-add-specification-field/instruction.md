# Task: Fix Missing 'specification' Field in Database Schema

## Problem Description

When creating functions or sites in the application, the `specification` attribute is not properly stored because it's missing from the collection schema definitions. This causes data integrity issues when the application attempts to read or use the specification value.

## Task

The collection schemas in the projects configuration need to define a `specification` field. This field should be added to both the `functions` and `sites` collections, positioned before the `buildSpecification` field in the attributes list.

The field should have the following characteristics:
- Use `Database::VAR_STRING` as the type
- Reference the `APP_COMPUTE_SPECIFICATION_DEFAULT` constant for its default value
- Have a size of 128 characters
- Be unsigned (`signed` = false)
- Be optional (`required` = false)
- Not be an array (`array` = false)
- Have an empty format string
- Have an empty filters array

After your fix, both collections should properly define this field so that specification values can be stored and retrieved correctly.
