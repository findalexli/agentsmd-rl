The Appwrite Origin validator currently rejects `tauri://localhost` as an invalid origin. Tauri is a popular framework for building desktop applications using web technologies, and it uses `tauri://localhost` as the origin for its webviews.

When a Tauri app tries to connect to Appwrite with origin `tauri://localhost`, the validator rejects it with an "Invalid Scheme" or "Invalid Origin" error, even when `localhost` is registered as an allowed hostname.

Your task is to add support for the `tauri://` scheme in the origin validation system:

1. **Platform definition** (`src/Appwrite/Network/Platform.php`): Add a new scheme constant named exactly `SCHEME_TAURI` with value `'tauri'`. Register it with the user-friendly name `"Web (Tauri)"` via the `getNameByScheme()` method

2. **Origin validation** (`src/Appwrite/Network/Validator/Origin.php`): Include the Tauri scheme (referenced via `Platform::SCHEME_TAURI`) in the list of web platforms that should undergo hostname validation. The `Origin` validator constructor accepts two arguments: an array of allowed hostnames and an array of allowed schemes. For example: `new Origin(['localhost'], ['tauri'])`

3. **Tests** (`tests/unit/Network/Validators/OriginTest.php`): Add test cases covering:
   - `tauri://localhost` being valid when localhost is registered
   - `tauri://example.com` being invalid with the proper error message containing `"Web (Tauri)"` and directing users to register the hostname

The validator already handles similar schemes like HTTP (`Platform::SCHEME_HTTP`), HTTPS (`Platform::SCHEME_HTTPS`), and browser extension schemes (`Platform::SCHEME_CHROME_EXTENSION`, etc.) by checking the hostname against an allowlist. The Tauri scheme should follow the same pattern.

After your changes, `tauri://localhost` should be accepted when `localhost` is in the allowed hostnames list, and `tauri://<unregistered-host>` should produce a descriptive error message containing `"Web (Tauri)"` that tells users to register the hostname as a new platform.
