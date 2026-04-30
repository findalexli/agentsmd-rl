"""Behavioral checks for firebase-ios-sdk-ai-add-agentsmd-for-firebaseaisources (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/firebase-ios-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/AGENTS.md')
    assert '- **`Chat.swift`**: Defines the `Chat` class, which represents a back-and-forth chat with a `GenerativeModel`. It is instantiated via the `startChat(history:)` method on a `GenerativeModel` instance. ' in text, "expected to find: " + '- **`Chat.swift`**: Defines the `Chat` class, which represents a back-and-forth chat with a `GenerativeModel`. It is instantiated via the `startChat(history:)` method on a `GenerativeModel` instance. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/AGENTS.md')
    assert '- **`AILog.swift`**: Defines an internal `AILog` enum for logging within the Firebase AI SDK. It includes a `MessageCode` enum for various log messages, and helper functions for logging at different l' in text, "expected to find: " + '- **`AILog.swift`**: Defines an internal `AILog` enum for logging within the Firebase AI SDK. It includes a `MessageCode` enum for various log messages, and helper functions for logging at different l'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/AGENTS.md')
    assert "- **`GenerateContentResponse.swift`**: Defines the `GenerateContentResponse` struct, which represents the model's response to a generate content request. It also defines nested structs like `UsageMeta" in text, "expected to find: " + "- **`GenerateContentResponse.swift`**: Defines the `GenerateContentResponse` struct, which represents the model's response to a generate content request. It also defines nested structs like `UsageMeta"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/AGENTS.md')
    assert '- **[`Internal/`](Internal/AGENTS.md)**: This directory contains internal protocols not meant for public consumption.' in text, "expected to find: " + '- **[`Internal/`](Internal/AGENTS.md)**: This directory contains internal protocols not meant for public consumption.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/AGENTS.md')
    assert 'These protocols define contracts for data models and services, ensuring a consistent and predictable structure.' in text, "expected to find: " + 'These protocols define contracts for data models and services, ensuring a consistent and predictable structure.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/AGENTS.md')
    assert 'When adding new features, refer to the existing protocols to maintain consistency.' in text, "expected to find: " + 'When adding new features, refer to the existing protocols to maintain consistency.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/Internal/AGENTS.md')
    assert '- **`CodableProtoEnum.swift`**: This file provides helper protocols for encoding and decoding protobuf enums. It defines `ProtoEnum` as a base protocol for types that represent a Protocol Buffer raw e' in text, "expected to find: " + '- **`CodableProtoEnum.swift`**: This file provides helper protocols for encoding and decoding protobuf enums. It defines `ProtoEnum` as a base protocol for types that represent a Protocol Buffer raw e'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/Internal/AGENTS.md')
    assert 'Protocols in this directory are subject to change without notice and should not be relied upon by external code.' in text, "expected to find: " + 'Protocols in this directory are subject to change without notice and should not be relied upon by external code.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Protocols/Internal/AGENTS.md')
    assert 'This directory contains internal protocols not meant for public consumption.' in text, "expected to find: " + 'This directory contains internal protocols not meant for public consumption.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/AGENTS.md')
    assert '- **[`Internal/`](Internal/AGENTS.md)**: Internal types are used for the internal implementation of the library and are not meant for public consumption. They can change at any time without notice.' in text, "expected to find: " + '- **[`Internal/`](Internal/AGENTS.md)**: Internal types are used for the internal implementation of the library and are not meant for public consumption. They can change at any time without notice.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/AGENTS.md')
    assert 'When adding a new data type, consider whether it should be part of the public API or not and place it in the corresponding directory.' in text, "expected to find: " + 'When adding a new data type, consider whether it should be part of the public API or not and place it in the corresponding directory.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/AGENTS.md')
    assert '- **[`Public/`](Public/AGENTS.md)**: Public types are part of the public API of the library and are safe to be used by developers.' in text, "expected to find: " + '- **[`Public/`](Public/AGENTS.md)**: Public types are part of the public API of the library and are safe to be used by developers.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/AGENTS.md')
    assert 'This directory is further organized into subdirectories based on the feature they are related to, for example:' in text, "expected to find: " + 'This directory is further organized into subdirectories based on the feature they are related to, for example:'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/AGENTS.md')
    assert 'This directory contains internal data types used for the implementation of the FirebaseAI library.' in text, "expected to find: " + 'This directory contains internal data types used for the implementation of the FirebaseAI library.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/AGENTS.md')
    assert 'These types are not part of the public API and should not be used directly by developers.' in text, "expected to find: " + 'These types are not part of the public API and should not be used directly by developers.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Errors/AGENTS.md')
    assert '- **`BackendError.swift`**: Defines an error structure for capturing detailed error information from the backend service. It includes the HTTP response code, a message, an RPC status, and additional d' in text, "expected to find: " + '- **`BackendError.swift`**: Defines an error structure for capturing detailed error information from the backend service. It includes the HTTP response code, a message, an RPC status, and additional d'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Errors/AGENTS.md')
    assert '- **`EmptyContentError.swift`**: Defines a specific error for when a `Candidate` is returned with no content and no finish reason. This is a nested struct within an extension of `Candidate`.' in text, "expected to find: " + '- **`EmptyContentError.swift`**: Defines a specific error for when a `Candidate` is returned with no content and no finish reason. This is a nested struct within an extension of `Candidate`.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Errors/AGENTS.md')
    assert 'These errors are not part of the public API and are used to handle specific error conditions within the SDK.' in text, "expected to find: " + 'These errors are not part of the public API and are used to handle specific error conditions within the SDK.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Imagen/AGENTS.md')
    assert '- **`ImagenGenerationRequest.swift`**: Defines the `ImagenGenerationRequest` struct, which encapsulates the entire request sent to the Imagen API, including the model, API configuration, instances, an' in text, "expected to find: " + '- **`ImagenGenerationRequest.swift`**: Defines the `ImagenGenerationRequest` struct, which encapsulates the entire request sent to the Imagen API, including the model, API configuration, instances, an'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Imagen/AGENTS.md')
    assert '- **`ImageGenerationParameters.swift`**: Defines the `ImageGenerationParameters` struct, which holds all the parameters for an image generation request, such as `sampleCount`, `storageURI`, `negativeP' in text, "expected to find: " + '- **`ImageGenerationParameters.swift`**: Defines the `ImageGenerationParameters` struct, which holds all the parameters for an image generation request, such as `sampleCount`, `storageURI`, `negativeP'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Imagen/AGENTS.md')
    assert '- **`InternalImagenImage.swift`**: Defines the `_InternalImagenImage` struct, which is the internal representation of an Imagen image, containing the `mimeType`, `bytesBase64Encoded`, and `gcsURI`.' in text, "expected to find: " + '- **`InternalImagenImage.swift`**: Defines the `_InternalImagenImage` struct, which is the internal representation of an Imagen image, containing the `mimeType`, `bytesBase64Encoded`, and `gcsURI`.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Live/AGENTS.md')
    assert '- **`BidiGenerateContentServerMessage.swift`**: Defines the `BidiGenerateContentServerMessage` struct and its nested `MessageType` enum, representing a response message from the server in a bidirectio' in text, "expected to find: " + '- **`BidiGenerateContentServerMessage.swift`**: Defines the `BidiGenerateContentServerMessage` struct and its nested `MessageType` enum, representing a response message from the server in a bidirectio'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Live/AGENTS.md')
    assert '- **`LiveSessionService.swift`**: Defines the `LiveSessionService` actor, which manages the connection and communication with the backend for a `LiveSession`. It handles setting up the web socket, sen' in text, "expected to find: " + '- **`LiveSessionService.swift`**: Defines the `LiveSessionService` actor, which manages the connection and communication with the backend for a `LiveSession`. It handles setting up the web socket, sen'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Live/AGENTS.md')
    assert '- **`AsyncWebSocket.swift`**: Provides an async/await wrapper around `URLSessionWebSocketTask` for interacting with web sockets. It simplifies sending and receiving messages and provides a custom erro' in text, "expected to find: " + '- **`AsyncWebSocket.swift`**: Provides an async/await wrapper around `URLSessionWebSocketTask` for interacting with web sockets. It simplifies sending and receiving messages and provides a custom erro'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Requests/AGENTS.md')
    assert '- **`CountTokensRequest.swift`**: Defines the request structure for the `countTokens` API endpoint, used to calculate the number of tokens in a prompt. It includes the model name and the content to be' in text, "expected to find: " + '- **`CountTokensRequest.swift`**: Defines the request structure for the `countTokens` API endpoint, used to calculate the number of tokens in a prompt. It includes the model name and the content to be'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Requests/AGENTS.md')
    assert 'These types encapsulate the data that needs to be sent to the backend for various operations.' in text, "expected to find: " + 'These types encapsulate the data that needs to be sent to the backend for various operations.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Requests/AGENTS.md')
    assert 'They are not part of the public API and can change at any time.' in text, "expected to find: " + 'They are not part of the public API and can change at any time.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Tools/AGENTS.md')
    assert '- **`URLContext.swift`**: Defines the `URLContext` struct. It is currently an empty struct that serves to enable the URL context tool. Its presence in a `Tool` enables the feature, and it may be expan' in text, "expected to find: " + '- **`URLContext.swift`**: Defines the `URLContext` struct. It is currently an empty struct that serves to enable the URL context tool. Its presence in a `Tool` enables the feature, and it may be expan'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Tools/AGENTS.md')
    assert 'These types are used to provide context to tools that can be executed by the model.' in text, "expected to find: " + 'These types are used to provide context to tools that can be executed by the model.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Internal/Tools/AGENTS.md')
    assert 'This directory contains internal data types related to tools and function calling.' in text, "expected to find: " + 'This directory contains internal data types related to tools and function calling.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/AGENTS.md')
    assert '- **`Part.swift`**: Defines the `Part` protocol and several conforming structs: `TextPart`, `InlineDataPart`, `FileDataPart`, `FunctionCallPart`, `FunctionResponsePart`, `ExecutableCodePart`, and `Cod' in text, "expected to find: " + '- **`Part.swift`**: Defines the `Part` protocol and several conforming structs: `TextPart`, `InlineDataPart`, `FileDataPart`, `FunctionCallPart`, `FunctionResponsePart`, `ExecutableCodePart`, and `Cod'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/AGENTS.md')
    assert '- **`Backend.swift`**: Defines the `Backend` struct, which is used to configure the backend API for the Firebase AI SDK. It provides static methods `vertexAI(location:)` and `googleAI()` to create ins' in text, "expected to find: " + '- **`Backend.swift`**: Defines the `Backend` struct, which is used to configure the backend API for the Firebase AI SDK. It provides static methods `vertexAI(location:)` and `googleAI()` to create ins'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/AGENTS.md')
    assert '- **`Schema.swift`**: Defines the `Schema` class, which allows the definition of input and output data types for function calling. It supports various data types like string, number, integer, boolean,' in text, "expected to find: " + '- **`Schema.swift`**: Defines the `Schema` class, which allows the definition of input and output data types for function calling. It supports various data types like string, number, integer, boolean,'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Imagen/AGENTS.md')
    assert '- **`ImagenGenerationConfig.swift`**: Defines the `ImagenGenerationConfig` struct, which contains configuration options for generating images with Imagen, such as `negativePrompt`, `numberOfImages`, `' in text, "expected to find: " + '- **`ImagenGenerationConfig.swift`**: Defines the `ImagenGenerationConfig` struct, which contains configuration options for generating images with Imagen, such as `negativePrompt`, `numberOfImages`, `'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Imagen/AGENTS.md')
    assert '- **`ImagenAspectRatio.swift`**: Defines the `ImagenAspectRatio` struct, which represents the aspect ratio for images generated by Imagen. It provides static properties for common aspect ratios like `' in text, "expected to find: " + '- **`ImagenAspectRatio.swift`**: Defines the `ImagenAspectRatio` struct, which represents the aspect ratio for images generated by Imagen. It provides static properties for common aspect ratios like `'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Imagen/AGENTS.md')
    assert '- **`ImagenGenerationResponse.swift`**: Defines the `ImagenGenerationResponse` struct, which is the response from a request to generate images. It contains the generated `images` and a `filteredReason' in text, "expected to find: " + '- **`ImagenGenerationResponse.swift`**: Defines the `ImagenGenerationResponse` struct, which is the response from a request to generate images. It contains the generated `images` and a `filteredReason'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Live/AGENTS.md')
    assert '- **`LiveSession.swift`**: Defines the `LiveSession` class, which represents a live WebSocket session. It provides methods for sending real-time data (like `sendAudioRealtime(_:)`, `sendVideoRealtime(' in text, "expected to find: " + '- **`LiveSession.swift`**: Defines the `LiveSession` class, which represents a live WebSocket session. It provides methods for sending real-time data (like `sendAudioRealtime(_:)`, `sendVideoRealtime('[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Live/AGENTS.md')
    assert '- **`LiveGenerativeModel.swift`**: Defines the `LiveGenerativeModel` class, which is a multimodal model capable of real-time content generation based on various input types, supporting bidirectional s' in text, "expected to find: " + '- **`LiveGenerativeModel.swift`**: Defines the `LiveGenerativeModel` class, which is a multimodal model capable of real-time content generation based on various input types, supporting bidirectional s'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Live/AGENTS.md')
    assert '- **`LiveServerContent.swift`**: Defines the `LiveServerContent` struct, which represents an incremental server update generated by the model in response to client messages. It includes properties lik' in text, "expected to find: " + '- **`LiveServerContent.swift`**: Defines the `LiveServerContent` struct, which represents an incremental server update generated by the model in response to client messages. It includes properties lik'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Tools/AGENTS.md')
    assert "- **`CodeExecution.swift`**: Defines the `CodeExecution` struct, which is a tool that allows the model to execute code. This can be used to solve complex problems by leveraging the model's ability to " in text, "expected to find: " + "- **`CodeExecution.swift`**: Defines the `CodeExecution` struct, which is a tool that allows the model to execute code. This can be used to solve complex problems by leveraging the model's ability to "[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Tools/AGENTS.md')
    assert 'These types are used by developers to define and configure tools that the model can execute.' in text, "expected to find: " + 'These types are used by developers to define and configure tools that the model can execute.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Types/Public/Tools/AGENTS.md')
    assert 'This directory contains public data types related to tools and function calling.' in text, "expected to find: " + 'This directory contains public data types related to tools and function calling.'[:80]

