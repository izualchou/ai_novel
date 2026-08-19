# -*- coding: utf-8 -*-
"""整合《百年回响，次元归途》全书，导出整合 Markdown / Word(.docx) / EPUB(.epub)。"""
import os
import re

BASE = r"d:\Documents\AI_novel\ai_novel\novels\百年回响，次元归途"
CHAPTERS = os.path.join(BASE, "chapters")

BOOK_TITLE = "百年回响，次元归途"
SUBTITLE = "次元有壁，爱意无疆。百年回响，终有归途。"

# 章节文件顺序与卷归属
ORDER = [
    "第01章-一九二六，烟雨沪上.md",
    "第02章-乱世心事，尽付虚空.md",
    "第03章-单向时空，百年遥望.md",
    "第04章-乱世余生，遗憾落幕.md",
    "第05章-百年沉淀，医生沈聿.md",
    "第06章-盛世重生，少女林晚.md",
    "第07章-次元破壁，双向互通.md",
    "第08章-第一声回应，百年如愿.md",
    "第09章-独属于两人的秘密.md",
    "第10章-双向治愈，彼此救赎.md",
    "第11章-次元恋爱的极致拉扯.md",
    "第12章-七夕星河，时空共赴.md",
    "第13章-执念成研，破壁之路.md",
    "第14章-百年破壁，终得相逢.md",
    "第15章-次元归期，余生相守.md",
    "番外一-雨夜微光.md",
    "番外二-少年心事.md",
    "番外三-归期.md",
    "番外四-命中注定.md",
]

# 卷定义：(卷标题, 起始章节号[含], 结束章节号[含])；番外单独一卷
VOLUMES = [
    ("第一卷 梧桐旧梦・百年无声", 1, 4),
    ("第二卷 盛世重逢・次元共鸣", 5, 8),
    ("第三卷 次元相恋・无人知晓的深爱", 9, 11),
    ("第四卷 星河七夕・百年一遇", 12, 12),
    ("第五卷 破壁终章・岁岁归途", 13, 15),
]
FANWAI_TITLE = "番外篇"


def parse_chapter(fname):
    """返回 (序号/番外标记, 章标题, 正文文本)。"""
    path = os.path.join(CHAPTERS, fname)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    # 找到首个 # 标题行
    title = fname
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.startswith("#"):
            title = ln.lstrip("#").strip()
            body_start = i + 1
            break
    # 去掉标题后的连续空行
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1
    body = "\n".join(lines[body_start:]).strip()
    is_fanwai = fname.startswith("番外")
    return is_fanwai, title, body


