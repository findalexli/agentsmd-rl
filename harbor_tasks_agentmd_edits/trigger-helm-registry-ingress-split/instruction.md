# Separate Webapp and Registry Ingress in Helm Chart

## Problem

The Trigger.dev Helm chart currently uses a single shared ingress configuration for both the webapp and the Docker registry. This means you cannot configure different hostnames, TLS certificates, or annotations for the registry independently from the webapp. Additionally, the origin config (`appOrigin`, `loginOrigin`, `apiOrigin`) lives under a top-level `config:` key instead of being grouped with the `webapp:` section where it belongs.

When deploying to production with a separate registry domain (e.g., `registry.example.com` vs `trigger.example.com`), the current chart structure makes this impossible without manual template overrides.

## Expected Behavior

1. **Separate ingress resources**: The webapp and registry should each have their own ingress template and configuration block in `values.yaml`. The webapp ingress should be configurable under `webapp.ingress` and the registry ingress under `registry.ingress`.

2. **Relocated origin config**: The `appOrigin`, `loginOrigin`, and `apiOrigin` settings should move from the top-level `config:` section into the `webapp:` section, and all templates that reference them should be updated accordingly.

3. **Updated helpers**: The shared ingress annotation helper in `_helpers.tpl` should be split into separate webapp and registry helpers.

4. **Registry validation**: The external registry validation should no longer require a separate `port` field — the host string should include the port if needed (e.g., `localhost:5001`).

5. **Documentation**: The Helm chart's README should be updated to reflect the new configuration structure, showing the separate ingress blocks and the relocated origin settings.

## Files to Look At

- `hosting/k8s/helm/values.yaml` — default chart values
- `hosting/k8s/helm/values-production-example.yaml` — production example
- `hosting/k8s/helm/templates/ingress.yaml` — current shared ingress template
- `hosting/k8s/helm/templates/_helpers.tpl` — template helpers including ingress annotations
- `hosting/k8s/helm/templates/webapp.yaml` — webapp deployment referencing origin config
- `hosting/k8s/helm/templates/validate-external-config.yaml` — external service validation
- `hosting/k8s/helm/templates/NOTES.txt` — post-install notes
- `hosting/k8s/helm/README.md` — chart documentation
