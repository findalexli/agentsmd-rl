#!/bin/bash
set -e

cd /workspace/goose

# Check if already patched (idempotency)
# The patch adds two occurrences of using pkgPathBase.pkgName format for globals.get.
# We check for the specific change in selectorExprAddr (around line 609).
if ! grep -q 'pkgName, ok := getIdent(e.X)' goose.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/goose.go b/goose.go
index a47f372b..aa57f8ac 100644
--- a/goose.go
+++ b/goose.go
@@ -606,13 +606,11 @@ func (ctx *Ctx) getPkgAndName(obj types.Object) (pkg string, name string) {
 func (ctx *Ctx) selectorExprAddr(e *ast.SelectorExpr) glang.Expr {
 	selection := ctx.info.Selections[e]
 	if selection == nil {
-		pkgName, ok := getIdent(e.X)
-		if !ok {
-			ctx.unsupported(e, "expected package selector with idtent, got %T", e.X)
-		}
+		pkg := ctx.info.ObjectOf(e.Sel).Pkg()
+		pkgIdent := fmt.Sprintf("%s.%s", filepath.Base(pkg.Path()), pkg.Name())
 		if _, ok := ctx.info.ObjectOf(e.Sel).(*types.Var); ok {
 			return glang.NewCallExpr(glang.GallinaIdent("globals.get"),
-				glang.StringVal{Value: glang.GallinaIdent(pkgName)},
+				glang.StringVal{Value: glang.GallinaIdent(pkgIdent)},
 				glang.StringVal{Value: glang.StringLiteral{Value: e.Sel.Name}},
 			)
 		} else {
@@ -1901,12 +1899,8 @@ func (ctx *Ctx) exprAddr(e ast.Expr) glang.Expr {
 		obj := ctx.info.ObjectOf(e)
 		if _, ok := obj.(*types.Var); ok {
 			if obj.Pkg().Scope() == obj.Parent() {
-				pkgIdent := ""
-				if obj.Pkg().Path() == ctx.pkgPath {
-					pkgIdent = ctx.pkgIdent
-				} else {
-					pkgIdent = obj.Pkg().Name()
-				}
+				pkg := obj.Pkg()
+				pkgIdent := fmt.Sprintf("%s.%s", filepath.Base(pkg.Path()), pkg.Name())
 				return glang.NewCallExpr(glang.GallinaIdent("globals.get"),
 					glang.StringVal{Value: glang.GallinaIdent(pkgIdent)},
 					glang.StringVal{Value: glang.StringLiteral{Value: e.Name}},
PATCH

echo "Patch applied successfully"
