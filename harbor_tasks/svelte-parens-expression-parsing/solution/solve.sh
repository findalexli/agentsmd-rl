#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q 'preserveParens: true' packages/svelte/src/compiler/phases/1-parse/acorn.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/svelte/src/compiler/phases/1-parse/acorn.js b/packages/svelte/src/compiler/phases/1-parse/acorn.js
index 77ce4a461c2c..797ab4cea5eb 100644
--- a/packages/svelte/src/compiler/phases/1-parse/acorn.js
+++ b/packages/svelte/src/compiler/phases/1-parse/acorn.js
@@ -1,5 +1,6 @@
 /** @import { Comment, Program } from 'estree' */
 /** @import { AST } from '#compiler' */
+/** @import { Parser } from './index.js' */
 import * as acorn from 'acorn';
 import { walk } from 'zimmerframe';
 import { tsPlugin } from '@sveltejs/acorn-typescript';
@@ -66,26 +67,22 @@ export function parse(source, comments, typescript, is_script) {
 }

 /**
+ * @param {Parser} parser
  * @param {string} source
- * @param {Comment[]} comments
- * @param {boolean} typescript
  * @param {number} index
  * @returns {acorn.Expression & { leadingComments?: CommentWithLocation[]; trailingComments?: CommentWithLocation[]; }}
  */
