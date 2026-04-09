#!/bin/bash
set -e

cd /workspace/dagster

# Apply the gold patch for init container digest support
patch -p1 << 'PATCH'
diff --git a/helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml b/helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml
index d83d8eb47ea90..5c7aea9191140 100644
--- a/helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml
+++ b/helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml
@@ -46,7 +46,9 @@ spec:
       securityContext: {{ $deployment.podSecurityContext | toYaml | nindent 8 }}
       {{- if $deployment.initContainers }}
       initContainers:
-        {{- toYaml $deployment.initContainers | nindent 8 }}
+        {{- range $container := $deployment.initContainers }}
+        - {{ include "dagster.initContainer" (list $ $container) | nindent 10 | trim }}
+        {{- end }}
       {{- end }}
       containers:
         - name: {{ $.Chart.Name }}
diff --git a/helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl b/helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl
index 76d66fe415b99..96e5b7b3758e7 100644
--- a/helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl
+++ b/helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl
@@ -43,6 +43,53 @@ If release name contains chart name it will be used as a full name.
   {{- end }}
 {{- end }}

+{{/*
+Render init container image name from structured or string format.
+Supports both legacy string format ("repo:tag") and structured format ({repository, tag, digest}).
+*/}}
+{{- define "dagster.initContainerImage.name" }}
+  {{- $ := index . 0 }}
+  {{- $image := index . 1 }}
+
+  {{- /* Handle string image format (backwards compat) */}}
+  {{- if kindIs "string" $image }}
+    {{- $image }}
+  {{- else }}
+    {{- /* Handle structured image format */}}
+    {{- if and $image.digest (ne $image.digest "") }}
+      {{- printf "%s@%s" $image.repository $image.digest }}
+    {{- else if $image.tag }}
+      {{- $tag := $image.tag | toYaml | trimAll "\"" }}
+      {{- printf "%s:%s" $image.repository $tag }}
+    {{- else }}
+      {{- printf "%s:%s" $image.repository $.Chart.Version }}
+    {{- end }}
+  {{- end }}
+{{- end }}
+
+{{/*
+Render a full init container spec, processing structured image format if present.
+*/}}
+{{- define "dagster.initContainer" }}
+  {{- $ := index . 0 }}
+  {{- $container := index . 1 }}
+
+  {{- /* If container.image is a string, pass through the whole container */}}
+  {{- if kindIs "string" $container.image }}
+    {{- toYaml $container }}
+  {{- else }}
+    {{- /* Build container with processed image */}}
+    {{- $processedImage := include "dagster.initContainerImage.name" (list $ $container.image) | trim }}
+    {{- $imagePullPolicy := $container.image.pullPolicy }}
+    {{- $containerWithoutImage := omit $container "image" }}
+    {{- $newContainer := merge (dict "image" $processedImage) $containerWithoutImage }}
+    {{- if $imagePullPolicy }}
+      {{- $newContainer = merge (dict "imagePullPolicy" $imagePullPolicy) $newContainer }}
+    {{- end }}
+    {{- toYaml $newContainer }}
+  {{- end }}
+{{- end }}
+
 {{/*
 Create chart name and version as used by the chart label.
 */}}
@@ -147,7 +194,10 @@ DAGSTER_K8S_PIPELINE_RUN_ENV_CONFIGMAP: "{{ template "dagster.fullname" . }}-pip
         containers: {{- toYaml .sidecarContainers | nindent 10 }}
         {{- end }}
         {{- if .initContainers }}
-        init_containers: {{- toYaml .initContainers | nindent 10 }}
+        init_containers:
+          {{- range $container := .initContainers }}
+          - {{ include "dagster.initContainer" (list $ $container) | nindent 12 | trim }}
+          {{- end }}
         {{- end }}
       {{- if .annotations }}
       pod_template_spec_metadata:
diff --git a/helm/dagster/charts/dagster-user-deployments/values.schema.json b/helm/dagster/charts/dagster-user-deployments/values.schema.json
index 05a66a716ef97..f4ccd000b970c 100644
--- a/helm/dagster/charts/dagster-user-deployments/values.schema.json
+++ b/helm/dagster/charts/dagster-user-deployments/values.schema.json
@@ -119,6 +119,77 @@
             "title": "Image",
             "type": "object"
         },
