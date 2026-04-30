#!/usr/bin/env bash
set -euo pipefail

cd /workspace/client-sdk-android

# Idempotency guard
if grep -qF "Entry types such as `LiveKit` and `ConnectOptions` live in the `io.livekit.andro" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -10,26 +10,37 @@ Supported platforms: Android (minimum API level 21)
 
 ## Architecture
 
-The SDK is provided through the `livekit-sdk-android` module.
+The SDK is provided through the `livekit-android-sdk` Gradle module (package root `io.livekit.android`).
 
 ```
-livekit-sdk-android/src/main/java/io/livekit
+livekit-android-sdk/src/main/java/io/livekit/android
 ├── annotations/           # Annotations for marking APIs (e.g. @Beta)
 ├── audio/                 # AudioHandler, AudioProcessingController
 ├── coroutines/            # Utility methods relating to coroutines
 ├── dagger/                # Dependency injection internal to LiveKit SDK
 ├── e2ee/                  # End-to-end encryption
 ├── events/                # RoomEvent, TrackEvent, ParticipantEvent
-├── room/                  # Room management
+├── memory/                # Resource lifecycle helpers
+├── renderer/              # Video render views
+├── room/                  # Room, SignalClient, RTCEngine, tracks
 │   ├── datastream/        # Incoming/outgoing datastream IO
+│   ├── metrics/           # RTC metrics
+│   ├── network/           # Reconnect and network callbacks
 │   ├── participant/       # LocalParticipant, RemoteParticipant
-│   ├── track/             # AudioTrack, VideoTrack, TrackPublication
-│   └── types/             # Externally predefined types
+│   ├── provisions/        # Internal provisioning helpers
+│   ├── rpc/               # Room-scoped RPC
+│   ├── track/             # Audio/video/screencast tracks and publications
+│   ├── types/             # Shared room-related types
+│   └── util/              # Room-internal utilities
+├── rpc/                   # RPC error types (package-level)
+├── stats/                 # Client/network stats helpers
 ├── token/                 # TokenSource implementations for auth
 ├── util/                  # Generic utility methods, logging, FlowDelegate
-└── webrtc/                # WebRTC helper classes
+└── webrtc/                # WebRTC helper classes and extensions
 ```
 
+Entry types such as `LiveKit` and `ConnectOptions` live in the `io.livekit.android` package alongside these directories.
+
 Key components:
 
 - `LiveKit` - main entry point; creates a `Room` object.
@@ -51,7 +62,7 @@ Key classes:
 - `PeerConnectionTransport` - wraps a `PeerConnection`; handles ICE candidates, SDP offer/answer
 - `RTCEngine` - integrates the SignalClient and PeerConnectionTransport into a consolidated
   connection
-- `io.livekit.webrtc` package - convenience extensions on WebRTC types
+- `io.livekit.android.webrtc` package - convenience extensions on WebRTC types
 
 Threading:
 
PATCH

echo "Gold patch applied."
