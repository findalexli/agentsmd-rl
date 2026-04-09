# Missing Angular v19 template in create-analog package

## Problem

When users try to create a new Analog project with the Angular v19 template, the `create-analog` command fails to include the template files in the generated project. The `template-angular-v19` directory exists in the source repository, but it's not being included in the published npm package.

This means users who want to bootstrap an Analog project with Angular 19 support cannot do so — the template files are missing from the package distribution.

## Expected Behavior

The `template-angular-v19` directory should be included in the npm package when published, allowing users to create new Analog projects with Angular 19 support.

## Files to Look At

- `packages/create-analog/package.json` — This file defines which files/directories are included in the npm package via the `files` array. The fix involves adding the missing template directory to this list.
