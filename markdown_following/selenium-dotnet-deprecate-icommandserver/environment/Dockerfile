# syntax=docker/dockerfile:1.4
FROM mcr.microsoft.com/dotnet/sdk:8.0

# System tools for tests + git for cloning
RUN apt-get update && \
    apt-get install -y --no-install-recommends git python3 python3-pip ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

# Clone Selenium at the base commit. We use --filter=blob:none to avoid pulling
# the full git history; the agent only needs the working tree at the base SHA.
ARG REPO_URL=https://github.com/SeleniumHQ/selenium.git
ARG BASE_COMMIT=77f325f198b2d660b8bba483623fe9770a08f77a

RUN git clone --filter=blob:none --no-checkout ${REPO_URL} /workspace/selenium && \
    cd /workspace/selenium && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/selenium

# A standalone "reflcheck" console app. Selenium's full WebDriver build is
# Bazel-driven (it generates CDP bindings + resource utilities at build time),
# so we cannot do `dotnet build` on the WebDriver csproj inside this image
# without installing Bazel (heavyweight). Instead, we use Roslyn to:
#   - Compile ICommandServer.cs in isolation (it only depends on IDisposable)
#     and reflect on the resulting assembly to verify the [Obsolete] attribute.
#   - Parse DriverService.cs syntactically to verify its base/inheritance list.
RUN mkdir -p /workspace/reflcheck
COPY <<'EOF' /workspace/reflcheck/Reflcheck.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <RootNamespace>Reflcheck</RootNamespace>
    <Nullable>enable</Nullable>
    <LangVersion>12.0</LangVersion>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" />
  </ItemGroup>
</Project>
EOF

COPY <<'EOF' /workspace/reflcheck/Program.cs
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

internal static class Program
{
    private const string DriverServicePath = "/workspace/selenium/dotnet/src/webdriver/DriverService.cs";
    private const string ICommandServerPath = "/workspace/selenium/dotnet/src/webdriver/Remote/ICommandServer.cs";

