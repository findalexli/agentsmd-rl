# Remove outdated Payload Cloud and git clone references from templates

## Problem

Several template files in the `templates/` directory contain outdated information:

1. **Outdated cloning instructions**: The ecommerce and website template READMEs list a `git clone` / `git sparse-checkout` method for getting started. This method no longer works because the templates' `package.json` files use `workspace:*` syntax, which requires going through `create-payload-app`. Users who follow these instructions will get broken installs.

2. **Payload Cloud references**: Multiple templates reference Payload Cloud (a discontinued hosting service) in their README deployment sections and in the admin dashboard's "getting started" component. These references are misleading since the service is no longer available.

## Expected Behavior

- Template READMEs should only recommend `create-payload-app` as the way to get started (no `git clone` / `git sparse-checkout` methods)
- All references to Payload Cloud should be removed from README files and UI components
- The deployment sections should link to the general deployment docs instead of promoting Payload Cloud
- The admin dashboard's BeforeDashboard component should not mention Payload Cloud

## Files to Look At

- `templates/website/README.md` — has Payload Cloud clone method, git clone method, and "Deploying to Payload Cloud" section
- `templates/ecommerce/README.md` — has git clone method as "Method 2"
- `templates/_template/README.md` — references Payload Cloud in description and deployment section
- `templates/website/src/components/BeforeDashboard/index.tsx` — dashboard component with Payload Cloud mention
- `templates/with-vercel-website/src/components/BeforeDashboard/index.tsx` — same dashboard component

After fixing the code, update the relevant documentation to reflect the changes. Make sure the `create-payload-app` instructions and other valid content are preserved.
