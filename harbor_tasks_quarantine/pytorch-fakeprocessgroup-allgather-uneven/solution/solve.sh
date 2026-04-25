#!/usr/bin/env bash
set -euo pipefail
cd /workspace/pytorch

# Idempotent: skip if already applied
grep -q 'tensor.size(0) != inputTensors\[0\].size(0)' torch/csrc/distributed/c10d/FakeProcessGroup.hpp && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/torch/csrc/distributed/c10d/FakeProcessGroup.hpp b/torch/csrc/distributed/c10d/FakeProcessGroup.hpp
index b0cb420eb6fca..f5947b8d65094 100644
--- a/torch/csrc/distributed/c10d/FakeProcessGroup.hpp
+++ b/torch/csrc/distributed/c10d/FakeProcessGroup.hpp
@@ -97,6 +97,9 @@ class FakeProcessGroup : public Backend {
       const AllgatherOptions& /* opts */ = AllgatherOptions()) override {
     checkCollectiveError();
     for (auto& tensor : outputTensors[0]) {
+      if (tensor.size(0) != inputTensors[0].size(0)) {
+        continue;
+      }
       tensor.copy_(inputTensors[0]);
     }
     return c10::make_intrusive<FakeWork>();

PATCH
