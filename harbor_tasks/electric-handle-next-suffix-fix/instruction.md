# Fix: Handle -next suffix accumulation on repeated 409s

## Problem

When the Electric sync server returns a 409 "must-refetch" response, the client fetches a new shape. If the server provides an `electric-handle` header, the client uses it. If not (e.g., a proxy or CDN strips the header), the client may fabricate a new handle by appending `-next` to the current one.

This causes two problems:
1. **Unbounded growth**: Repeated 409s lead to handles like `handle-next-next-next-next...` eventually causing 414 URI Too Long errors
2. **Invalid handles**: When the initial handle was undefined, this produces strings like `undefined-next-next-next...`

## Symptom

After repeated 409 responses from the server, clients experience:
- 414 URI Too Long HTTP errors
- Handles containing `-next` repeated many times
- Valid handles spiraling into invalid URI fragments

## Correct Behavior

When handling 409 responses:

1. **No `-next` suffix**: The code must not construct handles by appending `-next` to existing handles when the server's 409 response lacks a handle header

2. **Warning emission**: When a 409 response lacks the handle header, the client must emit a warning containing the exact phrases:
   - "Received 409 response without a shape handle header"
   - "proxy or CDN stripping required headers"

3. **Proper handle absence**: When no handle header is present, the reset mechanism must be called without fabricating a string handle (passing `undefined` rather than constructing one)

4. **Unique cache busting**: Retried requests without a handle header must use a unique cache-busting strategy to ensure URL uniqueness (e.g., time-based + random value appended to the URL)

5. **One-shot cache buster**: The cache-busting value must be consumed on the retry and must not persist on subsequent normal requests

## What to Look For

Look at how the `ShapeStream` class processes 409 `must-refetch` responses. The buggy behavior fabricates new handles by appending `-next` when the server's 409 response lacks a handle header — this is what causes the problems described above.
