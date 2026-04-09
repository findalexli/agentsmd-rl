#!/bin/bash
set -e

cd /workspace/ant-design

# Check if already patched (idempotency check)
if grep -q "linkTargetOffsetRef" components/anchor/Anchor.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/anchor/Anchor.tsx b/components/anchor/Anchor.tsx
index f4babc9c8206..e000f2afa23c 100644
--- a/components/anchor/Anchor.tsx
+++ b/components/anchor/Anchor.tsx
@@ -114,10 +114,10 @@ export interface AnchorDefaultProps extends AnchorProps {
 export type AnchorDirection = 'vertical' | 'horizontal';

 export interface AntAnchor {
-  registerLink: (link: string) => void;
+  registerLink: (link: string, targetOffset?: number) => void;
   unregisterLink: (link: string) => void;
   activeLink: string | null;
-  scrollTo: (link: string) => void;
+  scrollTo: (link: string, targetOffset?: number) => void;
   onClick?: (
     e: React.MouseEvent<HTMLAnchorElement, MouseEvent>,
     link: { title: React.ReactNode; href: string },
@@ -171,6 +171,7 @@ const Anchor: React.FC<AnchorProps> = (props) => {
   const spanLinkNodeRef = React.useRef<HTMLSpanElement>(null);
   const animatingRef = React.useRef<boolean>(false);
   const scrollRequestIdRef = React.useRef<(() => void) | null>(null);
+  const linkTargetOffsetRef = React.useRef<Record<string, number>>({});

   const {
     direction,
@@ -192,17 +193,24 @@ const Anchor: React.FC<AnchorProps> = (props) => {

   const dependencyListItem: React.DependencyList[number] = JSON.stringify(links);

-  const registerLink = useEvent<AntAnchor['registerLink']>((link) => {
-    if (!links.includes(link)) {
-      setLinks((prev) => [...prev, link]);
+  const registerLink: AntAnchor['registerLink'] = (link, newTargetOffset) => {
+    setLinks((prev) => {
+      if (!prev.includes(link)) {
+        return [...prev, link];
+      }
+      return prev;
+    });
+    // Store link-level targetOffset for scroll detection
+    if (newTargetOffset !== undefined) {
+      linkTargetOffsetRef.current[link] = newTargetOffset;
     }
-  });
+  };

-  const unregisterLink = useEvent<AntAnchor['unregisterLink']>((link) => {
-    if (links.includes(link)) {
-      setLinks((prev) => prev.filter((i) => i !== link));
-    }
-  });
+  const unregisterLink: AntAnchor['unregisterLink'] = (link) => {
+    setLinks((prev) => prev.filter((i) => i !== link));
+    // Clean up targetOffset when unregistering
+    delete linkTargetOffsetRef.current[link];
+  };

   const updateInk = () => {
     const linkNode = wrapperRef.current?.querySelector<HTMLElement>(
@@ -221,7 +229,12 @@ const Anchor: React.FC<AnchorProps> = (props) => {
     }
   };

-  const getInternalCurrentAnchor = (_links: string[], _offsetTop = 0, _bounds = 5): string => {
+  const getInternalCurrentAnchor = (
+    _links: string[],
+    _offsetTop: number,
+    _bounds = 5,
+    _linkTargetOffset?: Record<string, number>,
+  ): string => {
     const linkSections: Section[] = [];
     const container = getCurrentContainer();
     _links.forEach((link) => {
@@ -231,8 +244,10 @@ const Anchor: React.FC<AnchorProps> = (props) => {
       }
       const target = document.getElementById(sharpLinkMatch[1]);
       if (target) {
+        // Use link-level targetOffset if provided, otherwise use global offsetTop
+        const linkOffsetTop = _linkTargetOffset?.[link] ?? _offsetTop;
         const top = getOffsetTop(target, container);
-        if (top <= _offsetTop + _bounds) {
+        if (top <= linkOffsetTop + _bounds) {
           linkSections.push({ link, top });
         }
       }
@@ -271,13 +286,14 @@ const Anchor: React.FC<AnchorProps> = (props) => {
       links,
       targetOffset !== undefined ? targetOffset : offsetTop || 0,
       bounds,
+      linkTargetOffsetRef.current,
     );

     setCurrentActiveLink(currentActiveLink);
   }, [links, targetOffset, offsetTop, bounds]);

-  const handleScrollTo = React.useCallback<(link: string) => void>(
-    (link) => {
+  const handleScrollTo = React.useCallback<(link: string, targetOffsetParams?: number) => void>(
+    (link, targetOffsetParams) => {
       const previousActiveLink = activeLinkRef.current;
       setCurrentActiveLink(link);
       const sharpLinkMatch = sharpMatcherRegex.exec(link);
@@ -300,7 +316,8 @@ const Anchor: React.FC<AnchorProps> = (props) => {
       const scrollTop = getScroll(container);
       const eleOffsetTop = getOffsetTop(targetElement, container);
       let y = scrollTop + eleOffsetTop;
-      y -= targetOffset !== undefined ? targetOffset : offsetTop || 0;
+      const finalTargetOffset = targetOffsetParams ?? targetOffset ?? offsetTop ?? 0;
+      y -= finalTargetOffset;
       animatingRef.current = true;
       scrollRequestIdRef.current = scrollTo(y, {
         getContainer: getCurrentContainer,
diff --git a/components/anchor/AnchorLink.tsx b/components/anchor/AnchorLink.tsx
index 144cf6734738..94eefb814923 100644
--- a/components/anchor/AnchorLink.tsx
+++ b/components/anchor/AnchorLink.tsx
@@ -13,6 +13,7 @@ export interface AnchorLinkBaseProps {
   title: React.ReactNode;
   className?: string;
   replace?: boolean;
+  targetOffset?: number;
 }

 export interface AnchorLinkProps extends AnchorLinkBaseProps {
@@ -28,6 +29,7 @@ const AnchorLink: React.FC<AnchorLinkProps> = (props) => {
     className,
     target,
     replace,
+    targetOffset,
   } = props;

   const context = React.useContext<AntAnchor | undefined>(AnchorContext);
@@ -44,15 +46,15 @@ const AnchorLink: React.FC<AnchorLinkProps> = (props) =>  {
   } = context || {};

   React.useEffect(() => {
-    registerLink?.(href);
+    registerLink?.(href, targetOffset);
     return () => {
       unregisterLink?.(href);
     };
-  }, [href]);
+  }, [href, targetOffset]);

   const handleClick = (e: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
     onClick?.(e, { title, href });
-    scrollTo?.(href);
+    scrollTo?.(href, targetOffset);

     // Support clicking on an anchor does not record history.
     if (e.defaultPrevented) {
PATCH

echo "Patch applied successfully"
