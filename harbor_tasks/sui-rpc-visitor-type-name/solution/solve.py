#!/usr/bin/env python3
"""Apply TypeName support changes to the Sui codebase."""

import re
import os

REPO = "/workspace/sui"

def modify_base_types():
    """Add TypeName constants and layout function to base_types.rs."""
    filepath = os.path.join(REPO, "crates/sui-types/src/base_types.rs")

    with open(filepath, "r") as f:
        content = f.read()

    # Add TypeName constants after RESOLVED_UTF8_STR
    type_name_constants = '''pub const RESOLVED_UTF8_STR: (&AccountAddress, &IdentStr, &IdentStr) = (
    &MOVE_STDLIB_ADDRESS,
    STD_UTF8_MODULE_NAME,
    STD_UTF8_STRUCT_NAME,
);

pub const STD_TYPE_NAME_MODULE_NAME: &IdentStr = ident_str!("type_name");
pub const STD_TYPE_NAME_STRUCT_NAME: &IdentStr = ident_str!("TypeName");
pub const RESOLVED_STD_TYPE_NAME: (&AccountAddress, &IdentStr, &IdentStr) = (
    &MOVE_STDLIB_ADDRESS,
    STD_TYPE_NAME_MODULE_NAME,
    STD_TYPE_NAME_STRUCT_NAME,
);'''

    # Replace the RESOLVED_UTF8_STR definition
    pattern = r'pub const RESOLVED_UTF8_STR: \(&AccountAddress, &IdentStr, &IdentStr\) = \(\s*&MOVE_STDLIB_ADDRESS,\s*STD_UTF8_MODULE_NAME,\s*STD_UTF8_STRUCT_NAME,\s*\);'
    content = re.sub(pattern, type_name_constants, content)

    # Add type_name_layout function after url_layout function
    type_name_layout_func = '''}

pub fn type_name_layout() -> A::MoveStructLayout {
    A::MoveStructLayout {
        type_: StructTag {
            address: MOVE_STDLIB_ADDRESS,
            module: STD_TYPE_NAME_MODULE_NAME.to_owned(),
            name: STD_TYPE_NAME_STRUCT_NAME.to_owned(),
            type_params: vec![],
        },
        fields: vec![A::MoveFieldLayout::new(
            ident_str!("name").into(),
            A::MoveTypeLayout::Struct(Box::new(move_ascii_str_layout())),
        )],
    }
}

// The Rust'''

    # Find url_layout function ending and add type_name_layout after it
    pattern = r'\}\s*\n\s*\/\/ The Rust representation of the Move `TxContext`'
    content = re.sub(pattern, type_name_layout_func, content)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Modified {filepath}")