+        "InitContainerImage": {
+            "description": "Image specification for init containers, with all fields optional except repository.",
+            "properties": {
+                "repository": {
+                    "title": "Repository",
+                    "type": "string"
+                },
+                "tag": {
+                    "anyOf": [
+                        {
+                            "type": "string"
+                        },
+                        {
+                            "type": "integer"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null,
+                    "title": "Tag"
+                },
+                "digest": {
+                    "anyOf": [
+                        {
+                            "type": "string"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null,
+                    "title": "Digest"
+                },
+                "pullPolicy": {
+                    "anyOf": [
+                        {
+                            "$ref": "#/$defs/PullPolicy"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null
+                }
+            },
+            "required": [
+                "repository"
+            ],
+            "title": "InitContainerImage",
+            "type": "object"
+        },
+        "InitContainerWithStructuredImage": {
+            "additionalProperties": true,
+            "description": "Init container with structured image specification (repository/tag/digest).",
+            "properties": {
+                "name": {
+                    "title": "Name",
+                    "type": "string"
+                },
+                "image": {
+                    "$ref": "#/$defs/InitContainerImage"
+                }
+            },
+            "required": [
+                "name",
+                "image"
+            ],
+            "title": "InitContainerWithStructuredImage",
+            "type": "object"
+        },
         "LivenessProbe": {
             "$ref": "https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/v1.19.0/_definitions.json#/definitions/io.k8s.api.core.v1.Probe",
             "additionalProperties": true,
@@ -523,7 +594,14 @@
                     "anyOf": [
                         {
                             "items": {
-                                "$ref": "#/$defs/Container"
+                                "anyOf": [
+                                    {
+                                        "$ref": "#/$defs/Container"
+                                    },
+                                    {
+                                        "$ref": "#/$defs/InitContainerWithStructuredImage"
+                                    }
+                                ]
                             },
                             "type": "array"
                         },
diff --git a/helm/dagster/charts/dagster-user-deployments/values.yaml b/helm/dagster/charts/dagster-user-deployments/values.yaml
index bd3bd045535de..858e0ff65fc44 100644
--- a/helm/dagster/charts/dagster-user-deployments/values.yaml
+++ b/helm/dagster/charts/dagster-user-deployments/values.yaml
@@ -117,6 +117,21 @@ deployments:

     # Init containers to run before the main container. See:
     # https://kubernetes.io/docs/concepts/workloads/pods/init-containers/
+    #
+    # Image can be specified as a string or structured object:
+    #
+    # initContainers:
+    #   - name: init-permissions
+    #     image: "busybox:latest"  # Legacy string format
+    #     command: ["sh", "-c", "chmod 755 /data"]
+    #
+    #   - name: init-with-digest
+    #     image:                    # Structured format (digest takes precedence over tag)
+    #       repository: "busybox"
+    #       tag: "1.36"
+    #       digest: "sha256:abc123..."
+    #       pullPolicy: "IfNotPresent"
+    #     command: ["sh", "-c", "echo hello"]
     initContainers: []

     # Additional containers (i.e. sidecars) to run alongside the main container. See:
diff --git a/helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py b/helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py
index 719289cb022ec..f490f1532ac47 100644
--- a/helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py
+++ b/helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py
@@ -39,7 +39,9 @@ class UserDeployment(BaseModel):
     volumeMounts: Optional[list[kubernetes.VolumeMount]] = None
     volumes: Optional[list[kubernetes.Volume]] = None
     schedulerName: Optional[str] = None
-    initContainers: Optional[list[kubernetes.Container]] = None
+    initContainers: Optional[
+        list[Union[kubernetes.Container, kubernetes.InitContainerWithStructuredImage]]
+    ] = None
     sidecarContainers: Optional[list[kubernetes.Container]] = None
     deploymentStrategy: Optional[kubernetes.DeploymentStrategy] = None

diff --git a/helm/dagster/schema/schema/charts/utils/kubernetes.py b/helm/dagster/schema/schema/charts/utils/kubernetes.py
index 623105f44e38e..fdb1c74a28e44 100644
--- a/helm/dagster/schema/schema/charts/utils/kubernetes.py
+++ b/helm/dagster/schema/schema/charts/utils/kubernetes.py
@@ -56,6 +56,24 @@ class ExternalImage(Image):
     tag: str


+class InitContainerImage(BaseModel):
+    """Image specification for init containers, with all fields optional except repository."""
+
+    repository: str
+    tag: Optional[Union[str, int]] = None
+    digest: Optional[str] = None
+    pullPolicy: Optional[PullPolicy] = None
+
+    @property
+    def name(self) -> str:
+        if self.digest:
+            return f"{self.repository}@{self.digest}"
+        elif self.tag:
+            return f"{self.repository}:{self.tag}"
+        else:
+            return self.repository
+
+
 class Service(BaseModel, extra="forbid"):
     type: str
     port: int
@@ -119,6 +137,17 @@ class InitContainer(BaseModel):
     }


+class InitContainerWithStructuredImage(BaseModel):
+    """Init container with structured image specification (repository/tag/digest)."""
+
+    name: str
+    image: InitContainerImage
+
+    model_config = {
+        "extra": "allow",
+    }
+
+
 class Resources(RootModel[dict[str, Any]]):
     model_config = {
         "json_schema_extra": {
diff --git a/helm/dagster/schema/schema_tests/test_user_deployments.py b/helm/dagster/schema/schema_tests/test_user_deployments.py
index ae6647b5b7add..697e0ee354294 100644
--- a/helm/dagster/schema/schema_tests/test_user_deployments.py
+++ b/helm/dagster/schema/schema_tests/test_user_deployments.py
@@ -688,6 +688,164 @@ def test_user_deployment_digest_only(template: HelmTemplate):
     assert image == "repo/foo@sha256:abc123def456789"


+def test_init_container_with_string_image(template: HelmTemplate):
+    """Test that init containers with legacy string image format still work."""
+    deployment = create_simple_user_deployment("foo")
+    deployment.initContainers = [
+        kubernetes.Container.construct(
+            None,
+            name="init-test",
+            image="busybox:latest",
+            command=["sh", "-c", "echo hello"],
+        )
+    ]
+
+    helm_values = DagsterHelmValues.construct(
+        dagsterUserDeployments=UserDeployments.construct(
+            enabled=True,
+            enableSubchart=True,
+            deployments=[deployment],
+        )
+    )
+
+    user_deployments = template.render(helm_values)
+
+    assert len(user_deployments) == 1
+    init_containers = user_deployments[0].spec.template.spec.init_containers
+    assert len(init_containers) == 1
+    assert init_containers[0].name == "init-test"
+    assert init_containers[0].image == "busybox:latest"
+    assert init_containers[0].command == ["sh", "-c", "echo hello"]
+
+
+def test_init_container_with_structured_image_tag(template: HelmTemplate):
+    """Test init container with structured image format using tag."""
+    deployment = create_simple_user_deployment("foo")
+    deployment.initContainers = [
+        kubernetes.InitContainerWithStructuredImage.construct(
+            name="init-test",
+            image=kubernetes.InitContainerImage(
+                repository="busybox",
+                tag="1.36",
+            ),
+            command=["sh", "-c", "echo hello"],
+        )
+    ]
+
+    helm_values = DagsterHelmValues.construct(
+        dagsterUserDeployments=UserDeployments.construct(
+            enabled=True,
+            enableSubchart=True,
+            deployments=[deployment],
+        )
+    )
+
+    user_deployments = template.render(helm_values)
+
+    assert len(user_deployments) == 1
+    init_containers = user_deployments[0].spec.template.spec.init_containers
+    assert len(init_containers) == 1
+    assert init_containers[0].name == "init-test"
+    assert init_containers[0].image == "busybox:1.36"
+
+
+def test_init_container_with_structured_image_digest(template: HelmTemplate):
+    """Test init container with structured image format using digest."""
+    deployment = create_simple_user_deployment("foo")
+    deployment.initContainers = [
+        kubernetes.InitContainerWithStructuredImage.construct(
+            name="init-test",
+            image=kubernetes.InitContainerImage(
+                repository="busybox",
+                digest="sha256:abc123def456",
+            ),
+            command=["sh", "-c", "echo hello"],
+        )
+    ]
+
+    helm_values = DagsterHelmValues.construct(
+        dagsterUserDeployments=UserDeployments.construct(
+            enabled=True,
+            enableSubchart=True,
+            deployments=[deployment],
+        )
+    )
+
+    user_deployments = template.render(helm_values)
+
+    assert len(user_deployments) == 1
+    init_containers = user_deployments[0].spec.template.spec.init_containers
+    assert len(init_containers) == 1
+    assert init_containers[0].name == "init-test"
+    assert init_containers[0].image == "busybox@sha256:abc123def456"
+
+
+def test_init_container_digest_takes_precedence_over_tag(template: HelmTemplate):
+    """Test that digest takes precedence over tag for init container images."""
+    deployment = create_simple_user_deployment("foo")
+    deployment.initContainers = [
+        kubernetes.InitContainerWithStructuredImage.construct(
+            name="init-test",
+            image=kubernetes.InitContainerImage(
+                repository="busybox",
+                tag="1.36",
+                digest="sha256:abc123def456",
+            ),
+            command=["sh", "-c", "echo hello"],
+        )
+    ]
+
+    helm_values = DagsterHelmValues.construct(
+        dagsterUserDeployments=UserDeployments.construct(
+            enabled=True,
+            enableSubchart=True,
+            deployments=[deployment],
+        )
+    )
+
+    user_deployments = template.render(helm_values)
+
+    assert len(user_deployments) == 1
+    init_containers = user_deployments[0].spec.template.spec.init_containers
+    assert len(init_containers) == 1
+    assert init_containers[0].name == "init-test"
+    # Digest should take precedence over tag
+    assert init_containers[0].image == "busybox@sha256:abc123def456"
+
+
+def test_init_container_with_pull_policy(template: HelmTemplate):
+    """Test that pullPolicy is properly set for init containers with structured images."""
+    deployment = create_simple_user_deployment("foo")
+    deployment.initContainers = [
+        kubernetes.InitContainerWithStructuredImage.construct(
+            name="init-test",
+            image=kubernetes.InitContainerImage(
+                repository="busybox",
+                tag="1.36",
+                pullPolicy="IfNotPresent",
+            ),
+            command=["sh", "-c", "echo hello"],
+        )
+    ]
+
+    helm_values = DagsterHelmValues.construct(
+        dagsterUserDeployments=UserDeployments.construct(
+            enabled=True,
+            enableSubchart=True,
+            deployments=[deployment],
+        )
+    )
+
+    user_deployments = template.render(helm_values)
+
+    assert len(user_deployments) == 1
+    init_containers = user_deployments[0].spec.template.spec.init_containers
+    assert len(init_containers) == 1
+    assert init_containers[0].name == "init-test"
+    assert init_containers[0].image == "busybox:1.36"
+    assert init_containers[0].image_pull_policy == "IfNotPresent"
+
+
 def _assert_no_container_context(user_deployment):
     # No container context set by default
     env_names = [env.name for env in user_deployment.spec.template.spec.containers[0].env]
diff --git a/helm/dagster/values.schema.json b/helm/dagster/values.schema.json
index ce40dd0c1bd26..76800e034d1b8 100644
--- a/helm/dagster/values.schema.json
+++ b/helm/dagster/values.schema.json
@@ -1513,6 +1513,77 @@
             "title": "InitContainer",
             "type": "object"
         },
+        "InitContainerImage": {
+            "description": "Image specification for init containers, with all fields optional except repository.",
+            "properties": {
+                "repository": {
+                    "title": "Repository",
+                    "type": "string"
+                },
+                "tag": {
+                    "anyOf": [
+                        {
+                            "type": "string"
+                        },
+                        {
+                            "type": "integer"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null,
+                    "title": "Tag"
+                },
+                "digest": {
+                    "anyOf": [
+                        {
+                            "type": "string"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null,
+                    "title": "Digest"
+                },
+                "pullPolicy": {
+                    "anyOf": [
+                        {
+                            "$ref": "#/$defs/PullPolicy"
+                        },
+                        {
+                            "type": "null"
+                        }
+                    ],
+                    "default": null
+                }
+            },
+            "required": [
+                "repository"
+            ],
+            "title": "InitContainerImage",
+            "type": "object"
+        },
+        "InitContainerWithStructuredImage": {
+            "additionalProperties": true,
+            "description": "Init container with structured image specification (repository/tag/digest).",
+            "properties": {
+                "name": {
+                    "title": "Name",
+                    "type": "string"
+                },
+                "image": {
+                    "$ref": "#/$defs/InitContainerImage"
+                }
+            },
+            "required": [
+                "name",
+                "image"
+            ],
+            "title": "InitContainerWithStructuredImage",
+            "type": "object"
+        },
         "K8sRunLauncherConfig": {
             "additionalProperties": false,
             "properties": {
@@ -3301,7 +3372,14 @@
                     "anyOf": [
                         {
                             "items": {
-                                "$ref": "#/$defs/Container"
+                                "anyOf": [
+                                    {
+                                        "$ref": "#/$defs/Container"
+                                    },
+                                    {
+                                        "$ref": "#/$defs/InitContainerWithStructuredImage"
+                                    }
+                                ]
                             },
                             "type": "array"
                         },
PATCH

echo "Patch applied successfully!"
