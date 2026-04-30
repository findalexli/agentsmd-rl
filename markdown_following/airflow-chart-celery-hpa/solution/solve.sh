#!/bin/bash
set -e

cd /workspace/airflow

# Check if already patched (idempotency check)
if grep -q "workers.celery.hpa.enabled" chart/values.yaml 2>/dev/null; then
    echo "Already patched, skipping"
    exit 0
fi

echo "Patching values.yaml..."

# Add deprecation notes to old workers.hpa section
python3 << 'PYEOF'
with open('chart/values.yaml', 'r') as f:
    content = f.read()

# Add deprecation notes to the old workers.hpa section
old_hpa_section = '''  # Allow HPA for Airflow Celery workers (KEDA must be disabled)
  hpa:
    enabled: false

    # Minimum number of Airflow Celery workers created by HPA
    minReplicaCount: 0

    # Maximum number of Airflow Celery workers created by HPA
    maxReplicaCount: 5

    # Specifications for which to use to calculate the desired replica count
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 80

    # Scaling behavior of the target in both Up and Down directions
    behavior: {}'''

new_hpa_section = '''  # Allow HPA for Airflow Celery workers (KEDA must be disabled)
  # (deprecated, use `workers.celery.hpa` instead)
  hpa:
    # (deprecated, use `workers.celery.hpa.enabled` instead)
    enabled: false

    # (deprecated, use `workers.celery.hpa.minReplicaCount` instead)
    # Minimum number of Airflow Celery workers created by HPA
    minReplicaCount: 0

    # (deprecated, use `workers.celery.hpa.maxReplicaCount` instead)
    # Maximum number of Airflow Celery workers created by HPA
    maxReplicaCount: 5

    # (deprecated, use `workers.celery.hpa.metrics` instead)
    # Specifications for which to use to calculate the desired replica count
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 80

    # (deprecated, use `workers.celery.hpa.behavior` instead)
    # Scaling behavior of the target in both Up and Down directions
    behavior: {}'''

if old_hpa_section in content:
    content = content.replace(old_hpa_section, new_hpa_section)
    with open('chart/values.yaml', 'w') as f:
        f.write(content)
    print("Updated old workers.hpa deprecation notes in values.yaml")
else:
    print("Old workers.hpa section not found in expected format")
PYEOF

echo "Adding workers.celery.hpa section to values.yaml..."

# Add new workers.celery.hpa section using Python
python3 << 'PYEOF'
with open('chart/values.yaml', 'r') as f:
    content = f.read()

# Find the line with "    # Resource configuration for Airflow Celery workers"
# and insert the hpa section before it
hpa_section = '''    # Allow HPA for Airflow Celery workers (KEDA must be disabled)
    hpa:
      enabled: ~

      # Minimum number of Airflow Celery workers created by HPA
      minReplicaCount: ~

      # Maximum number of Airflow Celery workers created by HPA
      maxReplicaCount: ~

      # Specifications for which to use to calculate the desired replica count
      metrics: ~

      # Scaling behavior of the target in both Up and Down directions
      behavior: {}

'''

marker = "    # Resource configuration for Airflow Celery workers"
if marker in content and "    # Allow HPA for Airflow Celery workers (KEDA must be disabled)" not in content:
    content = content.replace(marker, hpa_section + marker)
    with open('chart/values.yaml', 'w') as f:
        f.write(content)
    print("Added hpa section to values.yaml")
else:
    print("Could not find insertion point or already exists")
PYEOF

echo "Patching values.schema.json..."

# Update values.schema.json
python3 << 'PYEOF'
import json

with open('chart/values.schema.json', 'r') as f:
    schema = json.load(f)

