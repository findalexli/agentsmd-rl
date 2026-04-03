# Remove the expo_splash_screen_status_bar_translucent attribute

## Problem

The `expo_splash_screen_status_bar_translucent` Android string resource was introduced to let users control whether the status bar was translucent during the splash screen. However, since the `expo-splash-screen` rewrite to use the Android SplashScreen API, the status bar is **always** translucent. The old resource and the `statusBarTranslucent: Boolean` parameter threading through the codebase are dead code that should be cleaned up.

## Expected Behavior

- The `expo_splash_screen_status_bar_translucent` string resource should be removed from all `strings.xml` files across the apps (`bare-expo`, `expo-go`, `minimal-tester`).
- The `getStatusBarTranslucent` helper should be removed.
- The `statusBarTranslucent: Boolean` parameter should be dropped from all `SplashScreen.show` / `ensureShown` overloads.
- `SplashScreenStatusBar.configureTranslucent(activity, translucent)` should be simplified to always apply the translucent insets listener (renamed to reflect this).
- `ExperienceActivityUtils.setTranslucent` should be similarly simplified to always apply translucency.
- The `packages/expo-splash-screen/README.md` documentation sections that describe customizing the StatusBar translucent flag should be removed, and the migration guide updated to no longer reference this attribute.

## Files to Look At

- `apps/bare-expo/android/app/src/main/res/values/strings.xml`
- `apps/expo-go/android/expoview/src/main/res/values/strings.xml`
- `apps/minimal-tester/android/app/src/main/res/values/strings.xml`
- `apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt`
- `apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt`
- `apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt`
- `apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt`
- `apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt`
- `packages/expo-splash-screen/README.md` — remove obsolete translucent documentation and update migration guide
