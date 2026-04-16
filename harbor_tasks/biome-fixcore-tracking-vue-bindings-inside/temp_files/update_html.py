import re

with open("/workspace/biome/crates/biome_service/src/file_handlers/html.rs", "r") as f:
    content = f.read()

# Update imports
content = content.replace(
    "use biome_html_syntax::{
    AstroEmbeddedContent",
    "use biome_html_syntax::{
    AnySvelteDirective, HtmlAttributeInitializerClause,
    AstroEmbeddedContent"
)

content = content.replace(
    "HtmlVariant,
};",
    "HtmlVariant,
    VueDirective, VueVBindShorthandDirective, VueVOnShorthandDirective, VueVSlotShorthandDirective,
};"
)

content = content.replace(
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode};",
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode, TextSize};"
)

# Add helper functions
helpers = '''fn parse_directive_string_value(
    value: &HtmlAttributeInitializerClause,
    cache: &mut NodeCache,
    biome_path: &BiomePath,
    settings: &SettingsWithEditor,
    file_source: JsFileSource,
) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
    let value_node = value.value().ok()?;
    let html_string = value_node.as_html_string()?;
    let content_token = html_string.value_token().ok()?;
    let inner_text = html_string.inner_string_text().ok()?;
    let text = inner_text.text();
    let token_range = content_token.text_trimmed_range();
    let inner_offset = token_range.start() + TextSize::from(1);
    let document_file_source = DocumentFileSource::Js(file_source);
    let options = settings.parse_options::<JsLanguage>(biome_path, &document_file_source);
    let parse = parse_js_with_offset_and_cache(text, inner_offset, file_source, options, cache);
    let snippet = EmbeddedSnippet::new(parse.into(), value.range(), token_range, inner_offset);
    Some((snippet, document_file_source))
}

fn parse_directive_text_expression(
    value: &HtmlAttributeInitializerClause,
    cache: &mut NodeCache,
    biome_path: &BiomePath,
    settings: &SettingsWithEditor,
    file_source: JsFileSource,
) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
    let value_node = value.value().ok()?;
    let text_expression = value_node.as_html_attribute_single_text_expression()?;
    let expression = text_expression.expression().ok()?;
    let document_file_source = DocumentFileSource::Js(file_source);
    parse_text_expression(expression, cache, biome_path, settings, file_source)
        .map(|(snippet, _)| (snippet, document_file_source))
}

'''

content = content.replace(
    "parse_text_expression(expression, cache, biome_path, settings, file_source)
}

fn debug_syntax_tree",
    "parse_text_expression(expression, cache, biome_path, settings, file_source)
}

" + helpers + "fn debug_syntax_tree"
)

with open("/workspace/biome/crates/biome_service/src/file_handlers/html.rs", "w") as f:
    f.write(content)

print("html.rs updated")
