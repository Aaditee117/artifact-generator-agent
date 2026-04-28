"""Fills the Optimus Info branded PPTX template in-place with AI-generated content.

POC/MVP Template slide index mapping (0-based) — 12 slides total:
  0  Title slide
  1  Agenda                (untouched)
  2  Our Understanding     ph idx=1 exists (forced textbox for multi-section formatting)
  3  Objective             no ph idx=1 -> textbox
  4  Scope                 ph idx=1 exists -> write via placeholder
  5  High Level Design     no ph idx=1 -> arch image or textbox
  6  Prerequisite          no ph idx=1 -> textbox (bold Category: desc format)
  7  Definition of Done    ph idx=1 exists (forced textbox for bold-section formatting)
  8  Out Of Scope          ph idx=1 exists -> write via placeholder
  9  Timelines & Effort    no ph idx=1 -> textbox
  10 Timelines and Cost    ph idx=1 is tiny (top=3077093) -> forced textbox
  11 Next Steps            no ph idx=1 -> textbox

HARDCODED STYLES (from sample.pptx inspection):
  Font Family: Open Sans
  Body Text: 14pt (main content bullets)
  Heading Text: 16pt bold (section headers like "Our Understanding:", "Current Challenges:")
  Title Text: 20pt (slide titles — handled by template)
  Cover Title: 28pt bold
  Cover Subtitle: 16pt
  Colors: #000000 (black text), #404040 (subtle/date text)
  Bullet char: • (U+2022) + two spaces
  Line spacing: paragraph space-before = 6pt for breathing room
"""
import os
from lxml import etree
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from io import BytesIO

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
TEMPLATE_POC = os.path.join(TEMPLATES_DIR, "POC template.pptx")
TEMPLATE_MVP = os.path.join(TEMPLATES_DIR, "MVP template.pptx")
TEMPLATE_PATH = TEMPLATE_POC

# ============================================================================
# HARDCODED STYLES (verified against sample.pptx)
# ============================================================================
FONT = "Open Sans"
BODY_PT = Pt(14)            # Body bullets — 14pt
HEADING_PT = Pt(16)         # Section headers (bold) — 16pt
COVER_TITLE_PT = Pt(28)     # Cover slide title
SUBTITLE_PT = Pt(16)        # Cover subtitle / client + date

COLOR_BLACK = RGBColor(0x00, 0x00, 0x00)
COLOR_GRAY  = RGBColor(0x40, 0x40, 0x40)   # date/subtitle

BULLET_CHAR = "\u2022"      # •

# XML namespace
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"

# ---------------------------------------------------------------------------
# Content-area textbox rectangles (left, top, width, height) in EMU.
# Derived from template placeholder positions.
#
# Slide 2  Our Understanding  — ph idx=1 top=919349/1004248, h=5373298
# Slide 3  Objective          — no ph; use measured area
# Slide 5  High Level Design  — no ph (arch image goes here)
# Slide 6  Prerequisite       — no ph
# Slide 7  Definition of Done — ph idx=1 top=998007, forced textbox
# Slide 9  Timelines&Effort   — no ph
# Slide 10 Timelines and Cost — ph idx=1 tiny (top=3077093), forced textbox
# Slide 11 Next Steps         — no ph
# ---------------------------------------------------------------------------
_TEXTBOX_AREA = {
    2:  (368056, 1150000, 11056800, 5100000),   # Our Understanding
    3:  (499727, 1200000, 11056800, 4900000),   # Objective
    4:  (499727, 1200000, 11056800, 4900000),   # Scope
    5:  (499727, 1300000, 11056800, 4400000),   # HLD text fallback
    6:  (499727, 1200000, 11056800, 4900000),   # Prerequisite
    7:  (499727, 1200000, 11056800, 4900000),   # Definition of Done
    8:  (499727, 1200000, 11056800, 4900000),   # Out Of Scope
    9:  (499727, 1200000, 11056800, 4900000),   # Timelines & Effort
    10: (499727, 1200000, 11056800, 4900000),   # Timelines and Cost
    11: (499727, 1200000, 11056800, 4900000),   # Next Steps
}

