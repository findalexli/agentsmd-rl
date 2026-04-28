#!/usr/bin/env bash
set -euo pipefail

cd /workspace/magda-core

# Idempotency guard
if grep -qF "description: Audio thread safety and lock-free programming patterns for JUCE/Tra" ".claude/skills/audio-thread/SKILL.md" && grep -qF "description: JUCE threading model and component lifecycle safety. Use when writi" ".claude/skills/juce-threading/SKILL.md" && grep -qF "Listeners fire on the thread that made the change. If a property is set from the" ".claude/skills/valuetree/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/audio-thread/SKILL.md b/.claude/skills/audio-thread/SKILL.md
@@ -0,0 +1,322 @@
+---
+name: audio-thread
+description: Audio thread safety and lock-free programming patterns for JUCE/Tracktion Engine. Use when writing Plugin::applyToBuffer(), real-time audio callbacks, metering, or any code that touches the audio thread. Covers what is forbidden, lock-free communication, and codebase-specific patterns.
+---
+
+# Audio Thread Safety & Lock-Free Patterns
+
+The audio thread in JUCE/Tracktion Engine runs under strict real-time constraints. Any blocking or unbounded operation causes audible glitches (clicks, dropouts, silence). This skill covers what is forbidden, how to communicate safely between threads, and the patterns used in this codebase.
+
+## What Is Forbidden on the Audio Thread
+
+All of the following can block, allocate, or take unbounded time. Never do any of these inside `Plugin::applyToBuffer()`, `AudioProcessor::processBlock()`, or any code called from the audio callback.
+
+### 1. Memory Allocation
+
+```cpp
+// FORBIDDEN - all of these may call malloc/new
+auto* p = new MyObject();                  // heap allocation
+std::vector<float> temp(numSamples);       // heap allocation on resize
+juce::String s = "level: " + juce::String(value);  // heap allocation
+juce::Array<int> arr;
+arr.add(42);                               // may reallocate
+myStdVector.push_back(x);                  // may reallocate
+```
+
+**Instead:** Pre-allocate in `initialise()` or use stack-allocated fixed-size buffers.
+
+```cpp
+// OK - stack allocation with known size
+float temp[2048];
+
+// OK - pre-allocated in initialise(), reused in applyToBuffer()
+std::vector<float> scratchBuffer;  // member variable, resized in initialise()
+```
+
+### 2. Locks and Mutexes
+
+```cpp
+// FORBIDDEN - may block waiting for another thread
+juce::ScopedLock sl(criticalSection);
+std::lock_guard<std::mutex> lock(mutex);
+std::unique_lock<std::mutex> ul(mutex);
+```
+
+**Instead:** Use atomics, lock-free queues, or `juce::AbstractFifo`.
+
+### 3. MessageManager Calls
+
+```cpp
+// FORBIDDEN - posts to message thread, may allocate, may block
+juce::MessageManager::callAsync([this] { /* ... */ });
+sendChangeMessage();
+triggerAsyncUpdate();  // OK only from non-audio thread
+```
+
+### 4. File I/O
+
+```cpp
+// FORBIDDEN - unbounded latency
+juce::File("x.wav").loadFileAsData();
+fopen(), fread(), fwrite();
+DBG("value: " + juce::String(x));  // writes to stderr
+```
+
+### 5. Objective-C Message Sends (macOS)
+
+```cpp
+// FORBIDDEN - ObjC runtime may take locks
+// Any call that crosses into ObjC (NSLog, CoreFoundation bridged calls, etc.)
+```
+
+### 6. Unbounded Operations
+
+```cpp
+// FORBIDDEN - unknown iteration count
+while (!ready.load()) { /* spin */ }  // unbounded spin
+for (auto& item : dynamicContainer) { /* ... */ }  // if container can grow
+```
+
+## Lock-Free Communication Patterns
+
+### Pattern 1: std::atomic for Simple Values
+
+Use for single values shared between audio and UI threads. `memory_order_relaxed` is sufficient when there is no ordering dependency between multiple variables.
+
+```cpp
+class MyPlugin : public te::Plugin {
+    std::atomic<float> gainLevel{1.0f};
+
+    // Message thread (UI/parameter change):
+    void setGain(float g) {
+        gainLevel.store(g, std::memory_order_relaxed);
+    }
+
+    // Audio thread:
+    void applyToBuffer(const PluginRenderContext& rc) override {
+        float g = gainLevel.load(std::memory_order_relaxed);
+        rc.destBuffer->applyGain(0, rc.bufferNumSamples, g);
+    }
+};
+```
+
+### Pattern 2: Atomic Exchange for Peak Metering
+
+The audio thread writes a running maximum. The UI thread reads and resets in one atomic operation, ensuring no peaks are lost and no lock is needed.
+
+```cpp
+class MyPlugin : public te::Plugin {
+    std::atomic<float> peakLeft{0.0f};
+    std::atomic<float> peakRight{0.0f};
+
+    // Audio thread: update running peak
+    void applyToBuffer(const PluginRenderContext& rc) override {
+        auto& buf = *rc.destBuffer;
+        float newPeakL = buf.getMagnitude(0, rc.bufferStartSample, rc.bufferNumSamples);
+        float newPeakR = buf.getMagnitude(1, rc.bufferStartSample, rc.bufferNumSamples);
+
+        // Only store if new peak is greater than current
+        auto prevL = peakLeft.load(std::memory_order_relaxed);
+        if (newPeakL > prevL)
+            peakLeft.store(newPeakL, std::memory_order_relaxed);
+
+        auto prevR = peakRight.load(std::memory_order_relaxed);
+        if (newPeakR > prevR)
+            peakRight.store(newPeakR, std::memory_order_relaxed);
+    }
+
+    // UI thread (timer callback): read and reset
+    float consumePeakLeft() {
+        return peakLeft.exchange(0.0f, std::memory_order_relaxed);
+    }
+    float consumePeakRight() {
+        return peakRight.exchange(0.0f, std::memory_order_relaxed);
+    }
+};
+```
+
+### Pattern 3: juce::CachedValue for ValueTree-Backed Properties
+
+`CachedValue<T>` caches a ValueTree property in a local variable that is safe to read on the audio thread (the cached copy is updated on the message thread via listener, but the read is just a plain member access).
+
+```cpp
+class MyPlugin : public te::Plugin {
+    juce::CachedValue<float> levelParam;
+    juce::CachedValue<float> panParam;
+
+    void initialise(const PluginInitialisationInfo&) override {
+        // Bind to ValueTree properties (message thread)
+        levelParam.referTo(state, IDs::level, nullptr, 0.8f);
+        panParam.referTo(state, IDs::pan, nullptr, 0.0f);
+    }
+
+    void applyToBuffer(const PluginRenderContext& rc) override {
+        // Safe to read cached value on audio thread
+        float level = levelParam.get();
+        float pan = panParam.get();
+        // ... apply to buffer ...
+    }
+};
+```
+
+### Pattern 4: std::atomic<bool> for Flags and Triggers
+
+Use for one-shot triggers (e.g., pad hit, reset signal) or boolean state flags.
+
+```cpp
+class DrumPad {
+    std::atomic<bool> triggered{false};
+
+    // UI/MIDI thread: fire trigger
+    void hit() {
+        triggered.store(true, std::memory_order_relaxed);
+    }
+
+    // Audio thread: consume trigger
+    void processBlock(juce::AudioBuffer<float>& buffer) {
+        if (triggered.exchange(false, std::memory_order_relaxed)) {
+            // Start sample playback from beginning
+            playbackPosition = 0;
+        }
+        // ... render audio ...
+    }
+};
+```
+
+### Pattern 5: juce::AbstractFifo / Lock-Free Queues
+
+Use when you need to pass variable-sized data or multiple messages between threads.
+
+```cpp
+class MeterBridge {
+    juce::AbstractFifo fifo{512};
+    std::array<float, 512> buffer{};
+
+    // Audio thread: write meter values
+    void pushMeterValue(float value) {
+        const auto scope = fifo.write(1);
+        if (scope.blockSize1 > 0)
+            buffer[(size_t)scope.startIndex1] = value;
+    }
+
+    // UI thread: read meter values
+    float popMeterValue() {
+        float result = 0.0f;
+        const auto scope = fifo.read(1);
+        if (scope.blockSize1 > 0)
+            result = buffer[(size_t)scope.startIndex1];
+        return result;
+    }
+};
+```
+
+## Tracktion Engine Specifics
+
+### Plugin Lifecycle & Threading
+
+```
+Message Thread                    Audio Thread
+──────────────                    ────────────
+Plugin::initialise()              Plugin::applyToBuffer()
+Plugin::deinitialise()              (called every audio block)
+Plugin::restorePluginStateFromValueTree()
+ValueTree listeners fire
+```
+
+- `Plugin::applyToBuffer(const PluginRenderContext& rc)` runs on the **audio thread**.
+- `Plugin::initialise()` and `Plugin::deinitialise()` run on the **message thread**.
+- Never access `Edit&`, `ValueTree`, or `UndoManager` from `applyToBuffer()`. Use `CachedValue` instead.
+
+### PluginRenderContext Quick Reference
+
+```cpp
+void applyToBuffer(const PluginRenderContext& rc) override {
+    auto& audio = *rc.destBuffer;          // juce::AudioBuffer<float>&
+    auto& midi  = *rc.bufferForMidiMessages; // MidiMessageArray&
+    int startSample = rc.bufferStartSample;
+    int numSamples  = rc.bufferNumSamples;
+    double sampleRate = sampleRateValue;   // from initialise()
+}
+```
+
+### Rack Wrapping
+
+When a plugin is rack-wrapped (inserted into a RackType), Tracktion Engine manages the audio routing. The plugin's `applyToBuffer()` is still called on the audio thread, but the buffer routing is handled by the rack. Initialise/deinitialise lifecycle is managed by the rack's node graph.
+
+## Common Patterns in This Codebase
+
+### Per-Chain Peak Metering
+
+```cpp
+// In a multi-chain plugin (e.g., drum grid with multiple output chains):
+struct Chain {
+    std::atomic<float> peak{0.0f};
+    // ... other chain state ...
+};
+
+std::array<Chain, 16> chains;
+
+// Audio thread: update peak for each chain
+void applyToBuffer(const PluginRenderContext& rc) override {
+    for (int i = 0; i < numActiveChains; ++i) {
+        float mag = getChainMagnitude(i, rc);
+        auto prev = chains[i].peak.load(std::memory_order_relaxed);
+        if (mag > prev)
+            chains[i].peak.store(mag, std::memory_order_relaxed);
+    }
+}
+
+// UI thread: consume peaks for meter display
+float consumePeak(int chainIndex) {
+    return chains[chainIndex].peak.exchange(0.0f, std::memory_order_relaxed);
+}
+```
+
+### Pad Trigger Flags
+
+```cpp
+// Array of atomic trigger flags, one per pad
+std::array<std::atomic<bool>, 16> padTriggers{};
+
+// MIDI/UI thread
+void triggerPad(int padIndex) {
+    padTriggers[padIndex].store(true, std::memory_order_relaxed);
+}
+
+// Audio thread
+void applyToBuffer(const PluginRenderContext& rc) override {
+    for (int i = 0; i < 16; ++i) {
+        if (padTriggers[i].exchange(false, std::memory_order_relaxed)) {
+            startPadPlayback(i);
+        }
+    }
+}
+```
+
+### CachedValue for Level/Pan
+
+```cpp
+// Backed by ValueTree so values persist and can be automated
+juce::CachedValue<float> level, pan;
+
+void initialise(const PluginInitialisationInfo& info) override {
+    level.referTo(state, IDs::level, nullptr, 0.8f);
+    pan.referTo(state, IDs::pan, nullptr, 0.0f);
+}
+
+void applyToBuffer(const PluginRenderContext& rc) override {
+    float l = level.get();
+    float p = pan.get();
+    // Apply gain and panning to buffer...
+}
+```
+
+## Debugging Checklist
+
+If you hear clicks, dropouts, or glitches:
+
+1. **Search for allocations** in `applyToBuffer()` - look for `new`, `String`, `Array`, `vector` operations
+2. **Search for locks** - grep for `ScopedLock`, `lock_guard`, `CriticalSection` in audio path
+3. **Check for DBG()** calls in audio code - these do file I/O
+4. **Verify pre-allocation** - all buffers sized in `initialise()`, not in `applyToBuffer()`
+5. **Check CachedValue usage** - ensure `referTo()` is called in `initialise()`, not in `applyToBuffer()`
diff --git a/.claude/skills/juce-threading/SKILL.md b/.claude/skills/juce-threading/SKILL.md
@@ -0,0 +1,423 @@
+---
+name: juce-threading
+description: JUCE threading model and component lifecycle safety. Use when writing UI components, async callbacks, timers, or any code that crosses thread boundaries. Covers destruction ordering, SafePointer, LookAndFeel cleanup, and common crash patterns.
+---
+
+# JUCE Threading Model & Component Lifecycle
+
+This skill covers thread safety and component lifecycle patterns critical for avoiding crashes in MAGDA.
+
+## Threading Model
+
+### Three Thread Contexts
+
+```
+MessageThread (UI)     — Component::paint, resized, mouse events, Timer callbacks, callAsync lambdas
+Audio Thread (RT)      — processBlock, no allocations, no locks, no MessageManager calls
+Background Threads     — juce::Thread, juce::ThreadPool, long-running tasks
+```
+
+### Check Which Thread You're On
+
+```cpp
+// Assert you're on the message thread
+jassert(juce::MessageManager::getInstance()->isThisTheMessageThread());
+
+// Check without asserting
+if (juce::MessageManager::getInstance()->isThisTheMessageThread())
+    component.repaint();
+```
+
+### Cross-Thread Communication
+
+```cpp
+// Audio thread → UI thread (fire-and-forget)
+juce::MessageManager::callAsync([this] {
+    // Runs on message thread. WARNING: `this` may be dead — see SafePointer below.
+    label.setText("Done", juce::dontSendNotification);
+});
+
+// Audio thread → UI thread (coalesced, no allocation)
+struct MyComp : juce::Component, juce::AsyncUpdater {
+    void audioCallback() {
+        latestValue.store(newVal);
+        triggerAsyncUpdate();  // Safe from any thread, coalesces multiple calls
+    }
+    void handleAsyncUpdate() override {
+        // Runs on message thread, once per coalesced batch
+        slider.setValue(latestValue.load());
+    }
+    std::atomic<float> latestValue { 0.0f };
+};
+
+// Periodic polling from UI thread
+struct MyComp : juce::Component, juce::Timer {
+    MyComp() { startTimerHz(30); }
+    ~MyComp() override { stopTimer(); }  // MUST stop in destructor
+    void timerCallback() override {
+        // Runs on message thread
+        repaint();
+    }
+};
+
+// Delayed one-shot on message thread
+juce::MessageManager::callAsync([] {
+    juce::Timer::callAfterDelay(500, [] {
+        // Runs on message thread after 500ms
+    });
+});
+```
+
+### Audio Thread Rules
+
+```cpp
+void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midi) override
+{
+    // NEVER do any of these on the audio thread:
+    // - new / delete / malloc
+    // - juce::String construction or concatenation
+    // - MessageManager::callAsync (allocates — use AsyncUpdater instead)
+    // - Lock acquisition (mutex, CriticalSection)
+    // - File I/O
+    // - DBG() in release builds
+
+    // SAFE on audio thread:
+    // - std::atomic reads/writes
+    // - Lock-free queues (juce::AbstractFifo)
+    // - Raw pointer/buffer arithmetic
+    // - triggerAsyncUpdate() (lock-free)
+}
+```
+
+## Component Lifecycle & Destruction Safety
+
+### Destruction Ordering
+
+```cpp
+struct ParentComp : juce::Component {
+    ~ParentComp() override
+    {
+        stopTimer();            // 1. Stop all timers
+        removeListener(this);   // 2. Remove all listener registrations
+        // 3. Children are destroyed automatically after this (member order, reverse)
+    }
+
+    ChildComp child;  // Destroyed BEFORE ParentComp destructor body runs?
+                      // NO — members are destroyed AFTER destructor body.
+                      // So stopTimer() in destructor body is safe.
+};
+```
+
+**Rule**: Stop timers and remove listeners in the destructor body, before members are destroyed.
+
+### SafePointer for Async Safety
+
+```cpp
+// DANGEROUS — `this` may be deleted before lambda runs
+juce::MessageManager::callAsync([this] {
+    setText("done");  // CRASH if component was deleted
+});
+
+// SAFE — SafePointer becomes nullptr if component is deleted
+juce::MessageManager::callAsync([safeThis = juce::Component::SafePointer<MyComp>(this)] {
+    if (auto* self = safeThis.getComponent())
+        self->setText("done");
+});
+
+// SAFE — shorter form
+auto safeThis = juce::Component::SafePointer<MyComp>(this);
+juce::MessageManager::callAsync([safeThis]() mutable {
+    if (safeThis != nullptr)
+        safeThis->setText("done");
+});
+```
+
+### Timer Safety
+
+```cpp
+struct MyComp : juce::Component, juce::Timer {
+    MyComp() { startTimerHz(30); }
+
+    ~MyComp() override {
+        stopTimer();  // MANDATORY — timer callback must not fire after destruction
+    }
+
+    void timerCallback() override {
+        // Safe to access members here — guaranteed on message thread,
+        // and stopTimer() in destructor prevents post-destruction calls
+        repaint();
+    }
+};
+```
+
+### LookAndFeel Cleanup
+
+```cpp
+// DANGEROUS — components reference L&F that's already destroyed
+struct MyApp {
+    CustomLookAndFeel lnf;       // Destroyed SECOND (after mainWindow)
+    std::unique_ptr<MainWindow> mainWindow;  // Destroyed FIRST — but its children
+                                              // may still reference lnf during teardown
+};
+
+// SAFE — clear default L&F before destroying components
+struct MyApp {
+    ~MyApp() {
+        juce::LookAndFeel::setDefaultLookAndFeel(nullptr);  // Clear global L&F
+        mainWindow.reset();  // Now safe to destroy components
+    }
+    CustomLookAndFeel lnf;
+    std::unique_ptr<MainWindow> mainWindow;
+};
+
+// SAFE — per-component L&F cleanup
+struct MyComp : juce::Component {
+    ~MyComp() override {
+        setLookAndFeel(nullptr);  // Detach before L&F may be destroyed
+    }
+};
+```
+
+### Listener Removal
+
+```cpp
+struct MyComp : juce::Component, juce::Value::Listener {
+    MyComp(juce::Value& v) : value(v) {
+        value.addListener(this);
+    }
+
+    ~MyComp() override {
+        value.removeListener(this);  // MUST remove before destruction
+    }
+
+    void valueChanged(juce::Value&) override {
+        repaint();
+    }
+
+    juce::Value value;
+};
+```
+
+### JUCE Leak Detector
+
+```cpp
+class MyComponent : public juce::Component {
+public:
+    MyComponent();
+    ~MyComponent() override;
+
+private:
+    // Place at the END of the class — detects leaked instances on shutdown
+    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MyComponent)
+};
+```
+
+## Common Crash Patterns & Fixes
+
+### 1. Timer fires after component deleted
+
+```cpp
+// BUG: no stopTimer() in destructor
+struct Bad : juce::Component, juce::Timer {
+    ~Bad() override { /* timer still running! */ }
+};
+
+// FIX:
+struct Good : juce::Component, juce::Timer {
+    ~Good() override { stopTimer(); }
+};
+```
+
+### 2. callAsync lambda captures dead `this`
+
+```cpp
+// BUG:
+juce::MessageManager::callAsync([this] { repaint(); });
+
+// FIX:
+juce::MessageManager::callAsync(
+    [safe = juce::Component::SafePointer<MyComp>(this)] {
+        if (safe != nullptr) safe->repaint();
+    });
+```
+
+### 3. LookAndFeel destroyed before components
+
+```cpp
+// BUG: member destruction order destroys L&F while components still reference it
+struct App {
+    CustomLookAndFeel lnf;
+    std::unique_ptr<MainWindow> window;  // window's children still use lnf during destruction
+};
+
+// FIX: explicit teardown order
+struct App {
+    ~App() {
+        juce::LookAndFeel::setDefaultLookAndFeel(nullptr);
+        window.reset();
+    }
+    CustomLookAndFeel lnf;
+    std::unique_ptr<MainWindow> window;
+};
+```
+
+### 4. Listener not removed before object destroyed
+
+```cpp
+// BUG: broadcaster calls dead listener
+struct Bad : juce::Button::Listener {
+    Bad(juce::Button& b) : button(b) { button.addListener(this); }
+    ~Bad() { /* forgot removeListener! */ }
+    juce::Button& button;
+};
+
+// FIX:
+struct Good : juce::Button::Listener {
+    Good(juce::Button& b) : button(b) { button.addListener(this); }
+    ~Good() { button.removeListener(this); }
+    juce::Button& button;
+};
+```
+
+### 5. Component deleted during its own callback
+
+```cpp
+// BUG: deleting yourself inside a button callback
+void buttonClicked(juce::Button*) override {
+    owner.removeChildComponent(this);
+    delete this;  // CRASH — stack still unwinding through JUCE event dispatch
+}
+
+// FIX: defer deletion
+void buttonClicked(juce::Button*) override {
+    juce::MessageManager::callAsync([this, &owner = this->owner] {
+        owner.removeAndDeleteChild(this);
+    });
+}
+```
+
+### 6. Accessing MessageManager from audio thread
+
+```cpp
+// BUG: called from processBlock
+void processBlock(...) {
+    if (clipping)
+        component.repaint();  // WRONG — repaint() posts to message thread internally,
+                               // but is not safe from audio thread
+}
+
+// FIX: use atomic flag + timer or AsyncUpdater
+void processBlock(...) {
+    if (clipping)
+        clipFlag.store(true);  // Lock-free
+}
+
+void timerCallback() override {
+    if (clipFlag.exchange(false))
+        clipIndicator.repaint();
+}
+```
+
+## Prefer RAII Over Manual Resource Management
+
+Always use RAII classes instead of manual acquire/release patterns. This prevents resource leaks when exceptions occur or early returns are taken.
+
+### Smart Pointers Over Raw new/delete
+
+```cpp
+// BAD — leak if exception or early return between new and delete
+auto* comp = new MyComponent();
+addAndMakeVisible(comp);
+// ... if something throws or returns, comp is leaked
+
+// GOOD — ownership is automatic
+auto comp = std::make_unique<MyComponent>();
+addAndMakeVisible(comp.get());
+ownedComponents.push_back(std::move(comp));
+```
+
+### Scoped Locks
+
+```cpp
+// BAD — manual lock/unlock, easy to forget unlock on early return
+mutex.lock();
+doWork();
+if (error) return;  // BUG: mutex not unlocked!
+mutex.unlock();
+
+// GOOD — RAII lock, always released on scope exit
+{
+    const juce::ScopedLock sl(mutex);
+    doWork();
+    if (error) return;  // mutex automatically unlocked
+}
+```
+
+### Tracktion Engine RAII Helpers
+
+```cpp
+// Prevent expensive playback graph rebuilds during batch operations
+{
+    te::TransportControl::ReallocationInhibitor inhibitor(transport);
+    // ... make many changes to tracks/plugins ...
+}  // Single graph rebuild happens here
+
+// Restore playback state after temporary stop
+{
+    te::TransportControl::ScopedPlaybackRestarter restarter(transport);
+    transport.stop(false, false);
+    // ... do work that requires transport stopped ...
+}  // Playback automatically resumes
+
+// Group undo operations
+{
+    te::Edit::UndoTransactionInhibitor inhibitor(*edit);
+    // ... multiple operations won't be grouped into one undo step ...
+}
+```
+
+### RAII for Listener Registration
+
+```cpp
+// Pattern: register in constructor, unregister in destructor
+struct ScopedListener {
+    ScopedListener(juce::Value& v, juce::Value::Listener* l)
+        : value(v), listener(l) { value.addListener(listener); }
+    ~ScopedListener() { value.removeListener(listener); }
+    juce::Value& value;
+    juce::Value::Listener* listener;
+};
+```
+
+### RAII for Timer Management
+
+```cpp
+// If you inherit from Timer, always stop in destructor:
+~MyComp() override { stopTimer(); }
+
+// Or use a helper that auto-stops:
+struct ScopedTimer : juce::Timer {
+    std::function<void()> callback;
+    ~ScopedTimer() override { stopTimer(); }
+    void timerCallback() override { if (callback) callback(); }
+};
+```
+
+## Thread-Safe Data Patterns
+
+```cpp
+// Atomic for simple values
+std::atomic<float> gain { 1.0f };
+std::atomic<bool> shouldStop { false };
+
+// Lock-free FIFO for messages (audio → UI)
+juce::AbstractFifo fifo { 512 };
+std::array<float, 512> buffer;
+
+// SpinLock for very short critical sections (avoid on audio thread if possible)
+juce::SpinLock lock;
+{
+    const juce::SpinLock::ScopedLockType sl(lock);
+    // Very brief work only
+}
+```
diff --git a/.claude/skills/valuetree/SKILL.md b/.claude/skills/valuetree/SKILL.md
@@ -0,0 +1,379 @@
+---
+name: valuetree
+description: JUCE ValueTree and serialization patterns for Tracktion Engine plugins. Use when working with plugin state, CachedValue properties, ValueTree listeners, or state persistence/restoration.
+---
+
+# JUCE ValueTree & Serialization Patterns
+
+ValueTree is the core data model in JUCE and Tracktion Engine. Every plugin, track, and edit stores its state as a ValueTree. This skill covers the patterns used throughout the MAGDA codebase.
+
+## ValueTree Basics
+
+### Creating and Populating
+
+```cpp
+#include <juce_data_structures/juce_data_structures.h>
+
+// Create a tree with an Identifier type
+juce::ValueTree tree(juce::Identifier("MyPlugin"));
+
+// Set properties
+tree.setProperty("gain", 0.5f, nullptr);       // no undo
+tree.setProperty("name", "Lead", undoManager);  // with undo
+
+// Add child trees
+juce::ValueTree child(juce::Identifier("CHAIN"));
+child.setProperty("index", 0, nullptr);
+tree.addChild(child, -1, nullptr);  // -1 = append at end
+```
+
+### Reading Properties
+
+```cpp
+// Read with default fallback
+float gain = tree.getProperty("gain", 1.0f);
+juce::String name = tree.getProperty("name", "Default");
+
+// Check existence
+if (tree.hasProperty("gain")) { /* ... */ }
+
+// Get typed child
+juce::ValueTree chainTree = tree.getChildWithName("CHAIN");
+if (chainTree.isValid()) {
+    int idx = chainTree.getProperty("index");
+}
+```
+
+### Hierarchy Navigation
+
+```cpp
+// Parent access
+juce::ValueTree parent = tree.getParent();
+
+// Child iteration
+for (int i = 0; i < tree.getNumChildren(); ++i) {
+    auto child = tree.getChild(i);
+    if (child.hasType("CHAIN")) {
+        // process chain child
+    }
+}
+
+// Range-based iteration (JUCE 7+)
+for (auto child : tree) {
+    DBG(child.getType().toString());
+}
+
+// Find specific child by property
+for (int i = 0; i < tree.getNumChildren(); ++i) {
+    auto child = tree.getChild(i);
+    if (child.hasType("CHAIN") && (int)child.getProperty("index") == 2)
+        return child;
+}
+```
+
+### Identifier Constants
+
+Always define Identifiers as static constants to avoid repeated string hashing:
+
+**Header (.h):**
+```cpp
+class MyPlugin : public te::Plugin {
+    static const juce::Identifier gainId;
+    static const juce::Identifier chainId;
+    static const juce::Identifier muteId;
+};
+```
+
+**Source (.cpp):**
+```cpp
+const juce::Identifier MyPlugin::gainId("gain");
+const juce::Identifier MyPlugin::chainId("CHAIN");
+const juce::Identifier MyPlugin::muteId("mute");
+```
+
+## CachedValue<T>
+
+`CachedValue<T>` binds a C++ variable to a ValueTree property. It caches the value locally so reads are thread-safe (no locking), making it suitable for audio-thread reads.
+
+### Binding to a Property
+
+```cpp
+class MyPlugin : public te::Plugin {
+    juce::CachedValue<float> level;
+    juce::CachedValue<float> pan;
+    juce::CachedValue<bool> mute;
+    juce::CachedValue<bool> solo;
+
+    MyPlugin(te::PluginCreationInfo info) : te::Plugin(info) {
+        // referTo(tree, propertyId, undoManager, defaultValue)
+        level.referTo(state, "level", nullptr, 1.0f);
+        pan.referTo(state, "pan", nullptr, 0.0f);
+        mute.referTo(state, "mute", nullptr, false);
+        solo.referTo(state, "solo", nullptr, false);
+    }
+};
+```
+
+### Reading and Writing
+
+```cpp
+// Read — thread-safe, returns cached copy
+float currentLevel = level.get();
+
+// Can also use implicit conversion
+float val = level;
+
+// Write — updates the ValueTree property (triggers listeners)
+level = 0.75f;
+
+// Equivalent to:
+state.setProperty("level", 0.75f, nullptr);
+```
+
+### Force Update After State Restore
+
+After `restorePluginStateFromValueTree()` copies new values into the `state` tree, the CachedValues may still hold stale data. You must call `forceUpdateOfCachedValue()`:
+
+```cpp
+void restorePluginStateFromValueTree(const juce::ValueTree& v) override {
+    // This copies matching properties from v into this->state
+    te::copyPropertiesToCachedValues(state, v, nullptr);
+
+    // Force each CachedValue to re-read from the tree
+    level.forceUpdateOfCachedValue();
+    pan.forceUpdateOfCachedValue();
+    mute.forceUpdateOfCachedValue();
+    solo.forceUpdateOfCachedValue();
+}
+```
+
+## Serialization Pattern in Tracktion Engine Plugins
+
+### Plugin `state` Member
+
+Every `te::Plugin` has a `state` member which is a `juce::ValueTree`. This is the single source of truth for all plugin data.
+
+### Full Plugin Pattern
+
+```cpp
+// Header
+class MyPlugin : public te::Plugin {
+public:
+    MyPlugin(te::PluginCreationInfo);
+    ~MyPlugin() override;
+
+    static const char* xmlTypeName;
+
+    // te::Plugin overrides
+    void restorePluginStateFromValueTree(const juce::ValueTree&) override;
+    juce::String getName() const override { return "My Plugin"; }
+
+private:
+    static const juce::Identifier levelId;
+    static const juce::Identifier panId;
+    static const juce::Identifier chainTreeId;
+
+    juce::CachedValue<float> level;
+    juce::CachedValue<float> pan;
+
+    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MyPlugin)
+};
+
+// Source
+const juce::Identifier MyPlugin::levelId("level");
+const juce::Identifier MyPlugin::panId("pan");
+const juce::Identifier MyPlugin::chainTreeId("CHAIN");
+
+MyPlugin::MyPlugin(te::PluginCreationInfo info)
+    : te::Plugin(info)
+{
+    // Bind CachedValues to state
+    level.referTo(state, levelId, nullptr, 1.0f);
+    pan.referTo(state, panId, nullptr, 0.0f);
+
+    // Initialize child trees if not present
+    if (!state.getChildWithName(chainTreeId).isValid()) {
+        juce::ValueTree chainTree(chainTreeId);
+        chainTree.setProperty("index", 0, nullptr);
+        state.addChild(chainTree, -1, nullptr);
+    }
+}
+
+MyPlugin::~MyPlugin() {
+    notifyListenersOfDeletion();
+}
+
+void MyPlugin::restorePluginStateFromValueTree(const juce::ValueTree& v) {
+    te::copyPropertiesToCachedValues(state, v, nullptr);
+
+    level.forceUpdateOfCachedValue();
+    pan.forceUpdateOfCachedValue();
+
+    // Restore child trees
+    for (int i = state.getNumChildren(); --i >= 0;)
+        state.removeChild(i, nullptr);
+
+    for (auto child : v) {
+        state.addChild(child.createCopy(), -1, nullptr);
+    }
+}
+```
+
+## ValueTree::Listener
+
+### Implementing a Listener
+
+```cpp
+class MyComponent : public juce::Component,
+                    private juce::ValueTree::Listener
+{
+public:
+    MyComponent(juce::ValueTree stateToWatch)
+        : watchedState(stateToWatch)
+    {
+        watchedState.addListener(this);
+    }
+
+    ~MyComponent() override {
+        watchedState.removeListener(this);  // Always remove in destructor
+    }
+
+private:
+    void valueTreePropertyChanged(juce::ValueTree& tree,
+                                  const juce::Identifier& property) override
+    {
+        if (property == MyPlugin::levelId) {
+            // Update UI — but check what thread you're on!
+            // If changed from audio thread, use AsyncUpdater
+            triggerAsyncUpdate();
+        }
+    }
+
+    void valueTreeChildAdded(juce::ValueTree& parent,
+                             juce::ValueTree& child) override
+    {
+        // A child tree was added
+    }
+
+    void valueTreeChildRemoved(juce::ValueTree& parent,
+                               juce::ValueTree& child,
+                               int index) override
+    {
+        // A child tree was removed
+    }
+
+    juce::ValueTree watchedState;
+};
+```
+
+### Thread Safety Warning
+
+Listeners fire on the thread that made the change. If a property is set from the audio thread, the listener callback runs on the audio thread. Never do UI work directly in a listener that might be called from the audio thread. Use `juce::AsyncUpdater` or `juce::MessageManager::callAsync()` to bounce to the message thread.
+
+## UndoManager Integration
+
+```cpp
+// With undo support (UI-driven changes)
+state.setProperty("gain", newValue, &edit.getUndoManager());
+state.addChild(child, -1, &edit.getUndoManager());
+
+// Without undo (initialization, audio-thread, internal state)
+state.setProperty("gain", newValue, nullptr);
+state.addChild(child, -1, nullptr);
+
+// In TE plugins, get the undo manager via:
+auto* um = getUndoManager();
+state.setProperty("gain", newValue, um);
+```
+
+## Common Patterns in This Codebase
+
+### Chain Properties
+
+Plugins with multiple chains (e.g., drum grid, multi-output) store per-chain state as child trees:
+
+```cpp
+// Setting up chain state
+for (int i = 0; i < numChains; ++i) {
+    juce::ValueTree chainTree("CHAIN");
+    chainTree.setProperty("index", i, nullptr);
+    chainTree.setProperty("level", 1.0f, nullptr);
+    chainTree.setProperty("pan", 0.0f, nullptr);
+    chainTree.setProperty("mute", false, nullptr);
+    chainTree.setProperty("solo", false, nullptr);
+    state.addChild(chainTree, -1, nullptr);
+}
+
+// Reading chain state
+for (int i = 0; i < state.getNumChildren(); ++i) {
+    auto child = state.getChild(i);
+    if (child.hasType("CHAIN")) {
+        float chainLevel = child.getProperty("level", 1.0f);
+        float chainPan = child.getProperty("pan", 0.0f);
+        bool chainMute = child.getProperty("mute", false);
+    }
+}
+```
+
+### CachedValue Arrays for Chains
+
+When you need audio-thread-safe reads for multiple chains:
+
+```cpp
+struct ChainState {
+    juce::CachedValue<float> level;
+    juce::CachedValue<float> pan;
+    juce::CachedValue<bool> mute;
+    juce::CachedValue<bool> solo;
+
+    void referTo(juce::ValueTree& chainTree) {
+        level.referTo(chainTree, "level", nullptr, 1.0f);
+        pan.referTo(chainTree, "pan", nullptr, 0.0f);
+        mute.referTo(chainTree, "mute", nullptr, false);
+        solo.referTo(chainTree, "solo", nullptr, false);
+    }
+
+    void forceUpdate() {
+        level.forceUpdateOfCachedValue();
+        pan.forceUpdateOfCachedValue();
+        mute.forceUpdateOfCachedValue();
+        solo.forceUpdateOfCachedValue();
+    }
+};
+
+std::vector<ChainState> chainStates;
+```
+
+### Finding Child Trees by Type
+
+```cpp
+// Find a specific child tree
+juce::ValueTree findChainByIndex(const juce::ValueTree& parentState, int index) {
+    for (int i = 0; i < parentState.getNumChildren(); ++i) {
+        auto child = parentState.getChild(i);
+        if (child.hasType("CHAIN") && (int)child.getProperty("index") == index)
+            return child;
+    }
+    return {};  // invalid ValueTree
+}
+
+// Collect all children of a type
+std::vector<juce::ValueTree> getChains(const juce::ValueTree& parentState) {
+    std::vector<juce::ValueTree> chains;
+    for (int i = 0; i < parentState.getNumChildren(); ++i) {
+        auto child = parentState.getChild(i);
+        if (child.hasType("CHAIN"))
+            chains.push_back(child);
+    }
+    return chains;
+}
+```
+
+## Common Pitfalls
+
+1. **Forgetting `forceUpdateOfCachedValue()`** after `restorePluginStateFromValueTree()` — CachedValues will hold stale data
+2. **Setting properties from the audio thread** — Triggers listeners on the audio thread; use CachedValue for reads, avoid writes from audio thread when possible
+3. **Not removing listeners in destructors** — Dangling listener = crash
+4. **Using string literals instead of Identifier constants** — Creates a new Identifier each time, wastes CPU on hashing
+5. **Passing `undoManager` during initialization** — Use `nullptr` for initial setup; only pass undoManager for user-driven changes
+6. **Forgetting `isValid()` checks** — `getChildWithName()` returns an invalid ValueTree if not found; always check before use
PATCH

echo "Gold patch applied."
