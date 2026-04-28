# Fix Permission Frame Propagation in Electron

## Problem

Permission checks in Electron's browser shell do not correctly identify which frame originated the permission request. When a sub-frame triggers a permission check, the system uses the main frame instead of the actual requesting frame to determine the security origin.

Specifically:

- The `CheckPermission` method in the permission helper class does not receive a `content::RenderFrameHost*` for the requesting frame, so it cannot call `GetLastCommittedOrigin().GetURL()` on the correct frame. Instead, it calls `GetPrimaryMainFrame()` which always returns the top-level frame regardless of which frame initiated the request.
- The `CheckMediaAccessPermission` method does not accept a `content::RenderFrameHost*` parameter, so callers cannot pass `render_frame_host` to it, and it cannot forward the correct frame to `CheckPermission`.
- The `CheckSerialAccessPermission` method takes a `url::Origin` parameter instead of a `content::RenderFrameHost*`, preventing it from deriving the origin from the requesting frame. Callers like `ElectronSerialDelegate::CanRequestPortPermission` must pass the frame itself rather than a pre-extracted origin.
- The `WebContents::CheckMediaAccessPermission` method in the Electron API layer needs to propagate the `render_frame_host` it already has access to down to the permission helper.

## Expected Behavior

Permission checks triggered from any frame (main frame or sub-frame) must determine the security origin from the actual requesting frame. The origin should come from the `content::RenderFrameHost` that originated the request, not from the web contents' main frame. The `GetPrimaryMainFrame()` method should not be used for permission origin determination.

The permission helper methods `CheckPermission`, `CheckMediaAccessPermission`, and `CheckSerialAccessPermission` should accept a `content::RenderFrameHost*` parameter so callers can identify the requesting frame. Callers throughout the shell browser directory must propagate this frame through the call chain, passing the `render_frame_host` they receive from the browser process down to `CheckPermission`.

The `ElectronSerialDelegate::CanRequestPortPermission` method receives a frame from Chromium's serial API and must pass it directly to `CheckSerialAccessPermission` rather than extracting the origin first.

## Code Style Requirements

All C++ code must follow Chromium coding style, verified by these tools:

- **clang-format**: Run with `--style=file` using the project's `.clang-format` configuration. All modified files must be properly formatted.
- **cpplint**: All modified C++ files must pass cpplint checks (with filters matching the project's existing cpplint configuration).

Header guards must use the convention `#ifndef ELECTRON_SHELL_BROWSER_*_H_`.

## Agent Instructions

You are working on the Electron repository at commit `821b738db0a64c863e8371e7141564cef70d56b8`. The permission checking flow spans:
- The permission helper class (declaration in the header, implementation in the `.cc` file) in the browser shell directory
- The Electron API wrapper for web contents that bridges renderer requests to the permission helper
- The serial delegate that handles Web Serial API permission requests

Refer to `CLAUDE.md` for build tools and development workflow, and `.github/copilot-instructions.md` for C++ conventions and file naming. Follow Chromium coding style. Preserve existing code structure and patterns.

Fix the permission check methods so that the requesting frame's origin is used instead of the main frame's origin for all synchronous permission checks.
