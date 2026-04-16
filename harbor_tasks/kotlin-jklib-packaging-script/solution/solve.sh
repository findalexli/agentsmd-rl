#!/bin/bash
set -e

cd /workspace/kotlin

# Idempotency check: if the distinctive line already exists, skip
if grep -q "jklib-compiler.jar" prepare/jklib-compiler/build.gradle.kts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Create the directory and build.gradle.kts file
mkdir -p prepare/jklib-compiler
cat > prepare/jklib-compiler/build.gradle.kts << 'PATCH'
/*
 * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
 * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
 */

description = "JKlib Classes packaging script"

/*
 * Merges :compiler:ir.serialization.jklib and :compiler:cli-jklib jars into jklib-classes.jar
 *  and syncs the dist/jklib directory with the merged jar and license files
 *  runtimeClasspath from kotlinc's dist for jklib-classes.jar: kotlin-compiler.jar, kotlin-stdlib.jar and kotlin-reflect.jar
 */

plugins {
    kotlin("jvm")
}

val buildNumber by configurations.creating
val distContent by configurations.creating

dependencies {
    distContent(project(":compiler:cli-jklib")) { isTransitive = false }
    distContent(project(":compiler:ir.serialization.jklib")) { isTransitive = false }

    buildNumber(project(":prepare:build.version", configuration = "buildVersion"))
}

val jar by tasks.named<Jar>("jar") {
    archiveFileName.set("jklib-compiler.jar")
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE

    dependsOn(distContent)
    from({ distContent.map { zipTree(it) } })

    manifest {
        attributes(
            "Class-Path" to "kotlin-compiler.jar kotlin-stdlib.jar kotlin-reflect.jar",
            "Main-Class" to "org.jetbrains.kotlin.cli.jklib.K2JKlibCompiler"
        )
    }
}

val dist by tasks.registering(Sync::class) {
    val distDir = rootProject.layout.projectDirectory.dir("dist")
    val licenseDir = rootProject.layout.projectDirectory.dir("license")

    destinationDir = distDir.dir("jklib").asFile
    duplicatesStrategy = DuplicatesStrategy.FAIL

    from(buildNumber)

    into("license") {
        from(licenseDir)
    }

    into("lib") {
        from(jar)
        filePermissions {
            unix("rw-r--r--")
        }
    }
}
PATCH

# Update settings.gradle - add include and projectDir mapping
# First check if we already have the include statement
if ! grep -q ':kotlin-jklib-compiler' settings.gradle; then
    # Add include line after :prepare:kotlin-compiler-internal-test-framework
    sed -i 's/":prepare:kotlin-compiler-internal-test-framework",/":prepare:kotlin-compiler-internal-test-framework",\n        ":kotlin-jklib-compiler",/' settings.gradle

    # Add projectDir line after :kotlin-compiler projectDir
    sed -i "s|project(':kotlin-compiler').projectDir = \"\$rootDir/prepare/compiler\" as File|project(':kotlin-compiler').projectDir = \"\$rootDir/prepare/compiler\" as File\nproject(':kotlin-jklib-compiler').projectDir = \"\$rootDir/prepare/jklib-compiler\" as File|" settings.gradle
fi

echo "Patch applied successfully"