def main():
    items = []
    for fname in ORDER:
        if not os.path.exists(os.path.join(CHAPTERS, fname)):
            print("[warn] missing:", fname)
            continue
        is_fanwai, title, body = parse_chapter(fname)
        items.append((is_fanwai, title, body))

    # 按卷分组
    structure = []  # [(卷标题, [(章标题, 正文), ...])]
    for vol_title, lo, hi in VOLUMES:
        chapters = []
        for is_fanwai, title, body in items:
            if is_fanwai:
                continue
            m = re.match(r"第(\d+)章", title)
            if m and lo <= int(m.group(1)) <= hi:
                chapters.append((title, body))
        structure.append((vol_title, chapters))
    fanwai_chs = [(t, b) for (f, t, b) in items if f]
    structure.append((FANWAI_TITLE, fanwai_chs))

    # ============ 1. 整合 Markdown ============
    md_lines = [f"# {BOOK_TITLE}", "", SUBTITLE, "", "---", "", "## 目录", ""]
    for idx, (vol_title, chapters) in enumerate(structure, start=1):
        slug = f"vol{idx}"
        md_lines.append(f"- [{vol_title}](#{slug})")
        for j, (title, _) in enumerate(chapters, start=1):
            ch_slug = f"vol{idx}c{j}"
            md_lines.append(f"  - [{title}](#{ch_slug})")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    for idx, (vol_title, chapters) in enumerate(structure, start=1):
        slug = f"vol{idx}"
        md_lines.append(f"## {vol_title} {{#{slug}}}")
        md_lines.append("")
        for j, (title, body) in enumerate(chapters, start=1):
            ch_slug = f"vol{idx}c{j}"
            md_lines.append(f"### {title} {{#{ch_slug}}}")
            md_lines.append("")
            md_lines.append(body)
            md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("—— 全书完 ——")
    md_text = "\n".join(md_lines).rstrip() + "\n"

    md_path = os.path.join(BASE, f"{BOOK_TITLE}（全本）.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print("[ok] markdown:", md_path)

    # ============ 2. Word(.docx) ============
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()

    # 页面设置：A4
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.5)
    sec.left_margin = sec.right_margin = Cm(2.8)

    def set_style_font(style, cn_font, en_font, size, bold=None, color=None):
        style.font.name = en_font
        style.font.size = Pt(size)
        if bold is not None:
            style.font.bold = bold
        if color is not None:
            style.font.color.rgb = color
        rpr = style.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:eastAsia"), cn_font)

    # Normal：正文
    set_style_font(doc.styles["Normal"], "宋体", "Times New Roman", 12)
    pf = doc.styles["Normal"].paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(0)
    pf.first_line_indent = Pt(24)  # 两字符首行缩进

    # 标题样式
    h1 = doc.styles["Heading 1"]
    set_style_font(h1, "黑体", "Arial", 22, bold=True)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.first_line_indent = Pt(0)

    h2 = doc.styles["Heading 2"]
    set_style_font(h2, "黑体", "Arial", 16, bold=True)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(8)
    h2.paragraph_format.first_line_indent = Pt(0)

    h3 = doc.styles["Heading 3"]
    set_style_font(h3, "黑体", "Arial", 14, bold=True)
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(6)
    h3.paragraph_format.first_line_indent = Pt(0)

    # 页脚页码
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)

    def add_page_break():
        doc.add_page_break()

    # 封面页
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(BOOK_TITLE)
    r.font.name = "黑体"; r.font.size = Pt(28); r.font.bold = True
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(SUBTITLE)
    r.font.name = "楷体"; r.font.size = Pt(14)
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "楷体")
    add_page_break()

    # 目录页（TOC 域，Word 打开后更新域即可生成带页码目录）
    doc.add_paragraph("目 录", style="Heading 1")
    tip = doc.add_paragraph()
    tip.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rt = tip.add_run("（本目录为 Word 自动目录域：打开后全选 → 按 F9 或右键 → 更新域，即可生成带页码的完整目录。）")
    rt.font.size = Pt(10); rt.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    tp = doc.add_paragraph()
    run = tp.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t"); placeholder.text = "【目录将在更新域后生成】"
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(instr); run._r.append(f2); run._r.append(placeholder); run._r.append(f3)
    add_page_break()

    # 行内强调解析：**加粗**、*斜体*
    INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")

    def add_inline(paragraph, text):
        for part in INLINE.split(text):
            if not part:
                continue
            if part.startswith("**") and part.endswith("**"):
                r = paragraph.add_run(part[2:-2]); r.bold = True
            elif part.startswith("*") and part.endswith("*") and len(part) > 2:
                r = paragraph.add_run(part[1:-1]); r.italic = True
            else:
                paragraph.add_run(part)

    def add_body_block(text):
        for para_text in text.split("\n"):
            line = para_text.strip()
            if not line:
                continue
            p = doc.add_paragraph()
            add_inline(p, line)

    first_chapter_of_vol = True
    for vol_title, chapters in structure:
        h = doc.add_paragraph(vol_title, style="Heading 2")
        h.paragraph_format.page_break_before = True
        first_chapter_of_vol = True
        for title, body in chapters:
            h3p = doc.add_paragraph(title, style="Heading 3")
            if not first_chapter_of_vol:
                h3p.paragraph_format.page_break_before = True
            first_chapter_of_vol = False
            add_body_block(body)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.page_break_before = True
    r = p.add_run("—— 全书完 ——")
    r.font.size = Pt(14); r.font.bold = True

    docx_path = os.path.join(BASE, f"{BOOK_TITLE}（全本）.docx")
    doc.save(docx_path)
    print("[ok] docx:", docx_path)

    # ============ 3. EPUB ============
    import markdown as md_lib
    import ebooklib
    from ebooklib import epub

    CSS = """
body { font-family: "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
       line-height: 1.7; margin: 5% 6%; }
h1 { font-size: 1.6em; text-align: center; margin: 1.2em 0 0.6em; }
h2 { font-size: 1.35em; margin: 1.2em 0 0.5em; page-break-before: always; }
h3 { font-size: 1.15em; margin: 1em 0 0.4em; page-break-before: always; }
p  { text-indent: 2em; margin: 0.35em 0; }
blockquote { margin: 0.6em 1.5em; color: #444; font-style: italic; }
hr { border: none; border-top: 1px solid #999; margin: 1em 4em; }
.center { text-align: center; }
.subtitle { text-align: center; font-size: 1.05em; color: #555; }
.theend { text-align: center; font-size: 1.1em; margin-top: 2em; }
"""

    def md_to_html(text):
        return md_lib.markdown(text, extensions=["extra"])

    book = epub.EpubBook()
    book.set_identifier("shiji-100-echo-2026")
    book.set_title(BOOK_TITLE)
    book.set_language("zh-CN")
    book.add_author("佚名")

    style_sheet = epub.EpubItem(
        uid="style", file_name="style/style.css", media_type="text/css", content=CSS
    )
    book.add_item(style_sheet)

    # 扉页
    title_page = epub.EpubHtml(title="扉页", file_name="title.xhtml", lang="zh-CN")
    title_page.content = (
        f"<h1>{BOOK_TITLE}</h1>"
        f'<p class="subtitle">{SUBTITLE}</p>'
        f'<p class="subtitle">—— 全书完 ——</p>'
    )
    book.add_item(title_page)

    # 目录页
    toc_html = ["<h1>目录</h1><ul>"]
    toc_items = []  # epub toc 嵌套
    for idx, (vol_title, chapters) in enumerate(structure, start=1):
        toc_html.append(f"<li><strong>{vol_title}</strong><ul>")
        vol_links = []
        for j, (title, body) in enumerate(chapters, start=1):
            fname = f"vol{idx}c{j}.xhtml"
            item = epub.EpubHtml(title=title, file_name=fname, lang="zh-CN")
            item.content = (
                f'<h3>{title}</h3><div>{md_to_html(body)}</div>'
            )
            item.add_item(style_sheet)
            book.add_item(item)
            vol_links.append(item)
            toc_html.append(f'<li><a href="{fname}">{title}</a></li>')
        toc_html.append("</ul></li>")
        toc_items.append((epub.Section(vol_title), vol_links))
    toc_html.append("</ul>")
    toc_page = epub.EpubHtml(title="目录", file_name="toc.xhtml", lang="zh-CN")
    toc_page.content = "".join(toc_html)
    book.add_item(toc_page)

    book.toc = toc_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + [title_page, toc_page] + [
        item for _, links in toc_items for item in links
    ]

    epub_path = os.path.join(BASE, f"{BOOK_TITLE}（全本）.epub")
    epub.write_epub(epub_path, book, {})
    print("[ok] epub:", epub_path)

    # ============ 4. 统计 ============
    cn_chars = len(re.sub(r"\s", "", md_text))
    print(f"[info] 整合文本总字符数（不含空白）：{cn_chars}")
    print("[info] 卷数：%d；章节数：%d" % (len(structure), sum(len(c) for _, c in structure)))


if __name__ == "__main__":
    main()
