# Security: ZMQ sockets bind to all interfaces, exposing unauthenticated pickle deserialization

## Problem

Several ZeroMQ sockets in SGLang bind to `tcp://*`, making them reachable from any machine on the network. Because these sockets use `pickle.loads()` to deserialize incoming messages, a remote attacker can send crafted payloads to achieve arbitrary code execution.

There are three affected components:

1. **Multimodal generation ZMQ broker** (`python/sglang/multimodal_gen/runtime/scheduler_client.py`): The `run_zeromq_broker()` function creates a REP socket bound to `tcp://*:{broker_port}`. This socket deserializes incoming payloads with `pickle.loads()` and is reachable from any host.

2. **Disaggregation encode receiver** (`python/sglang/srt/disaggregation/encode_receiver.py`): The `get_zmq_socket_on_host()` utility is called without specifying a host, causing it to bind to `tcp://*`. This affects at least two call sites in the encode receiver that create PULL sockets for receiving embedding data.

3. **Network utility default** (`python/sglang/srt/utils/network.py`): The `get_zmq_socket_on_host()` function defaults to binding on `tcp://*` when no host is provided, which is an unsafe default for sockets that handle untrusted data.

## Expected Behavior

- ZMQ sockets should bind to localhost (`127.0.0.1`) by default so that only local processes can connect
- Call sites that genuinely need cross-machine reachability (disaggregation across nodes) should explicitly pass their host
- The OS kernel should reject remote TCP connections before any data reaches pickle deserialization

## Files to Investigate

- `python/sglang/srt/utils/network.py` — `get_zmq_socket_on_host()` function
- `python/sglang/multimodal_gen/runtime/scheduler_client.py` — `run_zeromq_broker()` function
- `python/sglang/srt/disaggregation/encode_receiver.py` — ZMQ socket creation in `WaitingImageRequest.__init__()` and `recv_mm_data()`
