#!/usr/bin/env bash
set -euo pipefail

cd /workspace/atopile

# Idempotency guard
if grep -qF "This release will contain deep core changes." ".claude/skills/ato-language/EXTENSION.md" && grep -qF "Every entity (a resistor, a power rail, an I2C bus, a voltage parameter) is a **" ".claude/skills/ato-language/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/ato-language/EXTENSION.md b/.claude/skills/ato-language/EXTENSION.md
@@ -2,21 +2,22 @@
 
 Skills are located in `.claude/skills/`.
 
+# 0.14.x
 
-# 0.14 Staging branch
-
-This release will contain deep core changes. 
+This release will contain deep core changes.
 Primarily using zig and the new graph language.
 Also restructuring of what faebryk means.
 
 Primary goals:
+
 - speed
 - maintainability
 - understanding of the core
 - more powerful graph
 - serializable graph
 
 ### Virtual Environment
+
 - This project uses a uv-managed virtual environment
 - If running in interactive shell activate with `source .venv/bin/activate`
 - Else run commands with `uv run <command>` prefix
@@ -30,6 +31,7 @@ Primary goals:
 To work with the graph, you need a `GraphView` (holds the entire graph state including types and instances) and a `TypeGraph` (manages type definitions).
 
 ### Example setting up graph, typegraph, defining type nodes, and instantiating instance nodes
+
 ```python
 # Setup graph and typegraph
 g = fabll.graph.GraphView.create()
@@ -44,22 +46,25 @@ parameter_instance = parameter_type.create_instance(g)
 electrical_type = F.Electrical.bind_typegraph(tg)
 electrical_instance = electrical_type.create_instance(g)
 ```
+
 ### Type Definition and Composition
+
 Most entities in the system (Modules, Interfaces, Parameters, etc.) are defined by subclassing `fabll.Node`.
 
 Composition is handled via the `MakeChild()` method, which creates "composition edges". When a class attribute is assigned the result of `SomeType.MakeChild()`, it declares that instances of this new type will contain an instance of `SomeType` as a child. This builds the structural hierarchy of the graph.
 
 Traits, on the other hand, use "trait edges". This is why the syntax differs: traits are attached using `MakeEdge()` (often wrapping `MakeChild()` if creating a new trait instance), whereas structural children use `MakeChild()` directly.
 
 #### MakeChild Example
+
 Using `ElectricPower` (from `src/faebryk/library/ElectricPower.py`) as a baseline:
 
 ```python
 class ElectricPower(fabll.Node):
     """
     Defines a new type 'ElectricPower' which is a fabll.Node.
     """
-    
+
     # Composition: ElectricPower contains two Electrical interfaces (hv and lv)
     # MakeChild() creates a definition that these children exist on this type.
     # When ElectricPower is instantiated, hv and lv will also be instantiated as children.
@@ -77,16 +82,21 @@ class ElectricPower(fabll.Node):
 ```
 
 ### Traits
+
 - Traits are the primary way nodes interact with eachother and functions are executed on nodes
 - One or many traits can be applied to type nodes or instance nodes
 
 is_interface trait example making and checking two node connections (assume setup from above)
+
 #### Definition Example
+
 ```python
 class Electrical(fabll.Node):
 	_is_interface = fabll.Traits.MakeEdge(fabll.is_interface.MakeChild())
 ```
+
 #### Usage Example
+
 ```python
 e1 = electrical_type.create_instance(g)
 e2 = electrical_type.create_instance(g)
@@ -97,6 +107,7 @@ bool connected = e1._is_interface.get().is_connected_to(e2)
 #### Checking for Traits: Instance Nodes vs Type Nodes
 
 **Instance Nodes** (runtime objects created from types):
+
 ```python
 instance = some_type.create_instance(g)
 instance.has_trait(F.some_trait)
