The Appwrite Origin validator currently rejects `tauri://localhost` as an invalid origin. Tauri is a popular framework for building desktop applications using web technologies, and it uses `tauri://localhost` as the origin for its webviews.

When a Tauri app tries to connect to Appwrite with origin `tauri://localhost`, the validator rejects it with an "Invalid Scheme" or "Invalid Origin" error, even when `localhost` is registered as an allowed hostname.

Your task is to add support for the `tauri://` scheme in the origin validation system:

1. **Platform definition** (`src/Appwrite/Network/Platform.php`): Add a new scheme constant for Tauri and register it with a user-friendly name like "Web (Tauri)"

2. **Origin validation** (`src/Appwrite/Network/Validator/Origin.php`): Include the Tauri scheme in the list of web platforms that should undergo hostname validation

3. **Tests** (`tests/unit/Network/Validators/OriginTest.php`): Add test cases covering:
   - `tauri://localhost` being valid when localhost is registered
   - `tauri://example.com` being invalid with the proper error message directing users to register it as a "Web (Tauri)" platform

The validator already handles similar schemes like `http://`, `https://`, and browser extension schemes (`chrome-extension://`, etc.) by checking the hostname against an allowlist. The Tauri scheme should follow the same pattern.

After your changes, `tauri://localhost` should be accepted when `localhost` is in the allowed hostnames list, and `tauri://<unregistered-host>` should produce a descriptive error message telling users to register the hostname as a new "Web (Tauri)" platform.
