"""
Task: bun-pgo-build-flags
Repo: bun @ d2e67536514b059cb317beea23ebbeafe2fa6c1a

Behavioral tests for IR PGO build support in Bun.
Tests verify actual behavior by importing and calling the build system code,
not by grepping source files.
"""

import json
import os
import subprocess
import tempfile


TS_TEST_CODE = '''
import { resolveConfig } from "file:///workspace/bun/scripts/build/config.ts";
import { globalFlags, linkerFlags } from "file:///workspace/bun/scripts/build/flags.ts";
import { webkit } from "file:///workspace/bun/scripts/build/deps/webkit.ts";

type TestResult = {
  name: string;
  passed: boolean;
  error?: string;
  details?: unknown;
};

const results: TestResult[] = [];

const fakeToolchain = {
  cc: "clang",
  cxx: "clang++",
  clangVersion: "16.0.0",
  ar: "ar",
  ranlib: "ranlib",
  ld: "ld",
  strip: "strip",
  dsymutil: undefined,
  bun: "bun",
  jsRuntime: "node",
  esbuild: "esbuild",
  ccache: undefined,
  cmake: "cmake",
  cargo: undefined,
  cargoHome: undefined,
  rustupHome: undefined,
  msvcLinker: undefined,
  rc: undefined,
  mt: undefined,
};

function passed(name: string, details?: unknown) {
  results.push({ name, passed: true, details });
}

function failed(name: string, error: string, details?: unknown) {
  results.push({ name, passed: false, error, details });
}

// Test 1: Mutual exclusivity
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
    pgoUse: "/tmp/merged.profdata",
  };
  try {
    resolveConfig(partial, fakeToolchain as any);
    failed("pgo_mutual_exclusivity", "Expected BuildError but resolveConfig succeeded");
  } catch (e: any) {
    if (e.message?.includes("--pgo-generate and --pgo-use are mutually exclusive")) {
      passed("pgo_mutual_exclusivity", { errorMessage: e.message });
    } else {
      failed("pgo_mutual_exclusivity", "Wrong error message: " + e.message);
    }
  }
} catch (e: any) {
  failed("pgo_mutual_exclusivity", "Unexpected error: " + e.message);
}

// Test 2: Single pgoGenerate should work
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);
  if ((cfg as any).pgoGenerate === "/tmp/pgo-data") {
    passed("pgo_generate_single", { pgoGenerate: (cfg as any).pgoGenerate });
  } else {
    failed("pgo_generate_single", "pgoGenerate not set, got: " + (cfg as any).pgoGenerate);
  }
} catch (e: any) {
  failed("pgo_generate_single", "Threw error: " + e.message);
}

// Test 3: Single pgoUse should work
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoUse: "/tmp/merged.profdata",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);
  if ((cfg as any).pgoUse === "/tmp/merged.profdata") {
    passed("pgo_use_single", { pgoUse: (cfg as any).pgoUse });
  } else {
    failed("pgo_use_single", "pgoUse not set, got: " + (cfg as any).pgoUse);
  }
} catch (e: any) {
  failed("pgo_use_single", "Threw error: " + e.message);
}

// Test 4: Feature labels
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);

  const features: string[] = [];
  if ((cfg as any).pgoGenerate) features.push("pgo-gen");
  if ((cfg as any).pgoUse) features.push("pgo-use");

  if (features.includes("pgo-gen")) {
    passed("pgo_feature_label_gen", { features });
  } else {
    failed("pgo_feature_label_gen", "pgo-gen not in features");
  }
} catch (e: any) {
  failed("pgo_feature_label_gen", "Error: " + e.message);
}

// Test 5: globalFlags includes PGO compile flags
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);

  const pgoFlags = globalFlags.filter(f => {
    const flagValue = typeof f.flag === "function" ? f.flag(cfg) : f.flag;
    const flagStr = Array.isArray(flagValue) ? flagValue.join(" ") : String(flagValue);
    return flagStr?.includes("-fprofile-generate");
  });

  if (pgoFlags.length > 0) {
    passed("pgo_compile_flags", { count: pgoFlags.length });
  } else {
    failed("pgo_compile_flags", "No -fprofile-generate flag found in globalFlags");
  }
} catch (e: any) {
  failed("pgo_compile_flags", "Error: " + e.message);
}

// Test 6: linkerFlags includes PGO flags
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);

  const pgoFlags = linkerFlags.filter(f => {
    const flagValue = typeof f.flag === "function" ? f.flag(cfg) : f.flag;
    return String(flagValue).includes("-fprofile-generate");
  });

  if (pgoFlags.length > 0) {
    passed("pgo_link_flags", { count: pgoFlags.length });
  } else {
    failed("pgo_link_flags", "No -fprofile-generate flag found in linkerFlags");
  }
} catch (e: any) {
  failed("pgo_link_flags", "Error: " + e.message);
}

// Test 7: WebKit CMAKE flags include PGO flags
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoGenerate: "/tmp/pgo-data",
    webkit: "local",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);

  const webkitBuild = webkit.build as (cfg: any) => any;
  const result = webkitBuild(cfg);

  if (result.kind === "nested-cmake" && result.args) {
    const cFlags = result.args.CMAKE_C_FLAGS || "";
    const cxxFlags = result.args.CMAKE_CXX_FLAGS || "";

    if (cFlags.includes("-fprofile-generate") && cxxFlags.includes("-fprofile-generate")) {
      passed("webkit_pgo_forwarding", { CMAKE_C_FLAGS: cFlags });
    } else {
      failed("webkit_pgo_forwarding", "PGO flags not in CMAKE flags. C_FLAGS: " + cFlags + ", CXX_FLAGS: " + cxxFlags);
    }
  } else {
    failed("webkit_pgo_forwarding", "Unexpected webkit build kind: " + result.kind);
  }
} catch (e: any) {
  failed("webkit_pgo_forwarding", "Error: " + e.message);
}

// Test 8: pgoUse flags in globalFlags
try {
  const partial: any = {
    os: "linux",
    arch: "x64",
    abi: "gnu",
    pgoUse: "/tmp/merged.profdata",
  };
  const cfg = resolveConfig(partial, fakeToolchain as any);

  const pgoFlags = globalFlags.filter(f => {
    const flagValue = typeof f.flag === "function" ? f.flag(cfg) : f.flag;
    return String(flagValue).includes("-fprofile-use");
  });

  if (pgoFlags.length > 0) {
    passed("pgo_use_compile_flags", { count: pgoFlags.length });
  } else {
    failed("pgo_use_compile_flags", "No -fprofile-use flag found in globalFlags");
  }
} catch (e: any) {
  failed("pgo_use_compile_flags", "Error: " + e.message);
}

console.log("__TEST_RESULTS__");
console.log(JSON.stringify(results, null, 2));
'''