@@ -105,18 +116,21 @@ instance.try_get_trait(F.some_trait)
 ```
 
 **Type Nodes** (type definitions in the typegraph):
+
 ```python
 type_bound = SomeType.bind_typegraph(tg)
 type_bound.try_get_type_trait(F.some_trait)
 type_bound.get_type_trait(F.some_trait)
 ```
 
 **Key Difference:**
+
 - Instance nodes: `.has_trait()`, `.try_get_trait()`, `.get_trait()`
 - Type nodes: `.try_get_type_trait()`, `.get_type_trait()` on `TypeNodeBoundTG`
 - `instance.get_type_node()` returns `BoundNodeReference` which has no trait methods - bind the type class instead
 
 ### Expressions
+
 Expressions are nodes that represent operations.
 
 `src/faebryk/library/Expressions.py`
@@ -127,55 +141,68 @@ anded = F.Expressions.And.bind_typegraph(tg).create_instance(g).setup(
 )
 ```
 
-
 ## Zig-Python Architecture
 
 ### Overview
+
 Core performance-critical functionality is implemented in Zig (`src/faebryk/core/zig/src/`). Python bindings expose this via the `pyzig` binding layer in `src/faebryk/core/zig/src/python/`.
 
 ### File Structure
+
 - `src/faebryk/core/zig/src/` - Core Zig implementations (graph, interfaces, algorithms)
 - `src/faebryk/core/zig/src/python/*_py.zig` - Python wrappers for Zig types/functions
 - `src/faebryk/core/zig/src/python/*/manual/*.pyi` - Type stubs for IDE support
 - `src/faebryk/core/zig/src/pyzig/` - Generic Python-Zig binding utilities
 
 ### Data Flow
+
 Python call → Python wrapper (Zig) parses args → Core Zig function → Wrapper converts result → Python receives native types
 
 ### Memory Management
+
 1. **Zig-owned**: Allocated with Zig allocator, must call `deinit()` when done
 2. **Python-owned wrappers**: Thin Python objects wrapping Zig data, custom deallocators call `deinit()` on GC
 3. **Ownership transfer**: Zig allocates → wraps in Python object → Python GC handles cleanup
 
 ### Adding Python-Accessible Functions
+
 1. Implement function in Zig (e.g., in `graph.zig` or `interface.zig`)
 2. Create wrapper in corresponding `*_py.zig` file using `wrap_*` pattern
 3. Add wrapper to appropriate `extra_methods` array
 4. Update type stub in `manual/*.pyi` file
 
 ### Error Handling
+
 Zig wrappers use "crash on error" philosophy - simplifies error handling by using `defer` for cleanup and letting Python GC handle successfully created objects.
 
 ## Testing
+
 ### Overall
+
 Run `ato dev test --llm` in root folder
+
 ### Zig Core
-`zig build test` 
+
+`zig build test`
 
 ## Test Reports (LLM + Tools)
+
 `ato dev test` writes a single source-of-truth JSON report at `artifacts/test-report.json`.
 Derived artifacts:
+
 - `artifacts/test-report.html` (human dashboard)
 - `artifacts/test-report.llm.json` (LLM-friendly; ANSI stripped, includes full tests + outputs)
 
 Key fields in `artifacts/test-report.json`:
+
 - `summary` (counts, regressions/fixed/new/removed, truncation stats)
 - `run` (argv, pytest args, environment subset, git info, worker stats)
 - `tests[]` (nodeid, file/class/function, status/outcome, duration, output preview, output_full logs, memory, worker log path)
 - `derived` (failures/regressions/slowest/memory_heaviest/collection_errors)
 - `llm` (jq recipes + recommended commands)
 
 LLM usage:
+
 - Prefer JSON over pytest output or HTML; it contains full stdout/stderr/logs/tracebacks (see `output_full`) plus truncation metadata.
 - Use jq for precise queries (examples are embedded in the `llm.jq_recipes` field).
 - `artifacts/test-report.llm.json` is always generated and has ANSI stripped logs.
diff --git a/.claude/skills/ato-language/SKILL.md b/.claude/skills/ato-language/SKILL.md
@@ -1,142 +1,256 @@
 ---
 name: ato-language
-description: "LLM-focused reference for the `ato` declarative DSL: mental model, syntax surface, experiments/feature flags, and common pitfalls when editing `.ato` and `ato.yaml`."
+description: "Reference for the `.ato` declarative DSL: type system, connection semantics, constraint model, and standard library. Use when authoring or reviewing `.ato` code."
 ---
 
-# ATO Language
+# The ato language
 
