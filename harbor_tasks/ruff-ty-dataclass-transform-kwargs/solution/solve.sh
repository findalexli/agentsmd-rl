#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check
if grep -q 'call_arguments.iter().find_map' crates/ty_python_semantic/src/types/call/bind.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --3way - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md b/crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md
index e4254cccbdd494..992ee570d8a9d5 100644
--- a/crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md
+++ b/crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md
@@ -371,6 +371,62 @@ t = TestMeta(name="test")
 t.name = "new"  # error: [invalid-assignment]
 ```

+### Transformers using `**kwargs`
+
+Dataclass transform parameters like `frozen` should be recognized even when the transformer doesn't
+explicitly list them in its signature, but instead uses `**kwargs`.
+
+#### Function-based transformer
+
+```py
+from typing import dataclass_transform, Callable
+
+@dataclass_transform()
+def create_model[T: type](**kwargs) -> Callable[[T], T]:
+    raise NotImplementedError
+
+@create_model(frozen=True)
+class Frozen:
+    name: str
+
+f = Frozen("Alice")
+f.name = "Bob"  # error: [invalid-assignment]
+```
+
+#### Metaclass-based transformer
+
+```py
+from typing import dataclass_transform
+
+@dataclass_transform()
+class ModelMeta(type):
+    def __new__(cls, name, bases, namespace, **kwargs): ...
+
+class ModelBase(metaclass=ModelMeta): ...
+
+class Frozen(ModelBase, frozen=True):
+    name: str
+
+f = Frozen(name="test")
+f.name = "new"  # error: [invalid-assignment]
+```
+
+#### Base-class-based transformer
+
+```py
+from typing import dataclass_transform
+
+@dataclass_transform()
+class ModelBase:
+    def __init_subclass__(cls, **kwargs): ...
+
+class Frozen(ModelBase, frozen=True):
+    name: str
+
+f = Frozen(name="test")
+f.name = "new"  # error: [invalid-assignment]
+```
+
 ### Combining parameters

 Combining several of these parameters also works as expected:
diff --git a/crates/ty_python_semantic/src/types/call/bind.rs b/crates/ty_python_semantic/src/types/call/bind.rs
index 5a81b9874cb3c1..a1d4be82e9d9de 100644
--- a/crates/ty_python_semantic/src/types/call/bind.rs
+++ b/crates/ty_python_semantic/src/types/call/bind.rs
@@ -1788,8 +1788,16 @@ impl<'db> Bindings<'db> {
                                 let mut flags = dataclass_params.flags(db);

                                 for (param, flag) in DATACLASS_FLAGS {
-                                    if let Ok(Some(ty)) =
-                                        overload.parameter_type_by_name(param, false)
+                                    if let Some(ty) =
+                                        call_arguments.iter().find_map(|(arg, arg_types)| {
+                                            if let Argument::Keyword(arg_name) = arg
+                                                && *arg_name == **param
+                                            {
+                                                arg_types.get_default()
+                                            } else {
+                                                None
+                                            }
+                                        })
                                         && let Some(LiteralValueTypeKind::Bool(value)) =
                                             ty.as_literal_value_kind()
                                     {
PATCH

echo "Patch applied successfully."
