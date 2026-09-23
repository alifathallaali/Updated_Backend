from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

BRAND_RED = HexColor("#2FA7A0")
INK = HexColor("#16324F")
MUTED = HexColor("#64748B")


def build_decision_brief_pdf(product_id: str, status: str, output: dict) -> bytes:
    buffer = BytesIO()
    doc = canvas.Canvas(buffer, pagesize=A4)
    doc.setTitle(f"{product_id} Decision Brief")
    doc.setAuthor("PharmaLens AI")
    width, _height = A4
    margin = 18 * mm
    y = 280 * mm

    def line(text: str, size: int, color, font: str = "Helvetica", dy: float = 8 * mm):
        nonlocal y
        doc.setFillColor(color)
        doc.setFont(font, size)
        doc.drawString(margin, y, text)
        y -= dy

    def wrapped(text: str, size: int, color, font: str = "Helvetica", max_chars: int = 92, dy: float = 6 * mm):
        nonlocal y
        doc.setFillColor(color)
        doc.setFont(font, size)
        words = text.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if len(trial) > max_chars:
                doc.drawString(margin, y, current)
                y -= dy
                current = word
            else:
                current = trial
        if current:
            doc.drawString(margin, y, current)
            y -= dy

    line("PHARMALENS AI", 10, BRAND_RED, "Helvetica-Bold", 14 * mm)
    line("Decision brief", 26, INK, "Helvetica-Bold", 10 * mm)
    line(product_id, 18, BRAND_RED, "Helvetica-Bold", 8 * mm)
    wrapped(output.get("summary") or "Saved pharmaceutical decision output.", 12, INK)
    line(f"Status: {status}", 10, MUTED, "Helvetica", 10 * mm)

    line("Decision signals", 13, BRAND_RED, "Helvetica-Bold", 7 * mm)
    for key, value in list((output.get("metrics") or {}).items())[:10]:
        dash = "\u2014"
        wrapped(f"{key.replace('_', ' ')}: {value if value is not None else dash}", 10, INK, dy=5.5 * mm)


    y -= 3 * mm
    line("Evidence & confidence", 13, BRAND_RED, "Helvetica-Bold", 7 * mm)
    for item in (output.get("evidence") or [])[:10]:
        wrapped(f"{item.get('field')}: {item.get('value') if item.get('value') is not None else '-'} ({item.get('source')})", 10, INK, dy=5.5 * mm)


    confidence = output.get("confidence") or {}
    score = round((confidence.get("score") or 0) * 100)
    line(f"Confidence: {score}% \u2014 {confidence.get('level') or 'unknown'}", 11, INK, "Helvetica-Bold", 6 * mm)
    wrapped(confidence.get("rationale") or "Review the evidence before making a business decision.", 9, MUTED)


    for chart in (output.get("visualizations") or [])[:4]:
        if y < 55 * mm:
            doc.showPage()
            y = 280 * mm
        role = (chart.get("presentationPriority") or {}).get("role", "diagnostic")
        title = (chart.get("meta") or {}).get("title") or chart.get("chartId") or "Visualization"
        line(("Primary visual — " if role == "primary" else "Diagnostic visual — ") + str(title), 12, BRAND_RED, "Helvetica-Bold", 6 * mm)
        if (chart.get("presentationQuality") or {}).get("warnings"):
            wrapped("Presentation note: review visual density.", 8, MUTED, dy=4.5 * mm)
        data = chart.get("data") or []
        series = chart.get("series") or []
        x_key = chart.get("xKey")
        data_key = series[0].get("dataKey") if series else None
        for row in data[:8]:
            label = row.get(x_key, "") if x_key else ""
            value = row.get(data_key, "") if data_key else ""
            wrapped(f"{label}: {value}", 9, INK, dy=4.8 * mm)

    y -= 10 * mm
    line("Made by PharmaLens AI   /   Evidence first / Decisions forward", 9, MUTED, "Helvetica-Bold")

    doc.showPage()
    doc.save()
    return buffer.getvalue()
