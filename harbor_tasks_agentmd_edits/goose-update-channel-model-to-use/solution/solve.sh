#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied
if grep -q "directCalls bool" goose.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full patch
git apply - <<'PATCH'
diff --git a/.github/workflows/build.yml b/.github/workflows/build.yml
index 3baac970..63f56e54 100644
--- a/.github/workflows/build.yml
+++ b/.github/workflows/build.yml
@@ -31,6 +31,7 @@ jobs:
         run: |
           go vet -composites=false ./...
           go test -v ./...
+          go test -v ./testdata/examples/...
       - name: End-to-end CLI tests
         run: |
           ./test/bats/bin/bats ./test/goose.bats
diff --git a/declfilter/declfilter.go b/declfilter/declfilter.go
index 8e9ed6ed..1a1cd2fd 100644
--- a/declfilter/declfilter.go
+++ b/declfilter/declfilter.go
@@ -37,6 +37,8 @@ type Bootstrap struct {
 	// These lines (typically imports from New.golang.defn) are joined to form
 	// the new prelude.
 	Prelude []string `toml:"prelude"`
+	// Translate function and method calls as direct calls, without using global state.
+	DirectCalls bool `toml:"direct_calls"`
 }

 type setOpType int
diff --git a/examples_test.go b/examples_test.go
index 56c031ce..c542332f 100644
--- a/examples_test.go
+++ b/examples_test.go
@@ -281,14 +281,3 @@ func TestAllChannelTests(t *testing.T) {

 // Tests of hand-translated channel model code
 // TODO: Once channel translation is implemented, remove
-func TestAllHandXlatedChannelTests(t *testing.T) {
-	chan_spec_raw_examples.TestHelloWorldSyncX()
-	chan_spec_raw_examples.TestHelloWorldWithTimeoutX()
-	chan_spec_raw_examples.TestDSPExampleX()
-	chan_spec_raw_examples.TestFibConsumerX()
-	chan_spec_raw_examples.TestSelectNbNoPanicX()
-	chan_spec_raw_examples.TestSelectReadyCaseNoPanicX()
-	chan_spec_raw_examples.LeakyBufferPipelineX()
-	// If we get here, none of the functions panic
-	t.Log("All channel tests passed successfully!")
-}
diff --git a/glang/coq.go b/glang/coq.go
index bc127312..a9b440ab 100644
--- a/glang/coq.go
+++ b/glang/coq.go
@@ -100,6 +100,10 @@ func binder(name string) string {
 	return quote(name)
 }

+func FuncImpl(name string) string {
+	return name + "ⁱᵐᵖˡ"
+}
+
 type ToValExpr struct {
 	Expr Expr
 }
@@ -714,12 +718,14 @@ func (e ForRangeSliceExpr) Coq(needs_paren bool) string {

 type ForRangeChanExpr struct {
 	Chan Expr
+	Elem Expr
 	Body Expr
 }

 func (e ForRangeChanExpr) Coq(needs_paren bool) string {
 	var pp buffer
-	pp.Add("chan.for_range %s (λ: \"$key\",",
+	pp.Add("chan.for_range %s %s (λ: \"$key\",",
+		e.Elem.Coq(true),
 		e.Chan.Coq(true),
 	)
 	pp.Indent(2)
diff --git a/goose.go b/goose.go
index fd2660a4..897a9760 100644
--- a/goose.go
+++ b/goose.go
@@ -68,7 +68,8 @@ type Ctx struct {

 	inits []glang.Expr

-	filter declfilter.DeclFilter
+	filter      declfilter.DeclFilter
+	directCalls bool
 }

 // NewPkgCtx initializes a context based on a properly loaded package
@@ -778,12 +779,17 @@ func (ctx *Ctx) selectorExpr(e *ast.SelectorExpr) glang.Expr {
 		} else if f, ok := ctx.info.ObjectOf(e.Sel).(*types.Func); ok {
 			// If there are type arguments, we must pass them
 			typeArgs := ctx.info.Instances[e.Sel].TypeArgs
-			return glang.NewCallExpr(
-				glang.GallinaVerbatim("func_call"),
-				glang.StringVal{Value: ctx.gallinaIdent(f.Pkg().Name() + "." + f.Name())},
-			).Append(
-				typesToExprs(ctx.convertTypeArgsToGlang(nil, typeArgs))...,
-			)
+			args := typesToExprs(ctx.convertTypeArgsToGlang(nil, typeArgs))
+			if ctx.directCalls {
+				return glang.NewCallExpr(
+					ctx.gallinaIdent(fmt.Sprintf("%s.%s", f.Pkg().Name(), glang.FuncImpl(f.Name()))),
+				).Append(args...)
+			} else {
+				return glang.NewCallExpr(
+					glang.GallinaVerbatim("func_call"),
+					glang.StringVal{Value: ctx.gallinaIdent(f.Pkg().Name() + "." + f.Name())},
+				).Append(args...)
+			}
 		} else {
 			return ctx.handleImplicitConversion(e,
 				ctx.info.TypeOf(e.Sel),
@@ -858,8 +864,19 @@ func (ctx *Ctx) selectorExpr(e *ast.SelectorExpr) glang.Expr {
 			ctx.nope(e.X, "expected a named type or a pointer to a named type for method call receiver")
 		}

-		return glang.NewCallExpr(glang.GallinaVerbatim("method_call"), typeIdExpr, methodExpr, receiver).Append(
-			typesToExprs(ctx.convertTypeArgsToGlang(nil, typeArgs))...)
+		args := typesToExprs(ctx.convertTypeArgsToGlang(nil, typeArgs))
+		if ctx.directCalls {
+			structName := ""
+			switch v := receiverType.(type) {
+			case *types.Named:
+				structName = ctx.qualifiedName(v.Obj())
+			case *types.Pointer:
+				structName = ctx.qualifiedName(types.Unalias(v.Elem()).(*types.Named).Obj())
+			}
+			return glang.NewCallExpr(glang.GallinaVerbatim(glang.TypeMethod(structName, e.Sel.Name)), receiver).Append(args...)
+		} else {
+			return glang.NewCallExpr(glang.GallinaVerbatim("method_call"), typeIdExpr, methodExpr, receiver).Append(args...)
+		}
 	}
 	panic("unreachable")
 }
@@ -1211,7 +1228,9 @@ func (ctx *Ctx) unaryExpr(e *ast.UnaryExpr, multipleBindings bool) glang.Expr {
 		return ctx.exprAddr(e.X)
 	}
 	if e.Op == token.ARROW {
-		var expr glang.Expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.receive"), ctx.expr(e.X))
+		var expr glang.Expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.receive"),
+			glang.GolangTypeExpr(ctx.glangType(e, chanElem(ctx.typeOf(e.X)))),
+			ctx.expr(e.X))
 		if !multipleBindings {
 			expr = glang.NewCallExpr(glang.GallinaVerbatim("Fst"), expr)
 		}
@@ -1345,7 +1364,9 @@ func (ctx *Ctx) builtinIdent(e *ast.Ident) glang.Expr {
 				return glang.GallinaVerbatim("StringLength")
 			}
 		case *types.Chan:
-			return glang.GallinaVerbatim("chan.len")
+			return glang.NewCallExpr(glang.GallinaVerbatim("chan.len"),
+				glang.GolangTypeExpr(ctx.glangType(e, ty.Elem())),
+			)
 		default:
 			ctx.unsupported(e, "length of object of type %v (%T)", ty, ty)
 		}
@@ -1356,7 +1377,9 @@ func (ctx *Ctx) builtinIdent(e *ast.Ident) glang.Expr {
 		case *types.Slice:
 			return glang.GallinaVerbatim("slice.cap")
 		case *types.Chan:
-			return glang.GallinaVerbatim("chan.cap")
+			return glang.NewCallExpr(glang.GallinaVerbatim("chan.cap"),
+				glang.GolangTypeExpr(ctx.glangType(e, ty.Elem())),
+			)
 		default:
 			ctx.unsupported(e, "capacity of object of type %v", ty)
 		}
@@ -1400,7 +1423,14 @@ func (ctx *Ctx) builtinIdent(e *ast.Ident) glang.Expr {
 		}
 		ctx.unsupported(e, "%s with final type %v", e.Name, t)
 	case "close":
-		return glang.GallinaVerbatim("chan.close")
+		funcT := ctx.typeOf(e).(*types.Signature)
+		if funcT.Params().Len() != 1 {
+			ctx.nope(e, "close with wrong number of params")
+		}
+		argT := funcT.Params().At(0).Type()
+		return glang.NewCallExpr(glang.GallinaVerbatim("chan.close"),
+			glang.GolangTypeExpr(ctx.glangType(e, chanElem(argT))),
+		)
 	case "iota":
 		o := ctx.info.ObjectOf(e)
 		t, v := ctx.constantLiteral(e, o.(*types.Const).Val())
@@ -1826,6 +1856,7 @@ func (ctx *Ctx) rangeStmt(s *ast.RangeStmt) glang.Expr {
 	case *types.Chan:
 		e = glang.ForRangeChanExpr{
 			Chan: glang.IdentExpr("$range"),
+			Elem: glang.GolangTypeExpr(ctx.glangType(s.X, chanElem(ctx.typeOf(s.X)))),
 			Body: body,
 		}
 	default:
@@ -2485,23 +2516,25 @@ func (ctx *Ctx) deferStmt(s *ast.DeferStmt, cont glang.Expr) (expr glang.Expr) {

 func (ctx *Ctx) selectStmt(s *ast.SelectStmt, cont glang.Expr) (expr glang.Expr) {
 	var ops glang.ListExpr
-	var def glang.Expr = glang.GallinaVerbatim("chan.select_no_default")
+	var def glang.Expr = nil

 	// build up select statement itself
 	for _, s := range s.Body.List {
 		s := s.(*ast.CommClause)
 		if s.Comm == nil {
-			def =
-				glang.NewCallExpr(glang.GallinaVerbatim("chan.select_default"), glang.FuncLit{Body: ctx.stmtList(s.Body, nil)})
+			// a default: case
+			def = glang.FuncLit{Body: ctx.stmtList(s.Body, nil)}
 		} else if c, ok := s.Comm.(*ast.SendStmt); ok {
 			ops = append(ops, glang.NewCallExpr(
 				glang.GallinaVerbatim("chan.select_send"),
-				ctx.expr(c.Value),
+				glang.GolangTypeExpr(ctx.glangType(s.Comm, chanElem(ctx.typeOf(c.Chan)))),
 				ctx.expr(c.Chan),
+				ctx.expr(c.Value),
 				glang.FuncLit{Body: ctx.stmtList(s.Body, nil)},
 			))
 		} else { // must be a receive stmt
 			var recvChan glang.Expr
+			var chanType types.Type
 			body := ctx.stmtList(s.Body, nil)

 			// want to figure out the first statment to run in the body
@@ -2512,6 +2545,7 @@ func (ctx *Ctx) selectStmt(s *ast.SelectStmt, cont glang.Expr) (expr glang.Expr
 					ctx.nope(comm.X, "expected recv statement")
 				}
 				recvChan = ctx.expr(recvExpr.X)
+				chanType = ctx.typeOf(recvExpr.X)
 				// nothing extra to run in the body
 			case *ast.AssignStmt:
 				// XXX: replace the RHS in the assignment statement with an
@@ -2532,6 +2566,7 @@ func (ctx *Ctx) selectStmt(s *ast.SelectStmt, cont glang.Expr) (expr glang.Expr
 					ctx.nope(comm.Rhs[0], "expected recv statement")
 				}
 				recvChan = ctx.expr(recvExpr.X)
+				chanType = ctx.typeOf(recvExpr.X)

 				// XXX: create a new AST node and enough typing information for
 				// an assignStmt to translate.
@@ -2549,21 +2584,32 @@ func (ctx *Ctx) selectStmt(s *ast.SelectStmt, cont glang.Expr) (expr glang.Expr
 			}

 			ops = append(ops, glang.NewCallExpr(glang.GallinaVerbatim("chan.select_receive"),
+				glang.GolangTypeExpr(ctx.glangType(s.Comm, chanElem(chanType))),
 				recvChan,
 				glang.FuncLit{Args: []glang.Binder{{Name: "$recvVal"}}, Body: body},
 			))
 		}
 	}

-	expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.select"), ops, def)
+	if def == nil {
+		expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.select_blocking"), ops)
+	} else {
+		expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.select_nonblocking"), ops, def)
+	}
 	expr = glang.SeqExpr{Expr: expr, Cont: cont}
 	return
 }

 func (ctx *Ctx) sendStmt(s *ast.SendStmt, cont glang.Expr) (expr glang.Expr) {
-	expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.send"), glang.IdentExpr("$chan"), glang.IdentExpr("$v"))
+	elemType := chanElem(ctx.typeOf(s.Chan))
+	expr = glang.NewCallExpr(glang.GallinaVerbatim("chan.send"),
+		glang.GolangTypeExpr(ctx.glangType(s, elemType)),
+		glang.IdentExpr("$chan"),
+		glang.IdentExpr("$v"))
 	// XXX: left-to-right evaluation, might not match Go
-	expr = glang.LetExpr{Names: []string{"$v"}, ValExpr: ctx.expr(s.Value), Cont: expr}
+	expr = glang.LetExpr{Names: []string{"$v"},
+		ValExpr: ctx.handleImplicitConversion(s.Value, ctx.typeOf(s.Value), elemType, ctx.expr(s.Value)),
+		Cont:    expr}
 	expr = glang.LetExpr{Names: []string{"$chan"}, ValExpr: ctx.expr(s.Chan), Cont: expr}
 	expr = glang.NewDoSeq(expr, cont)
 	return
@@ -2813,7 +2859,7 @@ func (ctx *Ctx) funcDecl(d *ast.FuncDecl) (ret []glang.Decl) {
 		}
 		fd.RecvArg = &glang.Binder{Name: name}
 	} else {
-		fd.Name = d.Name.Name + "ⁱᵐᵖˡ"
+		fd.Name = glang.FuncImpl(d.Name.Name)
 		switch ctx.filter.GetAction(funcName) {
 		case declfilter.Trust:
 			return
diff --git a/interface.go b/interface.go
index 02c48802..f240c87b 100644
--- a/interface.go
+++ b/interface.go
@@ -210,6 +210,7 @@ func translatePackage(pkg *packages.Package, config declfilter.FilterConfig) (gl
 			pkgErrors(pkg.Errors))
 	}
 	ctx := NewPkgCtx(pkg, declfilter.New(config))
+	ctx.directCalls = config.Bootstrap.DirectCalls
 	coqFile := ctx.initCoqFile(pkg, config)
 	imports, decls, errs := ctx.decls(pkg.Syntax)
 	coqFile.Imports = imports
diff --git a/types.go b/types.go
index 8515b803..3bcc6fc8 100644
--- a/types.go
+++ b/types.go
@@ -347,19 +347,26 @@ func (ctx *Ctx) glangType(n locatable, t types.Type) glang.Type {
 }

 func sliceElem(t types.Type) types.Type {
-	if t, ok := t.Underlying().(*types.Slice); ok {
+	if t, ok := underlyingType(t).(*types.Slice); ok {
 		return t.Elem()
 	}
 	panic(fmt.Errorf("expected slice type, got %v", t))
 }

 func ptrElem(t types.Type) types.Type {
-	if t, ok := t.Underlying().(*types.Pointer); ok {
+	if t, ok := underlyingType(t).(*types.Pointer); ok {
 		return t.Elem()
 	}
 	panic(fmt.Errorf("expected pointer type, got %v", t))
 }

+func chanElem(t types.Type) types.Type {
+	if t, ok := underlyingType(t).(*types.Chan); ok {
+		return t.Elem()
+	}
+	panic(fmt.Errorf("expected channel type, got %v", t))
+}
+
 func isProphId(t types.Type) bool {
 	if t, ok := t.(*types.Pointer); ok {
 		if t, ok := t.Elem().(*types.Named); ok {
PATCH

echo "Patch applied successfully."