-`ato` is a **declarative** DSL for electronics design in the atopile ecosystem. It is intentionally “Python-shaped”, but it is **not** Python: there is no procedural execution model and (most importantly) no user-defined side effects.
-
-This skill is the canonical repo-local language guide (replacing various editor/assistant-specific duplicates).
+ato is a **declarative, constraint-based DSL** for describing electronic circuits. There is no control flow, no mutation, and no execution order — you declare _what_ a circuit is, and the compiler + solver resolve it into a valid design.
 
 ## Quick Start
 
-- When changing `.ato` files: keep everything **declarative** (no “do X then Y” assumptions).
-- If you need syntax gated behind experiments, enable it with `#pragma experiment("<NAME>")` (see below).
-- To validate a change quickly in-repo:
-  - `ato build` (project-level build)
-  - `ato dev test --llm -k ato` (if you’re touching compiler/lsp behavior; adjust `-k`)
+A minimal complete `.ato` file:
+
+```ato
+#pragma experiment("BRIDGE_CONNECT")
+
+import Resistor
+import ElectricPower
+import Capacitor
 
-## Mental Model (What ATO “Is”)
+module PowerFilter:
+    """A simple decoupled power input with a pull-down resistor."""
+    power = new ElectricPower
+    decoupling_capacitor = new Capacitor
+    pulldown_resistor = new Resistor
+
+    power.hv ~> decoupling_capacitor ~> power.lv
+    power.hv ~> pulldown_resistor ~> power.lv
+
+    decoupling_capacitor.capacitance = 100nF +/- 20%
+    pulldown_resistor.resistance = 100kohm +/- 5%
+    assert power.voltage within 3.0V to 3.6V
+```
 
-- **Blocks**: `module`, `interface`, `component`
-  - `module`: a type that can be instantiated (`new ...`)
-  - `interface`: a connectable interface type (electrical, buses, etc.)
-  - `component`: “code-as-data” (often used for reusable fragments)
-- **Instances**: created with `new`, can be single or container-sized (`new M[10]`).
-- **Connections**: wiring between interfaces using `~` (direct) and `~>` (bridge/series) when enabled.
-- **Parameters + constraints**: values constrained with `assert ...`, used for picking/validation.
+Validate with `ato build` from the package directory.
 
-## Experiments (Feature Flags)
+## Core Concepts
 
-Some syntax is gated behind `#pragma experiment(...)`. The authoritative list lives in `src/atopile/compiler/ast_visitor.py` (`ASTVisitor._Experiment`).
+### 1. Everything is a Node in a Graph
 
-Currently:
-- `BRIDGE_CONNECT`: enables `a ~> bridge ~> b` style “bridge operator” chains.
-- `FOR_LOOP`: enables `for item in container:` syntax.
-- `TRAITS`: enables `trait ...` syntax in ATO.
-- `MODULE_TEMPLATING`: enables `new MyModule<param_=literal>` style instantiation templating.
-- `INSTANCE_TRAITS`: enables instance-level trait constructs (see compiler implementation).
+Every entity (a resistor, a power rail, an I2C bus, a voltage parameter) is a **node** in a typed graph. Nodes relate to each other through **edges**: composition (parent–child), connection (same-net), and traits (behavioral metadata). The `.ato` language is a surface syntax for constructing this graph declaratively.
+
+### 2. Three Block Types
+
+ato has exactly three ways to define a new type:
+
+| Keyword     | Semantics                                            | Typical Use                 |
+| ----------- | ---------------------------------------------------- | --------------------------- |
+| `module`    | A design unit that contains children and connections | Circuit blocks, subsystems  |
+| `interface` | A connectable boundary; can be wired with `~`        | Buses, power rails, signals |
+| `component` | A physical part with footprint/symbol                | Vendor ICs, connectors      |
+
+All three compile to graph nodes. The distinction controls which **traits** the compiler attaches (`is_module`, `is_interface`) and what operations are legal (by convention, interfaces appear on both sides of `~`).
+
+Inheritance uses `from`:
 
-Enable example:
 ```ato
-#pragma experiment("FOR_LOOP")
+module MyRegulator from Regulator:
+    pass
 ```
 
-## Syntax Reference (Representative Examples)
+### 3. Composition — Children and Instantiation
 
