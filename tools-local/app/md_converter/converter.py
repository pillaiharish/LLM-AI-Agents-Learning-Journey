import io
import markdown


# ──────────────────────────────────────────────────────────────────────────────
# CSS strategy:
#   BASE (no @media)  →  B&W-safe light styles. Used by WeasyPrint (PDF) and
#                         by @media print in browsers.
#   @media screen     →  Dark/coloured code blocks for a nicer browser preview.
#   @page             →  PDF page margins & page counter.
#
# Why: WeasyPrint renders in "print" mode, so it ignores @media screen.
# Keeping base styles light ensures every code block, diagram, and table
# prints cleanly on a black-and-white printer.
# ──────────────────────────────────────────────────────────────────────────────
_HTML_STYLE = """
<style>
  /* ── Reset ──────────────────────────────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  /* ── Page (WeasyPrint / print) ───────────────────────────────────────────  */
  @page {
    size: A4;
    margin: 2cm 2.2cm;
    @bottom-right {
      content: counter(page) " / " counter(pages);
      font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 9pt;
      color: #666;
    }
  }

  /* ── Body ────────────────────────────────────────────────────────────────── */
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                 Arial, sans-serif;
    font-size: 14px;
    line-height: 1.75;
    color: #111;
    background: #fff;
    max-width: 820px;
    margin: 2rem auto;
    padding: 0 2rem 4rem;
  }

  /* ── Headings ────────────────────────────────────────────────────────────── */
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.6em;
    margin-bottom: 0.45em;
    font-weight: 700;
    line-height: 1.25;
    color: #111;
    page-break-after: avoid;
  }
  h1 {
    font-size: 1.9rem;
    border-bottom: 2.5px solid #333;
    padding-bottom: 0.3em;
  }
  h2 {
    font-size: 1.45rem;
    border-bottom: 1px solid #bbb;
    padding-bottom: 0.2em;
  }
  h3 { font-size: 1.2rem; }
  h4 { font-size: 1.05rem; }
  h5, h6 { font-size: 0.95rem; color: #444; }

  /* Heading anchors (TOC ¶ links) — hide on print */
  .headerlink { display: none; }

  /* ── Paragraph / inline ──────────────────────────────────────────────────── */
  p { margin: 0.7em 0; }

  a { color: #333; text-decoration: underline; }

  strong { font-weight: 700; }
  em     { font-style: italic; }

  /* ── Inline code ─────────────────────────────────────────────────────────── */
  /* Light background + dark text — readable in B&W */
  code {
    font-family: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'Courier New',
                 monospace;
    font-size: 0.83em;
    background: #f0f0f0;
    border: 1px solid #d0d0d0;
    padding: 0.1em 0.35em;
    border-radius: 3px;
    color: #1a1a1a;
  }

  /* ── Block code / diagrams ───────────────────────────────────────────────── */
  /*
   * Light background + solid left-rule border.
   * Works in B&W: content is dark text on white/light-grey.
   * white-space: pre keeps ASCII box-drawing diagrams aligned.
   */
  pre {
    background: #f6f6f6;
    color: #1a1a1a;
    border: 1px solid #ccc;
    border-left: 4px solid #555;
    padding: 0.9rem 1rem;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre;
    word-wrap: normal;
    margin: 1em 0;
    page-break-inside: avoid;
    font-size: 0.82em;
    line-height: 1.55;
  }

  pre code {
    background: none;
    border: none;
    padding: 0;
    color: inherit;
    font-size: inherit;
  }

  /* ── Syntax-highlight overrides (codehilite) ─────────────────────────────── */
  /* Strip ALL pygments colours — everything becomes near-black for B&W print. */
  .highlight, .codehilite { background: #f6f6f6 !important; }
  .highlight span, .codehilite span {
    color: #1a1a1a !important;
    background: none !important;
  }
  /* Keep bold for keywords so they're still distinguishable in B&W */
  .highlight .k,  .highlight .kd, .highlight .kn,
  .highlight .kr, .highlight .kt, .highlight .kp { font-weight: 700; }
  /* Comments italic */
  .highlight .c,  .highlight .c1, .highlight .cm,
  .highlight .cs, .highlight .cp { font-style: italic; color: #555 !important; }
  /* Strings slightly lighter */
  .highlight .s,  .highlight .s1, .highlight .s2,
  .highlight .se, .highlight .sa { color: #333 !important; }

  /* ── Blockquote ──────────────────────────────────────────────────────────── */
  blockquote {
    border-left: 4px solid #888;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f9f9f9;
    color: #333;
    border-radius: 0 4px 4px 0;
    font-style: italic;
  }
  blockquote p { margin: 0; }

  /* ── Lists ───────────────────────────────────────────────────────────────── */
  ul, ol { margin: 0.7em 0 0.7em 1.6em; }
  li { margin: 0.2em 0; }
  li > ul, li > ol { margin-top: 0.2em; }

  /* ── Tables ──────────────────────────────────────────────────────────────── */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 0.88em;
    page-break-inside: avoid;
  }
  th {
    background: #e8e8e8;
    font-weight: 700;
    padding: 0.55em 0.8em;
    text-align: left;
    border: 1.5px solid #aaa;
    color: #111;
  }
  td {
    padding: 0.45em 0.8em;
    border: 1px solid #bbb;
    color: #111;
  }
  tr:nth-child(even) td { background: #f4f4f4; }

  /* ── HR ──────────────────────────────────────────────────────────────────── */
  hr {
    border: none;
    border-top: 1.5px solid #bbb;
    margin: 2em 0;
  }

  /* ── Images ──────────────────────────────────────────────────────────────── */
  img { max-width: 100%; page-break-inside: avoid; }

  /* ── Footnotes ───────────────────────────────────────────────────────────── */
  .footnote { font-size: 0.85em; border-top: 1px solid #ccc; margin-top: 2em; }

  /* ── Task lists ──────────────────────────────────────────────────────────── */
  .task-list-item { list-style: none; margin-left: -1.4em; }
  .task-list-item input { margin-right: 0.4em; }

  /* ── SCREEN ONLY — dark code blocks for a nicer browser preview ──────────── */
  @media screen {
    pre {
      background: #1e1e1e;
      color: #d4d4d4;
      border-color: #444;
      border-left-color: #999;
    }
    pre code { color: inherit; }

    .highlight, .codehilite { background: #1e1e1e !important; }
    .highlight span, .codehilite span { color: #d4d4d4 !important; }
    .highlight .k,  .highlight .kd { color: #569cd6 !important; font-weight: normal; }
    .highlight .s,  .highlight .s1, .highlight .s2 { color: #ce9178 !important; }
    .highlight .c,  .highlight .c1 { color: #6a9955 !important; font-style: normal; }
    .highlight .n  { color: #9cdcfe !important; }
    .highlight .o  { color: #d4d4d4 !important; }

    code { background: #2a2a2a; border-color: #555; color: #e0e0e0; }
  }
</style>
"""


