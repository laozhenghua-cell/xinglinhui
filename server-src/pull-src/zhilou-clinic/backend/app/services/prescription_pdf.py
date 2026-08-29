"""中医处方笺 PDF 生成（reportlab + 内置 CJK 字体）。

使用 reportlab 的 UnicodeCIDFont('STSong-Light') 内置中文字体，
无需额外字体文件即可输出中文 PDF。
"""
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# 注册内置中文字体（Adobe 宋体 CID 字体）
try:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    CJK_FONT = "STSong-Light"
except Exception:
    CJK_FONT = "Helvetica"


def _style(font_size: float, bold: bool = False, color=None, align: int = 0, leading: float = None):
    return ParagraphStyle(
        name=f"s{font_size}{bold}{color}",
        fontName=CJK_FONT,
        fontSize=font_size,
        leading=leading or (font_size * 1.5),
        bold=bold if CJK_FONT != "STSong-Light" else False,
        textColor=color or colors.black,
        alignment=align,
        wordWrap="CJK",
    )


def _fmt_composition(composition: Any) -> str:
    """把组成（数组或字符串）转成处方正文文本。"""
    if isinstance(composition, list):
        parts = []
        for h in composition:
            if isinstance(h, dict):
                name = h.get("name", "")
                dosage = h.get("dosage", "")
                unit = h.get("unit", "")
                note = h.get("note", "")
                seg = f"{name}{dosage}{unit}"
                if note:
                    seg += f"（{note}）"
                parts.append(seg)
            else:
                parts.append(str(h))
        return "、".join(parts)
    if isinstance(composition, str) and composition:
        return composition
    return ""


def build_prescription_pdf(
    patient: Dict[str, Any],
    doctor_name: str,
    formula_name: str,
    composition: Any,
    dosage_instructions: str,
    duration_days: int,
    syndrome_name: str = "",
    treatment_principle: str = "",
    notes: str = "",
) -> bytes:
    """生成处方 PDF，返回字节流。"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="中医处方笺",
    )

    title_style = _style(22, bold=True, color=colors.HexColor("#12352a"), align=1, leading=28)
    subtitle_style = _style(11, color=colors.HexColor("#666666"), align=1)
    label_style = _style(11, bold=True, color=colors.HexColor("#333333"))
    body_style = _style(11.5, leading=20)
    note_style = _style(9, color=colors.HexColor("#888888"), align=1, leading=14)

    story = []

    # 标题
    story.append(Paragraph("中医处方笺", title_style))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("华夏痔瘘辅助诊疗系统 · 传承中医临床经验", subtitle_style))
    story.append(Spacer(1, 8 * mm))

    # 分界线
    story.append(Table([[""]], colWidths=[170 * mm], rowHeights=[1 * mm], style=TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, colors.HexColor("#12352a")),
    ])))
    story.append(Spacer(1, 6 * mm))

    # 患者信息行
    gender = patient.get("gender") or ""
    age = patient.get("age")
    age_text = f"{age}岁" if age is not None else ""
    phone = patient.get("phone") or ""
    patient_line = f"姓名：{patient.get('name') or '—'}　性别：{gender or '—'}　年龄：{age_text or '—'}"
    if phone:
        patient_line += f"　电话：{phone}"
    story.append(Paragraph(patient_line, body_style))
    story.append(Spacer(1, 4 * mm))

    # 诊断与治则
    if syndrome_name:
        story.append(Paragraph(f"中医诊断：{syndrome_name}", body_style))
    if treatment_principle:
        story.append(Paragraph(f"治则：{treatment_principle}", body_style))
    story.append(Spacer(1, 5 * mm))

    # 方剂
    story.append(Paragraph(f"<b>R　{formula_name or '—'}</b>", body_style))
    story.append(Spacer(1, 3 * mm))
    comp = _fmt_composition(composition)
    if comp:
        story.append(Paragraph(f"组成：{comp}", body_style))
    if dosage_instructions:
        story.append(Paragraph(f"用法：{dosage_instructions}", body_style))
    story.append(Paragraph(f"剂数：{duration_days or 7} 剂", body_style))
    if notes:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(f"加减 / 医嘱：{notes}", body_style))

    story.append(Spacer(1, 14 * mm))

    # 医师签名 + 日期
    today = datetime.now().strftime("%Y年%m月%d日")
    footer = Table(
        [[f"医师：{doctor_name or '—'}", f"日期：{today}"]],
        colWidths=[85 * mm, 85 * mm],
        style=TableStyle([
            ("FONT", (0, 0), (-1, -1), CJK_FONT, 11),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]),
    )
    story.append(footer)

    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "本处方依据中医临床经验辨证生成，仅供执业医师临床决策参考；"
        "用药须结合患者年龄、妊娠哺乳、肝肾功能、过敏史及合并用药复核。",
        note_style,
    ))

    doc.build(story)
    return buf.getvalue()