-### Imports
-```ato
-import ModuleName
-import Module1, Module2.Submodule
+Types contain children. Inside a block body, `new` instantiates a child:
 
-from "path/to/source.ato" import SpecificModule
-import AnotherModule; from "another/source.ato" import AnotherSpecific
+```ato
+module Board:
+    power = new ElectricPower      # interface child
+    sensor = new BME280            # module child
+    caps = new Capacitor[4]        # array of 4 capacitors
 ```
 
-### Top-level statements
+Children are accessed via **dot-notation**: `sensor.power.voltage`, `caps[0].capacitance`.
+
+### 4. Connection — Declaring Electrical Identity
+
+The **wire operator `~`** declares that two interfaces _are the same net/bus_. It is bidirectional and requires matching types:
+
 ```ato
-pass
-"docstring-like statement"
-top_level_var = 123
-pass; another_var = 456; "another docstring"
+power_3v3 ~ sensor.power          # ElectricPower ~ ElectricPower
+i2c_bus ~ sensor.i2c              # I2C ~ I2C
 ```
 
-### Block definitions
+The **bridge operator `~>`** (requires `#pragma experiment("BRIDGE_CONNECT")`) inserts a component in series. The component must carry the `can_bridge` trait which defines its in/out mapping:
+
 ```ato
-component MyComponent:
-    pass
-    pass; internal_flag = True
+power_5v ~> regulator ~> power_3v3
+i2c.scl.line ~> pullup ~> power.hv
+```
 
-module AnotherBaseModule:
-    pin base_pin
-    base_param = 10
+### 5. Constraints — Physical Quantities and Assertions
 
-interface MyInterface:
-    pin io
+Values in ato carry **units** and **tolerances**. The solver uses these to select real parts.
 
-module DemoModule from AnotherBaseModule:
-    pin p1
-    signal my_signal
-    a_field: AnotherBaseModule
-```
+**Assignment** binds a value to a parameter:
 
-### Assignments
 ```ato
-value = 1
-value += 1; value -= 1
-flags |= 1; flags &= 2
+power.voltage = 3.3V +/- 5%
+resistor.resistance = 10kohm +/- 10%
+i2c.frequency = 400kHz
+i2c.address = 0x48
 ```
 
-### Connections
+**Assertions** declare constraints the solver must satisfy:
+
 ```ato
-p1 ~ base_pin
-iface_a ~ iface_b
-iface_a ~> bridge ~> iface_b     # requires BRIDGE_CONNECT
+assert power.voltage within 3.0V to 3.6V
+assert i2c.frequency <= 400kHz
+assert sensor.i2c.address is 0x50
 ```
 
-### Instantiation (and templating)
+Three value forms exist:
+
+- **Exact**: `3.3V`
+- **Bilateral tolerance**: `10kohm +/- 5%`
+- **Bounded range**: `3.0V to 3.6V`
+
+### 6. Traits — Behavioral Metadata
+
+Traits attach capabilities or metadata to nodes. They are not children — they use trait edges in the graph.
+
 ```ato
-instance = new MyComponent
-container = new MyComponent[10]
+#pragma experiment("TRAITS")
 
-templated_instance = new MyComponent<int_=1, float_=2.5>  # requires MODULE_TEMPLATING
+import has_part_removed
+import is_atomic_part
+
+module Placeholder:
+    trait has_part_removed          # mark as non-physical placeholder
+    trait is_atomic_part            # user-defined part with footprint
 ```
 
-### Assertions / constraints
+Key built-in traits:
+
+| Trait                   | Effect                                                           |
+| ----------------------- | ---------------------------------------------------------------- |
+| `can_bridge`            | Enables use with `~>` operator (defines in/out pin mapping)      |
+| `has_part_removed`      | No physical part placed (symbolic node)                          |
+| `is_atomic_part`        | User-defined part with `manufacturer`, `partnumber`, `footprint` |
+| `has_datasheet`         | Attaches a datasheet reference                                   |
+| `has_designator_prefix` | Sets PCB designator (R, C, U, etc.)                              |
+
+### 7. Import System
+
+**Bare imports** resolve to standard library types (1 line per import):
+
 ```ato
-assert x > 5V
-assert 5V < x < 10V
-assert current within 1A +/- 10mA
-assert resistance is 1kohm to 1.1kohm
+import ElectricPower
+import I2C
+import Resistor
 ```
 
-### Loops (syntactic sugar)
+**Path imports** resolve to types defined in other `.ato` files (1 line per import):
+
+```ato
+from "atopile/vendor-part/vendor-part.ato" import Vendor_Part
+```
+
+### 8. Pragma Feature Flags
+
+Experimental syntax is gated behind pragmas (file top, before imports):
+
 ```ato
