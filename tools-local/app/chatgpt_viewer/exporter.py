import io
import html


class ConversationExporter:
    @staticmethod
    def to_txt(conversation: dict) -> bytes:
        lines = [f"Title: {conversation.get('title', 'Untitled')}", f"Date: {conversation.get('create_time', 'Unknown')}", ""]
        for msg in conversation.get("messages", []):
            role = "You" if msg["role"] == "user" else "ChatGPT"
            lines.append(f"--- {role} ---")
            lines.append(msg.get("content", ""))
            lines.append("")
        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def to_html(conversation: dict) -> bytes:
        title = html.escape(conversation.get("title", "Untitled"))
        date = html.escape(conversation.get("create_time", ""))
        parts = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            f"<title>{title}</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;background:#1e1e1e;color:#d4d4d4;}",
            "h1{color:#e5a04b;font-size:1.4rem;}",
            ".meta{color:#9e9e9e;font-size:0.85rem;margin-bottom:1.5rem;}",
            ".msg{padding:0.75rem 1rem;margin-bottom:0.5rem;border-radius:8px;white-space:pre-wrap;word-wrap:break-word;font-size:0.9rem;}",
            ".user{background:#2d2d2d;border-left:3px solid #e5a04b;}",
            ".assistant{background:#252526;border-left:3px solid #a6e22e;}",
            ".role{font-size:0.75rem;font-weight:600;margin-bottom:0.3rem;}",
            ".role.user-role{color:#e5a04b;}",
            ".role.assistant-role{color:#a6e22e;}",
            "</style></head><body>",
            f"<h1>{title}</h1>",
            f"<div class='meta'>{date}</div>",
        ]
        for msg in conversation.get("messages", []):
            role = msg["role"]
            label = "You" if role == "user" else "ChatGPT"
            role_class = "user" if role == "user" else "assistant"
            content = html.escape(msg.get("content", ""))
            parts.append(f"<div class='msg {role_class}'><div class='role {role_class}-role'>{label}</div>{content}</div>")
        parts.append("</body></html>")
        return "\n".join(parts).encode("utf-8")

    @staticmethod
    def to_pdf(conversation: dict) -> bytes:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, conversation.get("title", "Untitled"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, conversation.get("create_time", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        for msg in conversation.get("messages", []):
            role = "You" if msg["role"] == "user" else "ChatGPT"
            # Role label
            pdf.set_font("Helvetica", "B", 10)
            if msg["role"] == "user":
                pdf.set_text_color(229, 160, 75)
            else:
                pdf.set_text_color(166, 226, 46)
            pdf.cell(0, 6, role, new_x="LMARGIN", new_y="NEXT")

            # Content
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(60, 60, 60)
            content = msg.get("content", "")
            # fpdf2 handles multi_cell well for wrapping
            pdf.multi_cell(0, 5, content)
            pdf.ln(3)

        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    @staticmethod
    def to_docx(conversation: dict) -> bytes:
        from docx import Document
        from docx.shared import Pt, RGBColor

        doc = Document()
        doc.add_heading(conversation.get("title", "Untitled"), level=1)
        p = doc.add_paragraph(conversation.get("create_time", ""))
        p.runs[0].font.color.rgb = RGBColor(150, 150, 150)
        p.runs[0].font.size = Pt(9)

        for msg in conversation.get("messages", []):
            role = "You" if msg["role"] == "user" else "ChatGPT"
            p = doc.add_paragraph()
            run = p.add_run(role)
            run.bold = True
            run.font.size = Pt(10)
            if msg["role"] == "user":
                run.font.color.rgb = RGBColor(229, 160, 75)
            else:
                run.font.color.rgb = RGBColor(166, 226, 46)

            content_p = doc.add_paragraph(msg.get("content", ""))
            content_p.runs[0].font.size = Pt(9) if content_p.runs else None

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
