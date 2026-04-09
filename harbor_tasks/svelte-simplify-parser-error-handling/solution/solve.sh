#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q 'handle_parse_error' packages/svelte/src/compiler/phases/1-parse/acorn.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/svelte/src/compiler/phases/1-parse/acorn.js b/packages/svelte/src/compiler/phases/1-parse/acorn.js
index 797ab4cea5eb..45a7c2a58c00 100644
--- a/packages/svelte/src/compiler/phases/1-parse/acorn.js
+++ b/packages/svelte/src/compiler/phases/1-parse/acorn.js
@@ -4,8 +4,10 @@
 import * as acorn from 'acorn';
 import { walk } from 'zimmerframe';
 import { tsPlugin } from '@sveltejs/acorn-typescript';
+import * as e from '../../errors.js';

-const ParserWithTS = acorn.Parser.extend(tsPlugin());
+const JSParser = acorn.Parser;
+const TSParser = JSParser.extend(tsPlugin());

 /**
  * @typedef {Comment & {
@@ -21,15 +23,15 @@ const ParserWithTS = acorn.Parser.extend(tsPlugin());
  * @param {boolean} [is_script]
  */
 export function parse(source, comments, typescript, is_script) {
-	const parser = typescript ? ParserWithTS : acorn.Parser;
+	const acorn = typescript ? TSParser : JSParser;

 	const { onComment, add_comments } = get_comment_handlers(
 		source,
 		/** @type {CommentWithLocation[]} */ (comments)
 	);

-	// @ts-ignore
-	const parse_statement = parser.prototype.parseStatement;
+	// @ts-expect-error
+	const parse_statement = acorn.prototype.parseStatement;

 	// If we're dealing with a <script> then it might contain an export
 	// for something that doesn't exist directly inside but is inside the
@@ -37,7 +39,7 @@ export function parse(source, comments, typescript, is_script) {
 	// an error in these cases
 	if (is_script) {
 		// @ts-ignore
-		parser.prototype.parseStatement = function (...args) {
+		acorn.prototype.parseStatement = function (...args) {
 			const v = parse_statement.call(this, ...args);
 			// @ts-ignore
 			this.undefinedExports = {};
@@ -45,25 +47,27 @@ export function parse(source, comments, typescript, is_script) {
 		};
 	}

-	let ast;
-
 	try {
-		ast = parser.parse(source, {
+		const ast = acorn.parse(source, {
 			onComment,
 			sourceType: 'module',
 			ecmaVersion: 16,
 			locations: true
 		});
+
+		add_comments(ast);
+
+		return /** @type {Program} */ (ast);
+	} catch (err) {
+		// TODO the `return` in necessary for TS<7 due to a bug; otherwise
+		// the `finally` block is regarded as unreachable
+		return handle_parse_error(err);
 	} finally {
 		if (is_script) {
-			// @ts-ignore
-			parser.prototype.parseStatement = parse_statement;
+			// @ts-expect-error
+			acorn.prototype.parseStatement = parse_statement;
 		}
 	}
-
-	add_comments(ast);
-
-	return /** @type {Program} */ (ast);
 }

 /**
@@ -73,21 +77,35 @@ export function parse(source, comments, typescript, is_script) {
  * @returns {acorn.Expression & { leadingComments?: CommentWithLocation[]; trailingComments?: CommentWithLocation[]; }}
  */
 export function parse_expression_at(parser, source, index) {
-	const _ = parser.ts ? ParserWithTS : acorn.Parser;
+	const acorn = parser.ts ? TSParser : JSParser;

 	const { onComment, add_comments } = get_comment_handlers(source, parser.root.comments, index);

-	const ast = _.parseExpressionAt(source, index, {
-		onComment,
-		sourceType: 'module',
-		ecmaVersion: 16,
-		locations: true,
-		preserveParens: true
-	});
+	try {
+		const ast = acorn.parseExpressionAt(source, index, {
+			onComment,
+			sourceType: 'module',
+			ecmaVersion: 16,
+			locations: true,
+			preserveParens: true
+		});

-	add_comments(ast);
+		add_comments(ast);

-	return ast;
+		return ast;
+	} catch (e) {
+		handle_parse_error(e);
+	}
+}
+
+const regex_position_indicator = / \(\d+:\d+\)$/;
+
+/**
+ * @param {any} err
+ * @returns {never}
+ */
+function handle_parse_error(err) {
+	e.js_parse_error(err.pos, err.message.replace(regex_position_indicator, ''));
 }

 /**
diff --git a/packages/svelte/src/compiler/phases/1-parse/index.js b/packages/svelte/src/compiler/phases/1-parse/index.js
index 81adbbb55523..5242cba31fcf 100644
--- a/packages/svelte/src/compiler/phases/1-parse/index.js
+++ b/packages/svelte/src/compiler/phases/1-parse/index.js
@@ -11,8 +11,6 @@ import { is_reserved } from '../../../utils.js';
 import { disallow_children } from '../2-analyze/visitors/shared/special-element.js';
 import * as state from '../../state.js';

-const regex_position_indicator = / \(\d+:\d+\)$/;
-
 /** @param {number} cc */
 function is_whitespace(cc) {
 	// fast path for common whitespace
@@ -175,14 +173,6 @@ export class Parser {
 		return this.stack[this.stack.length - 1];
 	}

-	/**
-	 * @param {any} err
-	 * @returns {never}
-	 */
-	acorn_error(err) {
-		e.js_parse_error(err.pos, err.message.replace(regex_position_indicator, ''));
-	}
-
 	/**
 	 * @param {string} str
 	 * @param {boolean} required
diff --git a/packages/svelte/src/compiler/phases/1-parse/read/context.js b/packages/svelte/src/compiler/phases/1-parse/read/context.js
index 24b7e2c6b00a..cdb239ef5be6 100644
--- a/packages/svelte/src/compiler/phases/1-parse/read/context.js
+++ b/packages/svelte/src/compiler/phases/1-parse/read/context.js
@@ -35,36 +35,32 @@ export default function read_pattern(parser) {

 	const pattern_string = parser.template.slice(start, i);

-	try {
-		// the length of the `space_with_newline` has to be start - 1
-		// because we added a `(` in front of the pattern_string,
-		// which shifted the entire string to right by 1
-		// so we offset it by removing 1 character in the `space_with_newline`
-		// to achieve that, we remove the 1st space encountered,
-		// so it will not affect the `column` of the node
-		let space_with_newline = parser.template
-			.slice(0, start)
-			.replace(regex_not_newline_characters, ' ');
-		const first_space = space_with_newline.indexOf(' ');
-		space_with_newline =
-			space_with_newline.slice(0, first_space) + space_with_newline.slice(first_space + 1);
-
-		/** @type {any} */
-		let expression = remove_parens(
-			parse_expression_at(parser, `${space_with_newline}(${pattern_string} = 1)`, start - 1)
-		);
-
-		expression = expression.left;
-
-		expression.typeAnnotation = read_type_annotation(parser);
-		if (expression.typeAnnotation) {
-			expression.end = expression.typeAnnotation.end;
-		}
-
-		return expression;
-	} catch (error) {
-		parser.acorn_error(error);
+	// the length of the `space_with_newline` has to be start - 1
+	// because we added a `(` in front of the pattern_string,
+	// which shifted the entire string to right by 1
+	// so we offset it by removing 1 character in the `space_with_newline`
+	// to achieve that, we remove the 1st space encountered,
+	// so it will not affect the `column` of the node
+	let space_with_newline = parser.template
+		.slice(0, start)
+		.replace(regex_not_newline_characters, ' ');
+	const first_space = space_with_newline.indexOf(' ');
+	space_with_newline =
+		space_with_newline.slice(0, first_space) + space_with_newline.slice(first_space + 1);
+
+	/** @type {any} */
+	let expression = remove_parens(
+		parse_expression_at(parser, `${space_with_newline}(${pattern_string} = 1)`, start - 1)
+	);
+
+	expression = expression.left;
+
+	expression.typeAnnotation = read_type_annotation(parser);
+	if (expression.typeAnnotation) {
+		expression.end = expression.typeAnnotation.end;
 	}
+
+	return expression;
 }

 /**
diff --git a/packages/svelte/src/compiler/phases/1-parse/read/expression.js b/packages/svelte/src/compiler/phases/1-parse/read/expression.js
index 16d4c4e50f12..1c8f097c2fe3 100644
--- a/packages/svelte/src/compiler/phases/1-parse/read/expression.js
+++ b/packages/svelte/src/compiler/phases/1-parse/read/expression.js
@@ -54,6 +54,6 @@ export default function read_expression(parser, opening_token, disallow_loose) {
 			}
 		}

-		parser.acorn_error(err);
+		throw err;
 	}
 }
diff --git a/packages/svelte/src/compiler/phases/1-parse/read/script.js b/packages/svelte/src/compiler/phases/1-parse/read/script.js
index 65153edfc867..4472ce61c3aa 100644
--- a/packages/svelte/src/compiler/phases/1-parse/read/script.js
+++ b/packages/svelte/src/compiler/phases/1-parse/read/script.js
@@ -31,14 +31,7 @@ export function read_script(parser, start, attributes) {
 		parser.template.slice(0, script_start).replace(regex_not_newline_characters, ' ') + data;
 	parser.read(regex_starts_with_closing_script_tag);

-	/** @type {Program} */
-	let ast;
-
-	try {
-		ast = acorn.parse(source, parser.root.comments, parser.ts, true);
-	} catch (err) {
-		parser.acorn_error(err);
-	}
+	const ast = acorn.parse(source, parser.root.comments, parser.ts, true);

 	ast.start = script_start;

PATCH

echo "Patch applied successfully."
