"""Behavioral checks for hermes-agent-featskills-add-baoyucomic-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/PORT_NOTES.md')
    assert '- **Character sheet PNG** is still generated for multi-page comics, but it is repositioned as a **human-facing review artifact** (for visual verification) and a reference for later regenerations / man' in text, "expected to find: " + '- **Character sheet PNG** is still generated for multi-page comics, but it is repositioned as a **human-facing review artifact** (for visual verification) and a reference for later regenerations / man'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/PORT_NOTES.md')
    assert "Art-style, tone, and layout reference files can usually be overwritten directly (they're upstream-verbatim). `SKILL.md`, `references/workflow.md`, `references/partial-workflows.md`, `references/auto-s" in text, "expected to find: " + "Art-style, tone, and layout reference files can usually be overwritten directly (they're upstream-verbatim). `SKILL.md`, `references/workflow.md`, `references/partial-workflows.md`, `references/auto-s"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/PORT_NOTES.md')
    assert "`image_generate`'s schema accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`). Upstream's reference-image flow (`--ref characters.png` for character consistency, plus user-s" in text, "expected to find: " + "`image_generate`'s schema accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`). Upstream's reference-image flow (`--ref characters.png` for character consistency, plus user-s"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/SKILL.md')
    assert '**7.1 Character sheet** — generate it (to `characters/characters.png`, aspect `landscape`) when the comic is multi-page with recurring characters. Skip for simple presets (e.g., four-panel minimalist)' in text, "expected to find: " + '**7.1 Character sheet** — generate it (to `characters/characters.png`, aspect `landscape`) when the comic is multi-page with recurring characters. Skip for simple presets (e.g., four-panel minimalist)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/SKILL.md')
    assert "**7.2 Pages** — each page's prompt MUST already be at `prompts/NN-{cover|page}-[slug].md` before invoking `image_generate`. Because `image_generate` is prompt-only, character consistency is enforced b" in text, "expected to find: " + "**7.2 Pages** — each page's prompt MUST already be at `prompts/NN-{cover|page}-[slug].md` before invoking `image_generate`. Because `image_generate` is prompt-only, character consistency is enforced b"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/SKILL.md')
    assert 'Trigger this skill when the user asks to create a knowledge/educational comic, biography comic, tutorial comic, or uses terms like "知识漫画", "教育漫画", or "Logicomix-style". The user provides content (text' in text, "expected to find: " + 'Trigger this skill when the user asks to create a knowledge/educational comic, biography comic, tutorial comic, or uses terms like "知识漫画", "教育漫画", or "Logicomix-style". The user provides content (text'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/analysis-framework.md')
    assert '1. **YAML Front Matter**: Metadata (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone, recommended_layout)' in text, "expected to find: " + '1. **YAML Front Matter**: Metadata (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone, recommended_layout)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/analysis-framework.md')
    assert '| `user_language` | Output language for comic (user-specified option > conversation language > source_language) |' in text, "expected to find: " + '| `user_language` | Output language for comic (user-specified option > conversation language > source_language) |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/analysis-framework.md')
    assert 'Deep analysis framework for transforming source content into effective visual storytelling.' in text, "expected to find: " + 'Deep analysis framework for transforming source content into effective visual storytelling.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/chalk.md')
    assert 'Classic classroom chalkboard aesthetic with hand-drawn chalk illustrations. Nostalgic educational feel with imperfect, sketchy lines that capture the warmth of traditional teaching.' in text, "expected to find: " + 'Classic classroom chalkboard aesthetic with hand-drawn chalk illustrations. Nostalgic educational feel with imperfect, sketchy lines that capture the warmth of traditional teaching.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/chalk.md')
    assert 'Educational content, tutorials, classroom themes, teaching materials, workshops, informal learning, knowledge sharing' in text, "expected to find: " + 'Educational content, tutorials, classroom themes, teaching materials, workshops, informal learning, knowledge sharing'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/chalk.md')
    assert '- Chalkboard Black (#1A1A1A) or Dark Green-Black (#1C2B1C)' in text, "expected to find: " + '- Chalkboard Black (#1A1A1A) or Dark Green-Black (#1C2B1C)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ink-brush.md')
    assert 'Traditional Chinese ink brush painting style adapted for comics. Combines calligraphic brush strokes with ink wash effects. Creates atmospheric, artistic visuals rooted in East Asian aesthetics.' in text, "expected to find: " + 'Traditional Chinese ink brush painting style adapted for comics. Combines calligraphic brush strokes with ink wash effects. Creates atmospheric, artistic visuals rooted in East Asian aesthetics.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ink-brush.md')
    assert 'Chinese historical stories, martial arts, traditional tales, contemplative narratives, artistic adaptations' in text, "expected to find: " + 'Chinese historical stories, martial arts, traditional tales, contemplative narratives, artistic adaptations'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ink-brush.md')
    assert '水墨画风 - Chinese ink brush aesthetics with dynamic strokes' in text, "expected to find: " + '水墨画风 - Chinese ink brush aesthetics with dynamic strokes'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ligne-claire.md')
    assert "Classic European comic style originating from Hergé's Tintin. Characterized by clean, uniform outlines and flat color fills without gradients. Creates a timeless, accessible aesthetic suitable for edu" in text, "expected to find: " + "Classic European comic style originating from Hergé's Tintin. Characterized by clean, uniform outlines and flat color fills without gradients. Creates a timeless, accessible aesthetic suitable for edu"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ligne-claire.md')
    assert 'Educational content, balanced narratives, biography comics, historical stories' in text, "expected to find: " + 'Educational content, balanced narratives, biography comics, historical stories'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/ligne-claire.md')
    assert '- Slightly stylized/cartoonish characters with realistic proportions' in text, "expected to find: " + '- Slightly stylized/cartoonish characters with realistic proportions'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/manga.md')
    assert 'Japanese manga art style characterized by large expressive eyes, dynamic poses, and visual emotion indicators. Versatile style that works across genres from educational to romantic to action.' in text, "expected to find: " + 'Japanese manga art style characterized by large expressive eyes, dynamic poses, and visual emotion indicators. Versatile style that works across genres from educational to romantic to action.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/manga.md')
    assert 'Educational tutorials, romance, action, coming-of-age, technical explanations, youth-oriented content' in text, "expected to find: " + 'Educational tutorials, romance, action, coming-of-age, technical explanations, youth-oriented content'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/manga.md')
    assert '- Clear emotional indicators (！, ？, sweat drops, sparkles)' in text, "expected to find: " + '- Clear emotional indicators (！, ？, sweat drops, sparkles)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/minimalist.md')
    assert 'Minimalist cartoon illustration characterized by clean black line art on white background with very limited spot color for emphasis. Characters are simplified to near-stick-figure abstraction, focusin' in text, "expected to find: " + 'Minimalist cartoon illustration characterized by clean black line art on white background with very limited spot color for emphasis. Characters are simplified to near-stick-figure abstraction, focusin'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/minimalist.md')
    assert 'Business allegory, management fables, short concept illustration, four-panel comic strips, quick-insight education, social media content' in text, "expected to find: " + 'Business allegory, management fables, short concept illustration, four-panel comic strips, quick-insight education, social media content'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/minimalist.md')
    assert '- Accent color used sparingly: highlighting key objects, text labels, concept indicators' in text, "expected to find: " + '- Accent color used sparingly: highlighting key objects, text labels, concept indicators'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/realistic.md')
    assert 'Full-color realistic manga style using digital painting techniques. Features anatomically accurate characters, rich gradients, and detailed environmental rendering. Sophisticated aesthetic for mature ' in text, "expected to find: " + 'Full-color realistic manga style using digital painting techniques. Features anatomically accurate characters, rich gradients, and detailed environmental rendering. Sophisticated aesthetic for mature '[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/realistic.md')
    assert 'Professional topics (wine, food, business), lifestyle content, adult narratives, documentary-style, mature educational guides' in text, "expected to find: " + 'Professional topics (wine, food, business), lifestyle content, adult narratives, documentary-style, mature educational guides'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/art-styles/realistic.md')
    assert '写实画风 - Digital painting with realistic proportions and lighting' in text, "expected to find: " + '写实画风 - Digital painting with realistic proportions and lighting'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/auto-selection.md')
    assert '- **Triggers**: Psychology, motivation, self-help, business narrative, management, leadership, personal growth, coaching, soft skills, abstract concept through story' in text, "expected to find: " + '- **Triggers**: Psychology, motivation, self-help, business narrative, management, leadership, personal growth, coaching, soft skills, abstract concept through story'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/auto-selection.md')
    assert '- **Triggers**: Business allegory, fable, parable, short insight, four-panel, 四格, 四格漫画, single-page comic, minimalist comic strip' in text, "expected to find: " + '- **Triggers**: Business allegory, fable, parable, short insight, four-panel, 四格, 四格漫画, single-page comic, minimalist comic strip'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/auto-selection.md')
    assert '**Note**: Art Style × Tone × Layout can be freely combined. Incompatible combinations work but may produce unexpected results.' in text, "expected to find: " + '**Note**: Art Style × Tone × Layout can be freely combined. Incompatible combinations work but may produce unexpected results.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/base-prompt.md')
    assert "- Camera angles vary: eye level, bird's eye, low angle, close-up, wide shot" in text, "expected to find: " + "- Camera angles vary: eye level, bird's eye, low angle, close-up, wide shot"[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/base-prompt.md')
    assert '- All text in Chinese (中文) unless source material is in another language' in text, "expected to find: " + '- All text in Chinese (中文) unless source material is in another language'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/base-prompt.md')
    assert '- Research period-specific details: costumes, technology, architecture' in text, "expected to find: " + '- Research period-specific details: costumes, technology, architecture'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/character-template.md')
    assert '- Front view: Young man, 30s, short dark wavy hair, thoughtful expression, wearing tweed jacket with elbow patches, white shirt' in text, "expected to find: " + '- Front view: Young man, 30s, short dark wavy hair, thoughtful expression, wearing tweed jacket with elbow patches, white shirt'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/character-template.md')
    assert 'Without unified character definition, AI generates inconsistent appearances. The reference sheet provides:' in text, "expected to find: " + 'Without unified character definition, AI generates inconsistent appearances. The reference sheet provides:'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/character-template.md')
    assert '- Expressions: Processing (spinning dials) | Success (lights up) | Stuck (smoke wisps)' in text, "expected to find: " + '- Expressions: Processing (spinning dials) | Success (lights up) | Stuck (smoke wisps)'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/cinematic.md')
    assert '- **Structure**: Horizontal emphasis, wide aspect panels' in text, "expected to find: " + '- **Structure**: Horizontal emphasis, wide aspect panels'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/cinematic.md')
    assert 'Establishing shots, dramatic moments, landscapes' in text, "expected to find: " + 'Establishing shots, dramatic moments, landscapes'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/cinematic.md')
    assert '- Reading flow: Horizontal sweep, filmic rhythm' in text, "expected to find: " + '- Reading flow: Horizontal sweep, filmic rhythm'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/dense.md')
    assert 'Technical explanations, complex narratives, timelines' in text, "expected to find: " + 'Technical explanations, complex narratives, timelines'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/dense.md')
    assert '- Reading flow: Rapid progression, information-rich' in text, "expected to find: " + '- Reading flow: Rapid progression, information-rich'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/dense.md')
    assert '- **Structure**: Compact grid, smaller panels' in text, "expected to find: " + '- **Structure**: Compact grid, smaller panels'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/four-panel.md')
    assert '- Reading flow: Z-pattern — Panel 1 (top-left) → Panel 2 (top-right) → Panel 3 (bottom-left) → Panel 4 (bottom-right)' in text, "expected to find: " + '- Reading flow: Z-pattern — Panel 1 (top-left) → Panel 2 (top-right) → Panel 3 (bottom-left) → Panel 4 (bottom-right)'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/four-panel.md')
    assert 'Business allegory, quick-insight education, social media comics, fables, parables, single-concept explanation' in text, "expected to find: " + 'Business allegory, quick-insight education, social media comics, fables, parables, single-concept explanation'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/four-panel.md')
    assert '| 3 | Bottom-left | 转 Turn | Twist, key insight, or reversal — the pivotal moment |' in text, "expected to find: " + '| 3 | Bottom-left | 转 Turn | Twist, key insight, or reversal — the pivotal moment |'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/mixed.md')
    assert 'Action sequences, emotional arcs, complex stories' in text, "expected to find: " + 'Action sequences, emotional arcs, complex stories'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/mixed.md')
    assert '- **Structure**: Intentionally varied for pacing' in text, "expected to find: " + '- **Structure**: Intentionally varied for pacing'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/mixed.md')
    assert '- Reading flow: Guides eye through varied rhythm' in text, "expected to find: " + '- Reading flow: Guides eye through varied rhythm'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/splash.md')
    assert '- Reading flow: Splash dominates, supporting panels accent' in text, "expected to find: " + '- Reading flow: Splash dominates, supporting panels accent'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/splash.md')
    assert '- **Structure**: Dominant splash with supporting panels' in text, "expected to find: " + '- **Structure**: Dominant splash with supporting panels'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/splash.md')
    assert '- Panel sizes: 50-70% splash, remainder small' in text, "expected to find: " + '- Panel sizes: 50-70% splash, remainder small'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/standard.md')
    assert '- **Structure**: Regular grid with occasional variation' in text, "expected to find: " + '- **Structure**: Regular grid with occasional variation'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/standard.md')
    assert '- Reading flow: Left→right, top→bottom (Z-pattern)' in text, "expected to find: " + '- Reading flow: Left→right, top→bottom (Z-pattern)'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/standard.md')
    assert '- Panel sizes: Mostly equal, occasional variation' in text, "expected to find: " + '- Panel sizes: Mostly equal, occasional variation'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/webtoon.md')
    assert '- **Gutters**: Generous vertical spacing (20-40px), panels often bleed horizontally' in text, "expected to find: " + '- **Gutters**: Generous vertical spacing (20-40px), panels often bleed horizontally'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/webtoon.md')
    assert '- **Structure**: Single column, vertical flow optimized for scrolling' in text, "expected to find: " + '- **Structure**: Single column, vertical flow optimized for scrolling'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/layouts/webtoon.md')
    assert '- Panel sizes: Full width, variable height (1:1 to 1:2 aspect)' in text, "expected to find: " + '- Panel sizes: Full width, variable height (1:1 to 1:2 aspect)'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/ohmsha-guide.md')
    assert 'Custom characters: ask the user for role → name mappings (e.g., `Student:小明, Mentor:教授, Antagonist:Bug怪`).' in text, "expected to find: " + 'Custom characters: ask the user for role → name mappings (e.g., `Student:小明, Mentor:教授, Antagonist:Bug怪`).'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/ohmsha-guide.md')
    assert '| Antagonist (Role C, optional) | 胖虎 | Represents misunderstanding, or "noise" in the data |' in text, "expected to find: " + '| Antagonist (Role C, optional) | 胖虎 | Represents misunderstanding, or "noise" in the data |'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/ohmsha-guide.md')
    assert '| Student (Role A) | 大雄 | Confused, asks basic but crucial questions, represents reader |' in text, "expected to find: " + '| Student (Role A) | 大雄 | Confused, asks basic but crucial questions, represents reader |'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/partial-workflows.md')
    assert 'Options to run specific parts of the workflow. Trigger these via natural language (e.g., "just the storyboard", "regenerate page 3").' in text, "expected to find: " + 'Options to run specific parts of the workflow. Trigger these via natural language (e.g., "just the storyboard", "regenerate page 3").'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/partial-workflows.md')
    assert '**User cue**: "generate images from existing prompts", "run the images now" (pointing at an existing `comic/topic-slug/` directory).' in text, "expected to find: " + '**User cue**: "generate images from existing prompts", "run the images now" (pointing at an existing `comic/topic-slug/` directory).'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/partial-workflows.md')
    assert '- `characters/characters.md` (for agent-side consistency checks, if it was used originally)' in text, "expected to find: " + '- `characters/characters.md` (for agent-side consistency checks, if it was used originally)'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/concept-story.md')
    assert "**IMPORTANT**: Characters are created fresh each time based on the source content's domain (business, psychology, education, etc.). No default character set." in text, "expected to find: " + "**IMPORTANT**: Characters are created fresh each time based on the source content's domain (business, psychology, education, etc.). No default character set."[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/concept-story.md')
    assert '**Unlike ohmsha**: Dialogue panels are allowed and expected. The goal is to COMBINE visual metaphors WITH dialogue, not replace dialogue entirely.' in text, "expected to find: " + '**Unlike ohmsha**: Dialogue panels are allowed and expected. The goal is to COMBINE visual metaphors WITH dialogue, not replace dialogue entirely.'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/concept-story.md')
    assert 'This preset includes special rules beyond the art+tone combination. When the `concept-story` preset is selected, ALL rules below must be applied.' in text, "expected to find: " + 'This preset includes special rules beyond the art+tone combination. When the `concept-story` preset is selected, ALL rules below must be applied.'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/four-panel.md')
    assert '> A minimalist, clean line art digital comic strip in a four-panel grid layout (2×2). The style is simplified cartoon illustration with clear black outlines and a minimal color palette of black, white' in text, "expected to find: " + '> A minimalist, clean line art digital comic strip in a four-panel grid layout (2×2). The style is simplified cartoon illustration with clear black outlines and a minimal color palette of black, white'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/four-panel.md')
    assert '| 3 (转 Turn) | The twist or key insight | **Most important panel.** Show the unexpected reversal, contrast, or "aha" moment that makes the allegory work |' in text, "expected to find: " + '| 3 (转 Turn) | The twist or key insight | **Most important panel.** Show the unexpected reversal, contrast, or "aha" moment that makes the allegory work |'[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/four-panel.md')
    assert 'Business allegory, management fables, short insights, workplace parables, concept contrasts, social media educational content, quick-read comics' in text, "expected to find: " + 'Business allegory, management fables, short insights, workplace parables, concept contrasts, social media educational content, quick-read comics'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/ohmsha.md')
    assert '**IMPORTANT**: These Doraemon characters ARE the default for ohmsha preset. Generate character definitions using these exact characters unless user requests otherwise.' in text, "expected to find: " + '**IMPORTANT**: These Doraemon characters ARE the default for ohmsha preset. Generate character definitions using these exact characters unless user requests otherwise.'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/ohmsha.md')
    assert '| Student (Role A) | 大雄 (Nobita) | Boy, 10yo, round glasses, black hair, yellow shirt, navy shorts | Confused, asks basic but crucial questions, represents reader |' in text, "expected to find: " + '| Student (Role A) | 大雄 (Nobita) | Boy, 10yo, round glasses, black hair, yellow shirt, navy shorts | Confused, asks basic but crucial questions, represents reader |'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/ohmsha.md')
    assert '| Mentor (Role B) | 哆啦A梦 (Doraemon) | Blue robot cat, white belly, 4D pocket, red nose, golden bell | Knowledgeable, patient, uses gadgets as technical metaphors |' in text, "expected to find: " + '| Mentor (Role B) | 哆啦A梦 (Doraemon) | Blue robot cat, white belly, 4D pocket, red nose, golden bell | Knowledgeable, patient, uses gadgets as technical metaphors |'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/shoujo.md')
    assert 'This preset includes special rules beyond the art+tone combination. When the `shoujo` preset is selected, ALL rules below must be applied.' in text, "expected to find: " + 'This preset includes special rules beyond the art+tone combination. When the `shoujo` preset is selected, ALL rules below must be applied.'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/shoujo.md')
    assert 'Romance stories, coming-of-age, friendship narratives, school life, emotional drama, love stories' in text, "expected to find: " + 'Romance stories, coming-of-age, friendship narratives, school life, emotional drama, love stories'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/shoujo.md')
    assert 'Every emotional moment must include decorative elements:' in text, "expected to find: " + 'Every emotional moment must include decorative elements:'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/wuxia.md')
    assert 'This preset includes special rules beyond the art+tone combination. When the `wuxia` preset is selected, ALL rules below must be applied.' in text, "expected to find: " + 'This preset includes special rules beyond the art+tone combination. When the `wuxia` preset is selected, ALL rules below must be applied.'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/wuxia.md')
    assert 'Martial arts stories, Chinese historical fiction, wuxia/xianxia adaptations, action-heavy narratives' in text, "expected to find: " + 'Martial arts stories, Chinese historical fiction, wuxia/xianxia adaptations, action-heavy narratives'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/presets/wuxia.md')
    assert 'Martial arts power must be visible through qi effects:' in text, "expected to find: " + 'Martial arts power must be visible through qi effects:'[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/storyboard-template.md')
    assert '- Composition hinting at core theme (character silhouette, iconic symbol, concept diagram)' in text, "expected to find: " + '- Composition hinting at core theme (character silhouette, iconic symbol, concept diagram)'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/storyboard-template.md')
    assert 'aspect_ratio: "3:4"    # 3:4 (portrait), 4:3 (landscape), 16:9 (widescreen)' in text, "expected to find: " + 'aspect_ratio: "3:4"    # 3:4 (portrait), 4:3 (landscape), 16:9 (widescreen)'[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/storyboard-template.md')
    assert "- Camera angle: [bird's eye / low angle / eye level / close-up / wide shot]" in text, "expected to find: " + "- Camera angle: [bird's eye / low angle / eye level / close-up / wide shot]"[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/action.md')
    assert 'High-impact action atmosphere with dynamic movement, combat effects, and powerful visual energy. Creates visceral, exciting sequences.' in text, "expected to find: " + 'High-impact action atmosphere with dynamic movement, combat effects, and powerful visual energy. Creates visceral, exciting sequences.'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/action.md')
    assert '| Physical impacts | Radiating lines, debris |' in text, "expected to find: " + '| Physical impacts | Radiating lines, debris |'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/action.md')
    assert '| Flying debris | Environmental destruction |' in text, "expected to find: " + '| Flying debris | Environmental destruction |'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/dramatic.md')
    assert 'High-impact dramatic tone for pivotal moments, conflicts, and breakthroughs. Uses strong contrast and intense compositions to create emotional power.' in text, "expected to find: " + 'High-impact dramatic tone for pivotal moments, conflicts, and breakthroughs. Uses strong contrast and intense compositions to create emotional power.'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/dramatic.md')
    assert '| Brightness | Strong highlights, deep shadows |' in text, "expected to find: " + '| Brightness | Strong highlights, deep shadows |'[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/dramatic.md')
    assert '戏剧基调 - High contrast, intense, powerful moments' in text, "expected to find: " + '戏剧基调 - High contrast, intense, powerful moments'[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/energetic.md')
    assert 'High-energy atmosphere for exciting, discovery-filled content. Bright colors, dynamic compositions, and movement create engaging visuals for younger audiences.' in text, "expected to find: " + 'High-energy atmosphere for exciting, discovery-filled content. Bright colors, dynamic compositions, and movement create engaging visuals for younger audiences.'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/energetic.md')
    assert '| Background Alt | Bright pastels | Various |' in text, "expected to find: " + '| Background Alt | Bright pastels | Various |'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/energetic.md')
    assert '| Primary Yellow | Sunny yellow | #F6E05E |' in text, "expected to find: " + '| Primary Yellow | Sunny yellow | #F6E05E |'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/neutral.md')
    assert 'Default balanced tone suitable for educational and informative content. Neither overly emotional nor cold - creates accessible, professional atmosphere.' in text, "expected to find: " + 'Default balanced tone suitable for educational and informative content. Neither overly emotional nor cold - creates accessible, professional atmosphere.'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/neutral.md')
    assert 'Neutral is the default tone. Combine with any art style for baseline professional output. Most versatile tone option.' in text, "expected to find: " + 'Neutral is the default tone. Combine with any art style for baseline professional output. Most versatile tone option.'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/neutral.md')
    assert '中性基调 - Balanced, rational, educational' in text, "expected to find: " + '中性基调 - Balanced, rational, educational'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/romantic.md')
    assert 'Soft, dreamy atmosphere for romantic and emotionally delicate content. Features decorative elements, sparkles, and beautiful compositions that emphasize feeling and beauty.' in text, "expected to find: " + 'Soft, dreamy atmosphere for romantic and emotionally delicate content. Features decorative elements, sparkles, and beautiful compositions that emphasize feeling and beauty.'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/romantic.md')
    assert '**Essential decorations** (add to compositions):' in text, "expected to find: " + '**Essential decorations** (add to compositions):'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/romantic.md')
    assert '浪漫基调 - Soft, beautiful, emotionally delicate' in text, "expected to find: " + '浪漫基调 - Soft, beautiful, emotionally delicate'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/vintage.md')
    assert 'Historical atmosphere with aged paper effects and period-appropriate aesthetics. Creates sense of time, authenticity, and historical distance.' in text, "expected to find: " + 'Historical atmosphere with aged paper effects and period-appropriate aesthetics. Creates sense of time, authenticity, and historical distance.'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/vintage.md')
    assert '复古基调 - Historical, aged, period authenticity' in text, "expected to find: " + '复古基调 - Historical, aged, period authenticity'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/vintage.md')
    assert '- chalk: style mismatch (modern educational)' in text, "expected to find: " + '- chalk: style mismatch (modern educational)'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/warm.md')
    assert 'Warm, inviting atmosphere for personal stories and nostalgic content. Creates emotional connection through cozy aesthetics and comforting visuals.' in text, "expected to find: " + 'Warm, inviting atmosphere for personal stories and nostalgic content. Creates emotional connection through cozy aesthetics and comforting visuals.'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/warm.md')
    assert '- Nostalgic props (old photos, keepsakes)' in text, "expected to find: " + '- Nostalgic props (old photos, keepsakes)'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/tones/warm.md')
    assert '- Nature elements (autumn leaves, sunset)' in text, "expected to find: " + '- Nature elements (autumn leaves, sunset)'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/workflow.md')
    assert '**Important**: the downloaded sheet is a **human-facing review artifact** (so the user can visually verify character design) and a reference for later regenerations or manual prompt edits. It does **n' in text, "expected to find: " + '**Important**: the downloaded sheet is a **human-facing review artifact** (so the user can visually verify character design) and a reference for later regenerations or manual prompt edits. It does **n'[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/workflow.md')
    assert '**analysis.md Format**: YAML front matter (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone) + sections for Target Audie' in text, "expected to find: " + '**analysis.md Format**: YAML front matter (title, topic, time_span, source_language, user_language, aspect_ratio, recommended_page_count, recommended_art, recommended_tone) + sections for Target Audie'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/creative/baoyu-comic/references/workflow.md')
    assert 'With confirmed prompts from Step 5/6, use the `image_generate` tool. The tool accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`) and **returns a URL** — it does not accept ' in text, "expected to find: " + 'With confirmed prompts from Step 5/6, use the `image_generate` tool. The tool accepts only `prompt` and `aspect_ratio` (`landscape` | `portrait` | `square`) and **returns a URL** — it does not accept '[:80]

