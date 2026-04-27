#!/bin/bash
set -euo pipefail

cd /workspace/hugo

# Idempotency: skip if the fix marker is already present.
if grep -q 'Collect vectors from descendant pages to create section' hugolib/content_map_page_assembler.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/hugolib/content_map_page_assembler.go b/hugolib/content_map_page_assembler.go
index 5a61795c7c2..db0fb0ede7b 100644
--- a/hugolib/content_map_page_assembler.go
+++ b/hugolib/content_map_page_assembler.go
@@ -497,14 +497,14 @@ func (a *allPagesAssembler) doCreatePages(prefix string, depth int) error {

 		isTaxonomy := !a.h.getFirstTaxonomyConfig(s).IsZero()
 		isRootSection := !isTaxonomy && level == 1 && cnh.isBranchNode(n)
-
-		if isRootSection {
-			// This is a root section.
-			a.seenRootSections.SetIfAbsent(cnh.PathInfo(n).Section(), true)
-		} else if !isTaxonomy {
+		if !isTaxonomy {
 			p := cnh.PathInfo(n)
 			rootSection := p.Section()
 			_, err := a.seenRootSections.GetOrCreate(rootSection, func() (bool, error) {
+				if isRootSection {
+					return true, nil
+				}
+
 				// Try to preserve the original casing if possible.
 				sectionUnnormalized := p.Unnormalized().Section()
 				rootSectionPath := a.h.Conf.PathParser().Parse(files.ComponentFolderContent, "/"+sectionUnnormalized+"/_index.md")
@@ -520,6 +520,51 @@ func (a *allPagesAssembler) doCreatePages(prefix string, depth int) error {
 					return true, err
 				}
 				treePages.InsertRaw(rootSectionPath.Base(), rootSectionPages)
+
+				// Collect vectors from descendant pages to create section
+				// pages for all languages that have content in this section.
+				nm, replaced := contentNodeToContentNodesPage(rootSectionPages)
+				if replaced {
+					treePages.InsertRaw(rootSectionPath.Base(), nm)
+				}
+				missingVectors := sitesmatrix.Vectors{}
+				pw.WalkContext.AddEventListener("sitesmatrix", rootSectionPath.Base(),
+					func(e *doctree.Event[contentNode]) {
+						if cnh.isBranchNode(e.Source) && !a.h.getFirstTaxonomyConfig(e.Path).IsZero() {
+							return
+						}
+						n := e.Source
+						e.StopPropagation()
+						n.forEeachContentNode(
+							func(vec sitesmatrix.Vector, nn contentNode) bool {
+								if _, found := nm[vec]; !found {
+									missingVectors[vec] = struct{}{}
+								}
+								return true
+							})
+					},
+				)
+				pw.WalkContext.HooksPost().Push(
+					func() error {
+						if len(missingVectors) > 0 {
+							vec := missingVectors.VectorSample()
+							nm[vec] = &pageMetaSource{
+								pathInfo:            rootSectionPath,
+								sitesMatrixBase:     missingVectors,
+								sitesMatrixBaseOnly: true,
+								pageConfigSource: &pagemeta.PageConfigEarly{
+									Kind: kinds.KindSection,
+								},
+							}
+							_, _, err := transformPages(rootSectionPath.Base(), nm, cascades)
+							if err != nil {
+								return err
+							}
+						}
+						return nil
+					},
+				)
+
 				return true, nil
 			})
 			if err != nil {
PATCH

echo "Patch applied successfully."