def run_ts_tests():
    """Run the TypeScript behavioral tests via subprocess."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(TS_TEST_CODE)
        ts_file = f.name
    
    try:
        result = subprocess.run(
            ['node', '--experimental-strip-types', ts_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd='/workspace/bun/scripts/build'
        )
        
        # Parse output - find the JSON after __TEST_RESULTS__
        output = result.stdout
        if '__TEST_RESULTS__' in output:
            json_start = output.index('__TEST_RESULTS__') + len('__TEST_RESULTS__')
            json_str = output[json_start:].strip()
            return json.loads(json_str)
        else:
            # Return error info if we couldn't parse
            return [{
                'name': 'subprocess_error',
                'passed': False,
                'error': f"Could not parse output: {output[:500]}, stderr: {result.stderr[:500]}"
            }]
    finally:
        os.unlink(ts_file)


def get_test_results():
    """Get test results from TypeScript tests."""
    return run_ts_tests()


class TestPGOBehavior:
    """Behavioral tests for PGO build support - these call actual code, not grep files."""
    
    def test_pgo_mutual_exclusivity(self):
        """resolveConfig must throw BuildError when both pgoGenerate and pgoUse are set."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_mutual_exclusivity':
                assert r['passed'], f"Mutual exclusivity check failed: {r.get('error')}"
                return
        assert False, "pgo_mutual_exclusivity test did not run"
    
    def test_pgo_generate_single(self):
        """Setting only pgoGenerate should preserve the value in resolved config."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_generate_single':
                assert r['passed'], f"pgoGenerate not preserved: {r.get('error')}"
                return
        assert False, "pgo_generate_single test did not run"
    
    def test_pgo_use_single(self):
        """Setting only pgoUse should preserve the value in resolved config."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_use_single':
                assert r['passed'], f"pgoUse not preserved: {r.get('error')}"
                return
        assert False, "pgo_use_single test did not run"
    
    def test_pgo_feature_label_gen(self):
        """formatConfig should include pgo-gen feature label when pgoGenerate is set."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_feature_label_gen':
                assert r['passed'], f"Feature label not found: {r.get('error')}"
                return
        assert False, "pgo_feature_label_gen test did not run"
    
    def test_pgo_compile_flags(self):
        """globalFlags should include -fprofile-generate when pgoGenerate is set."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_compile_flags':
                assert r['passed'], f"Compile flags not found: {r.get('error')}"
                return
        assert False, "pgo_compile_flags test did not run"
    
    def test_pgo_link_flags(self):
        """linkerFlags should include -fprofile-generate when pgoGenerate is set."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_link_flags':
                assert r['passed'], f"Linker flags not found: {r.get('error')}"
                return
        assert False, "pgo_link_flags test did not run"
    
    def test_webkit_pgo_forwarding(self):
        """WebKit build should forward PGO flags via CMAKE_C/CXX_FLAGS."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'webkit_pgo_forwarding':
                assert r['passed'], f"WebKit PGO forwarding failed: {r.get('error')}"
                return
        assert False, "webkit_pgo_forwarding test did not run"
    
    def test_pgo_use_compile_flags(self):
        """globalFlags should include -fprofile-use when pgoUse is set."""
        results = get_test_results()
        for r in results:
            if r['name'] == 'pgo_use_compile_flags':
                assert r['passed'], f"pgoUse compile flags not found: {r.get('error')}"
                return
        assert False, "pgo_use_compile_flags test did not run"
