#!/usr/bin/env bash
set -euo pipefail

cd /workspace/expo

# Idempotent: skip if already applied
if ! grep -q 'expo_splash_screen_status_bar_translucent' apps/bare-expo/android/app/src/main/res/values/strings.xml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/apps/bare-expo/android/app/src/main/res/values/strings.xml b/apps/bare-expo/android/app/src/main/res/values/strings.xml
index 3167987eb993fd..13bab2b14fd8d9 100644
--- a/apps/bare-expo/android/app/src/main/res/values/strings.xml
+++ b/apps/bare-expo/android/app/src/main/res/values/strings.xml
@@ -1,7 +1,6 @@
 <resources>
   <string name="app_name">BareExpo</string>
   <string name="expo_splash_screen_resize_mode" translatable="false">cover</string>
-  <string name="expo_splash_screen_status_bar_translucent" translatable="false">false</string>
   <string name="expo_runtime_version">1.0.0</string>
   <string name="expo_system_ui_user_interface_style" translatable="false">automatic</string>
 </resources>
\ No newline at end of file
diff --git a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt
index 119f613d9d05de..3fd6268d8e3968 100644
--- a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt
+++ b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt
@@ -407,7 +407,7 @@ open class ExperienceActivity : BaseExperienceActivity(), StartReactInstanceDele
         ReactSurfaceView::class.java,
         splashScreenView
       )
-      SplashScreen.show(this, managedAppSplashScreenViewController!!, true)
+      SplashScreen.show(this, managedAppSplashScreenViewController!!)
     } else {
       managedAppSplashScreenViewProvider!!.updateSplashScreenViewWithManifest(
         manifest!!
diff --git a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt
index 6920bb78f4858c..1475282a04040b 100644
--- a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt
+++ b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt
@@ -15,8 +15,7 @@ class SplashScreenReactActivityLifecycleListener : ReactActivityLifecycleListene
     SplashScreen.ensureShown(
       activity,
       getResizeMode(activity),
-      ReactRootView::class.java,
-      getStatusBarTranslucent(activity)
+      ReactRootView::class.java
     )
   }
 }
@@ -30,8 +29,7 @@ class SplashScreenReactActivityHandler : ReactActivityHandler {
       SplashScreen.ensureShown(
         it,
         getResizeMode(it),
-        ReactRootView::class.java,
-        getStatusBarTranslucent(it)
+        ReactRootView::class.java
       )
     }
     return null
@@ -43,6 +41,3 @@ private fun getResizeMode(context: Context): SplashScreenImageResizeMode =
     context.getString(R.string.expo_splash_screen_resize_mode).lowercase()
   )
     ?: SplashScreenImageResizeMode.CONTAIN
