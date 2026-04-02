"""
Task: slime-httpx-disable-system-proxy
Repo: THUDM/slime @ e46e660059b5f2ae949ad812c7d49af823f415a3
PR:   1714

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import sys
import types
from pathlib import Path

TARGET = Path("/workspace/slime/slime/utils/http_utils.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def _make_args(num_gpus, concurrency, gpus_per_engine=1, distributed=False):
    return types.SimpleNamespace(
        rollout_num_gpus=num_gpus,
        sglang_server_concurrency=concurrency,
        rollout_num_gpus_per_engine=gpus_per_engine,
        use_distributed_post=distributed,
    )


def _get_fresh_client(mod, args):
    """Reset global and create a fresh client via init_http_client."""
    mod._http_client = None
    mod.init_http_client(args)
    return mod._http_client


# [pr_diff] fail_to_pass
def test_init_client_trust_env_disabled():
    """init_http_client creates AsyncClient with trust_env=False across varied configs."""
    import httpx

    os.environ["HTTP_PROXY"] = "http://fake-proxy:8080"
    os.environ["HTTPS_PROXY"] = "http://fake-proxy:8080"

    sys.path.insert(0, "/workspace/slime")
    import slime.utils.http_utils as mod

    # Test with three different arg configurations to prevent hardcoding
    configs = [
        _make_args(num_gpus=2, concurrency=10),
        _make_args(num_gpus=4, concurrency=8, gpus_per_engine=2),
        _make_args(num_gpus=1, concurrency=32),
    ]
    for args in configs:
        client = _get_fresh_client(mod, args)
        assert isinstance(client, httpx.AsyncClient), "Must create an AsyncClient"
        assert not client._trust_env, (
            f"Client must have trust_env=False (args: gpus={args.rollout_num_gpus}, "
            f"concurrency={args.sglang_server_concurrency})"
        )


# [pr_diff] fail_to_pass
def test_init_client_proxy_not_mounted():
    """With proxy env vars set, init_http_client must not mount proxy transports."""
    import httpx

    os.environ["HTTP_PROXY"] = "http://fake-proxy:9090"
    os.environ["HTTPS_PROXY"] = "http://fake-proxy:9090"

    sys.path.insert(0, "/workspace/slime")
    import slime.utils.http_utils as mod

    client = _get_fresh_client(mod, _make_args(num_gpus=2, concurrency=16))

    # When trust_env=True and proxy vars are set, httpx adds proxy mounts
    # to client._mounts. With trust_env=False, _mounts is empty.
    assert len(client._mounts) == 0, (
        f"Client should not have proxy mounts (found {len(client._mounts)} mounts). "
        "Set trust_env=False to prevent httpx from reading proxy env vars."
    )


# [pr_diff] fail_to_pass
def test_ray_actor_trust_env_disabled():
    """_HttpPosterActor creates AsyncClient with trust_env=False.

    The actor class is nested inside _init_ray_distributed_post and decorated
    with @ray.remote, so direct instantiation requires a Ray cluster.
    # AST-only because: class is nested in a function and requires Ray runtime
    """
    source = TARGET.read_text()
    tree = ast.parse(source)

    # Locate _init_ray_distributed_post → _HttpPosterActor
    actor_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_init_ray_distributed_post":
            for child in ast.walk(node):
                if isinstance(child, ast.ClassDef) and "HttpPoster" in child.name:
                    actor_class = child
                    break
            break

    assert actor_class is not None, "_HttpPosterActor class not found in _init_ray_distributed_post"

    # Find __init__ → httpx.AsyncClient(...) call → trust_env=False keyword
    found_trust_env_false = False
    for method in ast.iter_child_nodes(actor_class):
        if isinstance(method, ast.FunctionDef) and method.name == "__init__":
            for call_node in ast.walk(method):
                if not isinstance(call_node, ast.Call):
                    continue
                func = call_node.func
                is_async_client = (
                    (isinstance(func, ast.Attribute) and func.attr == "AsyncClient")
                    or (isinstance(func, ast.Name) and func.id == "AsyncClient")
                )
                if is_async_client:
                    for kw in call_node.keywords:
                        if (
                            kw.arg == "trust_env"
                            and isinstance(kw.value, ast.Constant)
                            and kw.value.value is False
                        ):
                            found_trust_env_false = True

    assert found_trust_env_false, (
        "_HttpPosterActor.__init__ must create AsyncClient with trust_env=False"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_init_client_preserves_config():
    """init_http_client creates AsyncClient with connection limits and timeout."""
    import httpx

    sys.path.insert(0, "/workspace/slime")
    import slime.utils.http_utils as mod

    # Test with multiple configs to verify limits scale with args
    for num_gpus, concurrency, gpus_per_engine in [(4, 8, 2), (2, 16, 1), (8, 4, 4)]:
        args = _make_args(num_gpus, concurrency, gpus_per_engine)
        client = _get_fresh_client(mod, args)
        assert isinstance(client, httpx.AsyncClient), "Must create an AsyncClient"
        pool = client._transport._pool
        assert pool._max_connections > 1, (
            f"Client must configure connection limits "
            f"(gpus={num_gpus}, concurrency={concurrency})"
        )