# Update old hpa descriptions with deprecation notices
workers_props = schema.get('properties', {}).get('workers', {}).get('properties', {})
if 'hpa' in workers_props:
    hpa_props = workers_props['hpa']
    if 'deprecated' not in hpa_props.get('description', '').lower():
        hpa_props['description'] = 'HPA configuration for Airflow Celery workers (deprecated, use ``workers.celery.hpa`` instead).'

    if 'properties' in hpa_props:
        if 'enabled' in hpa_props['properties']:
            desc = hpa_props['properties']['enabled'].get('description', '')
            if 'deprecated' not in desc.lower():
                hpa_props['properties']['enabled']['description'] = 'Allow HPA autoscaling (KEDA must be disabled) (deprecated, use ``workers.celery.hpa.enabled`` instead).'
        if 'minReplicaCount' in hpa_props['properties']:
            desc = hpa_props['properties']['minReplicaCount'].get('description', '')
            if 'deprecated' not in desc.lower():
                hpa_props['properties']['minReplicaCount']['description'] = 'Minimum number of Airflow Celery workers created by HPA (deprecated, use ``workers.celery.hpa.minReplicaCount`` instead).'
        if 'maxReplicaCount' in hpa_props['properties']:
            desc = hpa_props['properties']['maxReplicaCount'].get('description', '')
            if 'deprecated' not in desc.lower():
                hpa_props['properties']['maxReplicaCount']['description'] = 'Maximum number of Airflow Celery workers created by HPA (deprecated, use ``workers.celery.hpa.maxReplicaCount`` instead).'
        if 'metrics' in hpa_props['properties']:
            desc = hpa_props['properties']['metrics'].get('description', '')
            if 'deprecated' not in desc.lower():
                hpa_props['properties']['metrics']['description'] = 'Specifications for which to use to calculate the desired replica count (deprecated, use ``workers.celery.hpa.metrics`` instead).'
        if 'behavior' in hpa_props['properties']:
            desc = hpa_props['properties']['behavior'].get('description', '')
            if 'deprecated' not in desc.lower():
                hpa_props['properties']['behavior']['description'] = 'HorizontalPodAutoscalerBehavior configures the scaling behavior of the target (deprecated, use ``workers.celery.hpa.behavior`` instead).'

# Add new hpa to workers.celery.properties if not already there
hpa_schema = {
    "description": "HPA configuration for Airflow Celery workers.",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "enabled": {
            "description": "Allow HPA autoscaling (KEDA must be disabled).",
            "type": ["boolean", "null"],
            "default": None
        },
        "minReplicaCount": {
            "description": "Minimum number of Airflow Celery workers created by HPA.",
            "type": ["integer", "null"],
            "default": None
        },
        "maxReplicaCount": {
            "description": "Maximum number of Airflow Celery workers created by HPA.",
            "type": ["integer", "null"],
            "default": None
        },
        "metrics": {
            "description": "Specifications for which to use to calculate the desired replica count.",
            "type": ["array", "null"],
            "default": None,
            "items": {"$ref": "#/definitions/io.k8s.api.autoscaling.v2.MetricSpec"}
        },
        "behavior": {
            "description": "HorizontalPodAutoscalerBehavior configures the scaling behavior of the target.",
            "type": "object",
            "default": {},
            "$ref": "#/definitions/io.k8s.api.autoscaling.v2.HorizontalPodAutoscalerBehavior"
        }
    }
}

celery_props = schema.get('properties', {}).get('workers', {}).get('properties', {}).get('celery', {}).get('properties', {})
if 'hpa' not in celery_props:
    celery_props['hpa'] = hpa_schema

with open('chart/values.schema.json', 'w') as f:
    json.dump(schema, f, indent=4)

print("Updated values.schema.json")
PYEOF

echo "Patching worker-hpa.yaml template..."

# Update worker-hpa.yaml template with full worker sets support
cat > chart/templates/workers/worker-hpa.yaml << 'EOF'
{{/*
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
*/}}

