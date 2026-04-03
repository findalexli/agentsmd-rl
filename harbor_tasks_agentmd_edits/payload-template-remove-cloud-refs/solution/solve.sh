#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if ! grep -q 'Payload Cloud' templates/website/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/templates/_template/README.md b/templates/_template/README.md
index 3b7fb775ce6..23334c425db 100644
--- a/templates/_template/README.md
+++ b/templates/_template/README.md
@@ -1,6 +1,6 @@
 # Payload Blank Template

-A blank template for [Payload](https://github.com/payloadcms/payload) to help you get up and running quickly. This repo may have been created by running `npx create-payload-app@latest` and selecting the "blank" template or by cloning this template on [Payload Cloud](https://payloadcms.com/new/clone/blank).
+A blank template for [Payload](https://github.com/payloadcms/payload) to help you get up and running quickly. This repo may have been created by running `npx create-payload-app@latest` and selecting the "blank" template.

 See the official [Examples Directory](https://github.com/payloadcms/payload/tree/main/examples) for details on how to use Payload in a variety of different ways.

@@ -35,7 +35,7 @@ To run Payload in production, you need to build and start the Admin panel. To do

 ### Deployment

-The easiest way to deploy your project is to use [Payload Cloud](https://payloadcms.com/new/import), a one-click hosting solution to deploy production-ready instances of your Payload apps directly from your GitHub repo. You can also deploy your app manually, check out the [deployment documentation](https://payloadcms.com/docs/production/deployment) for full details.
+Check out the [deployment documentation](https://payloadcms.com/docs/production/deployment) for details on how to deploy your project.

 ## Questions

diff --git a/templates/ecommerce/README.md b/templates/ecommerce/README.md
index b81d6494c7e..156aa584ca6 100644
--- a/templates/ecommerce/README.md
+++ b/templates/ecommerce/README.md
@@ -36,22 +36,12 @@ To spin up this example locally, follow these steps:

 If you have not done so already, you need to have standalone copy of this repo on your machine. If you've already cloned this repo, skip to [Development](#development).

-#### Method 1
-
 Use the `create-payload-app` CLI to clone this template directly to your machine:

 ```bash
 pnpx create-payload-app my-project -t ecommerce
 ```

-#### Method 2
-
-Use the `git` CLI to clone this template directly to your machine:
-
-```bash
-git clone -n --depth=1 --filter=tree:0 https://github.com/payloadcms/payload my-project && cd my-project && git sparse-checkout set --no-cone templates/ecommerce && git checkout && rm -rf .git && git init && git add . && git mv -f templates/ecommerce/{.,}* . && git add . && git commit -m "Initial commit"
-```
-
 ### Development

 1. First [clone the repo](#clone) if you have not done so already
diff --git a/templates/website/README.md b/templates/website/README.md
index 63a8142e60a..2413aad37da 100644
--- a/templates/website/README.md
+++ b/templates/website/README.md
@@ -31,26 +31,12 @@ To spin up this example locally, follow these steps:

 If you have not done so already, you need to have standalone copy of this repo on your machine. If you've already cloned this repo, skip to [Development](#development).

-#### Method 1 (recommended)
-
-Go to Payload Cloud and [clone this template](https://payloadcms.com/new/clone/website). This will create a new repository on your GitHub account with this template's code which you can then clone to your own machine.
-
-#### Method 2
-
 Use the `create-payload-app` CLI to clone this template directly to your machine:

 ```bash
 pnpx create-payload-app my-project -t website
 ```

-#### Method 3
-
-Use the `git` CLI to clone this template directly to your machine:
-
-```bash
-git clone -n --depth=1 --filter=tree:0 https://github.com/payloadcms/payload my-project && cd my-project && git sparse-checkout set --no-cone templates/website && git checkout && rm -rf .git && git init && git add . && git mv -f templates/website/{.,}* . && git add . && git commit -m "Initial commit"
-```
-
 ### Development

 1. First [clone the repo](#clone) if you have not done so already
@@ -256,10 +242,6 @@ To run Payload in production, you need to build and start the Admin panel. To do
 1. Finally run `pnpm start` or `npm run start` to run Node in production and serve Payload from the `.build` directory.
 1. When you're ready to go live, see Deployment below for more details.

-### Deploying to Payload Cloud
-
-The easiest way to deploy your project is to use [Payload Cloud](https://payloadcms.com/new/import), a one-click hosting solution to deploy production-ready instances of your Payload apps directly from your GitHub repo.
-
 ### Deploying to Vercel

 This template can also be deployed to Vercel for free. You can get started by choosing the Vercel DB adapter during the setup of the template or by manually installing and configuring it:
diff --git a/templates/website/src/components/BeforeDashboard/index.tsx b/templates/website/src/components/BeforeDashboard/index.tsx
index 9db54d50a63..25a95d86dfb 100644
--- a/templates/website/src/components/BeforeDashboard/index.tsx
+++ b/templates/website/src/components/BeforeDashboard/index.tsx
@@ -22,11 +22,6 @@ const BeforeDashboard: React.FC = () => {
           </a>
           {' to see the results.'}
         </li>
-        <li>
-          If you created this repo using Payload Cloud, head over to GitHub and clone it to your
-          local machine. It will be under the <i>GitHub Scope</i> that you selected when creating
-          this project.
-        </li>
         <li>
           {'Modify your '}
           <a>
diff --git a/templates/with-vercel-website/src/components/BeforeDashboard/index.tsx b/templates/with-vercel-website/src/components/BeforeDashboard/index.tsx
index 9db54d50a63..25a95d86dfb 100644
--- a/templates/with-vercel-website/src/components/BeforeDashboard/index.tsx
+++ b/templates/with-vercel-website/src/components/BeforeDashboard/index.tsx
@@ -22,11 +22,6 @@ const BeforeDashboard: React.FC = () => {
           </a>
           {' to see the results.'}
         </li>
-        <li>
-          If you created this repo using Payload Cloud, head over to GitHub and clone it to your
-          local machine. It will be under the <i>GitHub Scope</i> that you selected when creating
-          this project.
-        </li>
         <li>
           {'Modify your '}
           <a>

PATCH

echo "Patch applied successfully."
