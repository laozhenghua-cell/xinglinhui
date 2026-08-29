"""杏林汇 · 统一门诊处方笺 PDF(reportlab,内置 STSong CID 中文字体,无需字体文件)"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

INK = colors.HexColor("#17332E")
TEAL = colors.HexColor("#2E7D6B")
CINNABAR = colors.HexColor("#B03A2E")
GRAY = colors.HexColor("#55665F")
LINE = colors.HexColor("#D8D2C4")

SPECIALTY_NAMES = {
    "surgery": "外科疮疡",
    "anorectal": "肛肠痔漏",
    "pediatrics": "儿科",
    "alchemy": "丹药研究",
}


def _p(text: str, size: float = 10.5, color=INK, bold: bool = False, leading: float | None = None) -> Paragraph:
    return Paragraph(
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
        ParagraphStyle(
            "s", fontName="STSong-Light", fontSize=size, leading=leading or size * 1.55,
            textColor=color, spaceAfter=0, spaceBefore=0,
        ),
    )


def build_clinic_pdf(visit: dict[str, Any]) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title="杏林汇处方笺", author="杏林汇智能诊疗系统",
    )
    story = []

    # 抬头
    story.append(Paragraph("杏林汇 · 中医处方笺", ParagraphStyle(
        "h", fontName="STSong-Light", fontSize=19, leading=24, textColor=INK, alignment=1)))
    story.append(Spacer(1, 3))
    story.append(Paragraph("智能诊疗系统 · 辨证处方记录(仅供临床参考)", ParagraphStyle(
        "sub", fontName="STSong-Light", fontSize=9, leading=13, textColor=GRAY, alignment=1)))
    story.append(Spacer(1, 10))

    # 患者信息
    four = visit.get("four_diagnosis") or {}
    dx = visit.get("dx_result") or {}
    rx = visit.get("prescription") or {}
    fu = visit.get("followup") or {}
    info_rows = [
        ["患者", visit.get("patient_name") or "—", "性别", visit.get("gender") or "—"],
        ["年龄", str(visit.get("age") or "—"), "专科", SPECIALTY_NAMES.get(visit.get("specialty"), visit.get("specialty"))],
        ["主诉", (visit.get("chief_complaint") or "—")[:40], "日期", (visit.get("created_at") or "")[:16].replace("T", " ")],
    ]
    table_rows = []
    for r in info_rows:
        table_rows.append([_p(r[0], 9.5, GRAY), _p(r[1], 10.5), _p(r[2], 9.5, GRAY), _p(r[3], 10.5)])
    t = Table(table_rows)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2EFE7")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F2EFE7")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    def section(title: str, color=TEAL):
        story.append(Paragraph(title, ParagraphStyle(
            "sec", fontName="STSong-Light", fontSize=12, leading=16, textColor=color)))
        story.append(Spacer(1, 2))

    # 四诊
    section("【四诊】")
    parts = []
    if four.get("symptoms"):
        parts.append("症状:" + "、".join(four["symptoms"]))
    if four.get("tongue"):
        parts.append("舌象:" + four["tongue"])
    if four.get("pulse"):
        parts.append("脉象:" + four["pulse"])
    if four.get("local"):
        parts.append("局部:" + four["local"])
    if four.get("systemic"):
        parts.append("全身:" + four["systemic"])
    if four.get("detail"):
        parts.append("描述:" + four["detail"])
    story.append(_p(";".join(parts) if parts else "—"))
    story.append(Spacer(1, 7))

    # 辨证
    section("【辨证】")
    dx_lines = []
    for s in dx.get("syndromes") or []:
        dx_lines.append(f"证型:{s.get('name')}(匹配 {s.get('score')})")
    for d in dx.get("diseases") or []:
        dx_lines.append(f"病种:{d.get('name')}")
    if dx.get("ai"):
        ai = dx["ai"]
        if ai.get("syndrome_analysis"):
            dx_lines.append("AI 证型分析:" + ai["syndrome_analysis"])
        if ai.get("disease_suggestion"):
            dx_lines.append("AI 病种建议:" + ai["disease_suggestion"])
    story.append(_p("<br/>".join(dx_lines) if dx_lines else "—"))
    story.append(Spacer(1, 7))

    # 处方
    section("【处方】", CINNABAR)
    story.append(_p("方剂:" + ("、".join(rx.get("formulas") or []) or "—"), 11.5, CINNABAR))
    if rx.get("modification"):
        story.append(_p("加减化裁:" + rx["modification"]))
    if rx.get("external"):
        story.append(_p("外治法:" + rx["external"]))
    if rx.get("advice"):
        story.append(_p("医嘱/调护:" + rx["advice"]))
    if fu.get("note"):
        story.append(_p("随访:" + fu["note"]))
    if fu.get("followup_date"):
        story.append(_p("复诊日期:" + fu["followup_date"], color=CINNABAR))
    story.append(Spacer(1, 14))

    # 底部
    story.append(Paragraph("医师签名:________________        日期:________________", ParagraphStyle(
        "sig", fontName="STSong-Light", fontSize=11, leading=16, textColor=INK)))
    story.append(Spacer(1, 6))
    story.append(_p("⚠ 本处方笺由 AI 辅助辨证生成,仅供临床参考与教学研究,须经执业医师审核后方可使用;"
                    "涉及丹药(汞制剂等)严禁自行配制服用。", 8.5, GRAY))
    story.append(_p("杏林汇 · tcm.llixz.cn · 生成于 " + datetime.now().strftime("%Y-%m-%d %H:%M"), 8, GRAY))

    doc.build(story)
    return buf.getvalue()
