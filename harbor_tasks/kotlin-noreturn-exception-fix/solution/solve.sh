#!/bin/bash
set -e

cd /workspace/kotlin

# Fix 1: Update Exceptions.h
sed -i 's/void HandleCurrentExceptionWhenLeavingKotlinCode();/void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode();/' \
    kotlin-native/runtime/src/main/cpp/Exceptions.h

# Fix 2: Update Exceptions.cpp
sed -i 's/void HandleCurrentExceptionWhenLeavingKotlinCode() {/void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode() {/' \
    kotlin-native/runtime/src/main/cpp/Exceptions.cpp

# Fix 3: Update CAdapterApiExporter.kt
sed -i 's/void HandleCurrentExceptionWhenLeavingKotlinCode();/void HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN;/' \
    kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/cexport/CAdapterApiExporter.kt

echo "Gold patch applied successfully"
