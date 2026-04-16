#!/bin/bash
set -e
cd /workspace/biome

# Fix 1: In parse_inline_link_tail, inside the "if has_title" block,
# add whitespace consumer after parse_title_content, and remove the
# trailing whitespace skip loop after the if block.
python3 << 'PYTHON_SCRIPT'
import re

links_path = "crates/biome_markdown_parser/src/syntax/inline/links.rs"
with open(links_path) as f:
    content = f.read()

# Add whitespace consumer inside if has_title block, after parse_title_content
old_if_block = '''    if has_title {
        let title_m = p.start();
        let list_m = p.start();
        parse_title_content(p, get_title_close_char(p));
        list_m.complete(p, MD_INLINE_ITEM_LIST);
        title_m.complete(p, MD_LINK_TITLE);
    }'''

new_if_block = '''    if has_title {
        let title_m = p.start();
        let list_m = p.start();
        parse_title_content(p, get_title_close_char(p));
        // Consume trailing whitespace/newlines into the title's content list so the
        // bytes are properly accounted for in the tree. Without this, the whitespace
        // would be absorbed into the R_PAREN token range (see #9640).
        while is_title_separator_token(p) {
            bump_link_def_separator(p);
        }
        list_m.complete(p, MD_INLINE_ITEM_LIST);
        title_m.complete(p, MD_LINK_TITLE);
    }'''

content = content.replace(old_if_block, new_if_block)

# Remove the trailing whitespace skip loop
old_skip_loop = '''
    // Skip trailing whitespace/newlines before closing paren without creating nodes
    // (creating nodes would violate the MD_INLINE_LINK grammar which expects exactly 7 children)
    while is_title_separator_token(p) {
        skip_link_def_separator_tokens(p);
    }

    if !p.eat(R_PAREN) {'''

new_skip_loop = '''
    if !p.eat(R_PAREN) {'''

content = content.replace(old_skip_loop, new_skip_loop)

# Remove the skip_link_def_separator_tokens function
old_fn = '''
fn skip_link_def_separator_tokens(p: &mut MarkdownParser) {
    if p.at(NEWLINE) {
        p.bump(NEWLINE);
    } else {
        p.bump_link_definition();
    }
}

fn is_title_separator_token'''

new_fn = '''
fn is_title_separator_token'''

content = content.replace(old_fn, new_fn)

with open(links_path, "w") as f:
    f.write(content)

print("links.rs patched successfully")
PYTHON_SCRIPT

# Fix 2: Update the snapshot file
python3 << 'PYTHON_SCRIPT'
import re

snap_path = "crates/biome_markdown_parser/tests/md_test_suite/ok/inline_link_whitespace.md.snap"
with open(snap_path) as f:
    content = f.read()

# First occurrence: in the first inline link entry (around line 72)
# Change: add MdTextual whitespace entry, change R_PAREN
old_snap1 = '''                            MdTextual {
                                value_token: MD_TEXTUAL_LITERAL@58..65 "\\"title\\"" [] [],
                            },
                        ],
                    },
                    r_paren_token: R_PAREN@65..68 "  )" [] [],'''

new_snap1 = '''                            MdTextual {
                                value_token: MD_TEXTUAL_LITERAL@58..65 "\\"title\\"" [] [],
                            },
                            MdTextual {
                                value_token: MD_TEXTUAL_LITERAL@65..67 "  " [] [],
                            },
                        ],
                    },
                    r_paren_token: R_PAREN@67..68 ")" [] [],'''

content = content.replace(old_snap1, new_snap1)

# Second occurrence: in the second inline link entry (around line 283)
old_snap2 = '''          5: MD_LINK_TITLE@58..65
            0: MD_INLINE_ITEM_LIST@58..65
              0: MD_TEXTUAL@58..65
                0: MD_TEXTUAL_LITERAL@58..65 "\\"title\\"" [] []
          6: R_PAREN@65..68 "  )" [] []'''

new_snap2 = '''          5: MD_LINK_TITLE@58..67
            0: MD_INLINE_ITEM_LIST@58..67
              0: MD_TEXTUAL@58..65
                0: MD_TEXTUAL_LITERAL@58..65 "\\"title\\"" [] []
              1: MD_TEXTUAL@65..67
                0: MD_TEXTUAL_LITERAL@65..67 "  " [] []
          6: R_PAREN@67..68 ")" [] []'''

content = content.replace(old_snap2, new_snap2)

with open(snap_path, "w") as f:
    f.write(content)

print("snapshot updated successfully")
PYTHON_SCRIPT

# Build the fixed code
cargo build -p biome_markdown_parser
