#!/bin/bash
set -e

cd /workspace/selenium

# Check if already applied (idempotency check)
# The key change is removing the old JsonConverter from SourceActions base class
if ! grep -q "JsonConverter(typeof(InputSourceActionsConverter))" dotnet/src/webdriver/BiDi/Input/SourceActions.cs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch from the embedded patch file
cat <<'PATCH_EOF' | git apply -
diff --git a/dotnet/src/webdriver/BiDi/Input/InputModule.cs b/dotnet/src/webdriver/BiDi/Input/InputModule.cs
index f6c72fd81952a..3e94189a1e191 100644
--- a/dotnet/src/webdriver/BiDi/Input/InputModule.cs
+++ b/dotnet/src/webdriver/BiDi/Input/InputModule.cs
@@ -75,9 +75,5 @@ protected override void Initialize(IBiDi bidi, JsonSerializerOptions jsonSeriali
 [JsonSerializable(typeof(SetFilesCommand))]
 [JsonSerializable(typeof(SetFilesResult))]
 [JsonSerializable(typeof(FileDialogEventArgs))]
-[JsonSerializable(typeof(IEnumerable<IPointerSourceAction>))]
-[JsonSerializable(typeof(IEnumerable<IKeySourceAction>))]
-[JsonSerializable(typeof(IEnumerable<INoneSourceAction>))]
-[JsonSerializable(typeof(IEnumerable<IWheelSourceAction>))]

 internal partial class InputJsonSerializerContext : JsonSerializerContext;
diff --git a/dotnet/src/webdriver/BiDi/Input/SequentialSourceActions.cs b/dotnet/src/webdriver/BiDi/Input/SequentialSourceActions.cs
deleted file mode 100644
index 3fd207145bd6e..0000000000000
--- a/dotnet/src/webdriver/BiDi/Input/SequentialSourceActions.cs
+++ /dev/null
@@ -1,176 +0,0 @@
-// <copyright file="SequentialSourceActions.cs" company="Selenium Committers">
-// Licensed to the Software Freedom Conservancy (SFC) under one
-// or more contributor license agreements.  See the NOTICE file
-// distributed with this work for additional information
-// regarding copyright ownership.  The SFC licenses this file
-// to you under the Apache License, Version 2.0 (the
-// "License"); you may not use this file except in compliance
-// with the License.  You may obtain a copy of the License at
-//
-//   http://www.apache.org/licenses/LICENSE-2.0
-//
-// Unless required by applicable law or agreed to in writing,
-// software distributed under the License is distributed on an
-// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
-// KIND, either express or implied.  See the License for the
-// specific language governing permissions and limitations
-// under the License.
-// </copyright>
-
-//namespace OpenQA.Selenium.BiDi.Input;
-
-//public interface ISequentialSourceActions : IEnumerable<SourceActions>
-//{
-//    ISequentialSourceActions Pause(int duration);
-
-//    ISequentialSourceActions Type(string text);
-//    ISequentialSourceActions KeyDown(char key);
-//    ISequentialSourceActions KeyUp(char key);
-
-//    ISequentialSourceActions PointerDown(int button, PointerDownOptions? options = null);
-//    ISequentialSourceActions PointerUp(int button);
-//    ISequentialSourceActions PointerMove(int x, int y, PointerMoveOptions? options = null);
-//}
-
-//public record SequentialSourceActions : ISequentialSourceActions
-//{
-//    private readonly KeyActions _keyActions = [];
-//    private readonly PointerActions _pointerActions = [];
-//    private readonly WheelActions _wheelActions = [];
-//    private readonly WheelActions _noneActions = [];
-
-//    public ISequentialSourceActions Pause(int duration)
-//    {
-//        _noneActions.Add(new Pause { Duration = duration });
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions Type(string text)
-//    {
-//        _keyActions.Type(text);
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions KeyDown(char key)
-//    {
-//        _keyActions.Add(new Key.Down(key));
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions KeyUp(char key)
-//    {
-//        _keyActions.Add(new Key.Up(key));
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions PointerDown(int button, PointerDownOptions? options = null)
-//    {
-//        _pointerActions.Add(new Pointer.Down(button)
-//        {
-//            Width = options?.Width,
-//            Height = options?.Height,
-//            Pressure = options?.Pressure,
-//            TangentialPressure = options?.TangentialPressure,
-//            Twist = options?.Twist,
-//            AltitudeAngle = options?.AltitudeAngle,
-//            AzimuthAngle = options?.AzimuthAngle
-//        });
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions PointerUp(int button)
-//    {
-//        _pointerActions.Add(new Pointer.Up(button));
-
-//        return Normalized();
-//    }
-
-//    public ISequentialSourceActions PointerMove(int x, int y, PointerMoveOptions? options = null)
-//    {
-//        _pointerActions.Add(new Pointer.Move(x, y)
-//        {
-//            Duration = options?.Duration,
-//            Origin = options?.Origin,
-//            Width = options?.Width,
-//            Height = options?.Height,
-//            Pressure = options?.Pressure,
-//            TangentialPressure = options?.TangentialPressure,
-//            Twist = options?.Twist,
-//            AltitudeAngle = options?.AltitudeAngle,
-//            AzimuthAngle = options?.AzimuthAngle
-//        });
-
-//        return Normalized();
-//    }
-
-//    private SequentialSourceActions Normalized()
-//    {
-//        var max = new[] { _keyActions.Count(), _pointerActions.Count(), _wheelActions.Count(), _noneActions.Count() }.Max();
-
-//        for (int i = _keyActions.Count(); i < max; i++)
-//        {
-//            _keyActions.Add(new Pause());
-//        }
-
-//        for (int i = _pointerActions.Count(); i < max; i++)
-//        {
-//            _pointerActions.Add(new Pause());
-//        }
-
-//        for (int i = _wheelActions.Count(); i < max; i++)
-//        {
-//            _wheelActions.Add(new Pause());
-//        }
-
-//        for (int i = _noneActions.Count(); i < max; i++)
-//        {
-//            _noneActions.Add(new Pause());
-//        }
-
-//        return this;
-//    }
-
-//    public IEnumerator<SourceActions> GetEnumerator()
-//    {
-//        var sourceActions = new List<SourceActions>
-//        {
-//            _keyActions,
-//            _pointerActions,
-//            _wheelActions,
-//            _noneActions
-//        };
-//        return sourceActions.GetEnumerator();
-//    }
-
-//    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
-//}
-
-//public record PointerDownOptions : IPointerCommonProperties
-//{
-//    public int? Width { get; set; }
-//    public int? Height { get; set; }
-//    public double? Pressure { get; set; }
-//    public double? TangentialPressure { get; set; }
-//    public int? Twist { get; set; }
-//    public double? AltitudeAngle { get; set; }
-//    public double? AzimuthAngle { get; set; }
-//}
-
-//public record PointerMoveOptions : IPointerCommonProperties
-//{
-//    public int? Duration { get; set; }
-//    public Origin? Origin { get; set; }
-
-//    public int? Width { get; set; }
-//    public int? Height { get; set; }
-//    public double? Pressure { get; set; }
-//    public double? TangentialPressure { get; set; }
-//    public int? Twist { get; set; }
-//    public double? AltitudeAngle { get; set; }
-//    public double? AzimuthAngle { get; set; }
-//}
diff --git a/dotnet/src/webdriver/BiDi/Input/SourceActions.cs b/dotnet/src/webdriver/BiDi/Input/SourceActions.cs
index ae278158a184d..6735dda37285e 100644
--- a/dotnet/src/webdriver/BiDi/Input/SourceActions.cs
+++ b/dotnet/src/webdriver/BiDi/Input/SourceActions.cs
@@ -17,28 +17,22 @@
 // under the License.
 // </copyright>

-using System.Collections;
 using System.Text.Json.Serialization;
 using OpenQA.Selenium.BiDi.Json.Converters;
-using OpenQA.Selenium.BiDi.Json.Converters.Enumerable;

 namespace OpenQA.Selenium.BiDi.Input;

-[JsonConverter(typeof(InputSourceActionsConverter))]
-public abstract record SourceActions(string Id);
-
-public interface ISourceAction;
-
-public abstract record SourceActions<T>(string Id) : SourceActions(Id), IEnumerable<ISourceAction> where T : ISourceAction
-{
-    public IList<ISourceAction> Actions { get; init; } = [];
-
-    public IEnumerator<ISourceAction> GetEnumerator() => Actions.GetEnumerator();
+[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
+[JsonDerivedType(typeof(KeySourceActions), "key")]
+[JsonDerivedType(typeof(PointerSourceActions), "pointer")]
+[JsonDerivedType(typeof(WheelSourceActions), "wheel")]
+[JsonDerivedType(typeof(NoneSourceActions), "none")]
+public abstract record SourceActions;

-    IEnumerator IEnumerable.GetEnumerator() => Actions.GetEnumerator();
+public abstract record SourceActions<TSourceAction>(string Id, IEnumerable<TSourceAction> Actions)
+    : SourceActions where TSourceAction : ISourceAction;

-    public void Add(ISourceAction action) => Actions.Add(action);
-}
+public interface ISourceAction;

 [JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
 [JsonDerivedType(typeof(PauseAction), "pause")]
@@ -46,18 +40,14 @@ public abstract record SourceActions<T>(string Id) : SourceActions(Id), IEnumera
 [JsonDerivedType(typeof(KeyUpAction), "keyUp")]
 public interface IKeySourceAction : ISourceAction;

-public sealed record KeyActions(string Id) : SourceActions<IKeySourceAction>(Id)
+public sealed record KeySourceActions(string Id, IEnumerable<IKeySourceAction> Actions)
+    : SourceActions<IKeySourceAction>(Id, Actions)
 {
-    public KeyActions Type(string text)
+    // TODO move out as extension method
+    public KeySourceActions Type(string text) => this with
     {
-        foreach (var character in text)
-        {
-            Add(new KeyDownAction(character));
-            Add(new KeyUpAction(character));
-        }
-
-        return this;
-    }
+        Actions = [.. Actions, .. text.SelectMany<char, IKeySourceAction>(c => [new KeyDownAction(c), new KeyUpAction(c)])]
+    };
 }

 [JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
@@ -67,9 +57,10 @@ public KeyActions Type(string text)
 [JsonDerivedType(typeof(PointerMoveAction), "pointerMove")]
 public interface IPointerSourceAction : ISourceAction;

-public sealed record PointerActions(string Id) : SourceActions<IPointerSourceAction>(Id)
+public sealed record PointerSourceActions(string Id, IEnumerable<IPointerSourceAction> Actions)
+    : SourceActions<IPointerSourceAction>(Id, Actions)
 {
-    public PointerParameters? Options { get; init; }
+    public PointerParameters? Parameters { get; init; }
 }

 [JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
@@ -77,61 +68,55 @@ public sealed record PointerActions(string Id) : SourceActions<IPointerSourceAct
 [JsonDerivedType(typeof(WheelScrollAction), "scroll")]
 public interface IWheelSourceAction : ISourceAction;

-public sealed record WheelActions(string Id) : SourceActions<IWheelSourceAction>(Id);
+public sealed record WheelSourceActions(string Id, IEnumerable<IWheelSourceAction> Actions)
+    : SourceActions<IWheelSourceAction>(Id, Actions);

 [JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
 [JsonDerivedType(typeof(PauseAction), "pause")]
 public interface INoneSourceAction : ISourceAction;

-public sealed record NoneActions(string Id) : SourceActions<INoneSourceAction>(Id);
-
-public abstract record KeySourceAction : IKeySourceAction;
+public sealed record NoneSourceActions(string Id, IEnumerable<INoneSourceAction> Actions)
+    : SourceActions<INoneSourceAction>(Id, Actions);

-public sealed record KeyDownAction(char Value) : KeySourceAction;
+public sealed record KeyDownAction(char Value) : IKeySourceAction;

-public sealed record KeyUpAction(char Value) : KeySourceAction;
+public sealed record KeyUpAction(char Value) : IKeySourceAction;

-public abstract record PointerSourceAction : IPointerSourceAction;
-
-public sealed record PointerDownAction(int Button) : PointerSourceAction, IPointerCommonProperties
+public sealed record PointerDownAction(long Button) : IPointerSourceAction, IPointerCommonProperties
 {
-    public int? Width { get; init; }
-    public int? Height { get; init; }
+    public long? Width { get; init; }
+    public long? Height { get; init; }
     public double? Pressure { get; init; }
     public double? TangentialPressure { get; init; }
-    public int? Twist { get; init; }
+    public long? Twist { get; init; }
     public double? AltitudeAngle { get; init; }
     public double? AzimuthAngle { get; init; }
 }

-public sealed record PointerUpAction(int Button) : PointerSourceAction;
+public sealed record PointerUpAction(long Button) : IPointerSourceAction;

-public sealed record PointerMoveAction(double X, double Y) : PointerSourceAction, IPointerCommonProperties
+public sealed record PointerMoveAction(double X, double Y) : IPointerSourceAction, IPointerCommonProperties
 {
-    public int? Duration { get; init; }
+    public long? Duration { get; init; }

     public Origin? Origin { get; init; }

-    public int? Width { get; init; }
-    public int? Height { get; init; }
+    public long? Width { get; init; }
+    public long? Height { get; init; }
     public double? Pressure { get; init; }
     public double? TangentialPressure { get; init; }
-    public int? Twist { get; init; }
+    public long? Twist { get; init; }
     public double? AltitudeAngle { get; init; }
     public double? AzimuthAngle { get; init; }
 }

-public abstract record WheelSourceAction : IWheelSourceAction;
-
-public sealed record WheelScrollAction(int X, int Y, int DeltaX, int DeltaY) : WheelSourceAction
+public sealed record WheelScrollAction(long X, long Y, long DeltaX, long DeltaY) : IWheelSourceAction
 {
-    public int? Duration { get; init; }
+    public long? Duration { get; init; }

     public Origin? Origin { get; init; }
 }

-public abstract record NoneSourceAction : INoneSourceAction;
-
 public sealed record PauseAction : ISourceAction, IKeySourceAction, IPointerSourceAction, IWheelSourceAction, INoneSourceAction
 {
     public long? Duration { get; init; }
@@ -152,15 +137,15 @@ public enum PointerType

 public interface IPointerCommonProperties
 {
-    public int? Width { get; init; }
+    public long? Width { get; init; }

-    public int? Height { get; init; }
+    public long? Height { get; init; }

     public double? Pressure { get; init; }

     public double? TangentialPressure { get; init; }

-    public int? Twist { get; init; }
+    public long? Twist { get; init; }

     public double? AltitudeAngle { get; init; }

     public double? AzimuthAngle { get; init; }
 }
diff --git a/dotnet/src/webdriver/BiDi/Json/Converters/Enumerable/InputSourceActionsConverter.cs b/dotnet/src/webdriver/BiDi/Json/Converters/Enumerable/InputSourceActionsConverter.cs
deleted file mode 100644
index af1b6e54621f0..0000000000000
--- a/dotnet/src/webdriver/BiDi/Json/Converters/Enumerable/InputSourceActionsConverter.cs
+++ /dev/null
@@ -1,76 +0,0 @@
-// <copyright file="InputSourceActionsConverter.cs" company="Selenium Committers">
-// Licensed to the Software Freedom Conservancy (SFC) under one
-// or more contributor license agreements.  See the NOTICE file
-// distributed with this work for additional information
-// regarding copyright ownership.  The SFC licenses this file
-// to you under the Apache License, Version 2.0 (the
-// "License"); you may not use this file except in compliance
-// with the License.  You may obtain a copy of the License at
-//
-//   http://www.apache.org/licenses/LICENSE-2.0
-//
-// Unless required by applicable law or agreed to in writing,
-// software distributed under the License is distributed on an
-// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
-// KIND, either express or implied.  See the License for the
-// specific language governing permissions and limitations
-// under the License.
-// </copyright>
-
-using System.Text.Json;
-using System.Text.Json.Serialization;
-using OpenQA.Selenium.BiDi.Input;
-
-namespace OpenQA.Selenium.BiDi.Json.Converters.Enumerable;
-
-internal class InputSourceActionsConverter : JsonConverter<SourceActions>
-{
-    public override SourceActions Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
-    {
-        throw new NotImplementedException();
-    }
-
-    public override void Write(Utf8JsonWriter writer, SourceActions value, JsonSerializerOptions options)
-    {
-        writer.WriteStartObject();
-
-        writer.WriteString("id", value.Id);
-
-        switch (value)
-        {
-            case KeyActions keys:
-                writer.WriteString("type", "key");
-                writer.WritePropertyName("actions");
-                JsonSerializer.Serialize(writer, keys.Actions.Select(a => a as IKeySourceAction), options.GetTypeInfo<IEnumerable<IKeySourceAction?>>());
-
-                break;
-            case PointerActions pointers:
-                writer.WriteString("type", "pointer");
-                if (pointers.Options is not null)
-                {
-                    writer.WritePropertyName("parameters");
-                    JsonSerializer.Serialize(writer, pointers.Options, options.GetTypeInfo(typeof(PointerParameters)));
-                }
-
-                writer.WritePropertyName("actions");
-                JsonSerializer.Serialize(writer, pointers.Actions.Select(a => a as IPointerSourceAction), options.GetTypeInfo<IEnumerable<IPointerSourceAction?>>());
-
-                break;
-            case WheelActions wheels:
-                writer.WriteString("type", "wheel");
-                writer.WritePropertyName("actions");
-                JsonSerializer.Serialize(writer, wheels.Actions.Select(a => a as IWheelSourceAction), options.GetTypeInfo<IEnumerable<IWheelSourceAction?>>());
-
-                break;
-            case NoneActions none:
-                writer.WriteString("type", "none");
-                writer.WritePropertyName("actions");
-                JsonSerializer.Serialize(writer, none.Actions.Select(a => a as INoneSourceAction), options.GetTypeInfo<IEnumerable<INoneSourceAction?>>());
-
-                break;
-        }
-
-        writer.WriteEndObject();
-    }
-}
-
diff --git a/dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs b/dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs
index 432bdbbfba7e9..d922ecb150214 100644
--- a/dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs
+++ b/dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs
@@ -32,25 +32,25 @@ public async Task Paint()

         await Task.Delay(3000);

-        await context.Input.PerformActionsAsync([new PointerActions("id0") {
+        await context.Input.PerformActionsAsync([new PointerSourceActions("id0", [
             new PointerMoveAction(300, 300),
             new PointerDownAction(0),
             new PointerMoveAction(400, 400) { Duration = 2000, Width = 1, Twist = 1 },
             new PointerUpAction(0),
-        }]);
+        ])]);

-        await context.Input.PerformActionsAsync([new KeyActions("id1") {
+        await context.Input.PerformActionsAsync([new KeySourceActions("id1", [
             new KeyDownAction('U'),
             new KeyUpAction('U'),
             new PauseAction { Duration = 3000 }
-        }]);
+        ])]);

-        await context.Input.PerformActionsAsync([new PointerActions("id2") {
+        await context.Input.PerformActionsAsync([new PointerSourceActions("id2", [
             new PointerMoveAction(300, 300),
             new PointerDownAction(0),
             new PointerMoveAction(400, 400) { Duration = 2000 },
             new PointerUpAction(0),
-        }]);
+        ])]);

         await Task.Delay(3000);
     }
@@ -60,14 +60,40 @@ public async Task TestShiftClickingOnMultiSelectionList()
     {
         driver.Url = UrlBuilder.WhereIs("formSelectionPage.html");

-        var options = await context.LocateNodesAsync(new CssLocator("option"));
+        var options = (await context.LocateNodesAsync(new CssLocator("option"))).Nodes;

         await context.Input.PerformActionsAsync([
-            new PointerActions("id0")
-            {
-                new PointerDownAction(1),
-                new PointerUpAction(1),
-            }
-            ]);
+            new PointerSourceActions("pointer", [
+                new PointerMoveAction(0, 0) { Origin = new ElementOrigin(options[1]) },
+                new PointerDownAction(0),
+                new PointerUpAction(0),
+                new PauseAction(),  // align with shift key down
+                new PointerMoveAction(0, 0) { Origin = new ElementOrigin(options[3]) },
+                new PointerDownAction(0),
+                new PointerUpAction(0),
+            ]),
+            new KeySourceActions("key", [
+                new PauseAction(),  // align with first click (no modifier)
+                new PauseAction(),
+                new PauseAction(),
+                new KeyDownAction('\uE008'),  // Shift down
+                new PauseAction(),
+                new PauseAction(),
+                new KeyUpAction('\uE008'),  // Shift up
+            ]),
+        ]);
+
+        var showButton = (await context.LocateNodesAsync(new CssLocator("[name='showselected']"))).Nodes[0];
+        await context.Input.PerformActionsAsync([
+            new PointerSourceActions("pointer", [
+                new PointerMoveAction(0, 0) { Origin = new ElementOrigin(showButton) },
+                new PointerDownAction(0),
+                new PointerUpAction(0),
+            ]),
+        ]);
+
+        var resultText = driver.FindElement(By.Id("result")).Text;
+
+        Assert.That(resultText, Is.EqualTo("roquefort parmigiano cheddar"));
     }
 }
PATCH_EOF

echo "Gold patch applied successfully"