-export function parse_expression_at(source, comments, typescript, index) {
-	const parser = typescript ? ParserWithTS : acorn.Parser;
+export function parse_expression_at(parser, source, index) {
+	const _ = parser.ts ? ParserWithTS : acorn.Parser;

-	const { onComment, add_comments } = get_comment_handlers(
-		source,
-		/** @type {CommentWithLocation[]} */ (comments),
-		index
-	);
+	const { onComment, add_comments } = get_comment_handlers(source, parser.root.comments, index);

-	const ast = parser.parseExpressionAt(source, index, {
+	const ast = _.parseExpressionAt(source, index, {
 		onComment,
 		sourceType: 'module',
 		ecmaVersion: 16,
-		locations: true
+		locations: true,
+		preserveParens: true
 	});

 	add_comments(ast);
@@ -93,6 +90,18 @@ export function parse_expression_at(source, comments, typescript, index) {
 	return ast;
 }

+/**
+ * @param {acorn.Expression} node
+ * @returns {acorn.Expression}
+ */
+export function remove_parens(node) {
+	return walk(node, null, {
+		ParenthesizedExpression(node, context) {
+			return context.visit(node.expression);
+		}
+	});
+}
+
 /**
  * Acorn doesn't add comments to the AST by itself. This factory returns the capabilities
  * to add them after the fact. They are needed in order to support `svelte-ignore` comments
diff --git a/packages/svelte/src/compiler/phases/1-parse/read/context.js b/packages/svelte/src/compiler/phases/1-parse/read/context.js
index f90d59fa0bce..24b7e2c6b00a 100644
--- a/packages/svelte/src/compiler/phases/1-parse/read/context.js
+++ b/packages/svelte/src/compiler/phases/1-parse/read/context.js
@@ -1,7 +1,7 @@
 /** @import { Pattern } from 'estree' */
 /** @import { Parser } from '../index.js' */
 import { match_bracket } from '../utils/bracket.js';
-import { parse_expression_at } from '../acorn.js';
+import { parse_expression_at, remove_parens } from '../acorn.js';
 import { regex_not_newline_characters } from '../../patterns.js';
 import * as e from '../../../errors.js';

@@ -49,14 +49,12 @@ export default function read_pattern(parser) {
 		space_with_newline =
 			space_with_newline.slice(0, first_space) + space_with_newline.slice(first_space + 1);

-		const expression = /** @type {any} */ (
-			parse_expression_at(
-				`${space_with_newline}(${pattern_string} = 1)`,
-				parser.root.comments,
-				parser.ts,
-				start - 1
-			)
-		).left;
+		/** @type {any} */
+		let expression = remove_parens(
+			parse_expression_at(parser, `${space_with_newline}(${pattern_string} = 1)`, start - 1)
+		);
+
+		expression = expression.left;

 		expression.typeAnnotation = read_type_annotation(parser);
 		if (expression.typeAnnotation) {
@@ -92,13 +90,13 @@ function read_type_annotation(parser) {
 		// parameters as part of a sequence expression instead, and will then error on optional
 		// parameters (`?:`). Therefore replace that sequence with something that will not error.
 		parser.template.slice(parser.index).replace(/\?\s*:/g, ':');
-	let expression = parse_expression_at(template, parser.root.comments, parser.ts, a);
+	let expression = remove_parens(parse_expression_at(parser, template, a));

 	// `foo: bar = baz` gets mangled — fix it
 	if (expression.type === 'AssignmentExpression') {
 		let b = expression.right.start;
 		while (template[b] !== '=') b -= 1;
-		expression = parse_expression_at(template.slice(0, b), parser.root.comments, parser.ts, a);
+		expression = remove_parens(parse_expression_at(parser, template.slice(0, b), a));
 	}

 	// `array as item: string, index` becomes `string, index`, which is mistaken as a sequence expression - fix that
diff --git a/packages/svelte/src/compiler/phases/1-parse/read/expression.js b/packages/svelte/src/compiler/phases/1-parse/read/expression.js
index 5d21f85792b0..16d4c4e50f12 100644
--- a/packages/svelte/src/compiler/phases/1-parse/read/expression.js
+++ b/packages/svelte/src/compiler/phases/1-parse/read/expression.js
@@ -1,6 +1,6 @@
 /** @import { Expression } from 'estree' */
 /** @import { Parser } from '../index.js' */
-import { parse_expression_at } from '../acorn.js';
+import { parse_expression_at, remove_parens } from '../acorn.js';
 import { regex_whitespace } from '../../patterns.js';
 import * as e from '../../../errors.js';
 import { find_matching_bracket } from '../utils/bracket.js';
@@ -34,50 +34,16 @@ export function get_loose_identifier(parser, opening_token) {
  */
 export default function read_expression(parser, opening_token, disallow_loose) {
 	try {
-		let comment_index = parser.root.comments.length;
-
-		const node = parse_expression_at(
-			parser.template,
-			parser.root.comments,
-			parser.ts,
-			parser.index
-		);
-
-		let num_parens = 0;
-
-		let i = parser.root.comments.length;
-		while (i-- > comment_index) {
-			const comment = parser.root.comments[i];
-			if (comment.end < node.start) {
-				parser.index = comment.end;
-				break;
-			}
-		}
-
-		for (let i = parser.index; i < /** @type {number} */ (node.start); i += 1) {
-			if (parser.template[i] === '(') num_parens += 1;
-		}
+		const node = parse_expression_at(parser, parser.template, parser.index);

 		let index = /** @type {number} */ (node.end);

 		const last_comment = parser.root.comments.at(-1);
 		if (last_comment && last_comment.end > index) index = last_comment.end;

-		while (num_parens > 0) {
-			const char = parser.template[index];
-
-			if (char === ')') {
-				num_parens -= 1;
-			} else if (!regex_whitespace.test(char)) {
-				e.expected_token(index, ')');
-			}
-
-			index += 1;
-		}
-
 		parser.index = index;

-		return /** @type {Expression} */ (node);
+		return /** @type {Expression} */ (remove_parens(node));
 	} catch (err) {
 		// If we are in an each loop we need the error to be thrown in cases like
 		// `as { y = z }` so we still throw and handle the error there
diff --git a/packages/svelte/src/compiler/phases/1-parse/state/tag.js b/packages/svelte/src/compiler/phases/1-parse/state/tag.js
index d9518c726f81..ff153128a54c 100644
--- a/packages/svelte/src/compiler/phases/1-parse/state/tag.js
+++ b/packages/svelte/src/compiler/phases/1-parse/state/tag.js
@@ -392,12 +392,7 @@ function open(parser) {

 		let function_expression = matched
 			? /** @type {ArrowFunctionExpression} */ (
-					parse_expression_at(
-						prelude + `${params} => {}`,
-						parser.root.comments,
-						parser.ts,
-						params_start
-					)
+					parse_expression_at(parser, prelude + `${params} => {}`, params_start)
 				)
 			: { params: [] };


PATCH

echo "Patch applied successfully."