################################
## Airflow Worker HPA
#################################
{{- $globals := deepCopy . -}}
{{- $filteredCelery := include "removeNilFields" .Values.workers.celery | fromYaml -}}
{{- $mergedWorkers := (include "workersMergeValues" (list .Values.workers $filteredCelery "" (list "kerberosInitContainer" "kerberosSidecar")) | fromYaml) -}}
{{- $_ := unset $mergedWorkers "celery" -}}
{{- $workerSets := .Values.workers.celery.sets | default list -}}
{{- if .Values.workers.celery.enableDefault -}}
  {{- $workerSets = concat (list (dict "name" "default")) $workerSets -}}
{{- end -}}
{{- range $workerSet := $workerSets -}}
  {{- $workers := (include "workersMergeValues" (list $mergedWorkers $workerSet "" list) | fromYaml) -}}
  {{- $_ := set $globals.Values "workers" $workers -}}
  {{- with $globals -}}
{{- $oldHpaEnabled := .Values.workers.hpa.enabled -}}
{{- $newHpaEnabled := ((.Values.workers.celery).hpa).enabled | default false -}}
{{- $celeryHpa := (.Values.workers.celery).hpa | default dict -}}
{{- $oldHpa := .Values.workers.hpa -}}
{{- $hpa := dict -}}
{{- if $newHpaEnabled -}}
  {{- $hpa = $celeryHpa -}}
{{- else if $oldHpaEnabled -}}
  {{- $hpa = $oldHpa -}}
{{- end -}}
{{- $kedaEnabled := or .Values.workers.keda.enabled ((.Values.workers.celery).keda).enabled | default false -}}
{{- $hpaEnabled := or $oldHpaEnabled $newHpaEnabled -}}
{{- if and (not $kedaEnabled) $hpaEnabled (or (contains "CeleryExecutor" .Values.executor) (contains "CeleryKubernetesExecutor" .Values.executor)) }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "airflow.fullname" . }}-worker{{ if ne .Values.workers.name "default" }}-{{ .Values.workers.name }}{{ end }}
  labels:
    tier: airflow
    component: worker-horizontalpodautoscaler
    release: {{ .Release.Name }}
    chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
    heritage: {{ .Release.Service }}
    deploymentName: {{ .Release.Name }}-worker{{ if ne .Values.workers.name "default" }}-{{ .Values.workers.name }}{{ end }}
    {{- if or .Values.labels .Values.workers.labels }}
      {{- mustMerge .Values.workers.labels .Values.labels | toYaml | nindent 4 }}
    {{- end }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: {{ ternary "StatefulSet" "Deployment" .Values.workers.persistence.enabled }}
    name: {{ include "airflow.fullname" . }}-worker{{ if ne .Values.workers.name "default" }}-{{ .Values.workers.name }}{{ end }}
  minReplicas: {{ $hpa.minReplicaCount }}
  maxReplicas: {{ $hpa.maxReplicaCount }}
  metrics: {{- toYaml $hpa.metrics | nindent 4 }}
  {{- with $hpa.behavior }}
  behavior: {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
{{- end }}
{{- end }}
EOF

echo "Patching NOTES.txt..."

# Add deprecation warnings to NOTES.txt
python3 << 'PYEOF'
with open('chart/templates/NOTES.txt', 'r') as f:
    content = f.read()

# Check if already patched
if "workers.hpa.enabled has been renamed" in content:
    print("NOTES.txt already patched")
else:
    # Insert before "{{- if not .Values.workers.persistence.enabled }}"
    notes_patch = '''{{- if .Values.workers.hpa.enabled }}

 DEPRECATION WARNING:
    `workers.hpa.enabled` has been renamed to `workers.celery.hpa.enabled`.
    Please change your values as support for the old name will be dropped in a future release.

{{- end }}

{{- if ne (int .Values.workers.hpa.minReplicaCount) 0 }}

 DEPRECATION WARNING:
    `workers.hpa.minReplicaCount` has been renamed to `workers.celery.hpa.minReplicaCount`.
    Please change your values as support for the old name will be dropped in a future release.

{{- end }}

{{- if ne (int .Values.workers.hpa.maxReplicaCount) 5 }}

 DEPRECATION WARNING:
    `workers.hpa.maxReplicaCount` has been renamed to `workers.celery.hpa.maxReplicaCount`.
    Please change your values as support for the old name will be dropped in a future release.

{{- end }}

{{- if ne (toJson .Values.workers.hpa.metrics | quote) (toJson "[{\\"resource\\":{\\"name\\":\\"cpu\\",\\"target\\":{\\"averageUtilization\\":80,\\"type\\":\\"Utilization\\"}},\\"type\\":\\"Resource\\"}]") }}

 DEPRECATION WARNING:
    `workers.hpa.metrics` has been renamed to `workers.celery.hpa.metrics`.
    Please change your values as support for the old name will be dropped in a future release.

{{- end }}

{{- if not (empty .Values.workers.hpa.behavior) }}

 DEPRECATION WARNING:
    `workers.hpa.behavior` has been renamed to `workers.celery.hpa.behavior`.
    Please change your values as support for the old name will be dropped in a future release.

{{- end }}

'''

    insert_marker = "{{- if not .Values.workers.persistence.enabled }}"

    if insert_marker in content:
        content = content.replace(insert_marker, notes_patch + insert_marker)
        with open('chart/templates/NOTES.txt', 'w') as f:
            f.write(content)
        print("Added deprecation warnings to NOTES.txt")
    else:
        print("Could not find insertion point in NOTES.txt")
PYEOF

echo "Creating newsfragment..."
mkdir -p chart/newsfragments
if [ ! -f chart/newsfragments/64734.significant.rst ]; then
    echo '\`\`workers.hpa\`\` section is now deprecated in favor of \`\`workers.celery.hpa\`\`. Please update your configuration accordingly.' > chart/newsfragments/64734.significant.rst
fi

echo "Updating worker-deployment.yaml..."

# Update worker-deployment.yaml
python3 << 'PYEOF'
with open('chart/templates/workers/worker-deployment.yaml', 'r') as f:
    content = f.read()

old_pattern = '''{{- $persistence := or .Values.workers.persistence.enabled }}
{{- $keda := .Values.workers.keda.enabled }}
{{- $hpa := and .Values.workers.hpa.enabled (not .Values.workers.keda.enabled) }}
{{- if or (contains "CeleryExecutor" .Values.executor) (contains "CeleryKubernetesExecutor" .Values.executor) }}
---'''

new_pattern = '''{{- if or (contains "CeleryExecutor" .Values.executor) (contains "CeleryKubernetesExecutor" .Values.executor) }}
---
{{- $persistence := or .Values.workers.persistence.enabled }}
{{- $keda := .Values.workers.keda.enabled }}
{{- $hpa := and .Values.workers.hpa.enabled (not .Values.workers.keda.enabled) }}'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('chart/templates/workers/worker-deployment.yaml', 'w') as f:
        f.write(content)
    print("Updated worker-deployment.yaml")
else:
    print("Pattern not found in worker-deployment.yaml, may already be different")
PYEOF

echo "Patching test_hpa.py..."

# Patch test_hpa.py
python3 << 'PYEOF'
with open('helm-tests/tests/helm_tests/other/test_hpa.py', 'r') as f:
    content = f.read()

# Only patch if not already patched
if "workers.celery.hpa" not in content:
    # Update test_hpa_disabled_by_default - remove docstring
    content = content.replace('    def test_hpa_disabled_by_default(self):\n        """Disabled by default."""', '    def test_hpa_disabled_by_default(self):')

    # Update test_hpa_enabled to use parametrize with new paths
    old_test = '''    @pytest.mark.parametrize(
        "executor",
        [
            "CeleryExecutor",
            "CeleryKubernetesExecutor",
            "CeleryExecutor,KubernetesExecutor",
        ],
    )
    def test_hpa_enabled(self, executor):
        """HPA should only be created when enabled and executor is Celery or CeleryKubernetes."""
        docs = render_chart(
            values={
                "workers": {"hpa": {"enabled": True}, "celery": {"persistence": {"enabled": False}}},
                "executor": executor,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("metadata.name", docs[0]) == "release-name-worker"'''

    new_test = '''    @pytest.mark.parametrize(
        "executor",
        [
            "CeleryExecutor",
            "CeleryKubernetesExecutor",
            "CeleryExecutor,KubernetesExecutor",
        ],
    )
    @pytest.mark.parametrize(
        "workers_values",
        [
            {"hpa": {"enabled": True}, "celery": {"persistence": {"enabled": False}}},
            {"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}}},
            {
                "hpa": {"enabled": False},
                "celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}},
            },
        ],
    )
    def test_hpa_enabled(self, executor, workers_values):
        docs = render_chart(
            values={
                "workers": workers_values,
                "executor": executor,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("metadata.name", docs[0]) == "release-name-worker"'''

    if old_test in content:
        content = content.replace(old_test, new_test)

    # Add new test for default min/max
    if "def test_min_max_replicas_default(self):" not in content:
        insert_after = "assert jmespath.search(\"metadata.name\", docs[0]) == \"release-name-worker\""
        new_test_default = '''\n\n    def test_min_max_replicas_default(self):
        docs = render_chart(
            values={"workers": {"celery": {"hpa": {"enabled": True}}}},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.minReplicas", docs[0]) == 0
        assert jmespath.search("spec.maxReplicas", docs[0]) == 5'''

        if insert_after in content:
            content = content.replace(insert_after, insert_after + new_test_default)

    # Update test_min_max_replicas
    old_minmax = '''    @pytest.mark.parametrize(
        ("min_replicas", "max_replicas"),
        [
            (None, None),
            (2, 8),
        ],
    )
    def test_min_max_replicas(self, min_replicas, max_replicas):
        """Verify minimum and maximum replicas."""
        docs = render_chart(
            values={
                "workers": {
                    "hpa": {
                        "enabled": True,
                        **({"minReplicaCount": min_replicas} if min_replicas else {}),
                        **({"maxReplicaCount": max_replicas} if max_replicas else {}),
                    }
                },
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )
        assert jmespath.search("spec.minReplicas", docs[0]) == 0 if min_replicas is None else min_replicas
        assert jmespath.search("spec.maxReplicas", docs[0]) == 5 if max_replicas is None else max_replicas'''

    new_minmax = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}},
            {"celery": {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}}},
            {
                "hpa": {"enabled": True, "minReplicaCount": 1, "maxReplicaCount": 10},
                "celery": {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}},
            },
        ],
    )
    def test_min_max_replicas(self, workers_values):
        docs = render_chart(
            values={"workers": workers_values},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.minReplicas", docs[0]) == 2
        assert jmespath.search("spec.maxReplicas", docs[0]) == 8'''

    if old_minmax in content:
        content = content.replace(old_minmax, new_minmax)

    # Update test_hpa_behavior
    old_behavior = '''    @pytest.mark.parametrize(
        "executor", ["CeleryExecutor", "CeleryKubernetesExecutor", "CeleryExecutor,KubernetesExecutor"]
    )
    def test_hpa_behavior(self, executor):
        """Verify HPA behavior."""
        expected_behavior = {
            "scaleDown": {
                "stabilizationWindowSeconds": 300,
                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
            }
        }
        docs = render_chart(
            values={
                "workers": {
                    "hpa": {
                        "enabled": True,
                        "behavior": expected_behavior,
                    },
                },
                "executor": executor,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )
        assert jmespath.search("spec.behavior", docs[0]) == expected_behavior'''

    new_behavior = '''    @pytest.mark.parametrize(
        "executor", ["CeleryExecutor", "CeleryKubernetesExecutor", "CeleryExecutor,KubernetesExecutor"]
    )
    @pytest.mark.parametrize(
        "workers_values",
        [
            {
                "hpa": {
                    "enabled": True,
                    "behavior": {
                        "scaleDown": {
                            "stabilizationWindowSeconds": 300,
                            "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
                        }
                    },
                }
            },
            {
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "behavior": {
                            "scaleDown": {
                                "stabilizationWindowSeconds": 300,
                                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
                            }
                        },
                    }
                }
            },
            {
                "hpa": {
                    "behavior": {
                        "scaleUp": {
                            "stabilizationWindowSeconds": 300,
                            "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
                        }
                    }
                },
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "behavior": {
                            "scaleDown": {
                                "stabilizationWindowSeconds": 300,
                                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
                            }
                        },
                    }
                },
            },
        ],
    )
    def test_hpa_behavior(self, executor, workers_values):
        """Verify HPA behavior."""
        docs = render_chart(
            values={
                "workers": workers_values,
                "executor": executor,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )
        assert jmespath.search("spec.behavior", docs[0]) == {
            "scaleDown": {
                "stabilizationWindowSeconds": 300,
                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
            }
        }'''

    if old_behavior in content:
        content = content.replace(old_behavior, new_behavior)

    # Update test_persistence
    old_persist = '''    @pytest.mark.parametrize(
        ("workers_persistence_values", "kind"),
        [
            ({"celery": {"persistence": {"enabled": True}}}, "StatefulSet"),
            ({"celery": {"persistence": {"enabled": False}}}, "Deployment"),
            ({"persistence": {"enabled": True}}, "StatefulSet"),
            ({"persistence": {"enabled": False}}, "Deployment"),
        ],
    )
    def test_persistence(self, workers_persistence_values, kind):
        """If worker persistence is enabled, scaleTargetRef should be StatefulSet else Deployment."""
        docs = render_chart(
            values={
                "workers": {"hpa": {"enabled": True}, **workers_persistence_values},
                "executor": "CeleryExecutor",
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )'''

    new_persist = '''    @pytest.mark.parametrize(
        ("workers_values", "kind"),
        [
            ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": True}}}, "StatefulSet"),
            ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}}}, "Deployment"),
            ({"persistence": {"enabled": True}, "celery": {"hpa": {"enabled": True}}}, "StatefulSet"),
            ({"persistence": {"enabled": False}, "celery": {"hpa": {"enabled": True}}}, "Deployment"),
        ],
    )
    def test_persistence(self, workers_values, kind):
        """If worker persistence is enabled, scaleTargetRef should be StatefulSet else Deployment."""
        docs = render_chart(
            values={
                "workers": workers_values,
                "executor": "CeleryExecutor",
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )'''

    if old_persist in content:
        content = content.replace(old_persist, new_persist)

    with open('helm-tests/tests/helm_tests/other/test_hpa.py', 'w') as f:
        f.write(content)
    print("test_hpa.py patched")
else:
    print("test_hpa.py already patched")
PYEOF

echo "Patching test_worker.py..."

# Patch test_worker.py
python3 << 'PYEOF'
with open('helm-tests/tests/helm_tests/airflow_core/test_worker.py', 'r') as f:
    content = f.read()

# Only patch if not already patched
if "workers.celery.hpa" not in content:
    # Update test_should_be_disabled_on_keda_enabled
    old_keda = '''    @pytest.mark.parametrize(
        "workers_keda_values",
        [
            {"keda": {"enabled": True}},
            {"celery": {"keda": {"enabled": True}}},
        ],
    )
    def test_should_be_disabled_on_keda_enabled(self, workers_keda_values):
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    **workers_keda_values,
                    "hpa": {"enabled": True},
                    "labels": {"test_label": "test_label_value"},
                },
            },
            show_only=[
                "templates/workers/worker-kedaautoscaler.yaml",
                "templates/workers/worker-hpa.yaml",
            ],
        )
        assert "test_label" in jmespath.search("metadata.labels", docs[0])
        assert jmespath.search("metadata.labels", docs[0])["test_label"] == "test_label_value"
        assert len(docs) == 1'''

    new_keda = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {"keda": {"enabled": True}, "hpa": {"enabled": True}},
            {"celery": {"keda": {"enabled": True}}, "hpa": {"enabled": True}},
            {"celery": {"keda": {"enabled": True}, "hpa": {"enabled": True}}},
            {"keda": {"enabled": True}, "celery": {"hpa": {"enabled": True}}},
        ],
    )
    def test_should_be_disabled_on_keda_enabled(self, workers_values):
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": workers_values,
            },
            show_only=[
                "templates/workers/worker-kedaautoscaler.yaml",
                "templates/workers/worker-hpa.yaml",
            ],
        )

        assert len(docs) == 1'''

    if old_keda in content:
        content = content.replace(old_keda, new_keda)

    # Update test_should_add_component_specific_labels
    old_labels = '''            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "hpa": {"enabled": True},
                    "labels": {"test_label": "test_label_value"},
                },
            },'''

    new_labels = '''            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "celery": {"hpa": {"enabled": True}},
                    "labels": {"test_label": "test_label_value"},
                },
            },'''

    if old_labels in content:
        content = content.replace(old_labels, new_labels)

    # Update test_should_use_hpa_metrics
    old_metrics = '''    @pytest.mark.parametrize(
        ("metrics", "executor", "expected_metrics"),
        [
            # default metrics
            (
                None,
                "CeleryExecutor",
                {
                    "type": "Resource",
                    "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 80}},
                },
            ),
            # custom metric
            (
                [
                    {
                        "type": "Pods",
                        "pods": {
                            "metric": {"name": "custom"},
                            "target": {"type": "Utilization", "averageUtilization": 80},
                        },
                    }
                ],
                "CeleryKubernetesExecutor",
                {
                    "type": "Pods",
                    "pods": {
                        "metric": {"name": "custom"},
                        "target": {"type": "Utilization", "averageUtilization": 80},
                    },
                },
            ),
        ],
    )
    def test_should_use_hpa_metrics(self, metrics, executor, expected_metrics):
        docs = render_chart(
            values={
                "executor": executor,
                "workers": {
                    "hpa": {"enabled": True, **({"metrics": metrics} if metrics else {})},
                },
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )
        assert expected_metrics == jmespath.search("spec.metrics[0]", docs[0])'''

    new_metrics = '''    @pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
    @pytest.mark.parametrize(
        "workers_values",
        [
            {"hpa": {"enabled": True}},
            {"celery": {"hpa": {"enabled": True}}},
        ],
    )
    def test_hpa_metrics_default(self, executor, workers_values):
        docs = render_chart(
            values={
                "executor": executor,
                "workers": workers_values,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.metrics", docs[0]) == [
            {
                "type": "Resource",
                "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 80}},
            }
        ]

    @pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
    @pytest.mark.parametrize(
        "workers_values",
        [
            {
                "hpa": {
                    "enabled": True,
                    "metrics": [
                        {
                            "type": "Pods",
                            "pods": {
                                "metric": {"name": "custom"},
                                "target": {"type": "Utilization", "averageUtilization": 80},
                            },
                        }
                    ],
                }
            },
            {
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "metrics": [
                            {
                                "type": "Pods",
                                "pods": {
                                    "metric": {"name": "custom"},
                                    "target": {"type": "Utilization", "averageUtilization": 80},
                                },
                            }
                        ],
                    }
                }
            },
            {
                "hpa": {
                    "enabled": True,
                    "metrics": [
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "memory",
                                "target": {"type": "Utilization", "averageUtilization": 1},
                            },
                        }
                    ],
                },
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "metrics": [
                            {
                                "type": "Pods",
                                "pods": {
                                    "metric": {"name": "custom"},
                                    "target": {"type": "Utilization", "averageUtilization": 80},
                                },
                            }
                        ],
                    }
                },
            },
        ],
    )
    def test_hpa_metrics_override(self, executor, workers_values):
        docs = render_chart(
            values={
                "executor": executor,
                "workers": workers_values,
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.metrics", docs[0]) == [
            {
                "type": "Pods",
                "pods": {
                    "metric": {"name": "custom"},
                    "target": {"type": "Utilization", "averageUtilization": 80},
                },
            }
        ]'''

    if old_metrics in content:
        content = content.replace(old_metrics, new_metrics)

    with open('helm-tests/tests/helm_tests/airflow_core/test_worker.py', 'w') as f:
        f.write(content)
    print("test_worker.py patched")
else:
    print("test_worker.py already patched")
PYEOF

echo "Patching test_worker_sets.py..."

# Patch test_worker_sets.py
python3 << 'PYEOF'
with open('helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py', 'r') as f:
    content = f.read()

# Only patch if not already patched
if "workers.celery.hpa" not in content:
    # Update test_create_hpa_sets
    old_create = '''            name="test",
            values={
                "workers": {
                    "hpa": {"enabled": True},
                    "celery": {
                        "enableDefault": enable_default,
                        "sets": [
                            {"name": "set1"},'''

    new_create = '''            name="test",
            values={
                "workers": {
                    "celery": {
                        "hpa": {"enabled": True},
                        "enableDefault": enable_default,
                        "sets": [
                            {"name": "set1"},'''

    if old_create in content:
        content = content.replace(old_create, new_create)

    # Update test_overwrite_hpa_enabled
    old_overwrite = '''    def test_overwrite_hpa_enabled(self):
        docs = render_chart(
            values={
                "workers": {
                    "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]},
                }
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert len(docs) == 1'''

    new_overwrite = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {"celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]}},
            {
                "celery": {
                    "enableDefault": False,
                    "hpa": {"enabled": False},
                    "sets": [{"name": "test", "hpa": {"enabled": True}}],
                }
            },
            {
                "hpa": {"enabled": False},
                "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]},
            },
        ],
    )
    def test_overwrite_hpa_enabled(self, workers_values):
        docs = render_chart(
            values={"workers": workers_values},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert len(docs) == 1'''

    if old_overwrite in content:
        content = content.replace(old_overwrite, new_overwrite)

    # Update test_overwrite_hpa_disable
    old_disable = '''    def test_overwrite_hpa_disable(self):
        docs = render_chart(
            values={
                "workers": {
                    "hpa": {"enabled": True},
                    "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": False}}]},
                }
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert len(docs) == 0'''

    new_disable = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {
                "celery": {
                    "enableDefault": False,
                    "hpa": {"enabled": True},
                    "sets": [{"name": "test", "hpa": {"enabled": False}}],
                }
            },
            {
                "hpa": {"enabled": True},
                "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": False}}]},
            },
        ],
    )
    def test_overwrite_hpa_disable(self, workers_values):
        docs = render_chart(
            values={"workers": workers_values},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert len(docs) == 0'''

    if old_disable in content:
        content = content.replace(old_disable, new_disable)

    # Update test_overwrite_hpa_min_replica_count
    old_min = '''    def test_overwrite_hpa_min_replica_count(self):
        docs = render_chart(
            values={
                "workers": {
                    "celery": {
                        "enableDefault": False,
                        "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
                    },
                }
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.minReplicas", docs[0]) == 10'''

    new_min = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {
                "celery": {
                    "enableDefault": False,
                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
                }
            },
            {
                "celery": {
                    "enableDefault": False,
                    "hpa": {"minReplicaCount": 7},
                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
                }
            },
            {
                "hpa": {"minReplicaCount": 7},
                "celery": {
                    "enableDefault": False,
                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
                },
            },
        ],
    )
    def test_overwrite_hpa_min_replica_count(self, workers_values):
        docs = render_chart(
            values={"workers": workers_values},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.minReplicas", docs[0]) == 10'''

    if old_min in content:
        content = content.replace(old_min, new_min)

    # Update test_overwrite_hpa_max_replica_count
    old_max = '''    def test_overwrite_hpa_max_replica_count(self):
        docs = render_chart(
            values={
                "workers": {
                    "celery": {
                        "enableDefault": False,
                        "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
                    },
                }
            },
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.maxReplicas", docs[0]) == 10'''

    new_max = '''    @pytest.mark.parametrize(
        "workers_values",
        [
            {
                "celery": {
                    "enableDefault": False,
                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
                }
            },
            {
                "celery": {
                    "enableDefault": False,
                    "hpa": {"maxReplicaCount": 7},
                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
                }
            },
            {
                "hpa": {"maxReplicaCount": 7},
                "celery": {
                    "enableDefault": False,
                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
                },
            },
        ],
    )
    def test_overwrite_hpa_max_replica_count(self, workers_values):
        docs = render_chart(
            values={"workers": workers_values},
            show_only=["templates/workers/worker-hpa.yaml"],
        )

        assert jmespath.search("spec.maxReplicas", docs[0]) == 10'''

    if old_max in content:
        content = content.replace(old_max, new_max)

    with open('helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py', 'w') as f:
        f.write(content)
    print("test_worker_sets.py patched")
else:
    print("test_worker_sets.py already patched")
PYEOF

echo "All patches applied successfully!"