-
-private fun getStatusBarTranslucent(context: Context): Boolean =
-  context.getString(R.string.expo_splash_screen_status_bar_translucent).toBoolean()
diff --git a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt
index 2ad19dd1ae10fc..774cedce8649f8 100644
--- a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt
+++ b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt
@@ -27,7 +27,6 @@ object SplashScreen : SingletonModule {
    * @param activity Target Activity for SplashScreen to be mounted in.
    * @param splashScreenViewProvider Provider that created properly configured SplashScreenView
    * @param rootViewClass Class that is looked for in view hierarchy while autohiding is enabled.
-   * @param statusBarTranslucent Flag determining StatusBar translucency in a way ReactNative see it.
    * @param successCallback Callback to be called once SplashScreen is mounted in view hierarchy.
    * @param failureCallback Callback to be called once SplashScreen cannot be mounted.
    * @throws [expo.modules.splashscreen.exceptions.NoContentViewException] when [SplashScreen.show] is called before [Activity.setContentView] (when no ContentView is present for given activity).
@@ -38,15 +37,14 @@ object SplashScreen : SingletonModule {
     activity: Activity,
     splashScreenViewProvider: SplashScreenViewProvider,
     rootViewClass: Class<out ViewGroup>,
-    statusBarTranslucent: Boolean,
     successCallback: () -> Unit = {},
     failureCallback: (reason: String) -> Unit = { Log.w(TAG, it) }
   ) {
-    SplashScreenStatusBar.configureTranslucent(activity, statusBarTranslucent)
+    SplashScreenStatusBar.setTranslucent(activity)

     val splashView = splashScreenViewProvider.createSplashScreenView(activity)
     val controller = SplashScreenViewController(activity, rootViewClass, splashView)
-    show(activity, controller, statusBarTranslucent, successCallback, failureCallback)
+    show(activity, controller, successCallback, failureCallback)
   }

   /**
@@ -57,7 +55,6 @@ object SplashScreen : SingletonModule {
    * @param activity Target Activity for SplashScreen to be mounted in.
    * @param resizeMode SplashScreen imageView resizeMode.
    * @param rootViewClass Class that is looked for in view hierarchy while autohiding is enabled.
-   * @param statusBarTranslucent Flag determining StatusBar translucency in a way ReactNative see it.
    * @param splashScreenViewProvider
    * @param successCallback Callback to be called once SplashScreen is mounted in view hierarchy.
    * @param failureCallback Callback to be called once SplashScreen cannot be mounted.
@@ -69,12 +66,11 @@ object SplashScreen : SingletonModule {
     activity: Activity,
     resizeMode: SplashScreenImageResizeMode,
     rootViewClass: Class<out ViewGroup>,
-    statusBarTranslucent: Boolean,
     splashScreenViewProvider: SplashScreenViewProvider = NativeResourcesBasedSplashScreenViewProvider(resizeMode),
     successCallback: () -> Unit = {},
     failureCallback: (reason: String) -> Unit = { Log.w(TAG, it) }
   ) {
-    show(activity, splashScreenViewProvider, rootViewClass, statusBarTranslucent, successCallback, failureCallback)
+    show(activity, splashScreenViewProvider, rootViewClass, successCallback, failureCallback)
   }

   /**
@@ -84,7 +80,6 @@ object SplashScreen : SingletonModule {
    *
    * @param activity Target Activity for SplashScreen to be mounted in.
    * @param SplashScreenViewController SplashScreenViewController to manage the rootView and splashView
-   * @param statusBarTranslucent Flag determining StatusBar translucency in a way ReactNative see it.
    * @param successCallback Callback to be called once SplashScreen is mounted in view hierarchy.
    * @param failureCallback Callback to be called once SplashScreen cannot be mounted.
    * @throws [expo.modules.splashscreen.exceptions.NoContentViewException] when [SplashScreen.show] is called before [Activity.setContentView] (when no ContentView is present for given activity).
@@ -94,7 +89,6 @@ object SplashScreen : SingletonModule {
   fun show(
     activity: Activity,
     splashScreenViewController: SplashScreenViewController,
-    statusBarTranslucent: Boolean,
     successCallback: () -> Unit = {},
     failureCallback: (reason: String) -> Unit = { Log.w(TAG, it) }
   ) {
@@ -103,7 +97,7 @@ object SplashScreen : SingletonModule {
       return failureCallback("'SplashScreen.show' has already been called for this activity.")
     }

-    SplashScreenStatusBar.configureTranslucent(activity, statusBarTranslucent)
+    SplashScreenStatusBar.setTranslucent(activity)

     controllers[activity] = splashScreenViewController
     splashScreenViewController.showSplashScreen(successCallback)
@@ -159,12 +153,11 @@ object SplashScreen : SingletonModule {
   internal fun ensureShown(
     activity: Activity,
     resizeMode: SplashScreenImageResizeMode,
-    rootViewClass: Class<out ViewGroup>,
-    statusBarTranslucent: Boolean
+    rootViewClass: Class<out ViewGroup>
   ) {
     val controller = controllers[activity]
     if (controller == null) {
-      show(activity, resizeMode, rootViewClass, statusBarTranslucent)
+      show(activity, resizeMode, rootViewClass)
     } else {
       controller.showSplashScreen { }
     }
diff --git a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt
index 97bbd11c7d11d2..cafd6b26382609 100644
--- a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt
+++ b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt
@@ -4,27 +4,21 @@ import android.app.Activity
 import androidx.core.view.ViewCompat

 object SplashScreenStatusBar {
-  fun configureTranslucent(activity: Activity, translucent: Boolean?) {
-    translucent?.let {
-      activity.runOnUiThread {
-        // If the status bar is translucent hook into the window insets calculations
-        // and consume all the top insets so no padding will be added under the status bar.
-        val decorView = activity.window.decorView
-        if (it) {
-          decorView.setOnApplyWindowInsetsListener { v, insets ->
-            val defaultInsets = v.onApplyWindowInsets(insets)
-            defaultInsets.replaceSystemWindowInsets(
-              defaultInsets.systemWindowInsetLeft,
-              0,
-              defaultInsets.systemWindowInsetRight,
-              defaultInsets.systemWindowInsetBottom
-            )
-          }
-        } else {
-          decorView.setOnApplyWindowInsetsListener(null)
-        }
-        ViewCompat.requestApplyInsets(decorView)
+  fun setTranslucent(activity: Activity) {
+    activity.runOnUiThread {
+      // As the status bar is translucent, hook into the window insets calculations
+      // and consume all the top insets so no padding will be added under the status bar.
+      val decorView = activity.window.decorView
+      decorView.setOnApplyWindowInsetsListener { v, insets ->
+        val defaultInsets = v.onApplyWindowInsets(insets)
+        defaultInsets.replaceSystemWindowInsets(
+          defaultInsets.systemWindowInsetLeft,
+          0,
+          defaultInsets.systemWindowInsetRight,
+          defaultInsets.systemWindowInsetBottom
+        )
       }
+      ViewCompat.requestApplyInsets(decorView)
     }
   }
 }
diff --git a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt
index 8d1ac488016f35..9974cc4e882d05 100644
--- a/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt
+++ b/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt
@@ -104,10 +104,6 @@ object ExperienceActivityUtils {
       ExponentManifest.MANIFEST_STATUS_BAR_HIDDEN,
       false
     )
-    val statusBarTranslucent = statusBarOptions == null || statusBarOptions.optBoolean(
-      ExponentManifest.MANIFEST_STATUS_BAR_TRANSLUCENT,
-      true
-    )

     activity.runOnUiThread {
       // clear android:windowTranslucentStatus flag from Window as RN achieves translucency using WindowInsets
@@ -115,7 +111,7 @@ object ExperienceActivityUtils {

       setHidden(statusBarHidden, activity)

-      setTranslucent(statusBarTranslucent, activity)
+      setTranslucent(activity)

       val appliedStatusBarStyle = setStyle(statusBarStyle, activity)

@@ -162,22 +158,18 @@ object ExperienceActivityUtils {
   }

   @UiThread
-  fun setTranslucent(translucent: Boolean, activity: Activity) {
-    // If the status bar is translucent hook into the window insets calculations
+  fun setTranslucent(activity: Activity) {
+    // As the status bar is translucent, hook into the window insets calculations
     // and consume all the top insets so no padding will be added under the status bar.
     val decorView = activity.window.decorView
-    if (translucent) {
-      decorView.setOnApplyWindowInsetsListener { v: View, insets: WindowInsets? ->
-        val defaultInsets = v.onApplyWindowInsets(insets)
-        defaultInsets.replaceSystemWindowInsets(
-          defaultInsets.systemWindowInsetLeft,
-          0,
-          defaultInsets.systemWindowInsetRight,
-          defaultInsets.systemWindowInsetBottom
-        )
-      }
-    } else {
-      decorView.setOnApplyWindowInsetsListener(null)
+    decorView.setOnApplyWindowInsetsListener { v: View, insets: WindowInsets? ->
+      val defaultInsets = v.onApplyWindowInsets(insets)
+      defaultInsets.replaceSystemWindowInsets(
+        defaultInsets.systemWindowInsetLeft,
+        0,
+        defaultInsets.systemWindowInsetRight,
+        defaultInsets.systemWindowInsetBottom
+      )
     }
     ViewCompat.requestApplyInsets(decorView)
   }
diff --git a/apps/expo-go/android/expoview/src/main/res/values/strings.xml b/apps/expo-go/android/expoview/src/main/res/values/strings.xml
index 216cbad7378c39..4258f97d3bcc6c 100644
--- a/apps/expo-go/android/expoview/src/main/res/values/strings.xml
+++ b/apps/expo-go/android/expoview/src/main/res/values/strings.xml
@@ -40,7 +40,6 @@
   <string name="persistent_notification_channel_name">Experience notifications</string>
   <string name="persistent_notification_channel_desc">Persistent notifications that provide debug info about open experiences</string>
   <string name="expo_splash_screen_resize_mode" translatable="false">contain</string>
-  <string name="expo_splash_screen_status_bar_translucent" translatable="false">false</string>
   <string name="help_dialog">Make sure you are signed in to the same Expo account on your computer and this app. Also verify that your computer is connected to the internet, and ideally to the same Wi-Fi network as your mobile device. Lastly, ensure that you are using the latest version of Expo CLI. Pull to refresh to update.</string>

   <string-array name="currency_array">
diff --git a/apps/minimal-tester/android/app/src/main/res/values/strings.xml b/apps/minimal-tester/android/app/src/main/res/values/strings.xml
index 2b41aa0c74d678..df50c0f91d40c5 100644
--- a/apps/minimal-tester/android/app/src/main/res/values/strings.xml
+++ b/apps/minimal-tester/android/app/src/main/res/values/strings.xml
@@ -1,5 +1,4 @@
 <resources>
   <string name="app_name">minimal-tester</string>
   <string name="expo_splash_screen_resize_mode" translatable="false">contain</string>
-  <string name="expo_splash_screen_status_bar_translucent" translatable="false">false</string>
 </resources>
\ No newline at end of file
diff --git a/packages/expo-splash-screen/CHANGELOG.md b/packages/expo-splash-screen/CHANGELOG.md
index 019c41e3772845..620d915ae1437d 100644
--- a/packages/expo-splash-screen/CHANGELOG.md
+++ b/packages/expo-splash-screen/CHANGELOG.md
@@ -10,6 +10,8 @@

 ### 💡 Others

+- Removed the `expo_splash_screen_status_bar_translucent` Android leftover attribute. ([#43514](https://github.com/expo/expo/pull/43514) by [@zoontek](https://github.com/zoontek))
+
 ## 55.0.9 — 2026-02-25

 _This version does not introduce any user-facing changes._
diff --git a/packages/expo-splash-screen/README.md b/packages/expo-splash-screen/README.md
index 2663135acb7585..eea52947aea47d 100644
--- a/packages/expo-splash-screen/README.md
+++ b/packages/expo-splash-screen/README.md
@@ -668,50 +668,6 @@ Read more about `android:windowLightStatusBar` flag in [official Android documen

 To read more about Android multi-API-level support see [this official documentation](https://developer.android.com/guide/topics/resources/providing-resources).

-3. Customize `StatusBar color` option (a.k.a. `background color` of the StatusBar component)
-
-To achieve custom background color you need to create a new color resource and provide it to the SplashScreen `style` description.
-
-Create new color resource in your `res/values/colors.xml` (if your application supports dark mode, consider adding different color in `res/values-night/colors.xml` file):
-
-```diff
-  <resources>
-    <color name="splashscreen_background">#D0D0C0</color>
-+   <color name="splashscreen_statusbar_color">#(AA)RRGGBB</color> <!-- #AARRGGBB or #RRGGBB format -->
-  </resources>
-```
-
-Update your `res/values/styles.xml` file with the following entry:
-
-```diff
-  <!-- Main/SplashScreen activity theme. -->
-  <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
-    <item name="android:windowBackground">@drawable/splashscreen</item>
-+   <item name="android:statusBarColor">@color/splashscreen_statusbar_color</item>
-    <!-- Other style properties -->
-  </style>
-```
-
-If you have multiple `styles.xml` files located in different directories containing exactly the same `style` entry (e.g. in `res/values-night`, `res/values-night-v23`, etc.), be sure to update these files accordingly.
-
-Read more about `android:statusBarColor` option in [official Android documentation](https://developer.android.com/reference/android/R.attr#statusBarColor).
-
-4. Customize `StatusBar translucent` flag
-
-When the StatusBar is translucent, the app will be able to draw under the StatusBar component area.
-
-To make the StatusBar translucent update your `res/values/strings.xml` file with the following content:
-
-```diff
---- a/android/app/src/main/res/values/strings.xml
-+++ b/android/app/src/main/res/values/strings.xml
- <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
- <resources>
-   <string name="app_name">sdk42</string>
-+  <string name="expo_splash_screen_status_bar_translucent">true</string>
-</resources>
-```
-
 ## 👏 Contributing

 Contributions are very welcome! Please refer to guidelines described in the [contributing guide](https://github.com/expo/expo#contributing).
@@ -757,7 +713,7 @@ We try to keep changes backward compatible, the code for `expo-splash-screen` wi
    }
 ```

-3. Override default `resizeMode` and `statusBarTranslucent` in stings.xml
+3. Override default `resizeMode` in strings.xml

 ```diff
 --- a/android/app/src/main/res/values/strings.xml
@@ -766,7 +722,6 @@ We try to keep changes backward compatible, the code for `expo-splash-screen` wi
  <resources>
    <string name="app_name">sdk42</string>
 +  <string name="expo_splash_screen_resize_mode">contain</string>
-+  <string name="expo_splash_screen_status_bar_translucent">false</string>
 </resources>
 ```

PATCH

echo "Patch applied successfully."
