# Separate webapp and registry ingress configuration in Helm chart

## Problem

The Trigger.dev Helm chart at `hosting/k8s/helm/` currently uses a single shared `ingress` configuration block at the top level of `values.yaml`. This means both the webapp and the Docker registry share the same ingress settings, making it impossible to configure them independently (e.g., different hostnames, TLS certificates, or ingress classes).

Additionally, origin configuration (`appOrigin`, `loginOrigin`, `apiOrigin`) is under a top-level `config:` key instead of being grouped with the webapp where it belongs. The webapp template (`webapp.yaml`) references `.Values.config.appOrigin` etc.

The registry host helper in `_helpers.tpl` also concatenates `host:port` from separate fields, which is inflexible — the host value should include the port when needed.

## Expected Behavior

1. **Split ingress**: The webapp and registry should each have their own `ingress` section (`webapp.ingress` and `registry.ingress`) with independent hosts, TLS, annotations, and className settings.
2. **Move origins**: `appOrigin`, `loginOrigin`, `apiOrigin` should move from `config:` to `webapp:` in values.yaml. All templates referencing them must be updated.
3. **Separate ingress templates**: The single `ingress.yaml` template should become `webapp-ingress.yaml`, and a new `registry-ingress.yaml` should be created.
4. **Update helpers**: The `_helpers.tpl` annotation helper should be split into webapp- and registry-specific versions. The registry host helper should use the host value directly instead of concatenating host and port.
5. **Update validation**: The external config validation template should no longer require `registry.external.port`.
6. **Update documentation**: The Helm chart README (`hosting/k8s/helm/README.md`) must be updated to reflect the new configuration structure — showing webapp.ingress and registry.ingress as separate blocks, and the updated origin configuration under webapp.

## Files to Look At

- `hosting/k8s/helm/values.yaml` — default values, needs restructuring
- `hosting/k8s/helm/values-production-example.yaml` — production example config
- `hosting/k8s/helm/templates/ingress.yaml` — current shared ingress template (rename to webapp-ingress.yaml)
- `hosting/k8s/helm/templates/_helpers.tpl` — template helpers for annotations and registry host
- `hosting/k8s/helm/templates/webapp.yaml` — webapp deployment referencing config origins
- `hosting/k8s/helm/templates/NOTES.txt` — post-install notes referencing ingress config
- `hosting/k8s/helm/templates/validate-external-config.yaml` — external service validation
- `hosting/k8s/helm/README.md` — chart documentation that must reflect the new structure
