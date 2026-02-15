# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab", "Pillow"]
# ///
"""Build PDF for Coldstar Technical Whitepaper.

Page size: 6.0 x 9.0 inches (no bleed). Trade paperback format.
Technical aesthetic: Space Grotesk + Source Serif 4 + JetBrains Mono.
"""

import re
from pathlib import Path
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Paragraph, Spacer, PageBreak,
    Frame, PageTemplate, Flowable, HRFlowable, Table, TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# -- Paths -----------------------------------------------------------------
PROJECT = Path("/Volumes/Virtual Server/projects/coldstar")
WHITEPAPER = PROJECT / "whitepaper.md"
FONT_DIR = PROJECT / "book" / "fonts"
OUTPUT = PROJECT / "book" / "output" / "coldstar-whitepaper.pdf"

# -- Brand Assets ----------------------------------------------------------
LOGO_MAIN = PROJECT / "assets" / "coldstar-logo-main.png"   # White wordmark + star on transparent
ICON_1024 = PROJECT / "assets" / "favicons" / "coldstar-icon-1024.png"  # Star icon hi-res
ICON_STAR = PROJECT / "assets" / "coldstar-icon.png"        # Dual star mark
SCREENSHOT_WALLET = PROJECT / "attached_assets" / "Screenshot_2025-12-24_at_00.36.12_1766536575372.png"
SCREENSHOT_USB = PROJECT / "attached_assets" / "Screenshot_2025-12-24_at_00.41.39_1766536906322.png"