# Slides where we always use a textbox (even if ph idx=1 exists) because we
# need fine-grained bold/bullet formatting that placeholders cannot deliver.
_FORCE_TEXTBOX = {2, 6, 7, 8, 10}

# HLD arch image position (fills body area under title)
_HLD_IMG_L = Emu(499727)
_HLD_IMG_T = Emu(1300000)
_HLD_IMG_W = Emu(11056800)
_HLD_IMG_H = Emu(4400000)


# ================================================================== helpers ==

def _clear_placeholder(tf):
    """Remove all runs/breaks from a text frame, leaving exactly one empty paragraph."""
    tb = tf._txBody
    paras = tb.findall(f"{{{_A}}}p")
    for p in paras[1:]:
        tb.remove(p)
    first_p = paras[0]
    keep_tags = {f"{{{_A}}}pPr", f"{{{_A}}}endParaRPr"}
    for child in list(first_p):
        if child.tag not in keep_tags:
            first_p.remove(child)


def _add_run(para, text, bold=False, size=None, color=None):
    """Add a run to *para* with fully hardcoded Open Sans styling."""
    run = para.add_run()
    run.text = text
    run.font.name = FONT
    run.font.bold = bold
    run.font.size = size or BODY_PT
    run.font.color.rgb = color or COLOR_BLACK
    return run


def _set_para_spacing(para, space_before_pt=4):
    """Set paragraph space-before to avoid content overflow."""
    pPr = para._p.get_or_add_pPr()
    spcBef = etree.SubElement(pPr, qn("a:spcBef"))
    spcPts = etree.SubElement(spcBef, qn("a:spcPts"))
    spcPts.set("val", str(int(space_before_pt * 100)))


def _write_textbox(slide, lines, slide_idx):
    """Create a textbox at the pre-measured area and write *lines* into it.

    Line conventions (produced by _to_lines):
      - "" (empty)      → blank spacing paragraph
      - starts with "§" → bold section header (e.g. "§Our Understanding:")
      - starts with "•" → normal bullet line
      - anything else   → plain line (numbered steps, sub-items)
    """
    area = _TEXTBOX_AREA.get(slide_idx)
    if not area:
        print(f"[PPT] Error: No textbox area defined for slide {slide_idx}")
        return
    if not lines:
        print(f"[PPT] Error: No lines to write for slide {slide_idx}")
        return
        
    left, top, width, height = (Emu(v) for v in area)
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True
    
    print(f"[PPT] Writing {len(lines)} lines to textbox on slide {slide_idx}")

    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()

        if not line:
            # Empty spacer
            _add_run(para, "", size=Pt(6))
            continue

        if line.startswith("§"):
            # Bold section header
            text = line[1:]  # strip marker
            _add_run(para, text, bold=True, size=HEADING_PT)
            _set_para_spacing(para, 8)

        elif ":" in line and not line.startswith("\u2022"):
            # "Category: description" split — bold key, normal value
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip() if len(parts) > 1 else ""
            _add_run(para, f"\u2022  {key}:", bold=True)
            if val:
                _add_run(para, f" {val}", bold=False)
            _set_para_spacing(para, 4)

        elif line.startswith("\u2022"):
            _add_run(para, line)
            _set_para_spacing(para, 4)

        else:
            # Numbered steps / plain lines
            _add_run(para, line)
            _set_para_spacing(para, 4)


def _write_ph1(slide, lines):
    """Write *lines* into ph idx=1 of *slide*.

    Uses the same line conventions as _write_textbox but writes into the
    existing placeholder so that the template background / layout styling
    is preserved.  Returns True if ph found, False otherwise.
    """
    for shape in slide.shapes:
        if not (shape.is_placeholder and shape.placeholder_format.idx == 1):
            continue
        tf = shape.text_frame
        tf.word_wrap = True
        tf.clear()  # More aggressive clearing
        
        if not lines:
            return True

        for i, line in enumerate(lines):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()

            if not line:
                _add_run(para, "", size=Pt(6))
                continue

            if line.startswith("§"):
                _add_run(para, line[1:], bold=True, size=HEADING_PT)
                _set_para_spacing(para, 8)

            elif ":" in line and not line.startswith("\u2022"):
                parts = line.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ""
                _add_run(para, f"\u2022  {key}:", bold=True)
                if val:
                    _add_run(para, f" {val}", bold=False)
                _set_para_spacing(para, 4)

            elif line.startswith("\u2022"):
                _add_run(para, line)
                _set_para_spacing(para, 4)

            else:
                _add_run(para, line)
                _set_para_spacing(para, 4)

        return True
    return False


