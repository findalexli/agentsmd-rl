#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "The XML schema accepts any string for `fontFamily`, but names outside this list " "skills/lark-slides/references/supported-fonts.md" && grep -qF "> **\u5b57\u4f53\u517c\u5bb9\u6027**\uff1a`fontFamily` \u7684 schema \u7c7b\u578b\u662f\u5b57\u7b26\u4e32\uff0c\u4f46\u672a\u5217\u5165 [supported-fonts.md](supported-fon" "skills/lark-slides/references/xml-schema-quick-ref.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-slides/references/supported-fonts.md b/skills/lark-slides/references/supported-fonts.md
@@ -0,0 +1,151 @@
+# Supported Fonts
+
+This document lists commonly supported `fontFamily` values for Lark Slides XML.
+Use these names in `<theme><textStyles>` or `<content fontFamily="...">`.
+
+The XML schema accepts any string for `fontFamily`, but names outside this list may render with a fallback font.
+
+## Common Chinese Fonts
+
+- 思源宋体
+- 寒蝉德黑体
+- 标小智无界黑
+- 寒蝉锦书宋
+- 站酷小薇体
+- 寒蝉团圆体 圆体
+- 寒蝉团圆体 黑体
+- 荆南缘默体
+- 寒蝉端黑宋
+- 资源圆体
+- 钟齐流江毛草
+- 寒蝉端黑体
+- 站酷庆科黄油体
+- 寒蝉云墨黑
+- 有字库龙藏体
+- 寒蝉全圆体
+- 思源黑体
+- 钟齐志莽行书
+- 抖音美好体
+- 马善政毛笔楷体
+- 霞鹜 975 圆体
+
+## Common Latin Fonts
+
+- Francois One
+- Heebo
+- Lobster
+- Roboto Slab
+- Varela Round
+- PT Serif
+- Signika
+- Vollkorn
+- Mulish
+- Rokkitt
+- Inconsolata
+- PT Sans Caption
+- EB Garamond
+- Dancing Script
+- Rajdhani
+- Poppins
+- Merriweather
+- PT Sans Narrow
+- Libre Baskerville
+- Slabo 27px
+- Inter
+- Noto Serif
+- Yanone Kaffeesatz
+- Merriweather Sans
+- Lato
+- Source Code Pro
+- Mukta
+- Teko
+- Hind Siliguri
+- Catamaran
+- Arvo
+- Alegreya Sans
+- Titillium Web
+- Roboto Mono
+- Play
+- Indie Flower
+- Ubuntu Condensed
+- Libre Franklin
+- Barlow
+- PT Sans
+- Acme
+- Cuprum
+- Josefin Sans
+- DM Sans
+- Playfair Display
+- Rubik
+- Questrial
+- Anton
+- Oswald
+- Cabin
+- Ubuntu
+- Abel
+- Exo 2
+- Bree Serif
+- Roboto Condensed
+- Amatic SC
+- Abril Fatface
+- Comfortaa
+- IBM Plex Sans
+- Work Sans
+- Kanit
+- Noto Sans
+- Alegreya
+- Shadows Into Light
+- Barlow Condensed
+- Nunito Sans
+- Quicksand
+- Overpass
+- Bebas Neue
+- Raleway
+- Exo
+- Archivo Narrow
+- Hind
+- Open Sans
+- Poiret One
+- Asap
+- Roboto
+- Nunito
+- Bitter
+- Dosis
+- Oxygen
+- Prompt
+- Karla
+- Fjalla One
+- Fira Sans
+- Crimson Text
+- Pacifico
+- Arimo
+- Maven Pro
+- Cairo
+- Montserrat
+- Righteous
+- Lora
+
+## Other Language Fonts
+
+- 源ノ角ゴシック
+- 본고딕
+- Nanum Gothic
+
+## System Fonts
+
+- Arial
+- Arial Black
+- Calibri
+- Comic Sans Ms
+- Sans Serif
+- Serif
+- Times New Roman
+- Tahoma
+- Trebuchet MS
+- Verdana
+- Georgia
+- Garamond
+- 黑体
+- 宋体
+- 楷体
+- Hiragino Mincho
diff --git a/skills/lark-slides/references/xml-schema-quick-ref.md b/skills/lark-slides/references/xml-schema-quick-ref.md
@@ -78,6 +78,9 @@ XSD 中的 `title`、`headline`、`sub-headline`、`body`、`caption` 主要出
 | `color` | 字体颜色 |
 | `bold` / `italic` / `underline` / `strikethrough` | 文本样式 |
 
+> **字体兼容性**：`fontFamily` 的 schema 类型是字符串，但未列入 [supported-fonts.md](supported-fonts.md) 的字体可能在服务端或渲染端回退为默认字体。生成 PPT 时优先选用清单内字体。
+> 常用默认字体：`思源黑体`（中文通用/默认）、`思源宋体`（中文正式/衬线）、`Inter`（拉丁通用）。
+
 `<content>` 的子元素只能是：
 
 - `<p>`
PATCH

echo "Gold patch applied."
