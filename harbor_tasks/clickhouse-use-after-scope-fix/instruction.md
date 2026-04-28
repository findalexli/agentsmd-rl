# Fix Use-After-Scope Bug in Parallel Object Type Deserialization

## Problem Description

ClickHouse's Object type deserialization has a memory safety bug. When parallel tasks are scheduled via the thread pool for bulk deserialization of state prefixes, these tasks capture references to stack-local variables. If an exception occurs during or after task scheduling, stack unwinding may destroy those locals while the tasks are still executing, causing a **use-after-scope / use-after-free** vulnerability. Pool threads may dereference dangling references to stack locals that are already destroyed.

## Context

The vulnerable code is in `src/DataTypes/Serializations/SerializationObject.cpp`, specifically the `deserializeBinaryBulkStatePrefix` function. This function creates a `tasks` vector of scheduled thread pool tasks using `trySchedule`. Each task object provides `tryExecute()` and `wait()` methods that must be called to drain the task. The task scheduling loop iterates from `size_t i = 0` to `num_tasks`, with `task_size = std::max(...)` determining the work per task. ClickHouse uses the `SCOPE_EXIT` macro (defined in `base/scope_guard.h`) as the standard RAII pattern for ensuring cleanup runs on all exit paths.

Currently, there is no mechanism to drain scheduled tasks when an exception propagates out of the function. If an exception occurs after `trySchedule` has enqueued tasks (for example, during `task_size = std::max(...)` computation or in the `for` loop body), the stack frame is unwound but pool threads may still hold references to destroyed stack locals. This is a use-after-scope vulnerability.

## What You Need to Fix

Ensure that all scheduled tasks have their `tryExecute()` and `wait()` methods called before the function's stack frame is destroyed, on **all exit paths** including exceptions. Pool threads must not be left with dangling references to stack locals after the function completes.

The cleanup logic must be set up **before** the `for (size_t i = 0; i != num_tasks; ++i)` scheduling loop so that any exception thrown during scheduling also triggers task draining.

Add a clear comment near the cleanup code explaining why explicit task draining is required — specifically that it prevents use-after-scope by ensuring pool threads do not dereference dangling references to destroyed stack locals.

## Constraints

- Follow ClickHouse coding conventions (Allman-style braces, RAII patterns)
- Do not use sleep or synchronization primitives — tasks must be actively drained, not polled
- The fix must drain tasks on all exit paths including exceptions
- The cleanup mechanism must be declared before the task scheduling loop

## Code Style Requirements

- No tab characters in source files
- No trailing whitespace
- No `sleep(`, `usleep(`, `nanosleep(`, or `std::this_thread::sleep` calls — ClickHouse forbids using sleep to paper over race conditions