def modify_rpc_visitor():
    """Add TypeName support to rpc_visitor/mod.rs."""
    filepath = os.path.join(REPO, "crates/sui-types/src/object/rpc_visitor/mod.rs")

    with open(filepath, "r") as f:
        content = f.read()

    # Add import for type_name_layout
    content = content.replace(
        "use crate::base_types::move_utf8_str_layout;",
        "use crate::base_types::move_utf8_str_layout;\nuse crate::base_types::type_name_layout;"
    )

    # Add type_name_layout to the condition check
    content = content.replace(
        "|| layout == &url_layout()",
        "|| layout == &type_name_layout()\n            || layout == &url_layout()"
    )

    # Update comment to include TypeName
    content = content.replace(
        "// 0x1::ascii::String or 0x1::string::String or 0x2::url::Url",
        "// 0x1::ascii::String or 0x1::string::String or 0x1::type_name::TypeName or 0x2::url::Url"
    )

    # Simplify json_ascii_string test
    content = content.replace(
        '''let l = struct_!("0x1::ascii::String" {
            "bytes": vector_!(L::U8)
        });''',
        "let l = A::MoveTypeLayout::Struct(Box::new(move_ascii_str_layout()));"
    )

    # Simplify json_utf8_string test
    content = content.replace(
        '''let l = struct_!("0x1::string::String" {
            "bytes": vector_!(L::U8)
        });''',
        "let l = A::MoveTypeLayout::Struct(Box::new(move_utf8_str_layout()));"
    )

    # Simplify json_url test
    content = content.replace(
        '''let l = struct_!("0x2::url::Url" {
            "url": struct_!("0x1::ascii::String" {
                "bytes": vector_!(L::U8)
            })
        });''',
        "let l = A::MoveTypeLayout::Struct(Box::new(url_layout()));"
    )

    # Add json_type_name test after json_utf8_string test
    json_type_name_test = '''    #[test]
    fn json_utf8_string() {
        let l = A::MoveTypeLayout::Struct(Box::new(move_utf8_str_layout()));
        let actual = json(l, "The quick brown fox");
        let expect = json!("The quick brown fox");
        assert_eq!(expect, actual);
    }

    #[test]
    fn json_type_name() {
        let l = A::MoveTypeLayout::Struct(Box::new(type_name_layout()));
        let actual = json(
            l,
            "0000000000000000000000000000000000000000000000000000000000000002::coin::Coin<0000000000000000000000000000000000000000000000000000000000000002::sui::SUI>",
        );
        let expect = json!(
            "0000000000000000000000000000000000000000000000000000000000000002::coin::Coin<0000000000000000000000000000000000000000000000000000000000000002::sui::SUI>"
        );
        assert_eq!(expect, actual);
    }'''

    content = content.replace(
        '''    #[test]
    fn json_utf8_string() {
        let l = A::MoveTypeLayout::Struct(Box::new(move_utf8_str_layout()));
        let actual = json(l, "The quick brown fox");
        let expect = json!("The quick brown fox");
        assert_eq!(expect, actual);
    }''',
        json_type_name_test
    )

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Modified {filepath}")


def modify_sui_display():
    """Add TypeName support to sui-display value.rs."""
    filepath = os.path.join(REPO, "crates/sui-display/src/v2/value.rs")

    with open(filepath, "r") as f:
        content = f.read()

    # Add import for type_name_layout
    content = content.replace(
        "use sui_types::base_types::move_utf8_str_layout;",
        "use sui_types::base_types::move_utf8_str_layout;\nuse sui_types::base_types::type_name_layout;"
    )

    # Add type_name_layout to special layouts array
    content = content.replace(
        """if [
                        move_ascii_str_layout(),
                        move_utf8_str_layout(),
                        url_layout(),""",
        """if [
                        move_ascii_str_layout(),
                        move_utf8_str_layout(),
                        type_name_layout(),
                        url_layout(),"""
    )

    # Add type_name_bytes after str_bytes
    content = content.replace(
        'let str_bytes = bcs::to_bytes("hello").unwrap();',
        '''let str_bytes = bcs::to_bytes("hello").unwrap();
        let type_name_bytes = bcs::to_bytes("0000000000000000000000000000000000000000000000000000000000000002::coin::Coin<0000000000000000000000000000000000000000000000000000000000000002::sui::SUI>").unwrap();'''
    )

    # Add type_name_layout variable after str_layout
    content = content.replace(
        "let str_layout = L::Struct(Box::new(move_utf8_str_layout()));",
        "let str_layout = L::Struct(Box::new(move_utf8_str_layout()));\n        let type_name_layout = L::Struct(Box::new(type_name_layout()));"
    )

    # Add TypeName test case after str test case - find the pattern
    old_slice = '''Value::Slice(Slice {
                layout: &str_layout,
                bytes: &str_bytes,
            }),'''

    new_slice = '''Value::Slice(Slice {
                layout: &str_layout,
                bytes: &str_bytes,
            }),
            Value::Slice(Slice {
                layout: &type_name_layout,
                bytes: &type_name_bytes,
            }),'''

    content = content.replace(old_slice, new_slice)

    # Add expected atom for type_name
    content = content.replace(
        'Atom::Bytes(Cow::Borrowed("hello".as_bytes())),',
        '''Atom::Bytes(Cow::Borrowed("hello".as_bytes())),
            Atom::Bytes(Cow::Borrowed("0000000000000000000000000000000000000000000000000000000000000002::coin::Coin<0000000000000000000000000000000000000000000000000000000000000002::sui::SUI>".as_bytes())),'''
    )

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Modified {filepath}")


if __name__ == "__main__":
    modify_base_types()
    modify_rpc_visitor()
    modify_sui_display()
    print("All modifications applied successfully")