    private static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("usage: reflcheck <check>");
            Console.Error.WriteLine("checks: parse_ok | driverservice_base | icommandserver_obsolete | icommandserver_obsolete_attr_syntax");
            return 99;
        }

        try
        {
            switch (args[0])
            {
                case "parse_ok":
                    return ParseOk();
                case "driverservice_base":
                    return DriverServiceBase();
                case "icommandserver_obsolete":
                    return ICommandServerObsoleteCompiled();
                case "icommandserver_obsolete_attr_syntax":
                    return ICommandServerObsoleteSyntax();
                default:
                    Console.Error.WriteLine($"unknown check: {args[0]}");
                    return 99;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("EXCEPTION: " + ex);
            return 100;
        }
    }

    private static SyntaxTree LoadTree(string path)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException("Source file missing", path);
        }
        return CSharpSyntaxTree.ParseText(File.ReadAllText(path), path: path);
    }

    private static int ParseOk()
    {
        // Both source files must parse without syntax errors. This is a sanity
        // p2p — independent of whether the agent's edits are correct.
        foreach (var path in new[] { DriverServicePath, ICommandServerPath })
        {
            var tree = LoadTree(path);
            var diags = tree.GetDiagnostics()
                .Where(d => d.Severity == DiagnosticSeverity.Error)
                .ToList();
            if (diags.Count > 0)
            {
                Console.Error.WriteLine($"FAIL: {path} has parse errors:");
                foreach (var d in diags) Console.Error.WriteLine("  " + d);
                return 1;
            }
        }
        Console.WriteLine("OK: both files parse cleanly");
        return 0;
    }

    private static int DriverServiceBase()
    {
        // Verify the type-system change to DriverService:
        //   - It must NOT inherit/implement ICommandServer
        //   - It must inherit/implement IDisposable (directly or via a base type)
        var tree = LoadTree(DriverServicePath);
        var root = tree.GetRoot();
        var cls = root.DescendantNodes()
            .OfType<ClassDeclarationSyntax>()
            .FirstOrDefault(c => c.Identifier.ValueText == "DriverService");
        if (cls is null)
        {
            Console.Error.WriteLine("FAIL: DriverService class declaration not found");
            return 1;
        }

        var bases = cls.BaseList?.Types
            .Select(t => t.Type.ToString().Trim())
            .ToList() ?? new System.Collections.Generic.List<string>();
        Console.WriteLine("BASES: " + string.Join(", ", bases));

        if (bases.Any(b => b == "ICommandServer" || b.EndsWith(".ICommandServer")))
        {
            Console.Error.WriteLine("FAIL: DriverService still names ICommandServer in its base list");
            return 2;
        }

        bool hasDisposable = bases.Any(b =>
            b == "IDisposable" || b.EndsWith(".IDisposable") || b == "System.IDisposable");
        if (!hasDisposable)
        {
            Console.Error.WriteLine("FAIL: DriverService does not declare IDisposable as a base/interface");
            return 3;
        }

        Console.WriteLine("OK: DriverService inherits IDisposable directly and does not name ICommandServer");
        return 0;
    }

    private static int ICommandServerObsoleteCompiled()
    {
        // Compile ICommandServer.cs in isolation (it only depends on IDisposable
        // from System.Runtime), emit it as a DLL in memory, then reflect on the
        // ICommandServer type to verify the ObsoleteAttribute is applied with a
        // non-empty message.
        //
        // The real WebDriver csproj relies on <ImplicitUsings> for `using System;`,
        // so the source file does not import System explicitly. We synthesise a
        // companion tree that does the equivalent via a `global using`.
        var tree = LoadTree(ICommandServerPath);
        var globalUsings = CSharpSyntaxTree.ParseText(
            "global using global::System;\n",
            path: "GlobalUsings.cs");
        var trustedRoot = Path.GetDirectoryName(typeof(object).Assembly.Location)!;
        var refs = new[]
        {
            MetadataReference.CreateFromFile(typeof(object).Assembly.Location),
            MetadataReference.CreateFromFile(typeof(IDisposable).Assembly.Location),
            MetadataReference.CreateFromFile(typeof(ObsoleteAttribute).Assembly.Location),
            MetadataReference.CreateFromFile(Path.Combine(trustedRoot, "System.Runtime.dll")),
        };
        var compilation = CSharpCompilation.Create(
            assemblyName: "ICmdServerProbe",
            syntaxTrees: new[] { globalUsings, tree },
            references: refs,
            options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));

        using var ms = new MemoryStream();
        var result = compilation.Emit(ms);
        if (!result.Success)
        {
            Console.Error.WriteLine("FAIL: ICommandServer.cs failed to compile in isolation:");
            foreach (var d in result.Diagnostics.Where(d => d.Severity == DiagnosticSeverity.Error))
            {
                Console.Error.WriteLine("  " + d);
            }
            return 1;
        }

        ms.Seek(0, SeekOrigin.Begin);
        var asm = Assembly.Load(ms.ToArray());
        var t = asm.GetType("OpenQA.Selenium.Remote.ICommandServer");
        if (t is null)
        {
            Console.Error.WriteLine("FAIL: ICommandServer type not found in compiled assembly");
            return 2;
        }
        var ob = t.GetCustomAttribute<ObsoleteAttribute>(inherit: false);
        if (ob is null)
        {
            Console.Error.WriteLine("FAIL: ICommandServer does not carry [Obsolete]");
            return 3;
        }
        if (string.IsNullOrWhiteSpace(ob.Message))
        {
            Console.Error.WriteLine("FAIL: [Obsolete] message is empty");
            return 4;
        }
        Console.WriteLine("OK: ICommandServer is [Obsolete] with message: " + ob.Message);
        return 0;
    }

    private static int ICommandServerObsoleteSyntax()
    {
        // Cross-check the [Obsolete] attribute syntactically. This is
        // independent of compilation — it runs even if some symbol it
        // references is unavailable.
        var tree = LoadTree(ICommandServerPath);
        var iface = tree.GetRoot().DescendantNodes()
            .OfType<InterfaceDeclarationSyntax>()
            .FirstOrDefault(i => i.Identifier.ValueText == "ICommandServer");
        if (iface is null)
        {
            Console.Error.WriteLine("FAIL: ICommandServer interface declaration not found");
            return 1;
        }
        var attrNames = iface.AttributeLists
            .SelectMany(al => al.Attributes)
            .Select(a => a.Name.ToString())
            .ToList();
        Console.WriteLine("ATTRS: " + string.Join(", ", attrNames));
        if (!attrNames.Any(n => n == "Obsolete" || n == "ObsoleteAttribute" || n.EndsWith(".Obsolete") || n.EndsWith(".ObsoleteAttribute")))
        {
            Console.Error.WriteLine("FAIL: ICommandServer is not annotated with [Obsolete] in source");
            return 2;
        }
        Console.WriteLine("OK: ICommandServer carries an [Obsolete] attribute in source");
        return 0;
    }
}
EOF

# Pre-restore Roslyn packages so the test runs offline.
RUN cd /workspace/reflcheck && dotnet restore --verbosity quiet && \
    dotnet build -c Release --no-restore --verbosity quiet

RUN mkdir -p /logs/verifier