class MarkdownConverter:
    MD_EXTENSIONS = [
        "tables",
        "fenced_code",
        "codehilite",
        "toc",
        "footnotes",
        "attr_list",
        "def_list",
        "abbr",
        "nl2br",
        "sane_lists",
        "smarty",
        "meta",
    ]

    @staticmethod
    def md_to_html(md_text: str, title: str = "Document") -> str:
        """Convert Markdown text to a complete, styled HTML document."""
        import xml.etree.ElementTree as ET

        # Use safe extensions (skip codehilite if pygments missing)
        exts = ["tables", "fenced_code", "toc", "footnotes",
                 "attr_list", "def_list", "nl2br", "sane_lists", "smarty"]
        try:
            import pygments  # noqa
            exts.append("codehilite")
        except ImportError:
            pass

        md = markdown.Markdown(extensions=exts, extension_configs={
            "toc": {"permalink": True},
            "smarty": {"smart_quotes": True},
        })
        body_html = md.convert(md_text)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {_HTML_STYLE}
</head>
<body>
{body_html}
</body>
</html>"""

    @staticmethod
    def html_to_pdf(html: str) -> bytes:
        """Convert an HTML string to PDF bytes using WeasyPrint."""
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        font_config = FontConfiguration()
        pdf_bytes = HTML(string=html).write_pdf(font_config=font_config)
        return pdf_bytes

    @staticmethod
    def md_to_pdf(md_text: str, title: str = "Document") -> bytes:
        """Full pipeline: Markdown → HTML → PDF."""
        html = MarkdownConverter.md_to_html(md_text, title)
        return MarkdownConverter.html_to_pdf(html)
