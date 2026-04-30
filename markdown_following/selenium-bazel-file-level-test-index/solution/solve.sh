#!/bin/bash
set -euo pipefail

cd /workspace/selenium

if grep -q 'HIGH_IMPACT_DIRS = %w\[common rust/src javascript/atoms javascript/webdriver/atoms\]' rake_tasks/bazel.rake; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/workflows/ci-build-index.yml b/.github/workflows/ci-build-index.yml
index ef7de04e14179..e0673ea07475b 100644
--- a/.github/workflows/ci-build-index.yml
+++ b/.github/workflows/ci-build-index.yml
@@ -13,9 +13,9 @@ jobs:
     with:
       name: Build Test Index
       os: ubuntu
-      run: ./go bazel:build_test_index bazel-test-target-index
-      artifact-name: bazel-test-target-index
-      artifact-path: bazel-test-target-index
+      run: ./go bazel:build_test_index bazel-test-file-index
+      artifact-name: bazel-test-file-index
+      artifact-path: bazel-test-file-index

   cache:
     name: Cache Index
@@ -26,9 +26,9 @@ jobs:
       - name: Download index
         uses: actions/download-artifact@v4
         with:
-          name: bazel-test-target-index
+          name: bazel-test-file-index
       - name: Cache index
         uses: actions/cache/save@v4
         with:
-          path: bazel-test-target-index
-          key: bazel-test-target-index-${{ github.run_id }}
+          path: bazel-test-file-index
+          key: bazel-test-file-index-${{ github.run_id }}
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 4f186c397822a..8c3a91b478288 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -31,7 +31,7 @@ jobs:
     uses: ./.github/workflows/bazel.yml
     with:
       name: Check Targets
-      cache-name: bazel-test-target-index
+      cache-name: bazel-test-file-index
       run: |
         if [ "${{ github.event_name }}" == "schedule" ] || \
         [ "${{ github.event_name }}" == "workflow_call" ] || \
@@ -42,9 +42,9 @@ jobs:
           BASE_SHA="${{ github.event.pull_request.base.sha || github.event.before }}"
           HEAD_SHA="${{ github.event.pull_request.head.sha || 'HEAD' }}"
           if [ -n "$BASE_SHA" ]; then
-            ./go bazel:affected_targets "${BASE_SHA}..${HEAD_SHA}" bazel-test-target-index
+            ./go bazel:affected_targets "${BASE_SHA}..${HEAD_SHA}" bazel-test-file-index
           else
-            ./go bazel:affected_targets bazel-test-target-index
+            ./go bazel:affected_targets bazel-test-file-index
           fi
         fi
       artifact-name: check-targets
diff --git a/rake_tasks/bazel.rake b/rake_tasks/bazel.rake
index 221c9d0ad1291..799c3510d9d65 100644
--- a/rake_tasks/bazel.rake
+++ b/rake_tasks/bazel.rake
@@ -3,6 +3,10 @@
 require 'json'
 require 'set'

