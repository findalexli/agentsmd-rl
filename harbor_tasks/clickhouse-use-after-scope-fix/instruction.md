# Fix Use-After-Scope Bug in Parallel Object Type Deserialization

## Problem Description

ClickHouse's Object type deserialization has a memory safety bug. When parallel tasks are scheduled via the thread pool for bulk deserialization of state prefixes, these tasks capture references to stack-local variables. If an exception occurs during or after task scheduling, stack unwinding may destroy those locals while the tasks are still executing, causing a **use-after-scope / use-after-free** vulnerability.

## Context

The vulnerable code is in `src/DataTypes/Serializations/SerializationObject.cpp`, specifically the `deserializeBinaryBulkStatePrefix` function that handles Object type deserialization using a thread pool for parallelization.

## What You Need to Fix

The function schedules parallel tasks that capture references to stack-local variables. There is no mechanism to ensure these tasks complete before the function's stack frame is destroyed — particularly on exception paths.

## Constraints

- Follow ClickHouse coding conventions (Allman-style braces, RAII patterns)
- Do not use sleep or synchronization primitives — tasks must be actively drained
- The fix must handle all exit paths including exceptions

## Verification

After applying your fix:
1. All scheduled tasks should complete before their captured stack references become invalid
2. The cleanup should work on both normal and exception paths
3. The code should compile without errors
