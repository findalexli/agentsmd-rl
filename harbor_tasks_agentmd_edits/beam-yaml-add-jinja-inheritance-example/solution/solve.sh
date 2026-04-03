#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if [ -f sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/README.md ]; then
    echo "Patch already applied."
    exit 0
fi

# --- Create new directories ---
mkdir -p sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/base

# --- Create inheritance/README.md ---
cat > sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/README.md <<'READMEOF'
<!--
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
-->

# Jinja Inheritance Example

This folder contains an example of how to use Jinja2 inheritance in Beam YAML pipelines.

## Files

*   **base/base_pipeline.yaml**: A complete WordCount pipeline (Read -> Split -> Explode -> Combine -> MapToFields -> Write). It defines a block `extra_steps` between `Explode` and `MapToFields` to allow child pipelines to inject additional transforms.
*   **wordCountInheritance.yaml**: Extends `base/base_pipeline.yaml` and injects a `Combine` transform into the `extra_steps` block to combine words.

## Running the Example

To run the child pipeline (which includes the inherited base pipeline logic + the new filter):

General setup:
```sh
export PIPELINE_FILE=apache_beam/yaml/examples/transforms/jinja/inheritance/wordCountInheritance.yaml
export KINGLEAR="gs://dataflow-samples/shakespeare/kinglear.txt"
export TEMP_LOCATION="gs://MY-BUCKET/wordCounts/"
export PROJECT="MY-PROJECT"
export REGION="MY-REGION"

cd <PATH_TO_BEAM_REPO>/beam/sdks/python
```

Multiline Run Example:
```sh
python -m apache_beam.yaml.main \
  --project=${PROJECT} \
  --region=${REGION} \
  --yaml_pipeline_file="${PIPELINE_FILE}" \
  --jinja_variables='{
    "readFromTextTransform": {"path": "'"${KINGLEAR}"'"},
    "mapToFieldsSplitConfig": {
      "language": "python",
      "fields": {
        "value": "1"
      }
    },
    "explodeTransform": {"fields": "word"},
    "combineTransform": {
      "group_by": "word",
      "combine": {"value": "sum"}
    },
    "mapToFieldsCountConfig": {
      "language": "python",
      "fields": {"output": "word + \" - \" + str(value)"}
    },
    "writeToTextTransform": {"path": "'"${TEMP_LOCATION}"'"}
  }'
```

Single Line Run Example:
```sh
python -m apache_beam.yaml.main --project=${PROJECT} --region=${REGION} \
--yaml_pipeline_file="${PIPELINE_FILE}" --jinja_variables='{"readFromTextTransform":
{"path": "'"${KINGLEAR}"'"}, "mapToFieldsSplitConfig": {"language": "python", "fields":{"value":"1"}}, "explodeTransform":{"fields":"word"}, "combineTransform":{"group_by":"word", "combine":{"value":"sum"}}, "mapToFieldsCountConfig":{"language": "python", "fields":{"output":"word + \" - \" + str(value)"}}, "writeToTextTransform":{"path":"'"${TEMP_LOCATION}"'"}}'
```
READMEOF

# --- Create base/base_pipeline.yaml ---
cat > sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/base/base_pipeline.yaml <<'BASEEOF'
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

pipeline:
  type: chain
  transforms:
    - type: ReadFromText
      config:
        path: {{readFromTextTransform.path}}

    - type: MapToFields
      name: Split words
      config:
        language: python
        fields:
          word:
            callable: |-
              import re
              def my_mapping(row):
                return re.findall(r'[A-Za-z\']+', row.line.lower())
          value: {{mapToFieldsSplitConfig.fields.value}}
    - type: Explode
      config:
        fields:
          - {{explodeTransform.fields}}

    # Inheritance injection point: content added here by child pipelines will be executed
    # after Explode and before MapToFields.
{% block extra_steps %}
{% endblock %}

    - type: MapToFields
      name: Format output
      config:
        language: {{mapToFieldsCountConfig.language}}
        fields:
          output: {{mapToFieldsCountConfig.fields.output}}
    - name: Write to GCS
      type: WriteToText
      config:
        path: {{writeToTextTransform.path}}
BASEEOF

# --- Create wordCountInheritance.yaml ---
# Note: original PR had no trailing newline; we add one for cleanliness
cat > sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/wordCountInheritance.yaml <<'CHILDEOF'
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

{% extends "apache_beam/yaml/examples/transforms/jinja/inheritance/base/base_pipeline.yaml" %}

{% block extra_steps %}
    - name: Count words
      type: Combine
      config:
        group_by:
          - {{combineTransform.group_by}}
        combine:
          value: {{combineTransform.combine.value}}
{% endblock %}

# Expected:
#  Row(output='king - 311')
#  Row(output='lear - 253')
#  Row(output='dramatis - 1')
#  Row(output='personae - 1')
#  Row(output='of - 483')
#  Row(output='britain - 2')
#  Row(output='france - 32')
#  Row(output='duke - 26')
#  Row(output='burgundy - 20')
#  Row(output='cornwall - 75')
CHILDEOF

# --- Patch examples_test.py: register inheritance test in preprocessors ---
python3 <<'PYEOF'
import re

path = 'sdks/python/apache_beam/yaml/examples/testing/examples_test.py'
with open(path) as f:
    content = f.read()

# 1. Add to _wordcount_jinja_test_preprocessor (two occurrences)
# Pattern: list containing wordCountInclude and wordCountImport on one line
content = content.replace(
    "['test_wordCountInclude_yaml', 'test_wordCountImport_yaml'])",
    "[\n    'test_wordCountInclude_yaml',\n    'test_wordCountImport_yaml',\n    'test_wordCountInheritance_yaml'\n])"
)

# 2. Add to _io_write_test_preprocessor
content = content.replace(
    "    'test_wordCountImport_yaml',\n    'test_iceberg_to_alloydb_yaml'",
    "    'test_wordCountImport_yaml',\n    'test_wordCountInheritance_yaml',\n    'test_iceberg_to_alloydb_yaml'"
)

with open(path, 'w') as f:
    f.write(content)

print("examples_test.py patched successfully.")
PYEOF

# --- Patch input_data.py: add inheritance template data ---
python3 <<'PYEOF'
path = 'sdks/python/apache_beam/yaml/examples/testing/input_data.py'
with open(path) as f:
    content = f.read()

# Add elif block after the import case
insert_after = """        'apache_beam/yaml/examples/transforms/jinja/'
        'import/macros/wordCountMacros.yaml'
    ]"""

new_block = insert_after + """
  elif test_name == 'test_wordCountInheritance_yaml':
    return [
        'apache_beam/yaml/examples/transforms/jinja/'
        'inheritance/base/base_pipeline.yaml'
    ]"""

content = content.replace(insert_after, new_block)

with open(path, 'w') as f:
    f.write(content)

print("input_data.py patched successfully.")
PYEOF

echo "Patch applied successfully."
