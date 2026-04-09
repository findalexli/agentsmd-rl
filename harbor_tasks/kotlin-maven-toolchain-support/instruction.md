# Add Maven Toolchain Support to kotlin-maven-plugin

The `K2JVMCompileMojo` in the kotlin-maven-plugin needs to support [Maven Toolchains](https://maven.apache.org/guides/mini/guide-using-toolchains.html) for specifying the JDK to use for compilation.

## Problem

Currently, the plugin only supports specifying a JDK via the `jdkHome` parameter. Users want to use Maven Toolchains to automatically select the appropriate JDK based on version requirements.

## Required Changes

Modify `libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java` to:

1. **Add ToolchainManager dependency**: Add a `ToolchainManager` field injected with `@Component` annotation

2. **Add jdkToolchain parameter**: Add a `Map<String, String>` parameter to configure toolchain selection

3. **Implement getToolchain() method**: Query toolchains using:
   - First check if `jdkToolchain` parameter is set and use `toolchainManager.getToolchains(session, "jdk", jdkToolchain)`
   - Fallback to `toolchainManager.getToolchainFromBuildContext("jdk", session)`

4. **Implement getToolchainJdkHome() method**: Extract JDK home from a Toolchain:
   - Use `toolchain.findTool("javac")` to get the javac path
   - Traverse from javac location (in `bin/`) up to the JDK root
   - Return `null` if toolchain or javac is not found

5. **Update configureSpecificCompilerArguments()**: Modify the JDK home logic:
   - Call `getToolchainJdkHome()` to get toolchain-based JDK
   - If `jdkHome` is explicitly set, it takes precedence and logs: "Toolchains are ignored, overwritten by 'jdkHome' parameter" (warning) and "Overriding JDK home path with: {jdkHome}" (info)
   - If `jdkHome` is not set but toolchain JDK is available, use it and log: "Overriding JDK home path with toolchain JDK: {toolchainJdkHome}"

## Design Notes

- Toolchain retrieval: The `Toolchain` interface doesn't expose JDK home directly, so derive it from the `javac` tool path
- Precedence: `jdkHome` parameter > Toolchain > JAVA_HOME (default)
- The implementation should mirror the approach used in maven-compiler-plugin

## Testing

After implementation:
- The code should compile with `mvn compile`
- The logic should correctly handle all three precedence cases
