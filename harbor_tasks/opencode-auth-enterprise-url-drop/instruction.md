# Bug: Enterprise URL lost during OAuth auth flow

## Summary

When a plugin's OAuth callback returns extra fields (such as an enterprise URL), they are silently dropped before being stored. Only `access`, `refresh`, `expires`, and `accountId` are explicitly copied from the callback result into the auth store. Any additional fields the plugin returns are lost.

## Affected files

- `packages/opencode/src/provider/auth.ts` — the `callback` function in `ProviderAuth` namespace, specifically the `"refresh" in result` branch (~line 220). The code manually picks individual properties from the callback result rather than forwarding all of them.
- `packages/plugin/src/index.ts` — the `AuthOuathResult` type definition (~line 129 and ~line 149). The type doesn't declare `enterpriseUrl` as a valid field in the OAuth success response, so plugins have no way to type-safely return it.

## Expected behavior

When a plugin's OAuth callback returns additional fields beyond the core token fields, those extra fields should be preserved and stored in the auth entry. The type definition should also declare `enterpriseUrl` as an optional field so plugins can include it.

## How to reproduce

1. Configure an enterprise OAuth provider plugin that returns `{ type: "success", refresh: "...", access: "...", expires: 123, enterpriseUrl: "https://enterprise.example.com" }` from its callback
2. Complete the OAuth flow
3. Observe that `enterpriseUrl` is not persisted — it's dropped during the `auth.set` call
