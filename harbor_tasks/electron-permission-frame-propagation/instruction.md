# Fix Permission Frame Propagation in Electron

## Problem

Permission checks in Electron's `WebContentsPermissionHelper` class are not correctly identifying the origin of the requesting frame. When a permission check is triggered from an iframe (sub-frame), the system incorrectly uses the main frame's origin instead of the iframe's origin.

This causes security issues where:
- Permission handlers receive incorrect `requestingOrigin` values
- Cross-origin iframes are incorrectly attributed to the parent frame's origin
- The `setPermissionCheckHandler` callback gets wrong information for sub-frame permission requests

## Affected Files

The issue is in the permission checking flow involving these files:

1. **`shell/browser/web_contents_permission_helper.h`** and **`.cc`**
   - `CheckPermission()` method
   - `CheckMediaAccessPermission()` method
   - `CheckSerialAccessPermission()` method

2. **`shell/browser/api/electron_api_web_contents.cc`**
   - `WebContents::CheckMediaAccessPermission()` method

3. **`shell/browser/serial/electron_serial_delegate.cc`**
   - `ElectronSerialDelegate::CanRequestPortPermission()` method

## What Needs to Change

The synchronous permission check methods need to receive and use the requesting `RenderFrameHost*` (the frame that triggered the permission check) rather than always defaulting to the main frame.

Key requirements:
1. `CheckPermission` should accept a `content::RenderFrameHost* requesting_frame` parameter
2. `CheckMediaAccessPermission` should accept the requesting frame and pass it through
3. `CheckSerialAccessPermission` should accept the requesting frame instead of just an origin
4. The origin should be obtained from `requesting_frame->GetLastCommittedOrigin()` not from `web_contents_->GetLastCommittedURL()`
5. Callers (`WebContents`, `ElectronSerialDelegate`) must pass the frame they receive to the permission helper

## Agent Instructions

Refer to the repository's guidelines in:
- `CLAUDE.md` - for build tools, development workflow, and code style
- `.github/copilot-instructions.md` - for C++ conventions and file naming

Key conventions to follow:
- C++ follows Chromium coding style
- Header guards use format: `#ifndef ELECTRON_SHELL_BROWSER_*_H_`
- Preserve the existing code structure and patterns

Focus on the `WebContentsPermissionHelper` class and its callers. Ensure that when permission checks are made, the correct frame's origin is propagated through the entire call chain.
