#!/bin/bash
set -e

cd /workspace/sui

# Check if patch is already applied (idempotency check)
if grep -q "pub fn type_name_layout()" crates/sui-types/src/base_types.rs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

echo "Applying type_name_layout to base_types.rs..."

# Add the constants after RESOLVED_UTF8_STR
sed -i '/^pub const RESOLVED_UTF8_STR/,/);/{ /);/a\
\
pub const STD_TYPE_NAME_MODULE_NAME: \&IdentStr = ident_str!("type_name");\
pub const STD_TYPE_NAME_STRUCT_NAME: \&IdentStr = ident_str!("TypeName");\
pub const RESOLVED_STD_TYPE_NAME: (\&AccountAddress, \&IdentStr, \&IdentStr) = (\
    \&MOVE_STDLIB_ADDRESS,\
    STD_TYPE_NAME_MODULE_NAME,\
    STD_TYPE_NAME_STRUCT_NAME,\
);
}' crates/sui-types/src/base_types.rs

# Add type_name_layout function after url_layout function
sed -i '/^pub fn url_layout() -> A::MoveStructLayout {/,/^}$/{ /^}$/a\
\
pub fn type_name_layout() -> A::MoveStructLayout {\
    A::MoveStructLayout {\
        type_: StructTag {\
            address: MOVE_STDLIB_ADDRESS,\
            module: STD_TYPE_NAME_MODULE_NAME.to_owned(),\
            name: STD_TYPE_NAME_STRUCT_NAME.to_owned(),\
            type_params: vec![],\
        },\
        fields: vec![A::MoveFieldLayout::new(\
            ident_str!("name").into(),\
            A::MoveTypeLayout::Struct(Box::new(move_ascii_str_layout())),\
        )],\
    }\
}
}' crates/sui-types/src/base_types.rs

echo "Applying type_name_layout import to rpc_visitor/mod.rs..."

# Add import for type_name_layout
sed -i '/use crate::base_types::move_utf8_str_layout;/a\use crate::base_types::type_name_layout;' crates/sui-types/src/object/rpc_visitor/mod.rs

# Add type_name_layout to the condition check
sed -i 's/|| layout == &url_layout()/|| layout == \&type_name_layout()\n            || layout == \&url_layout()/' crates/sui-types/src/object/rpc_visitor/mod.rs

# Update the comment
sed -i 's/\/\/ 0x1::ascii::String or 0x1::string::String or 0x2::url::Url/\/\/ 0x1::ascii::String or 0x1::string::String or 0x1::type_name::TypeName or 0x2::url::Url/' crates/sui-types/src/object/rpc_visitor/mod.rs

echo "Applying type_name_layout to sui-display value.rs..."

# Add import for type_name_layout in sui-display
sed -i '/use sui_types::base_types::move_utf8_str_layout;/a\use sui_types::base_types::type_name_layout;' crates/sui-display/src/v2/value.rs

# Add type_name_layout to the special layouts list in the TryFrom impl
sed -i '/move_utf8_str_layout(),/a\                        type_name_layout(),' crates/sui-display/src/v2/value.rs

echo "All patches applied successfully!"
