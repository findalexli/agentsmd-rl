"""Verifier tests for the dotnet/efcore RemoveExtension / WithoutExtension /
RemoveDbContext API additions (PR #37891).

These tests inject a self-contained xUnit test class into the EFCore.Tests
project and then run `dotnet test`. Each pytest test asserts that a specific
xUnit test passed.

If the agent has not implemented the new public APIs, the verifier file fails
to compile and every pytest test fails with a build error (this is the
fail-to-pass behavior at base commit).
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path("/workspace/efcore")
TEST_PROJECT = REPO / "test/EFCore.Tests/EFCore.Tests.csproj"
VERIFIER_DEST = REPO / "test/EFCore.Tests/Verifier_RemoveProviderConfig.cs"
TRX_DIR = Path("/tmp/trx")
TRX_FILE = TRX_DIR / "verifier.trx"
FILTER = "FullyQualifiedName~Microsoft.EntityFrameworkCore.RemoveProviderConfigVerifier"

VERIFIER_CSHARP = r'''// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.

using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.InMemory.Infrastructure.Internal;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace Microsoft.EntityFrameworkCore.RemoveProviderConfigVerifier;

public class Verifier_RemoveProviderConfig
{
    private static IDbContextOptionsBuilderInfrastructure Infra(DbContextOptionsBuilder b) => b;

    public class FakeExtA : IDbContextOptionsExtension
    {
        private DbContextOptionsExtensionInfo _info;
        public DbContextOptionsExtensionInfo Info => _info ??= new ExtInfo(this);
        public void ApplyServices(IServiceCollection services) { }
        public void Validate(IDbContextOptions options) { }

        private sealed class ExtInfo(IDbContextOptionsExtension e) : DbContextOptionsExtensionInfo(e)
        {
            public override bool IsDatabaseProvider => false;
            public override int GetServiceProviderHashCode() => 0;
            public override bool ShouldUseSameServiceProvider(DbContextOptionsExtensionInfo other) => true;
            public override string LogFragment => "";
            public override void PopulateDebugInfo(IDictionary<string, string> debugInfo) { }
        }
    }

    public class FakeExtB : IDbContextOptionsExtension
    {
        private DbContextOptionsExtensionInfo _info;
        public DbContextOptionsExtensionInfo Info => _info ??= new ExtInfo(this);
        public void ApplyServices(IServiceCollection services) { }
        public void Validate(IDbContextOptions options) { }

        private sealed class ExtInfo(IDbContextOptionsExtension e) : DbContextOptionsExtensionInfo(e)
        {
            public override bool IsDatabaseProvider => false;
            public override int GetServiceProviderHashCode() => 0;
            public override bool ShouldUseSameServiceProvider(DbContextOptionsExtensionInfo other) => true;
            public override string LogFragment => "";
            public override void PopulateDebugInfo(IDictionary<string, string> debugInfo) { }
        }
    }

    public class FakeExtC : IDbContextOptionsExtension
    {
        private DbContextOptionsExtensionInfo _info;
        public DbContextOptionsExtensionInfo Info => _info ??= new ExtInfo(this);
        public void ApplyServices(IServiceCollection services) { }
        public void Validate(IDbContextOptions options) { }

        private sealed class ExtInfo(IDbContextOptionsExtension e) : DbContextOptionsExtensionInfo(e)
        {
            public override bool IsDatabaseProvider => false;
            public override int GetServiceProviderHashCode() => 0;
            public override bool ShouldUseSameServiceProvider(DbContextOptionsExtensionInfo other) => true;
            public override string LogFragment => "";
            public override void PopulateDebugInfo(IDictionary<string, string> debugInfo) { }
        }
    }

    public class CtxA : DbContext
    {
        public CtxA(DbContextOptions<CtxA> options) : base(options) { }
    }

    public class CtxB : DbContext
    {
        public CtxB(DbContextOptions<CtxB> options) : base(options) { }
    }

    [Fact]
    public void RemoveExtension_removes_extension_from_builder()
    {
        var builder = new DbContextOptionsBuilder();
        var ext = new FakeExtA();

        Infra(builder).AddOrUpdateExtension(ext);
        Assert.Same(ext, builder.Options.FindExtension<FakeExtA>());

        Infra(builder).RemoveExtension<FakeExtA>();

        Assert.Null(builder.Options.FindExtension<FakeExtA>());
        Assert.DoesNotContain(builder.Options.Extensions, e => e is FakeExtA);
    }

    [Fact]
    public void RemoveExtension_keeps_other_extensions()
    {
        var builder = new DbContextOptionsBuilder();
        var a = new FakeExtA();
        var b = new FakeExtB();

        Infra(builder).AddOrUpdateExtension(a);
        Infra(builder).AddOrUpdateExtension(b);

        Infra(builder).RemoveExtension<FakeExtA>();

        Assert.Null(builder.Options.FindExtension<FakeExtA>());
        Assert.Same(b, builder.Options.FindExtension<FakeExtB>());
        Assert.Single(builder.Options.Extensions);
    }

    [Fact]
    public void RemoveExtension_no_op_when_extension_absent()
    {
        var builder = new DbContextOptionsBuilder();
        var a = new FakeExtA();

        Infra(builder).AddOrUpdateExtension(a);

        Infra(builder).RemoveExtension<FakeExtB>();

        Assert.Single(builder.Options.Extensions);
        Assert.Same(a, builder.Options.FindExtension<FakeExtA>());
    }

    [Fact]
    public void WithoutExtension_returns_same_instance_when_extension_absent()
    {
        var options = new DbContextOptions<CtxA>();
        var result = options.WithoutExtension<FakeExtA>();
        Assert.Same(options, result);
    }

    [Fact]
    public void WithoutExtension_returns_new_instance_with_extension_removed()
    {
        var builder = new DbContextOptionsBuilder<CtxA>();
        Infra(builder).AddOrUpdateExtension(new FakeExtA());

        var options = builder.Options;
        Assert.NotNull(options.FindExtension<FakeExtA>());

        var result = options.WithoutExtension<FakeExtA>();

        Assert.NotSame(options, result);
        Assert.Null(result.FindExtension<FakeExtA>());
    }

    [Fact]
    public void WithoutExtension_preserves_other_extensions_and_renormalizes_ordinals()
    {
        var builder = new DbContextOptionsBuilder<CtxA>();
        Infra(builder).AddOrUpdateExtension(new FakeExtA());
        Infra(builder).AddOrUpdateExtension(new FakeExtB());
        Infra(builder).AddOrUpdateExtension(new FakeExtC());

        var afterRemove = builder.Options.WithoutExtension<FakeExtB>();

        Assert.Null(afterRemove.FindExtension<FakeExtB>());
        Assert.NotNull(afterRemove.FindExtension<FakeExtA>());
        Assert.NotNull(afterRemove.FindExtension<FakeExtC>());

        var enumerated = afterRemove.Extensions.ToList();
        Assert.Equal(2, enumerated.Count);
        Assert.IsType<FakeExtA>(enumerated[0]);
        Assert.IsType<FakeExtC>(enumerated[1]);

        var newB = new FakeExtB();
        var afterAdd = afterRemove.WithExtension(newB);
        var afterAddList = afterAdd.Extensions.ToList();
        Assert.Equal(3, afterAddList.Count);
        Assert.IsType<FakeExtA>(afterAddList[0]);
        Assert.IsType<FakeExtC>(afterAddList[1]);
        Assert.Same(newB, afterAddList[2]);
    }

    [Fact]
    public void RemoveDbContext_removes_context_and_typed_options_registrations()
    {
        var sc = new ServiceCollection();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("a-db"));

        Assert.Contains(sc, d => d.ServiceType == typeof(CtxA));
        Assert.Contains(sc, d => d.ServiceType == typeof(DbContextOptions<CtxA>));
        Assert.Contains(sc, d => d.ServiceType == typeof(IDbContextOptionsConfiguration<CtxA>));

        sc.RemoveDbContext<CtxA>();

        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(CtxA));
        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(DbContextOptions<CtxA>));
        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(IDbContextOptionsConfiguration<CtxA>));
    }

    [Fact]
    public void RemoveDbContext_does_not_remove_unrelated_context()
    {
        var sc = new ServiceCollection();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("a-db"));
        sc.AddDbContext<CtxB>(b => b.UseInMemoryDatabase("b-db"));

        sc.RemoveDbContext<CtxA>();

        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(CtxA));
        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(DbContextOptions<CtxA>));
        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(IDbContextOptionsConfiguration<CtxA>));

        Assert.Contains(sc, d => d.ServiceType == typeof(CtxB));
        Assert.Contains(sc, d => d.ServiceType == typeof(DbContextOptions<CtxB>));
        Assert.Contains(sc, d => d.ServiceType == typeof(IDbContextOptionsConfiguration<CtxB>));
    }

    [Fact]
    public void RemoveDbContext_with_removeConfigurationOnly_keeps_context_and_typed_options()
    {
        var sc = new ServiceCollection();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("a-db"));

        sc.RemoveDbContext<CtxA>(removeConfigurationOnly: true);

        Assert.Contains(sc, d => d.ServiceType == typeof(CtxA));
        Assert.Contains(sc, d => d.ServiceType == typeof(DbContextOptions<CtxA>));
        Assert.DoesNotContain(sc, d => d.ServiceType == typeof(IDbContextOptionsConfiguration<CtxA>));
    }

    [Fact]
    public void RemoveDbContext_then_re_register_uses_new_provider_configuration()
    {
        var sc = new ServiceCollection();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("OriginalDb"));
        sc.RemoveDbContext<CtxA>();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("ReplacementDb"));

        var sp = sc.BuildServiceProvider(validateScopes: true);
        using var scope = sp.GetRequiredService<IServiceScopeFactory>().CreateScope();
        var ctx = scope.ServiceProvider.GetRequiredService<CtxA>();

        var inMem = ctx.GetService<IDbContextOptions>().FindExtension<InMemoryOptionsExtension>();
        Assert.NotNull(inMem);
        Assert.Equal("ReplacementDb", inMem.StoreName);
    }

    [Fact]
    public void RemoveDbContext_returns_same_service_collection_for_chaining()
    {
        var sc = new ServiceCollection();
        sc.AddDbContext<CtxA>(b => b.UseInMemoryDatabase("a-db"));

        var returned = sc.RemoveDbContext<CtxA>();

        Assert.Same(sc, returned);
    }
}
'''


def _run_dotnet_test() -> tuple[int, str, dict[str, str]]:
    """Build + test once, parse TRX, return (returncode, captured_output, results_by_test_name)."""
    VERIFIER_DEST.write_text(VERIFIER_CSHARP)

    TRX_DIR.mkdir(parents=True, exist_ok=True)
    if TRX_FILE.exists():
        TRX_FILE.unlink()

    proc = subprocess.run(
        [
            "dotnet", "test", str(TEST_PROJECT),
            "--filter", FILTER,
            "--logger", f"trx;LogFileName={TRX_FILE}",
            "-v", "quiet",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )

    results: dict[str, str] = {}
    if TRX_FILE.exists():
        ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
        tree = ET.parse(TRX_FILE)
        for r in tree.getroot().findall(".//t:UnitTestResult", ns):
            name = r.attrib.get("testName", "")
            short = name.rsplit(".", 1)[-1]
            results[short] = r.attrib.get("outcome", "")

    captured = (proc.stdout + "\n" + proc.stderr)[-4000:]
    return proc.returncode, captured, results


@pytest.fixture(scope="module")
def dotnet_results():
    rc, out, results = _run_dotnet_test()
    return {"returncode": rc, "output": out, "results": results}


def _assert_passed(dotnet_results, test_name: str):
    results = dotnet_results["results"]
    if not results:
        # No TRX produced — almost always means the build failed.
        pytest.fail(
            f"No xUnit test results produced (likely build failure). "
            f"Last output:\n{dotnet_results['output']}"
        )
    outcome = results.get(test_name)
    assert outcome == "Passed", (
        f"xUnit test '{test_name}' outcome={outcome!r}. "
        f"Available results: {sorted(results.keys())}\n"
        f"Output tail:\n{dotnet_results['output']}"
    )


# --- f2p tests for the new public APIs ---


def test_remove_extension_removes_extension_from_builder(dotnet_results):
    """IDbContextOptionsBuilderInfrastructure.RemoveExtension<T>() removes the extension."""
    _assert_passed(dotnet_results, "RemoveExtension_removes_extension_from_builder")


def test_remove_extension_keeps_other_extensions(dotnet_results):
    """RemoveExtension only removes the requested type, leaves others intact."""
    _assert_passed(dotnet_results, "RemoveExtension_keeps_other_extensions")


def test_remove_extension_no_op_when_extension_absent(dotnet_results):
    """RemoveExtension is a no-op when the extension was never added."""
    _assert_passed(dotnet_results, "RemoveExtension_no_op_when_extension_absent")


def test_without_extension_returns_same_instance_when_absent(dotnet_results):
    """DbContextOptions.WithoutExtension<T>() returns `this` when extension not present."""
    _assert_passed(dotnet_results, "WithoutExtension_returns_same_instance_when_extension_absent")


def test_without_extension_returns_new_instance_with_extension_removed(dotnet_results):
    """WithoutExtension returns a new immutable instance with the extension stripped."""
    _assert_passed(dotnet_results, "WithoutExtension_returns_new_instance_with_extension_removed")


def test_without_extension_renormalizes_ordinals(dotnet_results):
    """WithoutExtension preserves remaining extensions and renormalizes their ordinals."""
    _assert_passed(
        dotnet_results, "WithoutExtension_preserves_other_extensions_and_renormalizes_ordinals"
    )


def test_remove_dbcontext_removes_typed_options(dotnet_results):
    """RemoveDbContext<TContext>() removes the context, typed options, and configuration registrations."""
    _assert_passed(dotnet_results, "RemoveDbContext_removes_context_and_typed_options_registrations")


def test_remove_dbcontext_does_not_remove_unrelated(dotnet_results):
    """RemoveDbContext<TContext>() does not affect registrations for a different DbContext type."""
    _assert_passed(dotnet_results, "RemoveDbContext_does_not_remove_unrelated_context")


def test_remove_dbcontext_with_remove_configuration_only(dotnet_results):
    """RemoveDbContext<TContext>(removeConfigurationOnly: true) keeps the context but strips configuration."""
    _assert_passed(
        dotnet_results, "RemoveDbContext_with_removeConfigurationOnly_keeps_context_and_typed_options"
    )


def test_remove_dbcontext_then_re_register(dotnet_results):
    """After RemoveDbContext<TContext>(), AddDbContext<TContext>(...) again uses the new configuration."""
    _assert_passed(
        dotnet_results, "RemoveDbContext_then_re_register_uses_new_provider_configuration"
    )


def test_remove_dbcontext_returns_collection_for_chaining(dotnet_results):
    """RemoveDbContext returns the same IServiceCollection for fluent chaining."""
    _assert_passed(dotnet_results, "RemoveDbContext_returns_same_service_collection_for_chaining")


# --- pass-to-pass: existing src/EFCore project must still compile after agent's edits ---


def test_p2p_efcore_src_builds():
    """The repo's main `src/EFCore` project must still compile cleanly. This catches
    regressions where the agent forgets to override a newly added abstract member or
    breaks an existing public API. Independent of the verifier file injection so it
    is meaningful at base commit, after a fix, and on the gold patch alike."""
    r = subprocess.run(
        ["dotnet", "build", "src/EFCore/EFCore.csproj", "-v", "quiet"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"src/EFCore build failed (exit {r.returncode}):\n"
        f"{(r.stdout + r.stderr)[-3000:]}"
    )