# ---------------------------------------------------------------------------
# Content → line list converters
# ---------------------------------------------------------------------------

def _to_lines(section):
    """Convert a content dict into a flat list of display-ready strings.

    Markers:
      "§Header:"  → bold section header
      "• text"    → bullet item
      ""          → blank spacer

    The section title is intentionally OMITTED to prevent repetition
    (the slide template already shows the title in ph idx=0).
    """
    if not section:
        return []

    result = []

    # --- Our Understanding: sections [{header, points}] ---
    if "sections" in section:
        for idx, sect in enumerate(section["sections"]):
            if idx > 0:
                result.append("")  # blank spacer between sections
            result.append(f"\u00a7{sect['header']}:")
            # Limit to 2 points per section to avoid content overflow
            for pt in sect.get("points", [])[:2]:
                result.append(f"\u2022  {pt}")
        return result

    # --- Prerequisites / Definition of Done: items [{category/section, description}] ---
    if "items" in section and isinstance(section["items"], list) and section["items"]:
        first = section["items"][0]
        key_field = "category" if "category" in first else "section" if "section" in first else "service"
        val_field = "description" if "description" in first else "cost"
        for item in section["items"]:
            key = item.get(key_field, "")
            val = item.get(val_field, "")
            result.append(f"{key}: {val}")
        return result

    # --- Simple bullet points ---
    if "points" in section:
        for pt in section["points"]:
            result.append(f"\u2022  {pt}")
        return result

    # --- Numbered steps ---
    if "steps" in section:
        for i, step in enumerate(section["steps"], 1):
            result.append(f"{i}. {step}")
        return result

    # --- Timeline phases ---
    if "phases" in section:
        for ph in section["phases"]:
            result.append(f"\u2022  {ph.get('phase', '')} \u2014 {ph.get('duration', '')}")
        return result

    # --- Legacy categories dict ---
    if "categories" in section:
        cats = section["categories"]
        if section.get("note"):
            result.append(f"\u2022  {section['note']}")
            result.append("")
        if isinstance(cats, dict):
            for cat, items in cats.items():
                result.append(f"\u00a7{cat}:")
                for item in (items if isinstance(items, list) else [items]):
                    result.append(f"\u2022  {item}")
        elif isinstance(cats, list):
            for c in cats:
                if isinstance(c, dict):
                    result.append(f"{c.get('item', '')}: {c.get('estimate', 'TBD')}")
        return result

    # --- Fallback: note only ---
    if section.get("note"):
        result.append(f"\u2022  {section['note']}")

    return result


def _fill_slide(slide, section, slide_idx):
    """Fill a content slide with the appropriate strategy."""
    lines = _to_lines(section)
    
    # Debug logging
    slide_names = {2: "Our Understanding", 3: "Objective", 4: "Scope", 5: "High Level Design", 
                   6: "Prerequisites", 7: "Definition of Done", 8: "Out of Scope", 
                   9: "Timeline & Effort", 10: "Cost", 11: "Next Steps"}
    slide_name = slide_names.get(slide_idx, f"Slide {slide_idx}")
    
    if slide_idx == 8:  # Debug Out of Scope specifically
        print(f"[PPT] {slide_name}: section={section}")
        print(f"[PPT] {slide_name}: generated {len(lines)} lines: {lines}")
    else:
        print(f"[PPT] Filling {slide_name} (index {slide_idx}): {len(lines)} lines")
    
    if not lines:
        print(f"[PPT] Warning: No lines generated for {slide_name}")
        return

    if slide_idx in _FORCE_TEXTBOX:
        _write_textbox(slide, lines, slide_idx)
    elif not _write_ph1(slide, lines):
        _write_textbox(slide, lines, slide_idx)


