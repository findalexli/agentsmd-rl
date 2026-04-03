#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'workflowDoc.contains(fname)' .github/build.gradle 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/build.gradle b/.github/build.gradle
index 09800091ed26..6effa8742f60 100644
--- a/.github/build.gradle
+++ b/.github/build.gradle
@@ -28,6 +28,7 @@ buildscript {
 /** check that yml are valid */
 task check {
   doLast {
+    def workflowDoc = new File("${project.projectDir}/workflows/README.md").text
     List<String> errors = []
     fileTree("${project.projectDir}/workflows").matching {
       include "*.yml"
@@ -68,6 +69,11 @@ task check {
           }
         }
       }
+
+      // Make sure the workflow is listed in README.md
+      if ( fname.startsWith("beam_") && !workflowDoc.contains(fname)) {
+        errors.add("Workflow ${fname} not listed in workflows/README.md");
+      }
     }
     if (!errors.isEmpty()) {
       throw new GradleException("Check failed: " + errors.join('\n'))
diff --git a/.github/workflows/README.md b/.github/workflows/README.md
index 85440166dc88..448a9e7363a7 100644
--- a/.github/workflows/README.md
+++ b/.github/workflows/README.md
@@ -297,6 +297,13 @@ PreCommit Jobs run in a schedule and also get triggered in a PR if relevant sour
 | [ PreCommit Whitespace ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Whitespace.yml) | N/A |`Run Whitespace PreCommit`| [![.github/workflows/beam_PreCommit_Whitespace.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Whitespace.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Whitespace.yml?query=event%3Aschedule) |
 | [ PreCommit Xlang Generated Transforms ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Xlang_Generated_Transforms.yml) | N/A |`Run Xlang_Generated_Transforms PreCommit`| [![.github/workflows/beam_PreCommit_Xlang_Generated_Transforms.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Xlang_Generated_Transforms.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Xlang_Generated_Transforms.yml?query=event%3Aschedule) |
 | [ PreCommit YAML Xlang Direct ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Yaml_Xlang_Direct.yml) | N/A |`Run Yaml_Xlang_Direct PreCommit`| [![.github/workflows/beam_PreCommit_Yaml_Xlang_Direct.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Yaml_Xlang_Direct.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Yaml_Xlang_Direct.yml?query=event%3Aschedule) |
+| [ PreCommit Flink Container ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Flink_Container.yml) | N/A |`Run Flink Container PreCommit`| [![.github/workflows/beam_PreCommit_Flink_Container.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Flink_Container.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Flink_Container.yml?query=event%3Aschedule) |
+| [ PreCommit GoPrism ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_GoPrism.yml) | N/A |`Run GoPrism PreCommit`| [![.github/workflows/beam_PreCommit_GoPrism.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_GoPrism.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_GoPrism.yml?query=event%3Aschedule) |
+| [ PreCommit Integration and Load Test Framework ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_ItFramework.yml) | N/A |`Run It_Framework PreCommit`| [![.github/workflows/beam_PreCommit_ItFramework.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_ItFramework.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_ItFramework.yml?query=event%3Aschedule) |
+| [ PreCommit Java PVR Prism Loopback ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_PVR_Prism_Loopback.yml) | N/A |`Run Java_PVR_Prism_Loopback PreCommit`| [![.github/workflows/beam_PreCommit_Java_PVR_Prism_Loopback.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_PVR_Prism_Loopback.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_PVR_Prism_Loopback.yml?query=event%3Aschedule) |
+| [ PreCommit Java Solace IO Direct ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_Solace_IO_Direct.yml) | N/A |`Run Java_Solace_IO_Direct PreCommit`| [![.github/workflows/beam_PreCommit_Java_Solace_IO_Direct.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_Solace_IO_Direct.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Java_Solace_IO_Direct.yml?query=event%3Aschedule) |
+| [ PreCommit Prism Python ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Prism_Python.yml) | ['3.10', '3.13'] |`Run Prism_Python PreCommit`| [![.github/workflows/beam_PreCommit_Prism_Python.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Prism_Python.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Prism_Python.yml?query=event%3Aschedule) |
+| [ PreCommit Python Dill tests with dill deps installed ](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Python_Dill.yml) | ['3.12'] |`Run Python_Dill PreCommit`| [![.github/workflows/beam_PreCommit_Python_Dill.yml](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Python_Dill.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PreCommit_Python_Dill.yml?query=event%3Aschedule) |

 Additional PreCommit jobs running basic SDK unit test on a matrices of operating systems. These workflows were setup differently and currently do not support trigger phrases

@@ -405,6 +412,10 @@ PostCommit Jobs run in a schedule against master branch and generally do not get
 | [ PostCommit XVR Spark3 ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_XVR_Spark3.yml) | N/A |`beam_PostCommit_XVR_Spark3.json`| [![.github/workflows/beam_PostCommit_XVR_Spark3.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_XVR_Spark3.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_XVR_Spark3.yml?query=event%3Aschedule) |
 | [ PostCommit YAML Xlang Direct ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Yaml_Xlang_Direct.yml) | N/A |`beam_PostCommit_Yaml_Xlang_Direct.json`| [![.github/workflows/beam_PostCommit_Yaml_Xlang_Direct.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Yaml_Xlang_Direct.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Yaml_Xlang_Direct.yml?query=event%3Aschedule) |
 | [ Python Validates Container Dataflow ARM ](https://github.com/apache/beam/actions/workflows/beam_Python_ValidatesContainer_Dataflow_ARM.yml) | N/A |`beam_Python_ValidatesContainer_Dataflow_ARM.json`|[![.github/workflows/beam_Python_ValidatesContainer_Dataflow_ARM.yml](https://github.com/apache/beam/actions/workflows/beam_Python_ValidatesContainer_Dataflow_ARM.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Python_ValidatesContainer_Dataflow_ARM.yml?query=event%3Aschedule) |
+| [ PostCommit Java ValidatesRunner Dataflow Streaming TagEncodingV2 ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_TagEncodingV2.yml) | N/A |`beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_TagEncodingV2.json`| [![.github/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_TagEncodingV2.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_TagEncodingV2.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_TagEncodingV2.yml?query=event%3Aschedule) |
+| [ PostCommit Java ValidatesRunner Dataflow Streaming Engine ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_Engine.yml) | N/A |`beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_Engine.json`| [![.github/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_Engine.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_Engine.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Java_ValidatesRunner_Dataflow_Streaming_Engine.yml?query=event%3Aschedule) |
+| [ PostCommit Python Portable Flink ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Portable_Flink.yml) | N/A |`beam_PostCommit_Python_Portable_Flink.json`| [![.github/workflows/beam_PostCommit_Python_Portable_Flink.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Portable_Flink.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Portable_Flink.yml?query=event%3Aschedule) |
+| [ PostCommit Python Xlang IO Direct ](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Xlang_IO_Direct.yml) | N/A |`beam_PostCommit_Python_Xlang_IO_Direct.json`| [![.github/workflows/beam_PostCommit_Python_Xlang_IO_Direct.yml](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Xlang_IO_Direct.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PostCommit_Python_Xlang_IO_Direct.yml?query=event%3Aschedule) |

 ### PerformanceTests and Benchmark Jobs

@@ -446,6 +457,7 @@ PostCommit Jobs run in a schedule against master branch and generally do not get
 | [ PerformanceTests XmlIOIT HDFS ](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT_HDFS.yml) | N/A | [![.github/workflows/beam_PerformanceTests_XmlIOIT_HDFS.yml](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT_HDFS.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT_HDFS.yml?query=event%3Aschedule)
 | [ PerformanceTests XmlIOIT ](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT.yml) | N/A | [![.github/workflows/beam_PerformanceTests_XmlIOIT.yml](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_XmlIOIT.yml?query=event%3Aschedule)
 | [ PerformanceTests xlang KafkaIO Python ](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_xlang_KafkaIO_Python.yml) | N/A | [![.github/workflows/beam_PerformanceTests_xlang_KafkaIO_Python.yml](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_xlang_KafkaIO_Python.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_PerformanceTests_xlang_KafkaIO_Python.yml?query=event%3Aschedule)
+| [ Python Cost Benchmarks Dataflow ](https://github.com/apache/beam/actions/workflows/beam_Python_CostBenchmarks_Dataflow.yml) | N/A | [![.github/workflows/beam_Python_CostBenchmarks_Dataflow.yml](https://github.com/apache/beam/actions/workflows/beam_Python_CostBenchmarks_Dataflow.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Python_CostBenchmarks_Dataflow.yml?query=event%3Aschedule) |

 ### LoadTests Jobs

@@ -502,6 +514,12 @@ PostCommit Jobs run in a schedule against master branch and generally do not get
 | [ LoadTests Python ParDo Flink Streaming ](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_ParDo_Flink_Streaming.yml) | N/A | [![.github/workflows/beam_LoadTests_Python_ParDo_Flink_Streaming.yml](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_ParDo_Flink_Streaming.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_ParDo_Flink_Streaming.yml?query=event%3Aschedule)
 | [ LoadTests Python SideInput Dataflow Batch ](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_SideInput_Dataflow_Batch.yml) | N/A | [![.github/workflows/beam_LoadTests_Python_SideInput_Dataflow_Batch.yml](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_SideInput_Dataflow_Batch.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_SideInput_Dataflow_Batch.yml?query=event%3Aschedule)
 | [ LoadTests Python Smoke ](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_Smoke.yml) | N/A | [![.github/workflows/beam_LoadTests_Python_Smoke.yml](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_Smoke.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Python_Smoke.yml?query=event%3Aschedule)
+| [ LoadTests Java PubsubIO ](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Java_PubsubIO.yml) | N/A | [![.github/workflows/beam_LoadTests_Java_PubsubIO.yml](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Java_PubsubIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_LoadTests_Java_PubsubIO.yml?query=event%3Aschedule) |
+| [ StressTests Java BigQueryIO ](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigQueryIO.yml) | N/A | [![.github/workflows/beam_StressTests_Java_BigQueryIO.yml](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigQueryIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigQueryIO.yml?query=event%3Aschedule) |
+| [ StressTests Java BigTableIO ](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigTableIO.yml) | N/A | [![.github/workflows/beam_StressTests_Java_BigTableIO.yml](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigTableIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_BigTableIO.yml?query=event%3Aschedule) |
+| [ StressTests Java KafkaIO ](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_KafkaIO.yml) | N/A | [![.github/workflows/beam_StressTests_Java_KafkaIO.yml](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_KafkaIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_KafkaIO.yml?query=event%3Aschedule) |
+| [ StressTests Java PubSubIO ](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_PubSubIO.yml) | N/A | [![.github/workflows/beam_StressTests_Java_PubSubIO.yml](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_PubSubIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_PubSubIO.yml?query=event%3Aschedule) |
+| [ StressTests Java SpannerIO ](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_SpannerIO.yml) | N/A | [![.github/workflows/beam_StressTests_Java_SpannerIO.yml](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_SpannerIO.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_StressTests_Java_SpannerIO.yml?query=event%3Aschedule) |

 ### Other Jobs

@@ -522,3 +540,8 @@ PostCommit Jobs run in a schedule against master branch and generally do not get
 | [ Release Nightly Snapshot Python ](https://github.com/apache/beam/actions/workflows/beam_Release_Python_NightlySnapshot.yml) | N/A | [![.github/workflows/beam_Release_Python_NightlySnapshot.yml](https://github.com/apache/beam/actions/workflows/beam_Release_Python_NightlySnapshot.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Release_Python_NightlySnapshot.yml?query=event%3Aschedule) |
 | [ Rotate IO-Datastores Cluster Credentials ](https://github.com/apache/beam/actions/workflows/beam_IODatastoresCredentialsRotation.yml) | N/A | [![.github/workflows/beam_IODatastoresCredentialsRotation.yml](https://github.com/apache/beam/actions/workflows/beam_IODatastoresCredentialsRotation.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_IODatastoresCredentialsRotation.yml?query=event%3Aschedule) |
 | [ Rotate Metrics Cluster Credentials ](https://github.com/apache/beam/actions/workflows/beam_MetricsCredentialsRotation.yml) | N/A | [![.github/workflows/beam_MetricsCredentialsRotation.yml](https://github.com/apache/beam/actions/workflows/beam_MetricsCredentialsRotation.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_MetricsCredentialsRotation.yml?query=event%3Aschedule) |
+| [ Beam Metrics Report ](https://github.com/apache/beam/actions/workflows/beam_Metrics_Report.yml) | N/A | [![.github/workflows/beam_Metrics_Report.yml](https://github.com/apache/beam/actions/workflows/beam_Metrics_Report.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Metrics_Report.yml?query=event%3Aschedule) |
+| [ GCP Security Log Analyzer ](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_SecurityLogging.yml) | N/A | [![.github/workflows/beam_Infrastructure_SecurityLogging.yml](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_SecurityLogging.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_SecurityLogging.yml?query=event%3Aschedule) |
+| [ Infrastructure Policy Enforcer ](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_PolicyEnforcer.yml) | N/A | [![.github/workflows/beam_Infrastructure_PolicyEnforcer.yml](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_PolicyEnforcer.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_PolicyEnforcer.yml?query=event%3Aschedule) |
+| [ Modify the GCP User Roles according to the infra/users.yml file ](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_UsersPermissions.yml) | N/A | [![.github/workflows/beam_Infrastructure_UsersPermissions.yml](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_UsersPermissions.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_UsersPermissions.yml?query=event%3Aschedule) |
+| [ Service Account Keys Management ](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_ServiceAccountKeys.yml) | N/A | [![.github/workflows/beam_Infrastructure_ServiceAccountKeys.yml](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_ServiceAccountKeys.yml/badge.svg?event=schedule)](https://github.com/apache/beam/actions/workflows/beam_Infrastructure_ServiceAccountKeys.yml?query=event%3Aschedule) |
diff --git a/.github/workflows/beam_PreCommit_GHA.yml b/.github/workflows/beam_PreCommit_GHA.yml
index ec6180a91e0f..8a2927962334 100644
--- a/.github/workflows/beam_PreCommit_GHA.yml
+++ b/.github/workflows/beam_PreCommit_GHA.yml
@@ -58,7 +58,7 @@ env:
 jobs:
   beam_PreCommit_GHA:
     name: ${{ matrix.job_name }} (${{ matrix.job_phrase }})
-    runs-on: [self-hosted, ubuntu-20.04, main]
+    runs-on: [self-hosted, ubuntu-20.04, small]
     strategy:
       matrix:
         job_name: [beam_PreCommit_GHA]
diff --git a/.github/workflows/beam_PreCommit_RAT.yml b/.github/workflows/beam_PreCommit_RAT.yml
index 51441207fa41..308b35c5619a 100644
--- a/.github/workflows/beam_PreCommit_RAT.yml
+++ b/.github/workflows/beam_PreCommit_RAT.yml
@@ -56,7 +56,7 @@ env:
 jobs:
   beam_PreCommit_RAT:
     name: ${{ matrix.job_name }} (${{ matrix.job_phrase }})
-    runs-on: [self-hosted, ubuntu-20.04, main]
+    runs-on: [self-hosted, ubuntu-20.04, small]
     strategy:
       matrix:
         job_name: [beam_PreCommit_RAT]
diff --git a/.github/workflows/beam_PreCommit_Whitespace.yml b/.github/workflows/beam_PreCommit_Whitespace.yml
index a378991dcfcb..9da6dd4e7011 100644
--- a/.github/workflows/beam_PreCommit_Whitespace.yml
+++ b/.github/workflows/beam_PreCommit_Whitespace.yml
@@ -57,7 +57,7 @@ env:
 jobs:
   beam_PreCommit_Whitespace:
     name: ${{ matrix.job_name }} (${{ matrix.job_phrase }})
-    runs-on: [self-hosted, ubuntu-20.04, main]
+    runs-on: [self-hosted, ubuntu-20.04, small]
     strategy:
       matrix:
         job_name: [beam_PreCommit_Whitespace]

PATCH

echo "Patch applied successfully."
