use biome_markdown_formatter::{MdFormatLanguage, context::MdFormatOptions};
use biome_markdown_parser::parse_markdown;

fn format_markdown(source: &str) -> String {
    let parse = parse_markdown(source);
    let options = MdFormatOptions::default();
    let result = biome_formatter::format_node(&parse.syntax(), MdFormatLanguage::new(options), false);
    let formatted = result.unwrap();
    formatted.print().unwrap().as_code().to_string()
}

#[test]
fn test_single_last_hardline() {
    // Single-line paragraph ending with hard line break (two spaces)
    // The trailing spaces should be removed since it's the end of the paragraph
    let source = "Hello world  ";
    let result = format_markdown(source);
    // The formatted output should NOT have trailing two spaces
    // since the hard line break is at the end of the paragraph
    assert!(
        !result.ends_with("  \n"),
        "Trailing hard line break should be removed from end of paragraph. Got: {:?}",
        result
    );
    // Should still have the text content
    assert!(result.contains("Hello world"), "Content should be preserved. Got: {:?}", result);
}

#[test]
fn test_multi_last_hardline() {
    // Multi-line paragraph with hard line breaks
    // Middle hard lines should keep "  ", but the last one should be removed
    let source = "Line one  \nLine two  ";
    let result = format_markdown(source);

    // Count lines to verify structure
    let lines: Vec<&str> = result.lines().collect();

    // The last line of the paragraph should not have trailing "  "
    // (paragraph ends at blank line or EOF)
    let last_content_line = lines.iter().rev()
        .find(|l| !l.trim().is_empty())
        .copied()
        .unwrap_or("");

    assert!(
        !last_content_line.ends_with("  "),
        "Last hard line break should be removed. Last line: {:?}, Full output: {:?}",
        last_content_line, result
    );
}

#[test]
fn test_varied_last_hardline() {
    // Different content to prevent hardcoded solutions
    let source = "Different text content here  ";
    let result = format_markdown(source);

    // Should not have trailing hard line break at end of paragraph
    assert!(
        !result.ends_with("  \n"),
        "Trailing hard line break should be removed from end of paragraph. Got: {:?}",
        result
    );
    assert!(
        !result.trim_end().ends_with("  "),
        "Trailing spaces should be removed. Got: {:?}",
        result
    );
}