# ----------------------------------------------------------------- generator --

def generate_ppt(content, arch_image=None, dfd_image=None, phase_type=None):
    """Load the correct 12-slide template and fill it in-place."""
    template = TEMPLATE_MVP if phase_type == "mvp" else TEMPLATE_POC
    if not os.path.exists(template):
        template = TEMPLATE_PATH

    prs = Presentation(template)
    s = list(prs.slides)   # 12 slides, 0-indexed

    # ---- Slide 0: Title ------------------------------------------------
    tc = content.get("title_slide", {})
    for shape in s[0].shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 0:
            tf = shape.text_frame
            _clear_placeholder(tf)
            p0 = tf.paragraphs[0]
            p0.alignment = PP_ALIGN.LEFT
            _add_run(p0, tc.get("title", "Presales Proposal"),
                     bold=True, size=COVER_TITLE_PT)

            cl = tc.get("client", "")
            dt = tc.get("date", "")
            info = (f"{cl}  \u2022  {dt}" if (cl and dt) else cl or dt)
            if info:
                p1 = tf.add_paragraph()
                p1.alignment = PP_ALIGN.LEFT
                _add_run(p1, info, size=SUBTITLE_PT, color=COLOR_GRAY)
            break

    # ---- Slide 1: Agenda — untouched -----------------------------------

    # ---- Slide 2: Our Understanding ------------------------------------
    _fill_slide(s[2], content.get("our_understanding", {}), 2)

    # ---- Slide 3: Objective --------------------------------------------
    _fill_slide(s[3], content.get("objective", {}), 3)

    # ---- Slide 4: Scope ------------------------------------------------
    _fill_slide(s[4], content.get("scope", {}), 4)

    # ---- Slide 5: High Level Design ------------------------------------
    if arch_image:
        # Remove existing ph idx=1 if present, then add picture
        for shape in list(s[5].shapes):
            if shape.is_placeholder and shape.placeholder_format.idx == 1:
                shape._element.getparent().remove(shape._element)
                break
        s[5].shapes.add_picture(
            BytesIO(arch_image), _HLD_IMG_L, _HLD_IMG_T, _HLD_IMG_W, _HLD_IMG_H
        )
        print(f"[PPT] Slide 5: Inserted architecture diagram image ({len(arch_image)} bytes)")
    else:
        # Always show fallback content when no image available
        hld = content.get("high_level_design", {})
        desc = hld.get("description", hld.get("note", ""))
        comps = hld.get("components", [])
        
        # Build fallback text
        if desc and desc.strip():
            fallback_points = [desc]
        else:
            fallback_points = ["Architecture diagram will be auto-generated and inserted here"]
        
        fallback_content = {"points": fallback_points + comps}
        print(f"[PPT] Slide 5: No image, using fallback content: {fallback_content}")
        _fill_slide(s[5], fallback_content, 5)

    # ---- Slide 6: Prerequisite -----------------------------------------
    _fill_slide(s[6], content.get("prerequisites", {}), 6)

    # ---- Slide 7: Definition of Done -----------------------------------
    _fill_slide(s[7], content.get("definition_of_done", {}), 7)

    # ---- Slide 8: Out Of Scope -----------------------------------------
    _fill_slide(s[8], content.get("out_of_scope", {}), 8)

    # ---- Slide 9: Timelines & Effort -----------------------------------
    _fill_slide(s[9], content.get("timeline_cost", {}), 9)

    # ---- Slide 10: Timelines and Cost (forced textbox) -----------------
    ce = content.get("cost_estimate", {})
    _fill_slide(s[10], ce, 10)

    # ---- Slide 11: Next Steps ------------------------------------------
    _fill_slide(s[11], content.get("next_steps", {}), 11)

    buf = BytesIO()
    prs.save(buf)
    return buf.getvalue()
