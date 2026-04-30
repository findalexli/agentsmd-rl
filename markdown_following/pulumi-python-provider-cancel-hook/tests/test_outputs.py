"""Tests for the Cancel hook on the Python Provider base classes and gRPC servers."""

import asyncio
import inspect
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/pulumi")


class _MockGrpcContext:
    """Minimal grpc.ServicerContext stand-in for unit-testing servicer methods."""

    def __init__(self) -> None:
        self.code = None
        self.details = None

    def set_code(self, code) -> None:
        self.code = code

    def set_details(self, details) -> None:
        self.details = details


# --- f2p tests --------------------------------------------------------------


def test_provider_base_cancel_returns_none():
    """The synchronous Provider base class exposes a no-op cancel() method."""
    from pulumi.provider.provider import Provider

    p = Provider(version="0.0.1")
    assert hasattr(p, "cancel"), "Provider base class is missing cancel()"
    assert not inspect.iscoroutinefunction(p.cancel), (
        "Provider.cancel must be synchronous (the experimental Provider has the async variant)"
    )
    result = p.cancel()
    assert result is None


def test_experimental_provider_base_cancel_is_async_and_returns_none():
    """The experimental Provider base class exposes an async cancel() coroutine."""
    from pulumi.provider.experimental.provider import Provider as ExpProvider

    assert hasattr(ExpProvider, "cancel"), (
        "experimental Provider base class is missing cancel()"
    )
    assert inspect.iscoroutinefunction(ExpProvider.cancel), (
        "experimental Provider.cancel must be a coroutine (async def)"
    )

    class MyProvider(ExpProvider):
        pass

    sub = MyProvider()
    result = asyncio.run(sub.cancel())
    assert result is None


@pytest.mark.asyncio
async def test_server_cancel_invokes_provider_cancel_and_returns_empty():
    """ProviderServicer.Cancel must call provider.cancel() and return google.protobuf.Empty."""
    from google.protobuf import empty_pb2
    from pulumi.provider.provider import Provider
    from pulumi.provider.server import ProviderServicer

    class TrackingProvider(Provider):
        def __init__(self) -> None:
            super().__init__(version="0.0.1")
            self.cancel_calls = 0

        def cancel(self) -> None:
            self.cancel_calls += 1

    prov = TrackingProvider()
    servicer = ProviderServicer(provider=prov, args=[], engine_address="127.0.0.1:0")

    response = await servicer.Cancel(None, _MockGrpcContext())

    assert prov.cancel_calls == 1, (
        f"provider.cancel() must be invoked exactly once by Cancel; got {prov.cancel_calls} calls"
    )
    assert isinstance(response, empty_pb2.Empty), (
        f"Cancel must return google.protobuf.Empty, got {type(response).__name__}"
    )


@pytest.mark.asyncio
async def test_server_cancel_propagates_provider_exception():
    """If the provider's cancel() raises, ProviderServicer.Cancel must propagate it."""
    from pulumi.provider.provider import Provider
    from pulumi.provider.server import ProviderServicer

    class FailingProvider(Provider):
        def __init__(self) -> None:
            super().__init__(version="0.0.1")

        def cancel(self) -> None:
            raise RuntimeError("cancel boom")

    prov = FailingProvider()
    servicer = ProviderServicer(provider=prov, args=[], engine_address="127.0.0.1:0")

    with pytest.raises(RuntimeError, match="cancel boom"):
        await servicer.Cancel(None, _MockGrpcContext())


@pytest.mark.asyncio
async def test_experimental_server_cancel_invokes_async_provider_cancel():
    """experimental ProviderServicer.Cancel must await provider.cancel() and return Empty."""
    from google.protobuf import empty_pb2
    from pulumi.provider.experimental.provider import Provider as ExpProvider
    from pulumi.provider.experimental.server import ProviderServicer as ExpProviderServicer

    class TrackingProvider(ExpProvider):
        def __init__(self) -> None:
            self.cancel_calls = 0
            self.was_awaited = False

        async def cancel(self) -> None:
            await asyncio.sleep(0)
            self.cancel_calls += 1
            self.was_awaited = True

    prov = TrackingProvider()
    servicer = ExpProviderServicer(
        args=[], version="0.0.1", provider=prov, engine_address="127.0.0.1:0"
    )

    response = await servicer.Cancel(None, _MockGrpcContext())

    assert prov.cancel_calls == 1
    assert prov.was_awaited, (
        "experimental Cancel must await provider.cancel() rather than scheduling it"
    )
    assert isinstance(response, empty_pb2.Empty)


@pytest.mark.asyncio
async def test_experimental_server_cancel_propagates_provider_exception():
    """If the async provider's cancel raises, the experimental servicer must propagate it."""
    from pulumi.provider.experimental.provider import Provider as ExpProvider
    from pulumi.provider.experimental.server import ProviderServicer as ExpProviderServicer

    class FailingProvider(ExpProvider):
        async def cancel(self) -> None:
            raise ValueError("async cancel boom")

    prov = FailingProvider()
    servicer = ExpProviderServicer(
        args=[], version="0.0.1", provider=prov, engine_address="127.0.0.1:0"
    )

    with pytest.raises(ValueError, match="async cancel boom"):
        await servicer.Cancel(None, _MockGrpcContext())


# --- pass-to-pass: existing repo tests must still pass ----------------------


def test_repo_provider_test_server_passes():
    """The existing sdk/python provider test suite must still pass."""
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "sdk/python/lib/test/provider/test_server.py",
            "-q",
            "--tb=line",
            "-p", "no:cacheprovider",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"existing provider test_server.py failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_repo_experimental_provider_tests_pass():
    """The existing experimental provider test suite must still pass."""
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "sdk/python/lib/test/provider/experimental/test_provider.py",
            "-q",
            "--tb=line",
            "-p", "no:cacheprovider",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"existing experimental test_provider.py failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
