#!/bin/bash
set -e

cd /workspace/ant-design

# Check if already applied (idempotency)
if grep -q "const currentYear = new Date().getFullYear();" components/layout/demo/fixed.tsx; then
    # Check if it's inside the App component (after theme.useToken())
    if grep -A5 "theme.useToken()" components/layout/demo/fixed.tsx | grep -q "const currentYear"; then
        echo "Patch already applied, skipping..."
        exit 0
    fi
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/components/layout/demo/fixed-sider.tsx b/components/layout/demo/fixed-sider.tsx
index 368d10514748..46cd628c12e4 100644
--- a/components/layout/demo/fixed-sider.tsx
+++ b/components/layout/demo/fixed-sider.tsx
@@ -39,12 +39,11 @@ const items: MenuProps['items'] = [
   label: `nav ${index + 1}`,
 }));

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();
+  const currentYear = new Date().getFullYear();

   return (
     <Layout hasSider>
diff --git a/components/layout/demo/fixed.tsx b/components/layout/demo/fixed.tsx
index 995046f26c5a..f616022b85a9 100644
--- a/components/layout/demo/fixed.tsx
+++ b/components/layout/demo/fixed.tsx
@@ -8,13 +8,13 @@ const items = Array.from({ length: 3 }).map((_, index) => ({
   label: `nav ${index + 1}`,
 }));

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();

+  const currentYear = new Date().getFullYear();
+
   return (
     <Layout>
       <Header
diff --git a/components/layout/demo/responsive.tsx b/components/layout/demo/responsive.tsx
index 66706d9d988b..b6486f185502 100644
--- a/components/layout/demo/responsive.tsx
+++ b/components/layout/demo/responsive.tsx
@@ -12,13 +12,13 @@ const items = [UserOutlined, VideoCameraOutlined, UploadOutlined, UserOutlined].
   }),
 );

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();

+  const currentYear = new Date().getFullYear();
+
   return (
     <Layout>
       <Sider
diff --git a/components/layout/demo/side.tsx b/components/layout/demo/side.tsx
index a159852aec2d..980dc2e437ba 100644
--- a/components/layout/demo/side.tsx
+++ b/components/layout/demo/side.tsx
@@ -39,14 +39,14 @@ const items: MenuItem[] = [
   getItem('Files', '9', <FileOutlined />),
 ];

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const [collapsed, setCollapsed] = useState(false);
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();

+  const currentYear = new Date().getFullYear();
+
   return (
     <Layout style={{ minHeight: '100vh' }}>
       <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
diff --git a/components/layout/demo/top-side.tsx b/components/layout/demo/top-side.tsx
index dc3288613619..1a961c209030 100644
--- a/components/layout/demo/top-side.tsx
+++ b/components/layout/demo/top-side.tsx
@@ -29,13 +29,13 @@ const items2: MenuProps['items'] = [UserOutlined, LaptopOutlined, NotificationOu
   },
 );

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();

+  const currentYear = new Date().getFullYear();
+
   return (
     <Layout>
       <Header style={{ display: 'flex', alignItems: 'center' }}>
diff --git a/components/layout/demo/top.tsx b/components/layout/demo/top.tsx
index 186cb9768fd5..e7ead0c254e5 100644
--- a/components/layout/demo/top.tsx
+++ b/components/layout/demo/top.tsx
@@ -8,13 +8,13 @@ const items = Array.from({ length: 15 }).map((_, index) => ({
   label: `nav ${index + 1}`,
 }));

-const currentYear = new Date().getFullYear();
-
 const App: React.FC = () => {
   const {
     token: { colorBgContainer, borderRadiusLG },
   } = theme.useToken();

+  const currentYear = new Date().getFullYear();
+
   return (
     <Layout>
       <Header style={{ display: 'flex', alignItems: 'center' }}>
PATCH

echo "Gold patch applied successfully"