# -- Register TTF fonts ----------------------------------------------------
pdfmetrics.registerFont(TTFont('SpaceGrotesk', str(FONT_DIR / 'SpaceGrotesk-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SpaceGrotesk-Medium', str(FONT_DIR / 'SpaceGrotesk-Medium.ttf')))
pdfmetrics.registerFont(TTFont('SpaceGrotesk-Bold', str(FONT_DIR / 'SpaceGrotesk-Bold.ttf')))
pdfmetrics.registerFont(TTFont('SpaceGrotesk-Light', str(FONT_DIR / 'SpaceGrotesk-Light.ttf')))
registerFontFamily('SpaceGrotesk',
    normal='SpaceGrotesk', bold='SpaceGrotesk-Bold')

pdfmetrics.registerFont(TTFont('SourceSerif', str(FONT_DIR / 'SourceSerif4-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SourceSerif-SemiBold', str(FONT_DIR / 'SourceSerif4-SemiBold.ttf')))
pdfmetrics.registerFont(TTFont('SourceSerif-Italic', str(FONT_DIR / 'SourceSerif4-Italic.ttf')))
registerFontFamily('SourceSerif',
    normal='SourceSerif', bold='SourceSerif-SemiBold', italic='SourceSerif-Italic')

pdfmetrics.registerFont(TTFont('JetBrains', str(FONT_DIR / 'JetBrainsMono-Regular.ttf')))
pdfmetrics.registerFont(TTFont('JetBrains-Bold', str(FONT_DIR / 'JetBrainsMono-Bold.ttf')))
registerFontFamily('JetBrains', normal='JetBrains', bold='JetBrains-Bold')

pdfmetrics.registerFont(TTFont('IBMPlexMono', str(FONT_DIR / 'IBMPlexMono-Regular.ttf')))
pdfmetrics.registerFont(TTFont('IBMPlexMono-Medium', str(FONT_DIR / 'IBMPlexMono-Medium.ttf')))
registerFontFamily('IBMPlexMono', normal='IBMPlexMono', bold='IBMPlexMono-Medium')

# Override Helvetica stubs
pdfmetrics.registerFont(TTFont('Helvetica', str(FONT_DIR / 'SourceSerif4-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Helvetica-Bold', str(FONT_DIR / 'SourceSerif4-SemiBold.ttf')))
pdfmetrics.registerFont(TTFont('Helvetica-Oblique', str(FONT_DIR / 'SourceSerif4-Italic.ttf')))
pdfmetrics.registerFont(TTFont('Helvetica-BoldOblique', str(FONT_DIR / 'SourceSerif4-SemiBold.ttf')))

# -- Page dimensions -- 6x9 no bleed --------------------------------------
PAGE_W = 6.0 * inch
PAGE_H = 9.0 * inch
MARGIN_GUTTER = 0.75 * inch
MARGIN_OUTSIDE = 0.5 * inch
MARGIN_TOP = 0.6 * inch
MARGIN_BOTTOM = 0.6 * inch

# -- Colors -- Dark Technical Aesthetic ------------------------------------
INK = HexColor("#1a1a1a")
INK_LIGHT = HexColor("#2d2d2d")
CYAN = HexColor("#0891b2")          # Print-friendly cyan (darker than site's #58d1eb)
CYAN_DARK = HexColor("#065f76")
LIME = HexColor("#4d7c0f")          # Print-friendly lime (darker than site's #98e024)
MUTED = HexColor("#666666")
RULE = HexColor("#d4d4d4")
WHITE = HexColor("#ffffff")
BG_LIGHT = HexColor("#f5f5f5")
CODE_BG = HexColor("#f0f0f0")


# -- Styles ----------------------------------------------------------------
def make_styles():
    body = ParagraphStyle(
        "Body",
        fontName="SourceSerif",
        fontSize=10,
        leading=16,
        textColor=INK_LIGHT,
        alignment=TA_JUSTIFY,
        spaceAfter=7,
    )
    return {
        "body": body,
        "body_italic": ParagraphStyle(
            "BodyItalic", parent=body,
            fontName="SourceSerif-Italic",
            textColor=MUTED,
            alignment=TA_LEFT,
            spaceAfter=7,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="SpaceGrotesk-Bold",
            fontSize=20,
            leading=26,
            textColor=INK,
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="SpaceGrotesk-Bold",
            fontSize=14,
            leading=20,
            textColor=INK,
            alignment=TA_LEFT,
            spaceBefore=16,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="SpaceGrotesk-Medium",
            fontSize=11,
            leading=16,
            textColor=CYAN_DARK,
            alignment=TA_LEFT,
            spaceBefore=14,
            spaceAfter=5,
        ),
        "h4": ParagraphStyle(
            "H4",
            fontName="SpaceGrotesk-Medium",
            fontSize=10,
            leading=14,
            textColor=INK,
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=body,
            leftIndent=20,
            firstLineIndent=0,
            bulletIndent=6,
            spaceAfter=5,
        ),
        "code_block": ParagraphStyle(
            "CodeBlock",
            fontName="JetBrains",
            fontSize=7.5,
            leading=11,
            textColor=INK_LIGHT,
            alignment=TA_LEFT,
            leftIndent=12,
            spaceAfter=8,
            spaceBefore=4,
        ),
        "code_inline": ParagraphStyle(
            "CodeInline",
            fontName="JetBrains",
            fontSize=8.5,
            leading=13,
            textColor=INK_LIGHT,
        ),
        "section_num": ParagraphStyle(
            "SectionNum",
            fontName="IBMPlexMono",
            fontSize=8,
            leading=13,
            textColor=CYAN,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            fontName="SpaceGrotesk-Bold",
            fontSize=22,
            leading=28,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "title_series": ParagraphStyle(
            "TitleSeries",
            fontName="IBMPlexMono",
            fontSize=8,
            leading=13,
            textColor=CYAN,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "title_main": ParagraphStyle(
            "TitleMain",
            fontName="SpaceGrotesk-Bold",
            fontSize=28,
            leading=34,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "title_subtitle": ParagraphStyle(
            "TitleSubtitle",
            fontName="SpaceGrotesk-Light",
            fontSize=11,
            leading=16,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "title_author": ParagraphStyle(
            "TitleAuthor",
            fontName="SpaceGrotesk-Medium",
            fontSize=13,
            leading=18,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "title_org": ParagraphStyle(
            "TitleOrg",
            fontName="IBMPlexMono",
            fontSize=7.5,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "title_publisher": ParagraphStyle(
            "TitlePublisher",
            fontName="SourceSerif-Italic",
            fontSize=10,
            leading=15,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "copyright": ParagraphStyle(
            "Copyright",
            fontName="SourceSerif",
            fontSize=8.5,
            leading=13,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "toc_heading": ParagraphStyle(
            "TOCHeading",
            fontName="SpaceGrotesk-Bold",
            fontSize=18,
            leading=24,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "toc_entry": ParagraphStyle(
            "TOCEntry",
            fontName="SourceSerif",
            fontSize=10,
            leading=20,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "toc_appendix": ParagraphStyle(
            "TOCAppendix",
            fontName="SourceSerif",
            fontSize=9.5,
            leading=18,
            textColor=MUTED,
            alignment=TA_LEFT,
            leftIndent=12,
        ),
        "abstract_body": ParagraphStyle(
            "AbstractBody",
            fontName="SourceSerif-Italic",
            fontSize=10,
            leading=16,
            textColor=INK_LIGHT,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            fontName="SpaceGrotesk-Medium",
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            fontName="SourceSerif",
            fontSize=8,
            leading=11,
            textColor=INK_LIGHT,
        ),
        "feature_item": ParagraphStyle(
            "FeatureItem",
            fontName="SourceSerif",
            fontSize=9.5,
            leading=15,
            textColor=INK_LIGHT,
            leftIndent=16,
            bulletIndent=4,
            spaceAfter=4,
        ),
    }


# -- Custom flowables ------------------------------------------------------
class CodeBlock(Flowable):
    """Code block with light background."""
    def __init__(self, text, style):
        super().__init__()
        self._text = text
        self._style = style

    def wrap(self, aW, aH):
        self._para = Paragraph(self._text, self._style)
        w, h = self._para.wrap(aW - 16, aH)
        self.width = aW
        self.height = h + 12
        return aW, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(BG_LIGHT)
        c.roundRect(0, -2, self.width, self.height + 2, 3, fill=1, stroke=0)
        c.setStrokeColor(CYAN)
        c.setLineWidth(2)
        c.line(0, -2, 0, self.height)
        self._para.drawOn(c, 10, 4)


class CyanAccentBlock(Flowable):
    """Blockquote/callout with left cyan accent border."""
    def __init__(self, text, style):
        super().__init__()
        self._text = text
        self._style = style

    def wrap(self, aW, aH):
        self._para = Paragraph(self._text, self._style)
        w, h = self._para.wrap(aW - 22, aH)
        self.width = aW
        self.height = h + 4
        return aW, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(CYAN)
        c.setLineWidth(3)
        c.line(0, 0, 0, self.height)
        self._para.drawOn(c, 22, 0)


class ScreenshotBlock(Flowable):
    """Embed a screenshot with border and caption."""
    def __init__(self, img_path, caption="", max_width=4.5*inch):
        super().__init__()
        self._img_path = str(img_path)
        self._caption = caption
        self._max_width = max_width
        from reportlab.lib.utils import ImageReader
        img = ImageReader(self._img_path)
        iw, ih = img.getSize()
        scale = min(self._max_width / iw, 3.0 * inch / ih)
        self._img_w = iw * scale
        self._img_h = ih * scale

    def wrap(self, aW, aH):
        self.width = aW
        caption_h = 16 if self._caption else 0
        self.height = self._img_h + 16 + caption_h  # padding + caption
        return aW, self.height

    def draw(self):
        c = self.canv
        x = (self.width - self._img_w) / 2  # center
        caption_h = 16 if self._caption else 0

        # Dark background behind screenshot
        c.setFillColor(HexColor("#1a1a1a"))
        c.roundRect(x - 6, caption_h, self._img_w + 12, self._img_h + 12, 4, fill=1, stroke=0)

        # Cyan border
        c.setStrokeColor(CYAN)
        c.setLineWidth(0.5)
        c.roundRect(x - 6, caption_h, self._img_w + 12, self._img_h + 12, 4, fill=0, stroke=1)

        # Image
        c.drawImage(self._img_path, x, caption_h + 6,
                     width=self._img_w, height=self._img_h,
                     preserveAspectRatio=True)

        # Caption
        if self._caption:
            c.setFont("IBMPlexMono", 7)
            c.setFillColor(MUTED)
            c.drawCentredString(self.width / 2, 2, self._caption)


class BrandIcon(Flowable):
    """Centered brand icon at a given size."""
    def __init__(self, img_path, size=0.6*inch):
        super().__init__()
        self._img_path = str(img_path)
        self._size = size

    def wrap(self, aW, aH):
        self.width = aW
        self.height = self._size + 8
        return aW, self.height

    def draw(self):
        c = self.canv
        x = (self.width - self._size) / 2
        c.drawImage(self._img_path, x, 4,
                     width=self._size, height=self._size,
                     preserveAspectRatio=True, mask='auto')


# -- Page templates --------------------------------------------------------
class WhitepaperDocTemplate(BaseDocTemplate):
    """Doc template with programmatic cover, alternating gutters, page numbers."""

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.page_count = 0

        frame_cover = Frame(
            0, 0, PAGE_W, PAGE_H, id="cover",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        frame_recto = Frame(
            MARGIN_GUTTER, MARGIN_BOTTOM,
            PAGE_W - MARGIN_GUTTER - MARGIN_OUTSIDE,
            PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="recto",
        )
        frame_verso = Frame(
            MARGIN_OUTSIDE, MARGIN_BOTTOM,
            PAGE_W - MARGIN_GUTTER - MARGIN_OUTSIDE,
            PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="verso",
        )

        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame_cover], onPage=self._draw_cover),
            PageTemplate(id="recto", frames=[frame_recto], onPage=self._draw_recto),
            PageTemplate(id="verso", frames=[frame_verso], onPage=self._draw_verso),
        ])

    def _draw_cover(self, canvas, doc):
        """Dark cover using actual Coldstar brand assets."""
        self.page_count += 1

        cx = PAGE_W / 2

        # Dark background
        canvas.setFillColor(HexColor("#0a0a0a"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        # Subtle geometric accent lines (circuit-board inspired)
        canvas.setStrokeColor(HexColor("#1a3a42"))
        canvas.setLineWidth(0.5)
        for y in range(0, int(PAGE_H), 24):
            canvas.line(0, y, PAGE_W * 0.12, y)
            canvas.line(PAGE_W * 0.88, y, PAGE_W, y)

        # Cyan accent bar at top
        canvas.setFillColor(CYAN)
        canvas.rect(0, PAGE_H - 4, PAGE_W, 4, fill=1, stroke=0)

        # Star icon (actual brand asset) — centered, upper portion
        if ICON_1024.exists():
            icon_w = 1.4 * inch
            icon_h = 1.4 * inch
            canvas.drawImage(str(ICON_1024), cx - icon_w / 2, 6.4 * inch,
                             width=icon_w, height=icon_h,
                             preserveAspectRatio=True, mask='auto')

        # Logo wordmark (actual brand asset) — below icon
        if LOGO_MAIN.exists():
            logo_w = 4.0 * inch
            logo_h = 1.2 * inch
            canvas.drawImage(str(LOGO_MAIN), cx - logo_w / 2, 4.8 * inch,
                             width=logo_w, height=logo_h,
                             preserveAspectRatio=True, mask='auto')

        # "TECHNICAL WHITEPAPER" label
        canvas.setFillColor(CYAN)
        canvas.setFont("IBMPlexMono", 7)
        canvas.drawCentredString(cx, 4.5 * inch, "TECHNICAL WHITEPAPER  \u2022  V1.0")

        # Subtitle
        canvas.setFont("SpaceGrotesk-Light", 11)
        canvas.setFillColor(HexColor("#a0a0a0"))
        canvas.drawCentredString(cx, 4.05 * inch, "A Python-Based Air-Gapped Cold Wallet")
        canvas.drawCentredString(cx, 3.8 * inch, "Tool for Solana")

        # Cyan rule
        canvas.setStrokeColor(CYAN)
        canvas.setLineWidth(2)
        rule_w = 1.5 * inch
        canvas.line(cx - rule_w / 2, 3.55 * inch, cx + rule_w / 2, 3.55 * inch)

        # Key features (stacked)
        features = [
            "Air-Gap Isolation",
            "Ed25519 Cryptography",
            "Alpine Linux (~50MB)",
            "100% Open Source",
        ]
        canvas.setFont("IBMPlexMono", 7)
        y = 3.2 * inch
        for feat in features:
            canvas.setFillColor(CYAN)
            canvas.drawString(cx - 1.1 * inch, y, "\u25a0")
            canvas.setFillColor(HexColor("#cccccc"))
            canvas.drawString(cx - 0.9 * inch, y, feat)
            y -= 0.22 * inch

        # Author
        canvas.setFont("SpaceGrotesk-Medium", 12)
        canvas.setFillColor(WHITE)
        canvas.drawCentredString(cx, 1.4 * inch, "</Syrem>")

        # Organization
        canvas.setFont("IBMPlexMono", 7)
        canvas.setFillColor(HexColor("#888888"))
        canvas.drawCentredString(cx, 1.1 * inch, "ChainLabs Technologies")

        # Bottom cyan bar
        canvas.setFillColor(CYAN)
        canvas.rect(0, 0, PAGE_W, 3, fill=1, stroke=0)

        # Date
        canvas.setFont("IBMPlexMono", 6.5)
        canvas.setFillColor(HexColor("#555555"))
        canvas.drawCentredString(cx, 0.35 * inch, "December 2025  \u2022  MIT License")

    def _draw_recto(self, canvas, doc):
        self.page_count += 1
        if self.page_count > 2:
            canvas.setFont("IBMPlexMono", 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(
                PAGE_W - MARGIN_OUTSIDE, MARGIN_BOTTOM - 0.25 * inch,
                str(self.page_count))
            # Header rule
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.3)
            canvas.line(MARGIN_GUTTER, PAGE_H - MARGIN_TOP + 0.15 * inch,
                       PAGE_W - MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 0.15 * inch)
            # Header text
            canvas.setFont("IBMPlexMono", 6)
            canvas.setFillColor(HexColor("#aaaaaa"))
            canvas.drawRightString(
                PAGE_W - MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 0.22 * inch,
                "COLDSTAR WHITEPAPER")

    def _draw_verso(self, canvas, doc):
        self.page_count += 1
        if self.page_count > 2:
            canvas.setFont("IBMPlexMono", 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(
                MARGIN_OUTSIDE, MARGIN_BOTTOM - 0.25 * inch,
                str(self.page_count))
            # Header rule
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.3)
            canvas.line(MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 0.15 * inch,
                       PAGE_W - MARGIN_GUTTER, PAGE_H - MARGIN_TOP + 0.15 * inch)
            # Header text
            canvas.setFont("IBMPlexMono", 6)
            canvas.setFillColor(HexColor("#aaaaaa"))
            canvas.drawString(
                MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 0.22 * inch,
                "COLDSTAR WHITEPAPER")

    def afterPage(self):
        if self.page_count == 1:
            self._nextPageTemplateIndex = 1
        elif self.page_count % 2 == 1:
            self._nextPageTemplateIndex = 2
        else:
            self._nextPageTemplateIndex = 1


# -- Markdown helpers ------------------------------------------------------
def clean_md(text):
    """Convert markdown inline formatting to reportlab XML."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Restore any intended HTML-like tags we use
    # Triple asterisk = bold+italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Double asterisk = bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Single asterisk = italic
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+?)`', r'<font name="JetBrains" size="8">\1</font>', text)
    return text


def parse_table(lines, styles):
    """Parse markdown table into reportlab Table flowable."""
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    if len(rows) < 2:
        return None

    # Remove separator row (---|---|---)
    if all(set(c.strip()) <= {'-', ':', ' '} for c in rows[1]):
        rows.pop(1)

    if not rows:
        return None

    # Build table data with Paragraphs
    header_row = rows[0]
    data_rows = rows[1:]

    table_data = []
    # Header
    table_data.append([Paragraph(clean_md(c), styles["table_header"]) for c in header_row])
    # Data
    for row in data_rows:
        # Pad short rows
        while len(row) < len(header_row):
            row.append("")
        table_data.append([Paragraph(clean_md(c), styles["table_cell"]) for c in row[:len(header_row)]])

    col_count = len(header_row)
    avail_w = PAGE_W - MARGIN_GUTTER - MARGIN_OUTSIDE - 0.2 * inch
    col_w = avail_w / col_count

    t = Table(table_data, colWidths=[col_w] * col_count)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, 0), INK),
        ('FONTNAME', (0, 0), (-1, 0), 'SpaceGrotesk-Medium'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, 0), 0.5, CYAN),
        ('LINEBELOW', (0, 0), (-1, 0), 1, CYAN),
        ('LINEBELOW', (0, 1), (-1, -2), 0.3, RULE),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, RULE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


# -- Section splitter ------------------------------------------------------
def split_whitepaper(text):
    """Split whitepaper into sections by ## headings."""
    # Strip title block (everything before first ---)
    # Find the abstract or first ## heading
    sections = []
    current_title = None
    current_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        # Main sections: ## 1. Introduction, ## Appendix A: ...
        if stripped.startswith("## "):
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines)))
            current_title = stripped[3:]
            current_lines = []
        else:
            current_lines.append(line)

    # Last section
    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines)))

    return sections


def parse_section_content(text, styles):
    """Parse section markdown content into flowables."""
    story = []
    lines = text.strip().split("\n")
    i = 0
    in_code = False
    code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block fence
        if stripped.startswith("```"):
            if in_code:
                # End code block
                code_text = "<br/>".join(
                    l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
                    for l in code_lines
                )
                if code_text.strip():
                    story.append(CodeBlock(code_text, styles["code_block"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Empty line
        if not stripped:
            i += 1
            continue

        # Table detection
        if "|" in stripped and i + 1 < len(lines) and "|" in lines[i + 1]:
            table_lines = []
            while i < len(lines) and "|" in lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            tbl = parse_table(table_lines, styles)
            if tbl:
                story.append(Spacer(1, 6))
                story.append(tbl)
                story.append(Spacer(1, 6))
            continue

        # H3 (### )
        if stripped.startswith("### "):
            title = stripped[4:]
            story.append(Paragraph(clean_md(title), styles["h2"]))
            i += 1
            continue

        # H4 (#### )
        if stripped.startswith("#### "):
            title = stripped[5:]
            story.append(Paragraph(clean_md(title), styles["h3"]))
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            story.append(Spacer(1, 8))
            story.append(HRFlowable(
                width="100%", thickness=0.5, color=RULE,
                spaceAfter=8, hAlign='LEFT'))
            i += 1
            continue

        # Bullet point
        if stripped.startswith("- "):
            text_content = stripped[2:]
            # Check for checkbox items
            text_content = text_content.replace("[ ]", "\u2610").replace("[x]", "\u2611")
            story.append(
                Paragraph(clean_md(text_content), styles["bullet"], bulletText="\u2022"))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            num, text_content = m.groups()
            story.append(
                Paragraph(clean_md(text_content), styles["bullet"], bulletText=f"{num}."))
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                bq_lines.append(lines[i].strip()[2:])
                i += 1
            quote_text = " ".join(bq_lines)
            story.append(CyanAccentBlock(clean_md(quote_text), styles["body_italic"]))
            continue

        # Regular paragraph
        story.append(Paragraph(clean_md(stripped), styles["body"]))
        i += 1

    return story


# -- Front matter ----------------------------------------------------------
def build_front_matter(styles, sections):
    story = []

    # Half title with star icon
    story.append(Spacer(1, 2.0 * inch))
    if ICON_STAR.exists():
        story.append(BrandIcon(ICON_STAR, size=0.8 * inch))
        story.append(Spacer(1, 16))
    story.append(Paragraph("COLDSTAR", styles["title_main"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Technical Whitepaper", styles["title_subtitle"]))
    story.append(PageBreak())

    # Title page with star icon
    story.append(Spacer(1, 0.8 * inch))
    if ICON_STAR.exists():
        story.append(BrandIcon(ICON_STAR, size=1.0 * inch))
        story.append(Spacer(1, 12))
    story.append(Paragraph("TECHNICAL WHITEPAPER  \u2022  V1.0", styles["title_series"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("COLDSTAR", styles["title_main"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(
        width="40%", thickness=2, color=CYAN,
        spaceAfter=12, spaceBefore=8, hAlign='CENTER'))
    story.append(Paragraph(
        "A Python-Based Air-Gapped Cold Wallet<br/>Tool for Solana",
        styles["title_subtitle"]))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("&lt;/Syrem&gt;", styles["title_author"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("ChainLabs Technologies", styles["title_org"]))
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph("Purple Squirrel Media", styles["title_publisher"]))
    story.append(PageBreak())

    # Copyright
    copyright_lines = [
        "COLDSTAR: A Python-Based Air-Gapped Cold Wallet Tool for Solana",
        "Technical Whitepaper \u2014 Current Implementation",
        None,
        "Version 1.0.0",
        "December 2025",
        None,
        "Author: &lt;/Syrem&gt;",
        "Organization: ChainLabs Technologies",
        None,
        "Licensed under the MIT License.",
        "Copyright \u00a9 2025 ChainLabs Technologies",
        None,
        "Published by Purple Squirrel Media",
        None,
        "Permission is hereby granted, free of charge, to any person obtaining a copy",
        "of this software and associated documentation files, to deal in the Software",
        "without restriction, including without limitation the rights to use, copy,",
        "modify, merge, publish, distribute, sublicense, and/or sell copies.",
        None,
        "First Edition",
    ]
    for line in copyright_lines:
        if line is None:
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(line, styles["copyright"]))
    story.append(PageBreak())

    # Table of Contents
    story.append(Paragraph("Contents", styles["toc_heading"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=CYAN,
        spaceAfter=16, hAlign='LEFT'))

    for title, _ in sections:
        # Detect appendix vs main section
        if title.startswith("Appendix"):
            story.append(Paragraph(clean_md(title), styles["toc_appendix"]))
        elif title in ("Abstract", "Table of Contents"):
            continue
        else:
            story.append(Paragraph(clean_md(title), styles["toc_entry"]))

    story.append(PageBreak())
    return story


# -- Build PDF -------------------------------------------------------------
def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()

    text = WHITEPAPER.read_text()
    sections = split_whitepaper(text)

    # Remove TOC section (we build our own)
    sections = [(t, c) for t, c in sections if t != "Table of Contents"]

    doc = WhitepaperDocTemplate(
        str(OUTPUT),
        pagesize=(PAGE_W, PAGE_H),
        title="COLDSTAR Technical Whitepaper",
        author="</Syrem> / ChainLabs Technologies",
    )

    story = []

    # Cover (handled by template)
    story.append(Spacer(1, 0))  # Trigger cover page
    story.append(PageBreak())

    # Front matter
    story.extend(build_front_matter(styles, sections))

    # Sections
    for title, content in sections:
        # Section number extraction
        m = re.match(r'^(\d+)\.\s+(.+)', title)
        if m:
            num, name = m.groups()
            story.append(Paragraph(f"SECTION {num}", styles["section_num"]))
            story.append(Paragraph(name, styles["section_title"]))
        elif title.startswith("Appendix"):
            story.append(Paragraph("APPENDIX", styles["section_num"]))
            # Extract letter and title: "Appendix A: Technical Specifications"
            app_m = re.match(r'Appendix\s+([A-Z]):\s+(.+)', title)
            if app_m:
                letter, name = app_m.groups()
                story.append(Paragraph(f"{letter}. {name}", styles["section_title"]))
            else:
                story.append(Paragraph(title.replace("Appendix ", ""), styles["section_title"]))
        elif title == "Abstract":
            story.append(Paragraph("ABSTRACT", styles["section_num"]))
            story.append(Paragraph("Abstract", styles["section_title"]))
        else:
            story.append(Paragraph(title, styles["section_title"]))

        story.append(HRFlowable(
            width="100%", thickness=1, color=CYAN,
            spaceAfter=14, hAlign='LEFT'))

        # Parse section content
        if title == "Abstract":
            # Render abstract in italic style
            for line in content.strip().split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("**Key Features:**"):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph("Key Features", styles["h3"]))
                elif stripped.startswith("- "):
                    story.append(Paragraph(
                        clean_md(stripped[2:]), styles["feature_item"], bulletText="\u25a0"))
                else:
                    story.append(Paragraph(clean_md(stripped), styles["abstract_body"]))
        else:
            story.extend(parse_section_content(content, styles))

            # Inject CLI screenshots for relevant sections
            if "5. User Guide" in title and SCREENSHOT_WALLET.exists():
                story.append(Spacer(1, 12))
                story.append(ScreenshotBlock(
                    SCREENSHOT_WALLET,
                    caption="Figure 1: Coldstar CLI \u2014 Wallet Status & Main Menu"))
            if "5. User Guide" in title and SCREENSHOT_USB.exists():
                story.append(Spacer(1, 12))
                story.append(ScreenshotBlock(
                    SCREENSHOT_USB,
                    caption="Figure 2: Coldstar CLI \u2014 USB Detection & Network Status"))

        story.append(PageBreak())

    doc.build(story)

    print(f"\nPDF saved: {OUTPUT}")
    print(f"Size: {OUTPUT.stat().st_size / 1024:.0f} KB")
    print(f"Pages: {doc.page_count}")


if __name__ == "__main__":
    build_pdf()
