# Add React Native Expo Router TypeScript Windows .cursorrules File

Source: [PatrickJS/awesome-cursorrules#16](https://github.com/PatrickJS/awesome-cursorrules/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `rules/react-native-expo-router-typescript-windows-cursorrules-prompt-file/.cursorrules`

## What to add / change

# Add React Native Expo Router TypeScript Windows .cursorrules File

This pull request introduces a `.cursorrules` file designed for a React Native Expo project utilizing Expo Router, TypeScript, and development on Windows. It provides detailed guidelines and best practices tailored to this setup, ensuring consistency and addressing specific library configurations and issues.

## Key Highlights:

### Best Practices
- Emphasizes the use of functional components, TypeScript, and Expo Router for navigation.
- Includes guidance for styling using `StyleSheet` and `NativeWind`, asset management with Expo's asset system, and push notification integration.

### Folder Structure
- Recommends an organized directory layout with: `assets/ src/ components/ screens/ hooks/ utils/ app/ _layout.tsx index.tsx`

### Specific Library Compatibility Notes
- **NativeWind and Tailwind CSS**:
- Specifies using `nativewind@2.0.11` and `tailwindcss@3.3.2` due to known issues with higher versions (e.g., "process(css).then(cb)" errors).
- Provides clear steps for uninstalling incompatible versions and installing the correct versions:
  ```
  npm remove nativewind tailwindcss
  npm install nativewind@2.0.11 tailwindcss@3.3.2
  ```
- **Babel Configuration**:
- Includes instructions to configure `nativewind/babel` in the Babel plugins array:
  - Ensure the plugin is properly ordered with `react-native-reanimated/plugin` following `nativewind/babel`.
- Avoids using `jsxImportSource` 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
