# Pin Browsers by Default in Bazel Build

## Problem

The Selenium project's Bazel build system currently defaults `pin_browsers` to `false`, meaning browser tests use whatever browser is on the system unless you explicitly pass `--pin_browsers=true`. In practice, every CI workflow already passes this flag explicitly — it's redundant boilerplate. The default should be flipped so that pinned (reproducible) browser versions are used automatically.

## Expected Behavior

- The `pin_browsers` bool_flag in `common/BUILD.bazel` should default to `True`
- All CI workflow files (`.github/workflows/ci-*.yml`) should have their now-redundant `--pin_browsers=true` / `--pin_browsers` flags removed from bazel test commands
- The `.bazelrc.remote` file should no longer set `--//common:pin_browsers` since it's now the default
- The project README should be updated to reflect this change — documentation currently describes `--pin_browsers` as something you pass to *enable* pinning, but it should now document `--pin_browsers=false` as the way to *disable* it

## Files to Look At

- `common/BUILD.bazel` — defines the `pin_browsers` bool_flag
- `.github/workflows/ci-dotnet.yml`, `ci-java.yml`, `ci-python.yml`, `ci-ruby.yml` — CI configs that pass the flag explicitly
- `.bazelrc.remote` — remote build config that sets the flag
- `README.md` — documents testing options including `--pin_browsers`