+# Dirs that affect all bindings - changes here trigger "run all tests"
+HIGH_IMPACT_DIRS = %w[common rust/src javascript/atoms javascript/webdriver/atoms].freeze
+HIGH_IMPACT_PATTERN = %r{\A(?:#{HIGH_IMPACT_DIRS.map { |d| Regexp.escape(d) }.join('|')})(?:/|$)}
+
 # ./go bazel:affected_targets                              --> HEAD^..HEAD with default index
 # ./go bazel:affected_targets abc123..def456               --> explicit range
 # ./go bazel:affected_targets abc123..def456 my-index      --> explicit range with custom index
@@ -12,7 +16,7 @@ task :affected_targets do |_task, args|
   values = args.to_a
   index_file = values.find { |value| File.exist?(value) }
   range = (values - [index_file]).first || 'HEAD'
-  index_file ||= 'build/bazel-test-target-index'
+  index_file ||= 'build/bazel-test-file-index'

   base_rev, head_rev = if range.include?('..')
                          range.split('..', 2)
@@ -25,11 +29,13 @@ task :affected_targets do |_task, args|
   changed_files = `git diff --name-only #{base_rev} #{head_rev}`.split("\n").map(&:strip).reject(&:empty?)
   puts "Changed files: #{changed_files.size}"

-  targets = if File.exist?(index_file)
+  targets = if changed_files.any? { |f| f.match?(HIGH_IMPACT_PATTERN) }
+              BINDING_TARGETS.values
+            elsif File.exist?(index_file)
               affected_targets_with_index(changed_files, index_file)
             else
               puts 'No index found, using directory-based fallback'
-              affected_targets_fallback(changed_files)
+              affected_targets_by_directory(changed_files)
             end

   if targets.empty?
@@ -42,13 +48,14 @@ task :affected_targets do |_task, args|
   end
 end

-# ./go bazel:build_test_index                    --> 'build/bazel-test-target-index'
+# ./go bazel:build_test_index                    --> 'build/bazel-test-file-index'
 # ./go bazel:build_test_index my-index           --> 'my-index'
 desc 'Build test target index for faster affected target lookup'
 task :build_test_index, [:index_file] do |_task, args|
-  output = args[:index_file] || 'build/bazel-test-target-index'
+  output = args[:index_file] || 'build/bazel-test-file-index'

-  index = {}
+  # Flat index: file path → [test targets]
+  index = Hash.new { |h, k| h[k] = [] }
   tests = []

   exclude_tags = %w[manual spotbugs ie]
@@ -60,38 +67,63 @@ task :build_test_index, [:index_file] do |_task, args|
   Bazel.execute('query', ['--output=label'], "kind(#{kind}, #{all_bindings}) #{tag_exclusions}") do |out|
     tests = out.lines.map(&:strip).select { |l| l.start_with?('//') }
   end
-  puts "Found #{tests.size} tests"
+  puts "Found #{tests.size} test targets"

+  puts 'Building file → tests mapping...'
+  srcs_cache = {}
   tests.each_with_index do |test, i|
     puts "Processing #{i + 1}/#{tests.size}: #{test}" if (i % 100).zero?

-    deps = []
-    Bazel.execute('query', ['--output=label'], "deps(#{test})") do |out|
-      deps = out.lines.map(&:strip).select { |l| l.start_with?('//', '@selenium//') }
+    query_test_deps(test).each do |dep|
+      srcs_cache[dep] ||= query_dep_srcs(dep)
+      add_test_to_index(index, test, srcs_cache[dep])
     end
+  end
+  puts "Cached #{srcs_cache.size} dep → srcs lookups"

-    deps.each do |dep|
-      pkg = bazel_label_to_package(dep)
-      next if pkg.nil? || pkg.empty?
-
-      index[pkg] ||= []
-      index[pkg] << test unless index[pkg].include?(test)
-    end
+  sorted_index = index.keys.sort.each_with_object({}) do |filepath, h|
+    h[filepath] = index[filepath].uniq.sort
   end

-  sorted_index = index.keys.sort.each_with_object({}) { |k, h| h[k] = index[k].sort }
   FileUtils.mkdir_p(File.dirname(output))
   File.write(output, JSON.pretty_generate(sorted_index))
-  puts "Wrote #{sorted_index.size} packages to #{output}"
+  puts "Wrote index with #{sorted_index.size} files to #{output}"
 end

-def bazel_label_to_package(label)
-  # Skip external deps (but allow @selenium// which is internal)
-  return nil if label.start_with?('@') && !label.start_with?('@selenium//')
+def query_test_deps(test)
+  deps = []
+  Bazel.execute('query', ['--output=label'], "deps(#{test}) intersect //... except attr(testonly, 1, //...)") do |out|
+    deps = out.lines.map(&:strip).select { |l| l.start_with?('//') }
+  end
+  deps.reject do |d|
+    # Skip high-impact dirs and root package targets (generated files, LICENSE, etc)
+    HIGH_IMPACT_DIRS.any? { |dir| d.start_with?("//#{dir}") } || d.start_with?('//:')
+  end
+rescue StandardError => e
+  puts "  Warning: Failed to query deps for #{test}: #{e.message}"
+  []
+end
+
+def add_test_to_index(index, test, srcs)
+  srcs.each do |src|
+    # Convert //pkg:file to pkg/file
+    filepath = src.sub(%r{^//}, '').tr(':', '/')
+    # Skip dotnet tests for java sources (dotnet depends on java server but has no remote tests)
+    next if filepath.start_with?('java/') && test.start_with?('//dotnet/')
+
+    index[filepath] << test
+  end
+end

-  # Normalize @selenium//foo to foo, //foo to foo
-  label = label.sub(%r{^@selenium//}, '').sub(%r{^//}, '')
-  label.split(':').first
+def query_dep_srcs(dep)
+  srcs = []
+  Bazel.execute('query', ['--output=label'], "labels(srcs, #{dep})") do |out|
+    srcs = out.lines.map(&:strip).select { |l| l.start_with?('//') && !l.start_with?('//:') }
+  end
+  srcs
+rescue StandardError => e
+  puts "  Warning: Failed to query srcs for #{dep}: #{e.message}"
+  []
 end

 def find_bazel_package(filepath)
@@ -107,49 +139,60 @@ end

 def affected_targets_with_index(changed_files, index_file)
   puts "Using index: #{index_file}"
+
   begin
     index = JSON.parse(File.read(index_file))
   rescue JSON::ParserError => e
     puts "Invalid JSON in index file: #{e.message}"
-    return affected_targets_fallback(changed_files)
+    puts 'Using directory-based fallback'
+    return affected_targets_by_directory(changed_files)
   end

-  test_files, lib_files = changed_files.partition { |f| f.match?(/[_-]test\.rb$|_test\.py$|Test\.java$|Tests?\.cs$|\.test\.[jt]s$|_spec\.rb$/) }
+  test_files, lib_files = changed_files.partition { |f| f.match?(%r{[_-]test\.rb$|_tests?\.py$|Test\.java$|\.test\.[jt]s$|_spec\.rb$|^dotnet/test/}) }

   affected = Set.new
+  # Just test the tests
   affected.merge(targets_from_tests(test_files))

   lib_files.each do |filepath|
-    pkg = find_bazel_package(filepath)
-    affected.merge(targets_from_lookup(pkg, index, filepath))
+    tests = index[filepath]
+    if tests
+      puts "  #{filepath} → #{tests.size} tests"
+      affected.merge(tests)
+    else
+      puts "  #{filepath} not in index, querying for affected tests"
+      affected.merge(query_unindexed_file(filepath))
+    end
   end

   affected.to_a
 end

-def targets_from_lookup(pkg, index, filepath)
-  # ignore files not associated with bazel package
-  return [] if pkg.nil?
+def query_unindexed_file(filepath)
+  pkg = find_bazel_package(filepath)
+  return [] unless pkg

-  # Root package is empty string, not '.'
+  rel = pkg == '.' ? filepath : filepath.sub(%r{^#{Regexp.escape(pkg)}/}, '')
   pkg = '' if pkg == '.'

-  # generate targets if package not in the index
-  test_targets = index[pkg] || query_package_dep(pkg)
-
-  # dotnet tests depend on java server, but there are no remote tests, so safe to ignore
-  filepath.start_with?('java/') ? test_targets.reject { |t| t.start_with?('//dotnet/') } : test_targets
-end
+  # Find targets that contain this file in their srcs
+  containing = []
+  Bazel.execute('query', ['--output=label'], "attr(srcs, '#{rel}', //#{pkg}:*)") do |out|
+    containing = out.lines.map(&:strip).select { |l| l.start_with?('//') }
+  end
+  return [] if containing.empty?

-def query_package_dep(pkg)
-  # Root package is empty string, not '.'
-  pkg = '' if pkg == '.'
-  puts "Package not in index, querying deps: //#{pkg}"
+  # Find tests that depend on those targets
   targets = []
-  Bazel.execute('query', ['--output=label'], "kind('.*_test', deps(//#{pkg}:all))") do |out|
+  Bazel.execute('query', ['--output=label'], "kind(_test, rdeps(//..., #{containing.join(' + ')}))") do |out|
     targets = out.lines.map(&:strip).select { |l| l.start_with?('//') }
   end
-  targets
+
+  # dotnet tests depend on java server, but there are no remote tests, so safe to ignore
+  filepath.start_with?('java/') ? targets.reject { |t| t.start_with?('//dotnet/') } : targets
+rescue StandardError => e
+  puts "  Warning: Failed to query unindexed file #{filepath}: #{e.message}"
+  []
 end

 def targets_from_tests(test_files)
@@ -158,7 +201,7 @@ def targets_from_tests(test_files)

   query = test_files.filter_map { |f|
     pkg = find_bazel_package(f)
-    next if pkg.nil?
+    next unless pkg

     # Bazel srcs often use paths relative to the package, not basenames.
     rel = f.sub(%r{^#{Regexp.escape(pkg)}/}, '')
@@ -168,13 +211,13 @@ def targets_from_tests(test_files)
   return [] if query.empty?

   targets = []
-  Bazel.execute('query', ['--output=label'], "kind('.*_test', #{query})") do |out|
+  Bazel.execute('query', ['--output=label'], "kind(_test, #{query})") do |out|
     targets = out.lines.map(&:strip).select { |l| l.start_with?('//') }
   end
   targets
 end

-def affected_targets_fallback(changed_files)
+def affected_targets_by_directory(changed_files)
   targets = Set.new
   top_level_dirs = changed_files.map { |f| f.split('/').first }.uniq

PATCH

echo "Gold patch applied successfully."
