from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def build_report(filename: str, profile: dict, messages: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"Analysis report — {filename}")
    styles = getSampleStyleSheet()
    story = [Paragraph(f"AI Data Analyst Report: {filename}", styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(f"Dataset contains {profile['rows']:,} rows and {profile['columns']:,} columns. Duplicates: {profile['duplicates']:,}.", styles["BodyText"]))
    story.extend([Spacer(1, 12), Paragraph("Conversation findings", styles["Heading2"])])
    for message in messages:
        if message["role"] != "assistant":
            continue
        story.append(Paragraph(message["content"], styles["BodyText"]))
        result = message.get("result") or {}
        for item in result.get("tables", [])[:1]:
            rows = [item.get("columns", [])] + item.get("rows", [])[:15]
            if rows and rows[0]:
                report_table = Table([[str(value)[:80] for value in row] for row in rows], repeatRows=1)
                report_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 7)]))
                story.extend([Spacer(1, 6), report_table, Spacer(1, 10)])
        chart = result.get("chart")
        if chart and chart.get("type") == "bar":
            rows = chart.get("data", {}).get("rows", [])[:10]
            try:
                drawing = Drawing(440, 180)
                bars = VerticalBarChart()
                bars.x, bars.y, bars.width, bars.height = 35, 25, 380, 125
                bars.data = [[float(row[1]) for row in rows]]
                bars.categoryAxis.categoryNames = [str(row[0])[:12] for row in rows]
                drawing.add(bars)
                story.extend([Paragraph(chart.get("title", "Chart"), styles["Heading3"]), drawing, Spacer(1, 10)])
            except (TypeError, ValueError, IndexError):
                pass
    doc.build(story)
    return buffer.getvalue()