-for item in container:
-    item ~ p1
+#pragma experiment("BRIDGE_CONNECT")     # ~> operator
+#pragma experiment("FOR_LOOP")           # for loops
+#pragma experiment("TRAITS")             # trait keyword
+#pragma experiment("MODULE_TEMPLATING")  # new Foo<p=v>
+#pragma experiment("INSTANCE_TRAITS")    # traits on instances
 ```
 
-## What Is *Not* In ATO
+Using gated syntax without the pragma is a compile error.
+
+## Statement Reference
+
+Every statement inside a block body is one of:
+
+| Statement | Syntax                              | Purpose                                |
+| --------- | ----------------------------------- | -------------------------------------- |
+| `assign`  | `name = value` or `name = new Type` | Bind a value or instantiate a child    |
+| `connect` | `a ~ b`                             | Wire two interfaces together           |
+| `bridge`  | `a ~> b ~> c`                       | Insert bridgeable components in series |
+| `assert`  | `assert expr <op> expr`             | Declare a constraint                   |
+| `retype`  | `name -> NewType`                   | Replace an inherited child's type      |
+| `pin`     | `pin VCC`                           | Declare a physical pin                 |
+| `signal`  | `signal reset`                      | Declare an electrical signal           |
+| `trait`   | `trait TraitName`                   | Attach a trait                         |
+| `import`  | `import Type`                       | Import a type                          |
+| `for`     | `for x in arr:`                     | Iterate over an array (pragma-gated)   |
+| `string`  | `"""..."""`                         | Documentation string                   |
+| `pass`    | `pass`                              | Empty placeholder                      |
+
+Statements within a block are **order-independent** — the compiler resolves the full graph, not a sequence of operations.
+
+## Type System
+
+### Interfaces (connectable with `~` or `~>`)
+
+| Type                                                          | Children / Parameters                                    | Purpose                              |
+| ------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------ |
+| `Electrical`                                                  | _(single node)_                                          | Raw electrical connection point      |
+| `ElectricPower`                                               | `.hv`, `.lv` (Electrical); `.voltage`, `.max_current`    | Power rails                          |
+| `ElectricLogic`                                               | `.line` (Electrical), `.reference` (ElectricPower)       | Digital signals with voltage context |
+| `ElectricSignal`                                              | `.line` (Electrical), `.reference` (ElectricPower)       | Analog signals                       |
+| `I2C`                                                         | `.scl`, `.sda` (ElectricLogic); `.frequency`, `.address` | I2C bus                              |
+| `SPI`                                                         | `.sclk`, `.mosi`, `.miso` (ElectricLogic); `.frequency`  | SPI bus                              |
+| `UART` / `UART_Base`                                          | `.tx`, `.rx` (ElectricLogic); flow control lines         | Serial                               |
+| `I2S`                                                         | audio data bus lines                                     | Digital audio                        |
+| `DifferentialPair`                                            | `.p`, `.n`                                               | Differential signals                 |
+| `USB2_0` / `USB3` / `USB2_0_IF`                               | USB data + power                                         | USB interfaces                       |
+| `CAN_TTL`                                                     | CAN bus lines                                            | CAN bus                              |
+| `SWD` / `JTAG`                                                | debug lines                                              | Debug interfaces                     |
+| `Ethernet` / `HDMI` / `RS232` / `PDM` / `XtalIF` / `MultiSPI` | protocol-specific                                        | Other protocols                      |
+
+### Modules (instantiable with `new`)
+
+| Type                                | Children / Parameters                                                                  | Designator |
+| ----------------------------------- | -------------------------------------------------------------------------------------- | ---------- |
+| `Resistor`                          | `.unnamed[0..1]`; `.resistance`, `.max_power`                                          | R          |
+| `Capacitor`                         | `.unnamed[0..1]`, `.power`; `.capacitance`, `.max_voltage`, `.temperature_coefficient` | C          |
+| `CapacitorPolarized`                | polarized variant of Capacitor                                                         | C          |
+| `Inductor`                          | `.unnamed[0..1]`; `.inductance`                                                        | L          |
+| `Fuse`                              | `.unnamed[0..1]`; `.trip_current`, `.fuse_type`                                        | F          |
+| `Diode`                             | `.anode`, `.cathode`; `.forward_voltage`, `.current`                                   | D          |
+| `LED`                               | `.diode`; `.brightness`, `.color`                                                      | D          |
+| `MOSFET`                            | `.source`, `.gate`, `.drain`; `.channel_type`, `.gate_source_threshold_voltage`        | Q          |
+| `BJT`                               | `.emitter`, `.base`, `.collector`; `.doping_type`                                      | Q          |
+| `Regulator` / `AdjustableRegulator` | `.power_in`, `.power_out`                                                              | —          |
+| `Crystal`                           | `.unnamed[0..1]`, `.gnd`; `.frequency`, `.load_capacitance`                            | XTAL       |
+| `Crystal_Oscillator`                | oscillator module                                                                      | —          |
+| `ResistorVoltageDivider`            | voltage divider circuit                                                                | —          |
+| `FilterElectricalRC`                | RC filter                                                                              | —          |
+| `Net`                               | `.part_of` (Electrical)                                                                | —          |
+| `TestPoint`                         | `.contact`; `.pad_size`, `.pad_type`                                                   | TP         |
+| `MountingHole` / `NetTie`           | mechanical                                                                             | —          |
+| `SPIFlash`                          | SPI flash memory                                                                       | —          |
+
+### Traits (attachable with `trait`)
+
+`has_part_removed`, `is_atomic_part`, `can_bridge`, `can_bridge_by_name`, `has_datasheet`, `has_designator_prefix`, `has_doc_string`, `has_net_name_affix`, `has_net_name_suggestion`, `has_package_requirements`, `has_single_electric_reference`, `is_auto_generated`, `requires_external_usage`
+
+## Units and Literals
 
-Do not write (or assume) any of these exist:
-- `if` statements
-- `while` loops
-- user-defined functions (calls or defs)
-- user-defined classes/objects
-- exceptions/generators
+**SI-prefixed units**: `V`, `mV` | `A`, `mA` | `ohm`, `kohm`, `Mohm` | `F`, `uF`, `nF`, `pF` | `Hz`, `kHz`, `MHz`, `GHz` | `s`, `ms` | `W`, `mW`
 
-## Relevant Files
+**Number formats**: decimal (`3.3`), scientific (`1e-6`), hex (`0x48`), binary (`0b1010`), underscore-separated (`1_000_000`)
 
-- Compiler/visitor (experiments + syntax gating): `src/atopile/compiler/ast_visitor.py`
-- Lexer/parser (grammar): `src/atopile/compiler/parser/` (ANTLR artifacts)
-- LSP implementation (pragma parsing, editor features): `src/atopile/lsp/lsp_server.py`
-- Codegen that emits experiment pragmas: `src/faebryk/libs/codegen/atocodegen.py`
-- VSCode extension rule templates (editor-facing guidance): `src/vscode-atopile/resources/templates/rules/`
+**Booleans**: `True`, `False`
 
-## Common Pitfalls (LLM Checklist)
+## Invariants
 
-- Don’t “invent” runtime semantics: ATO is declarative; ordering is not an execution model.
-- Prefer constraints with tolerances when they drive selection (exact values can make picking impossible).
-- If you introduce gated syntax, add the matching `#pragma experiment("...")` near the top of the file.
-- When editing `.ato`, verify the change through the compiler surface (`ato build` / targeted tests), not by eyeballing.
+1. **Type-safe connections**: `~` and `~>` should connect matching interface types. `ElectricPower ~ I2C` is a type mismatch (enforcement is being strengthened).
+2. **Pragma gates syntax**: using `~>`, `for`, `trait`, or `<>` without the matching pragma is a compile error.
+3. **Tolerances on passives**: `resistance = 10kohm` (zero tolerance) matches no real parts. Always use `+/- N%`.
+4. **ElectricLogic needs a reference**: logic signals require a power reference for voltage context. Set `signal.reference ~ power_rail`.
+5. **Order independence**: statements within a block are not sequentially executed. The solver resolves the full graph.
+6. **No procedural logic**: no `if`, `while`, `return`, functions, classes, or exceptions.
PATCH

echo "Gold patch applied."
