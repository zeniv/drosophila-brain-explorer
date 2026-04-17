"""
Генератор PDF-руководства по Drosophila Brain Explorer
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Шрифты (встроенные + Helvetica для кириллицы через Helvetica fallback) ──
# Используем DejaVu для кириллицы если доступен, иначе встроенный

def find_font(names):
    paths = [
        "C:/Windows/Fonts/",
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/",
    ]
    for name in names:
        for p in paths:
            fp = p + name
            if os.path.exists(fp):
                return fp
    return None

# Пытаемся найти шрифт с кириллицей
dejavu_regular = find_font(["DejaVuSans.ttf", "dejavu-sans.ttf"])
dejavu_bold    = find_font(["DejaVuSans-Bold.ttf", "dejavu-sans-bold.ttf"])
dejavu_italic  = find_font(["DejaVuSans-Oblique.ttf", "dejavu-sans-oblique.ttf"])

arial_regular = find_font(["Arial.ttf", "arial.ttf"])
arial_bold    = find_font(["Arial Bold.ttf", "arialbd.ttf", "Arial_Bold.ttf"])

FONT_REGULAR = "Helvetica"
FONT_BOLD    = "Helvetica-Bold"
FONT_ITALIC  = "Helvetica-Oblique"

if dejavu_regular and dejavu_bold:
    try:
        pdfmetrics.registerFont(TTFont("CyrRegular", dejavu_regular))
        pdfmetrics.registerFont(TTFont("CyrBold",    dejavu_bold))
        if dejavu_italic:
            pdfmetrics.registerFont(TTFont("CyrItalic", dejavu_italic))
        else:
            pdfmetrics.registerFont(TTFont("CyrItalic", dejavu_regular))
        FONT_REGULAR = "CyrRegular"
        FONT_BOLD    = "CyrBold"
        FONT_ITALIC  = "CyrItalic"
        print("Using DejaVu fonts (Cyrillic)")
    except Exception as e:
        print(f"DejaVu failed: {e}")
elif arial_regular and arial_bold:
    try:
        pdfmetrics.registerFont(TTFont("CyrRegular", arial_regular))
        pdfmetrics.registerFont(TTFont("CyrBold",    arial_bold))
        pdfmetrics.registerFont(TTFont("CyrItalic",  arial_regular))
        FONT_REGULAR = "CyrRegular"
        FONT_BOLD    = "CyrBold"
        FONT_ITALIC  = "CyrItalic"
        print("Using Arial fonts (Cyrillic)")
    except Exception as e:
        print(f"Arial failed: {e}")
else:
    print("Warning: no Cyrillic font found, using built-in (may show boxes)")

# ── Цвета ──────────────────────────────────────────────────────────────────
C_BRAND      = colors.HexColor("#0ea5e9")   # голубой (бренд)
C_DARK       = colors.HexColor("#0f172a")   # почти чёрный
C_ACCENT_G   = colors.HexColor("#22c55e")   # зелёный (возбуждение)
C_ACCENT_R   = colors.HexColor("#ef4444")   # красный (торможение)
C_ACCENT_Y   = colors.HexColor("#f59e0b")   # жёлтый (гипотезы)
C_GRAY_L     = colors.HexColor("#f1f5f9")   # светло-серый фон
C_GRAY_M     = colors.HexColor("#94a3b8")   # средний серый
C_BORDER     = colors.HexColor("#e2e8f0")   # граница таблицы

# ── Стили ──────────────────────────────────────────────────────────────────
def make_styles():
    s = {}

    s["cover_title"] = ParagraphStyle("cover_title",
        fontName=FONT_BOLD, fontSize=28, leading=34,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=8)

    s["cover_sub"] = ParagraphStyle("cover_sub",
        fontName=FONT_REGULAR, fontSize=13, leading=18,
        textColor=colors.HexColor("#bae6fd"), alignment=TA_CENTER)

    s["cover_meta"] = ParagraphStyle("cover_meta",
        fontName=FONT_ITALIC, fontSize=9, leading=13,
        textColor=colors.HexColor("#7dd3fc"), alignment=TA_CENTER)

    s["h1"] = ParagraphStyle("h1",
        fontName=FONT_BOLD, fontSize=18, leading=24,
        textColor=C_BRAND, spaceBefore=20, spaceAfter=8,
        borderPad=0)

    s["h2"] = ParagraphStyle("h2",
        fontName=FONT_BOLD, fontSize=13, leading=18,
        textColor=C_DARK, spaceBefore=14, spaceAfter=6)

    s["h3"] = ParagraphStyle("h3",
        fontName=FONT_BOLD, fontSize=11, leading=15,
        textColor=colors.HexColor("#1e40af"), spaceBefore=10, spaceAfter=4)

    s["body"] = ParagraphStyle("body",
        fontName=FONT_REGULAR, fontSize=10, leading=16,
        textColor=C_DARK, alignment=TA_JUSTIFY, spaceAfter=6)

    s["body_small"] = ParagraphStyle("body_small",
        fontName=FONT_REGULAR, fontSize=9, leading=13,
        textColor=colors.HexColor("#334155"), spaceAfter=4)

    s["bullet"] = ParagraphStyle("bullet",
        fontName=FONT_REGULAR, fontSize=10, leading=15,
        textColor=C_DARK, leftIndent=18, spaceAfter=4,
        firstLineIndent=-12)

    s["code"] = ParagraphStyle("code",
        fontName="Courier", fontSize=8.5, leading=13,
        textColor=colors.HexColor("#1e293b"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=C_BORDER, borderWidth=0.5,
        borderPad=6, leftIndent=10, spaceAfter=6)

    s["note"] = ParagraphStyle("note",
        fontName=FONT_ITALIC, fontSize=9, leading=13,
        textColor=colors.HexColor("#475569"),
        backColor=colors.HexColor("#f0f9ff"),
        borderColor=C_BRAND, borderWidth=1,
        borderPad=6, leftIndent=6, spaceAfter=8)

    s["caption"] = ParagraphStyle("caption",
        fontName=FONT_ITALIC, fontSize=8.5, leading=12,
        textColor=C_GRAY_M, alignment=TA_CENTER, spaceAfter=10)

    s["toc"] = ParagraphStyle("toc",
        fontName=FONT_REGULAR, fontSize=11, leading=20,
        textColor=C_DARK, leftIndent=10)

    s["page_num"] = ParagraphStyle("page_num",
        fontName=FONT_REGULAR, fontSize=8,
        textColor=C_GRAY_M, alignment=TA_CENTER)

    return s

# ── Вспомогательные блоки ──────────────────────────────────────────────────
def section_rule(color=C_BRAND):
    return HRFlowable(width="100%", thickness=2, color=color, spaceAfter=4)

def thin_rule():
    return HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceAfter=4)

def spacer(h=6):
    return Spacer(1, h)

def info_box(S, text, color=C_BRAND, bg=None):
    bg = bg or colors.HexColor("#f0f9ff")
    style = ParagraphStyle("info",
        fontName=FONT_REGULAR, fontSize=10, leading=15,
        backColor=bg, borderColor=color, borderWidth=1.5,
        borderPad=8, textColor=C_DARK, spaceAfter=10)
    return Paragraph(text, style)

def param_table(S, rows, col_widths=None):
    col_widths = col_widths or [3.5*cm, 2.2*cm, 2.5*cm, 8.5*cm]
    data = [["Параметр", "По умолчанию", "Диапазон", "Описание"]] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), C_BRAND),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,0), 9),
        ("FONTNAME",     (0,1), (-1,-1), FONT_REGULAR),
        ("FONTSIZE",     (0,1), (-1,-1), 8.5),
        ("BACKGROUND",   (0,1), (-1,-1), colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C_GRAY_L]),
        ("GRID",         (0,0), (-1,-1), 0.4, C_BORDER),
        ("ALIGN",        (1,0), (2,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ]))
    return t

def hyp_table(S, rows):
    data = [["Гипотеза", "Что проверяем", "Ожидаемый результат", "Статус"]] + rows
    cw = [4.5*cm, 5*cm, 5*cm, 2.2*cm]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), C_DARK),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,0), 8.5),
        ("FONTNAME",     (0,1), (-1,-1), FONT_REGULAR),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C_GRAY_L]),
        ("GRID",         (0,0), (-1,-1), 0.4, C_BORDER),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("ALIGN",        (3,0), (3,-1), "CENTER"),
    ]))
    return t

# ── Главная функция генерации ──────────────────────────────────────────────
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title="Drosophila Brain Explorer — Руководство",
        author="Drosophila Brain Explorer Team",
    )
    S = make_styles()
    story = []

    # ════════════════════════════════════════════════════════════
    # ОБЛОЖКА
    # ════════════════════════════════════════════════════════════
    cover_bg = Table(
        [[Paragraph("", S["body"])]],
        colWidths=[doc.width], rowHeights=[6.5*cm]
    )
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_DARK),
        ("TOPPADDING",  (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))

    # Эмоджи-заглушка вместо SVG
    title_inner = [
        Paragraph("Drosophila Brain Explorer", S["cover_title"]),
        spacer(8),
        Paragraph("Интерактивная платформа для симуляции нейронных цепей мозга", S["cover_sub"]),
        spacer(10),
        Paragraph("Leaky Integrate-and-Fire  |  FlyWire Connectome  |  125 000+ нейронов  |  15 М синапсов", S["cover_meta"]),
        spacer(14),
        Paragraph("Основано на: Shiu et al., Nature 634, 210–218 (2024)", S["cover_meta"]),
    ]
    cover_table = Table(
        [[item] for item in title_inner],
        colWidths=[doc.width]
    )
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_DARK),
        ("TOPPADDING",  (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING", (0,0),(-1,-1), 20),
        ("RIGHTPADDING",(0,0),(-1,-1), 20),
    ]))
    story.append(cover_table)
    story.append(spacer(16))

    # ── Краткое содержание (оглавление) ──────────────────────
    toc_data = [
        ["1", "Что такое мозг дрозофилы — и зачем его моделировать"],
        ["2", "Научная статья Nature 2024 — ключевые открытия"],
        ["3", "Архитектура модели: как работает симулятор"],
        ["4", "Именованные нейроны: цепочки от сенсора до мотора"],
        ["5", "FlyWire.ai — как получить IDs нейронов"],
        ["6", "Гипотезы, которые можно проверить"],
        ["7", "Приложение Drosophila Brain Explorer — интерфейс"],
        ["8", "Руководство по симуляциям: пошаговые сценарии"],
        ["9", "Полный справочник параметров"],
        ["10", "Как опубликовать результаты на arXiv"],
    ]
    toc_table = Table(toc_data, colWidths=[1*cm, doc.width - 1*cm])
    toc_table.setStyle(TableStyle([
        ("FONTNAME",  (0,0),(-1,-1), FONT_REGULAR),
        ("FONTSIZE",  (0,0),(-1,-1), 10),
        ("TEXTCOLOR", (0,0),(0,-1), C_BRAND),
        ("FONTNAME",  (0,0),(0,-1), FONT_BOLD),
        ("TOPPADDING",(0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LINEBELOW", (0,0),(-1,-2), 0.3, C_BORDER),
    ]))
    story.append(Paragraph("Содержание", S["h1"]))
    story.append(section_rule())
    story.append(toc_table)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 1 — ВВЕДЕНИЕ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Что такое мозг дрозофилы — и зачем его моделировать", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "Drosophila melanogaster — плодовая мушка — один из главных объектов нейробиологии последних 100 лет. "
        "Её мозг содержит около 125 000 нейронов (для сравнения: мозг мыши — 70 миллионов, человека — 86 миллиардов). "
        "Несмотря на кажущуюся простоту, дрозофила демонстрирует сложное поведение: поиск пищи, груминг, ухаживание, обучение и память. "
        "Именно поэтому её мозг стал первым объектом, для которого был построен полный коннектом — карта всех нейронных связей.",
        S["body"]))

    story.append(Paragraph("Что такое коннектом?", S["h2"]))
    story.append(Paragraph(
        "Коннектом — это полная «схема проводки» мозга: какой нейрон с каким соединён и сколько синапсов между ними. "
        "Проект FlyWire использовал электронную микроскопию для сканирования мозга дрозофилы с нанометровым разрешением "
        "и с помощью нейросетей реконструировал все 125 000 нейронов и 50 миллионов синаптических связей. "
        "Это заняло несколько лет и потребовало тысяч человеко-часов аннотации.",
        S["body"]))

    story.append(info_box(S,
        "Аналогия: представьте город, в котором 125 000 домов (нейроны), соединённых 50 миллионами дорог (синапсы). "
        "Коннектом — это полная карта этого города. Симуляция — эксперимент: что произойдёт, если поджечь один квартал?",
        C_ACCENT_G, colors.HexColor("#f0fdf4")))

    story.append(Paragraph("Почему именно дрозофила?", S["h2"]))
    body_why = [
        "• Полный коннектом известен — можно работать с реальными данными, а не моделями",
        "• Богатый генетический инструментарий: можно включать и выключать отдельные нейроны с помощью оптогенетики",
        "• Хорошо изученное поведение: кормление, груминг, полёт — есть «ground truth» для проверки предсказаний",
        "• Скорость: симуляция 125к нейронов занимает секунды, а не месяцы как для мозга млекопитающих",
    ]
    for b in body_why:
        story.append(Paragraph(b, S["bullet"]))

    story.append(spacer(8))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 2 — СТАТЬЯ NATURE
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("2. Научная статья Nature 2024 — ключевые открытия", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "В октябре 2024 года в журнале Nature (Vol. 634, стр. 210–218) вышла статья группы Кристин Скотт "
        "(Университет Калифорнии, Беркли): «A Drosophila computational brain model reveals sensorimotor processing». "
        "Авторы создали первую полную вычислительную модель мозга дрозофилы и проверили её предсказания экспериментально.",
        S["body"]))

    story.append(Paragraph("Главная идея", S["h2"]))
    story.append(info_box(S,
        "Только синаптическая связность + тип нейромедиатора — достаточно для воспроизведения сенсомоторных трансформаций. "
        "Никаких дополнительных биофизических параметров. Структура сети несёт в себе функцию.",
        C_BRAND))

    story.append(Paragraph("Ключевые результаты", S["h2"]))

    findings = [
        ["#", "Открытие", "Как проверено"],
        ["1", "Активация сахарных GRN-нейронов → возбуждение мотонейрона MN9 (пробосцис). Модель предсказала правильно.", "Оптогенетика + поведенческие тесты (>90% точность)"],
        ["2", "Сахарный и водный вкусовые пути используют 250 общих нейронов из ~380. Они аддитивно усиливают пробосцис.", "Кальциевая визуализация, silencing отдельных нейронов"],
        ["3", "Горький вкус (Gr66a) использует всего 2 общих нейрона с сахарным путём. Полная сегрегация аверсивного и аппетитного.", "Поведенческие тесты с sucrose + bitter одновременно"],
        ["4", "Механосенсорные нейроны Джонстонова органа → 8 нейронов грумингового каскада. Полный сенсомоторный путь.", "Анальная петля CsChrimson + подсчёт актов груминга"],
        ["5", "Нейроны Usnea — нейропептидергические. Модель не предсказала их роль корректно → указывает на ограничения.", "Нокдаун Amontillado → фенокопирует silencing Usnea"],
    ]
    t_findings = Table(findings, colWidths=[0.6*cm, 9*cm, 6.8*cm], repeatRows=1)
    t_findings.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), C_DARK),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE",     (0,0), (-1,0), 8.5),
        ("FONTNAME",     (0,1), (-1,-1), FONT_REGULAR),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",         (0,0), (-1,-1), 0.4, C_BORDER),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("ALIGN",        (0,0),(0,-1), "CENTER"),
        ("BACKGROUND",   (0,1),(0,5), colors.HexColor("#dbeafe")),
    ]))
    story.append(t_findings)
    story.append(spacer(8))

    story.append(Paragraph("Чем это важно для науки?", S["h2"]))
    story.append(Paragraph(
        "Статья доказала принцип: вычислительная модель на основе коннектома — самостоятельный инструмент для генерации "
        "гипотез, которые затем проверяются in vivo. Это меняет парадигму нейробиологии: вместо годами исследовать "
        "один нейрон, можно за секунды «активировать» тысячи и получить предсказание об их роли. "
        "Авторы сравнивают это с трансформацией в геномике, когда секвенирование ДНК стало рутинным инструментом.",
        S["body"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 3 — АРХИТЕКТУРА МОДЕЛИ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Архитектура модели: как работает симулятор", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph("Leaky Integrate-and-Fire (LIF) — нейрон-«конденсатор»", S["h2"]))
    story.append(Paragraph(
        "Каждый нейрон в модели описывается простым уравнением: мембранный потенциал накапливает входные сигналы "
        "(как конденсатор заряд) и «утекает» со временем. Когда потенциал превышает порог — нейрон «стреляет» "
        "(генерирует потенциал действия), сигнал передаётся соседям, а потенциал сбрасывается.",
        S["body"]))

    story.append(Paragraph("Уравнения динамики (α-синапс, точная модель из статьи):", S["h3"]))
    eq_style = ParagraphStyle("eq", fontName="Courier", fontSize=9.5, leading=15,
                       backColor=C_GRAY_L, borderPad=8, textColor=C_DARK,
                       leftIndent=10, spaceAfter=3)
    story.append(Paragraph("dv/dt = (g - (v - V_rest)) / T_mbr      [мембранный потенциал]", eq_style))
    story.append(Paragraph("dg/dt = -g / Tau                          [синаптический ток]",   eq_style))
    story.append(Paragraph(
        "Это α-синапс: при спайке пресинаптического нейрона переменная g мгновенно увеличивается на w (вес синапса), "
        "затем экспоненциально затухает к 0 с константой Tau=5 мс. Мембранный потенциал v стремится "
        "к (V_rest + g) и возвращается к V_rest при g→0. Если v > V_threshold → спайк, v сбрасывается в V_reset.",
        S["body_small"]))

    story.append(Paragraph("Что отличает эту модель от других?", S["h2"]))

    diff_data = [
        ["Обычные модели нейронных сетей (ML)", "Модель FlyWire LIF"],
        ["Произвольная топология, обучение градиентным спуском", "Реальная анатомия: 15М синапсов из EM-данных"],
        ["Веса синтетические, подобранные", "Веса = количество синапсов * 0.275 мВ (измерено)"],
        ["Нейрон — абстрактный узел", "Каждый нейрон = реальная клетка с FlyWire ID"],
        ["Нет биологической интерпретации", "Тип нейромедиатора определяет знак (+/-) синапса"],
        ["Обучение на данных", "Нет обучения — только структура + физика"],
    ]
    t_diff = Table(diff_data, colWidths=[8*cm, 8.4*cm], repeatRows=1)
    t_diff.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#374151")),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("FONTNAME",   (0,1),(-1,-1), FONT_REGULAR),
        ("BACKGROUND", (0,1),(0,-1), colors.HexColor("#fef3c7")),
        ("BACKGROUND", (1,1),(1,-1), colors.HexColor("#dcfce7")),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_diff)
    story.append(spacer(6))

    story.append(Paragraph("Данные коннектома (файлы)", S["h2"]))
    story.append(Paragraph(
        "Модель работает на двух файлах из репозитория Edmond MPG (doi:10.17617/3.CZODIW):",
        S["body"]))
    files_data = [
        ["Файл", "Размер", "Содержимое"],
        ["Connectivity_783.parquet", "97 MB", "15 091 983 синапса: Presynaptic_ID, Postsynaptic_ID, Excitatory (0/1), N_syn"],
        ["Completeness_783.csv", "3 MB", "138 639 нейронов FlyWire v783: root_id, Completed (True/False)"],
    ]
    t_files = Table(files_data, colWidths=[5.5*cm, 2*cm, 9*cm], repeatRows=1)
    t_files.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), C_BRAND),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("FONTNAME",   (0,1),(-1,-1), "Courier"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_files)
    story.append(Paragraph(
        "Примечание: results.zip на Edmond MPG — это уже готовые результаты симуляций из статьи (~несколько ГБ). "
        "Для запуска новых симуляций он не нужен.",
        S["note"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 4 — ИМЕНОВАННЫЕ НЕЙРОНЫ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("4. Именованные нейроны: цепочки от сенсора до мотора", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "Статья Shiu et al. 2024 не просто активировала «какие-то» нейроны — авторы идентифицировали "
        "конкретные клетки в FlyWire-коннектоме и дали им имена. Ниже — полные нейронные цепочки "
        "сенсомоторных преобразований. Каждый нейрон можно найти в FlyWire Codex и использовать его ID в симуляции.",
        S["body"]))

    story.append(Paragraph("Вкусовая цепочка: сахар → пробосцис (MN9)", S["h2"]))
    story.append(info_box(S,
        "GRN (Gr5a/Gr64f) → G2N-1 → Rattle → Usnea → FMIn → Sternum → "
        "Bract 1 / Bract 2 → Roundup / Roundtree / Rounddown → MN9 (мотонейрон пробосциса)",
        C_ACCENT_G, colors.HexColor("#f0fdf4")))

    chain_data = [
        ["Нейрон", "Порядок", "Тип", "Функция", "Реагирует на"],
        ["Gr5a GRN",     "0-й (ГРН)",  "Сенсорный",      "Детектор сахара на лабеллуме",              "Сахар (excit.)"],
        ["Gr64f GRN",    "0-й (ГРН)",  "Сенсорный",      "Детектор воды/влажности на лабеллуме",      "Вода (excit.)"],
        ["G2N-1",        "2-й",        "Интернейрон",     "Первый центральный узел вкусового пути",    "Сахар"],
        ["Rattle",       "2-й",        "Интернейрон",     "Усилитель сигнала sugar-пути в SEZ",        "Сахар"],
        ["Usnea",        "2-й",        "Нейропептидный",  "Нейропептидергический узел (Amontillado!)", "Вода (эксклюзивно)"],
        ["FMIn",         "2-й",        "Интернейрон",     "Прогностическое звено вкусового пути",      "Сахар"],
        ["Fudog",        "2-й",        "Интернейрон",     "Водно-сахарный интегратор в SEZ",           "Вода + Сахар"],
        ["Zorro",        "2-й",        "Интернейрон",     "Водный путь, необходим для PER на воду",    "Вода"],
        ["Phantom",      "2-й",        "Интернейрон",     "Общий нейрон вода+сахар путей",             "Вода + Сахар"],
        ["Sternum",      "3-й",        "Премоторный",     "Промежуточный узел к мотонейронам",         "Сахар + Вода"],
        ["Bract 1/2",    "3-й",        "Премоторный",     "Прямое возбуждение MN9",                   "Сахар + Вода"],
        ["Roundup/tree", "3-й",        "Премоторный",     "Параллельный путь к MN9",                  "Сахар + Вода"],
        ["MN9",          "Мотор",      "Мотонейрон",      "Непосредственное управление пробосцисом",   "Выход: PER"],
        ["MN6",          "Мотор",      "Мотонейрон",      "Расширение лабелл для потребления",         "Выход: feeding"],
    ]
    t_chain = Table(chain_data, colWidths=[2.6*cm, 2*cm, 2.6*cm, 5*cm, 4.2*cm], repeatRows=1)
    t_chain.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),   C_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),   colors.white),
        ("FONTNAME",      (0,0), (-1,0),   FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1),  8),
        ("FONTNAME",      (0,1), (-1,-1),  FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),  [colors.white, C_GRAY_L]),
        ("GRID",          (0,0), (-1,-1),  0.4, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1),  "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1),  4),
        ("BOTTOMPADDING", (0,0), (-1,-1),  4),
        ("LEFTPADDING",   (0,0), (-1,-1),  5),
        # Highlight motor neurons
        ("BACKGROUND",    (0,13),(- 1,14), colors.HexColor("#fef3c7")),
        # Highlight sensory
        ("BACKGROUND",    (0,1), (-1,2),   colors.HexColor("#dcfce7")),
    ]))
    story.append(t_chain)
    story.append(spacer(6))

    story.append(Paragraph("Груминговая цепочка: Джонстонов орган → aDN2", S["h2"]))
    story.append(info_box(S,
        "JON (JO-C / JO-E / JO-F) → aBN1 / aBN2 → aDN1 → aDN2  (нейрон-команда груминга антенн)",
        C_BRAND))
    groom_data = [
        ["Нейрон",   "Класс",              "Функция"],
        ["JO-C/E/F", "Механосенсорные JON","Детектируют вибрацию антенн, проецируют в AMMC/JOC"],
        ["aBN1",     "Интернейрон",        "Активируется JO-F; ключевой узел инициации груминга"],
        ["aBN2",     "Интернейрон",        "Параллельный путь; совместно с aBN1 запускает aDN"],
        ["aDN1",     "Нисходящий нейрон",  "Связь с aBN1; предшественник aDN2"],
        ["aDN2",     "Нисходящий нейрон",  "Финальная команда: инициирует груминг антенн во VNC"],
    ]
    t_groom = Table(groom_data, colWidths=[2.5*cm, 3.5*cm, 10.4*cm], repeatRows=1)
    t_groom.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),   C_BRAND),
        ("TEXTCOLOR",     (0,0), (-1,0),   colors.white),
        ("FONTNAME",      (0,0), (-1,0),   FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1),  8.5),
        ("FONTNAME",      (0,1), (-1,-1),  FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),  [colors.white, C_GRAY_L]),
        ("GRID",          (0,0), (-1,-1),  0.4, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1),  "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1),  5),
        ("BOTTOMPADDING", (0,0), (-1,-1),  5),
        ("LEFTPADDING",   (0,0), (-1,-1),  6),
    ]))
    story.append(t_groom)
    story.append(spacer(6))
    story.append(Paragraph(
        "Важно: 3 ингибиторных нейрона подавляют aBN1 при умеренной активации JO-F. "
        "Модель предсказала это — и эксперимент подтвердил (заглушение 3 нейронов → сильный рост aBN1).",
        S["note"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 5 — FLYWIRE
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("5. FlyWire.ai — как получить IDs нейронов", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "FlyWire (flywire.ai) — это онлайн-платформа, созданная командами Princeton, Cambridge и Google, "
        "где хранится и визуализируется коннектом мозга дрозофилы. Именно отсюда берутся root_id — "
        "уникальные 18-значные идентификаторы нейронов, которые используются в нашем симуляторе.",
        S["body"]))

    fw_data = [
        ["Ресурс",                      "URL",                            "Для чего"],
        ["FlyWire 3D Viewer",           "flywire.ai",                     "Интерактивный 3D-просмотр нейронов, сегментация EM"],
        ["FlyWire Codex",               "codex.flywire.ai",               "Поиск нейронов по имени / типу / региону, скачать CSV с IDs"],
        ["Codex — таблица нейронов",    "codex.flywire.ai/api/v1/neurons","JSON/CSV с root_id всех 139 255 нейронов и аннотациями"],
        ["bioRxiv preprint (модель LIF)","biorxiv.org 2023.05.02.539144", "Полные методы: параметры, уравнения, код GitHub"],
        ["Код модели (GitHub)",         "github.com/philshiu/Drosophila_brain_model", "Brian2-код оригинальной симуляции Shiu et al."],
        ["Данные коннектома (Edmond)",  "doi:10.17617/3.CZODIW",         "Parquet файлы синапсов и CSV нейронов для локального запуска"],
    ]
    t_fw = Table(fw_data, colWidths=[4*cm, 5.8*cm, 6.6*cm], repeatRows=1)
    t_fw.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  C_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (-1,-1), FONT_REGULAR),
        ("FONTNAME",      (1,1), (1,-1),  "Courier"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, C_GRAY_L]),
        ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(t_fw)
    story.append(spacer(10))

    story.append(Paragraph("Как найти root_id нейрона в FlyWire Codex", S["h2"]))
    story.append(Paragraph(
        "FlyWire Codex (codex.flywire.ai) — это поисковик по коннектому. Нейроны аннотированы "
        "сообществом: у большинства есть cell_type, super_class, region, neurotransmitter.",
        S["body"]))

    methods_fw = [
        ("Поиск по имени/типу",
         "Перейти на codex.flywire.ai → вкладка Cells → ввести имя (например: 'Gr5a', 'MN9', 'G2N-1'). "
         "Система вернёт список нейронов с их root_id. "
         "Скопируйте 18-значный ID (например: 720575940621039145) для использования в симуляторе."),
        ("Скачать CSV со всеми нейронами",
         "На codex.flywire.ai → Download → neurons.csv (~20 МБ). "
         "Содержит: root_id, cell_type, super_class, hemisphere, region, nt_type для всех 139 255 нейронов. "
         "Загрузите в pandas и фильтруйте по нужным типам."),
        ("Через fafbseg Python",
         "pip install fafbseg-py → from fafbseg.flywire import search_annotations → "
         "df = search_annotations('Gr5a') → df.root_id. "
         "Полная документация: fafbseg-py.readthedocs.io"),
        ("Через 3D viewer",
         "На flywire.ai открыть нейрон визуально → правая кнопка → 'Copy ID'. "
         "Или скопировать из адресной строки URL: /...#!{}...&sid=720575940621039145"),
    ]
    for title, text in methods_fw:
        story.append(Paragraph(f"<b>{title}:</b> {text}", S["bullet"]))

    story.append(spacer(8))
    story.append(Paragraph("Версии коннектома (материализации)", S["h2"]))
    story.append(Paragraph(
        "FlyWire периодически выпускает новые «материализации» (версии) коннектома с улучшенной аннотацией. "
        "Важно: root_id может меняться между версиями если нейрон был отредактирован!",
        S["body"]))
    ver_data = [
        ["Версия", "Нейронов", "Использование"],
        ["v630",   "127 400",  "Оригинальная статья Shiu et al. (bioRxiv 2023, Nature 2024) — данные в нашем симуляторе"],
        ["v783",   "138 639",  "Файлы Edmond MPG (doi:10.17617/3.CZODIW) — скачаны в F:/work/code/dro/data/"],
        ["v9xx",   "139 255",  "FlyWire Codex (codex.flywire.ai) — текущая версия, опубликованная в Nature 2024 (FlyWire paper)"],
    ]
    t_ver = Table(ver_data, colWidths=[2*cm, 2.5*cm, 11.9*cm], repeatRows=1)
    t_ver.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  C_BRAND),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (-1,-1), FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, C_GRAY_L]),
        ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(t_ver)
    story.append(spacer(6))
    story.append(info_box(S,
        "Практический совет: файлы в нашем симуляторе (connections.parquet, completeness.csv) соответствуют "
        "версии v783. IDs нейронов из Codex (v9xx) совместимы с v783 для большинства нейронов, "
        "но всегда проверяйте через поиск в /api/neurons/search перед запуском симуляции.",
        C_ACCENT_Y, colors.HexColor("#fefce8")))

    story.append(Paragraph("Что такое bioRxiv 2023.05.02.539144?", S["h2"]))
    story.append(Paragraph(
        "Это препринт статьи Shiu et al., опубликованный на bioRxiv 2 мая 2023 года — "
        "за 1.5 года до выхода в Nature (октябрь 2024). Препринты доступны бесплатно, "
        "статья в Nature — за платный доступ.",
        S["body"]))
    preprint_rows = [
        ["Аспект",          "bioRxiv препринт (2023)",                     "Nature (2024)"],
        ["URL",             "biorxiv.org/content/10.1101/2023.05.02.539144","nature.com/articles/s41586-024-07763-9"],
        ["Доступ",          "Бесплатно (Creative Commons)",                 "Платный (или через институт)"],
        ["Методы",          "Полный раздел Methods (стр. 21-27)",           "Краткие Methods + Extended Data"],
        ["Параметры",       "Все 11 параметров модели с ссылками",          "Суммировано в Extended Data"],
        ["Отличия",         "Предварительная версия, может расходиться",    "Финальная рецензированная версия"],
        ["Код",             "github.com/philshiu/Drosophila_brain_model",   "Тот же (не изменился)"],
    ]
    t_pr = Table(preprint_rows, colWidths=[2.8*cm, 6*cm, 7.6*cm], repeatRows=1)
    t_pr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  C_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("FONTNAME",      (0,1), (-1,-1), FONT_REGULAR),
        ("FONTNAME",      (1,1), (2,-1),  FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, C_GRAY_L]),
        ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    story.append(t_pr)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 6 — ГИПОТЕЗЫ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("6. Гипотезы, которые можно проверить", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "Модель — это инструмент для генерации и проверки гипотез о нейронных цепях. "
        "Ниже — гипотезы из оригинальной статьи, которые можно воспроизвести и расширить в нашем приложении.",
        S["body"]))

    hyp_rows = [
        ["H1: Сахарный путь\nактивирует MN9",
         "Активировать Gr5a GRN (сахарные нейроны)\nпри r_poi = 50–200 Гц",
         "Mean rate MN9 > 0 Гц;\nчем выше r_poi — тем выше MN9",
         "Подтверждена\nв статье"],
        ["H2: Аддитивность\nсахар + вода",
         "Сравнить Rate(sugar), Rate(water),\nRate(sugar+water) при одинаковых r_poi",
         "Rate(sugar+water) > Rate(sugar) и\n> Rate(water) по отдельности",
         "Подтверждена\n(250 общих нейронов)"],
        ["H3: Сегрегация\nсахар vs горький",
         "Активировать Sugar GRN + Bitter GRN\n(Gr66a) в одном эксперименте",
         "Только 2 общих нейрона;\nMN9 подавляется при bitter",
         "Подтверждена\nв статье"],
        ["H4: Механосенсорный\nгруминг",
         "Активировать Johnston's organ\n(анtennal mechanosensory)",
         "Активация 8 нейронов\nгрумингового каскада",
         "Подтверждена\n(оптогенетика)"],
        ["H5: Порог активации\n(v_th sensitivity)",
         "Grid search: v_th от -65 до -30 мВ\npри фиксированном r_poi",
         "Нелинейная зависимость:\nкритический порог ~-45 мВ",
         "Новая гипотеза —\nпроверить!"],
        ["H6: Вес синапса\nи топология",
         "Варьировать w_syn от 0.1 до 1.0 мВ\nпри активации sugar GRN",
         "Фазовый переход: при w_syn>\n0.5 мВ — каскад распространяется",
         "Новая гипотеза —\nпроверить!"],
        ["H7: Нейропептиды\n(Usnea circuit)",
         "Silencing Usnea нейронов при\nактивации sugar GRN",
         "MN9 firing снижается;\n>20% = нейрон необходим",
         "Частично в статье;\nрасширить"],
    ]
    story.append(hyp_table(S, hyp_rows))
    story.append(spacer(10))
    story.append(Paragraph(
        "Гипотезы H5 и H6 — полностью новые, сформулированные на основе возможностей нашей платформы. "
        "Они не содержатся в оригинальной статье и могут составить основу новой публикации.",
        S["note"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 7 — ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("7. Приложение Drosophila Brain Explorer — интерфейс", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph("Три основных раздела", S["h2"]))

    tabs_data = [
        ["Вкладка", "Иконка", "Назначение", "Основные действия"],
        ["Experiment", "Колба", "Запуск симуляций: выбор нейронов, настройка параметров, просмотр результатов",
         "Выбрать нейроны -> Настроить параметры -> Run Simulation -> Смотреть firing rates"],
        ["Hypotheses", "Лампочка", "Менеджер научных гипотез: создание, статус (подтверждена/опровергнута), аннотация для статьи",
         "New hypothesis -> Описать предсказание -> Привязать эксперименты -> Изменить статус"],
        ["Compare", "Весы", "Статистическое сравнение двух экспериментов: Mann-Whitney U, delta firing rates, визуализация",
         "Выбрать A и B -> Run comparison -> Смотреть p-value и delta"],
    ]
    t_tabs = Table(tabs_data, colWidths=[2.5*cm, 1.5*cm, 7*cm, 5.4*cm], repeatRows=1)
    t_tabs.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), C_DARK),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("FONTNAME",   (0,1),(-1,-1), FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_tabs)
    story.append(spacer(10))

    story.append(Paragraph("Панель нейронов (Neurons)", S["h2"]))
    story.append(Paragraph("Каждый нейрон идентифицируется по FlyWire ID — уникальному 18-значному числу. "
        "Три роли нейронов в эксперименте:", S["body"]))
    roles = [
        ("Excite (зелёный)", "Нейрон получает Poisson-входы с частотой r_poi. Это начальный стимул — аналог сенсорного раздражителя."),
        ("Silence (серый)",  "Все синапсы этого нейрона обнуляются — аналог генетического silencing (GtACR1 в экспериментах)."),
        ("Excite-2 (синий)", "То же что Excite, но с частотой r_poi2. Удобно для одновременной активации двух популяций с разными частотами."),
    ]
    for name, desc in roles:
        story.append(Paragraph(
            f"<b>{name}:</b> {desc}", S["bullet"]))

    story.append(spacer(6))
    story.append(Paragraph("Пресеты нейронов (из статьи Nature 2024):", S["h3"]))
    presets_data = [
        ["Пресет", "FlyWire IDs", "Гипотеза"],
        ["Sugar taste (Gr5a)", "720575940621039145, 720575940614307712", "Активация -> MN9 firing -> пробосцис"],
        ["Water taste (Gr64f)", "720575940617946228, 720575940628354985", "Водный путь активирует те же нейроны что сахар?"],
        ["Sugar + Water", "Все 4 нейрона выше", "Rate(combined) > Rate(A) + Rate(B)?"],
        ["Antennal grooming", "720575940616452186", "Johnston's organ -> груминговый каскад"],
    ]
    t_pre = Table(presets_data, colWidths=[3.5*cm, 7*cm, 6*cm], repeatRows=1)
    t_pre.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), C_BRAND),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("FONTNAME",   (0,1),(-1,-1), FONT_REGULAR),
        ("FONTNAME",   (1,1),(1,-1), "Courier"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_pre)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 6 — ПОШАГОВЫЕ СЦЕНАРИИ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("8. Руководство по симуляциям: пошаговые сценарии", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph("Сценарий A: Воспроизведение Figure 1 из статьи Nature", S["h2"]))
    story.append(info_box(S,
        "Цель: проверить, что активация сахарных GRN приводит к firing мотонейронов. "
        "Воспроизводит ключевой эксперимент статьи Shiu et al. 2024.",
        C_ACCENT_G, colors.HexColor("#f0fdf4")))

    steps_a = [
        ("1", "Открыть вкладку Hypotheses", "Нажать + New hypothesis\nTitle: 'Sugar GRN -> MN9 activation'\nPrediction: 'mean_network_rate > 5 Hz'\nArXiv section: Results"),
        ("2", "Открыть вкладку Experiment", "В панели Neurons -> нажать Presets\nВыбрать: Sugar taste (Gr5a)\nЭто добавит IDs: 720575940621039145, 720575940614307712"),
        ("3", "Настроить параметры", "t_run = 1000 мс, n_run = 30\nr_poi = 150 Гц (дефолт)\nv_th = -45 мВ (дефолт)"),
        ("4", "Запустить симуляцию", "Ввести имя: 'Sugar-Gr5a-base'\nВыбрать гипотезу из выпадающего списка\nНажать Run Simulation"),
        ("5", "Проанализировать результат", "Смотреть:\n- Total active neurons (ожидаем >10)\n- Mean network rate (ожидаем >5 Hz)\n- Top neurons: какие ID активны больше всего?"),
        ("6", "Обновить статус гипотезы", "Перейти в Hypotheses\nИзменить статус на Confirmed или Refuted\nДобавить Notes с наблюдаемыми значениями"),
    ]
    for num, title, detail in steps_a:
        inner = Table(
            [[Paragraph(f"<b>Шаг {num}.</b> {title}", S["body"]),
              Paragraph(detail, S["body_small"])]],
            colWidths=[5*cm, 11*cm])
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(0,0), C_BRAND),
            ("TEXTCOLOR",  (0,0),(0,0), colors.white),
            ("VALIGN",     (0,0),(-1,-1), "TOP"),
            ("TOPPADDING", (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING", (0,0),(-1,-1),8),
            ("GRID",       (0,0),(-1,-1),0.4,C_BORDER),
        ]))
        story.append(inner)
        story.append(spacer(3))

    story.append(spacer(10))
    story.append(Paragraph("Сценарий B: Гипотеза аддитивности (сахар + вода)", S["h2"]))
    story.append(info_box(S,
        "Цель: проверить H2. Является ли совместная активация сахарных и водных нейронов "
        "больше суммы по отдельности? Оригинальная статья показала 250 общих нейронов.",
        C_ACCENT_Y, colors.HexColor("#fefce8")))

    steps_b = [
        "1. Запустить 3 эксперимента с одинаковыми параметрами (t_run=1000, n_run=30, r_poi=150):",
        "   - Exp A: neu_exc = [сахарные GRN]",
        "   - Exp B: neu_exc = [водные GRN]",
        "   - Exp C: neu_exc = [сахарные + водные GRN] — пресет 'Sugar + Water'",
        "2. Дождаться завершения всех трёх",
        "3. Перейти в Compare -> выбрать Exp A vs Exp C -> Run comparison",
        "4. Смотреть: network_rate_delta > 0? p_value < 0.05?",
        "5. Повторить: Exp B vs Exp C",
        "6. Вывод: если Rate(C) > Rate(A) И Rate(C) > Rate(B) — аддитивность подтверждена",
    ]
    for s in steps_b:
        story.append(Paragraph(s, S["bullet"] if s.startswith("  ") else S["body"]))

    story.append(spacer(8))
    story.append(Paragraph("Сценарий C: Parameter Space Explorer (новые гипотезы)", S["h2"]))
    story.append(Paragraph(
        "Для изучения H5 (зависимость от v_th) запустите серию экспериментов вручную, "
        "изменяя v_th от -65 до -25 мВ с шагом 5 мВ при фиксированных остальных параметрах. "
        "Записывайте mean_network_rate в таблицу — это и будет «parameter space scan».",
        S["body"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 7 — СПРАВОЧНИК ПАРАМЕТРОВ
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("9. Полный справочник параметров симуляции", S["h1"]))
    story.append(section_rule())

    # ── Точная таблица из Methods (bioRxiv, стр. 21) ─────────────────────────
    story.append(Paragraph("Точные параметры из Methods статьи (Shiu et al., bioRxiv 2023, стр. 21)", S["h2"]))
    story.append(Paragraph(
        "Ниже — дословная таблица из раздела Computational Model статьи. "
        "Все параметры взяты из экспериментальных работ по Drosophila или предыдущих моделей LIF. "
        "Единственный подбираемый параметр — W_syn.",
        S["body"]))

    methods_params = [
        ["Символ",      "Значение",        "Описание",                                         "Источник"],
        ["V_resting",   "-52 мВ",          "Потенциал покоя",                                  "Kakaria & de Bivort, 2017"],
        ["V_reset",     "-52 мВ",          "Потенциал сброса после спайка",                    "Kakaria & de Bivort, 2017"],
        ["V_threshold", "-45 мВ",          "Порог генерации спайка",                           "Kakaria & de Bivort, 2017"],
        ["R_mbr",       "10 МОм",          "Мембранное сопротивление",                         "Kakaria & de Bivort, 2017"],
        ["C_mbr",       "0.002 мкФ",       "Мембранная ёмкость",                               "Kakaria & de Bivort, 2017"],
        ["T_mbr",       "C_mbr × R_mbr\n= 20 мс", "Мембранная постоянная времени (RC-цепь)",  "вычисляется"],
        ["T_refractory","2.2 мс",          "Рефрактерный период",                              "Kakaria & de Bivort, 2017;\nLazar et al., 2021"],
        ["Tau",         "5 мс",            "Постоянная времени синаптического тока",            "Jürgensen et al., 2021"],
        ["T_dly",       "1.8 мс",          "Задержка передачи спайка",                         "Paul et al., 2015"],
        ["W_syn",       "0.275 мВ ★",      "Вес одного синапса (EPSP). ЕДИНСТВЕННЫЙ свободный параметр. "
                                           "Подобран так, чтобы 100 Гц сахарных GRN давали ~80% макс. MN9.",
                                           "Dahanukar et al., 2007;\nInagaki et al., 2012"],
    ]
    t_methods = Table(methods_params, colWidths=[2.4*cm, 2.6*cm, 7.6*cm, 3.8*cm], repeatRows=1)
    t_methods.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),   C_DARK),
        ("TEXTCOLOR",     (0,0),  (-1,0),   colors.white),
        ("FONTNAME",      (0,0),  (-1,0),   FONT_BOLD),
        ("FONTSIZE",      (0,0),  (-1,-1),  8),
        ("FONTNAME",      (0,1),  (-1,-1),  FONT_REGULAR),
        ("FONTNAME",      (0,1),  (1,-1),   "Courier"),
        ("ROWBACKGROUNDS",(0,1),  (-1,-1),  [colors.white, C_GRAY_L]),
        ("GRID",          (0,0),  (-1,-1),  0.4, C_BORDER),
        ("VALIGN",        (0,0),  (-1,-1),  "TOP"),
        ("TOPPADDING",    (0,0),  (-1,-1),  4),
        ("BOTTOMPADDING", (0,0),  (-1,-1),  4),
        ("LEFTPADDING",   (0,0),  (-1,-1),  5),
        # Highlight W_syn as free parameter
        ("BACKGROUND",    (0,10), (-1,10),  colors.HexColor("#fef3c7")),
        ("FONTNAME",      (0,10), (1,10),   FONT_BOLD),
    ]))
    story.append(t_methods)
    story.append(spacer(4))

    story.append(Paragraph(
        "★ W_syn — единственный свободный параметр. Авторы подобрали 0.275 мВ экспериментально: "
        "при этом значении активация сахарных GRN на 100 Гц даёт примерно 80% от максимального "
        "firing rate MN9, что соответствует физиологическим данным (Dahanukar et al., 2007).",
        S["note"]))

    story.append(Paragraph(
        "Протокол симуляции (из статьи): 30 независимых прогонов по 1000 мс каждый. "
        "Все 127 400 нейронов FlyWire (материализация v630) включены в модель. "
        "Активация проводилась унилатерально (правое полушарие) — оно более полно реконструировано.",
        S["body_small"]))

    story.append(Paragraph("Определение нейромедиаторов (из Methods):", S["h3"]))
    story.append(Paragraph(
        "Нейромедиатор предсказан по EM-синапсам (Eckstein et al., 2020). "
        "Если >50% пресинаптических сайтов нейрона — GABA или глутамат → нейрон ингибиторный (вес w < 0). "
        "Иначе — возбуждающий (ацетилхолин, w > 0). "
        "Порог cleft score = 50. Каждый нейрон строго либо возбуждающий, либо ингибиторный.",
        S["body_small"]))
    story.append(spacer(10))

    story.append(Paragraph("Временные параметры", S["h2"]))
    story.append(param_table(S, [
        ["t_run", "1000 мс", "100–10000", "Длительность одного прогона симуляции. Увеличьте до 2000–5000 мс для медленных цепей (груминг, модуляция нейропептидами)."],
        ["n_run", "30", "1–200",   "Число независимых прогонов. Больше = лучше статистика. 30 — баланс точность/скорость. Для публикации используйте ≥50."],
    ]))

    story.append(Paragraph("Параметры мембраны (биофизика нейрона)", S["h2"]))
    story.append(param_table(S, [
        ["v_th",  "-45 мВ", "-65…-20", "Порог генерации спайка. Ключевой параметр возбудимости. Ниже порог -> легче активировать. Стандарт LIF: -40…-50 мВ."],
        ["v_0",   "-52 мВ", "-80…-30", "Потенциал покоя (resting potential). Используйте -65 мВ для более 'тихих' нейронов, -50 мВ для активных."],
        ["v_rst", "-52 мВ", "-80…-30", "Потенциал сброса после спайка. Обычно = v_0. Измените для изучения post-spike dynamics."],
        ["t_mbr", "20 мс",  "1–100",   "Мембранная постоянная времени. Больше = медленнее интеграция, меньше спайков. Пирамидальные нейроны: ~20 мс, интернейроны: ~5–10 мс."],
        ["tau",   "5 мс",   "0.5–50",  "Синаптическая постоянная времени (decay). Маленькие значения = быстрые синапсы (AMPA). Большие = медленные (NMDA, GABA-B)."],
        ["t_rfc", "2.2 мс", "0.5–20",  "Рефрактерный период. Минимальный интервал между спайками. Уменьшите для high-frequency interneurons."],
        ["t_dly", "1.8 мс", "0.1–10",  "Синаптическая задержка (transmission delay). Аксональная проводимость. Увеличьте для длинных связей (cross-hemisphere)."],
    ]))

    story.append(Paragraph("Синаптические параметры (входной сигнал)", S["h2"]))
    story.append(param_table(S, [
        ["w_syn",  "0.275 мВ", "0.01–2.0", "Вес одного синапса (EPSP amplitude). Из статьи: 0.275 мВ на синапс, умноженное на количество синапсов между парой нейронов."],
        ["r_poi",  "150 Гц",   "1–1000",   "Частота Poisson-входа для возбуждаемых нейронов. Отражает интенсивность стимула. В статье: 10–200 Гц для разных тестов."],
        ["r_poi2", "0 Гц",     "0–1000",   "Вторичная частота (для нейронов neu_exc2). Используйте для симуляции двух одновременных стимулов с разной интенсивностью."],
        ["f_poi",  "250",      "10–2000",  "Масштаб Poisson-синапсов. Число входных волокон. Больше = сильнее стимул при той же частоте. Не меняйте без причины."],
    ]))

    story.append(Paragraph("Рекомендуемые пресеты параметров", S["h2"]))
    presets_p = [
        ["Название", "v_th", "w_syn", "r_poi", "n_run", "Когда использовать"],
        ["Default (статья)", "-45", "0.275", "150", "30", "Воспроизведение результатов Shiu et al. 2024"],
        ["Sensitive network", "-50", "0.5",  "100", "30", "Когда нейроны не активируются дефолтом"],
        ["Strong stimulus",   "-45", "0.275","300", "50", "Проверка насыщения: что при очень сильном входе?"],
        ["Weak stimulus",     "-45", "0.1",  "50",  "50", "Нижний порог: минимальный стимул для активации"],
        ["Publication",       "-45", "0.275","150", "100","Финальный эксперимент для публикации (max n_run)"],
    ]
    t_pp = Table(presets_p, colWidths=[3.5*cm, 1.4*cm, 1.4*cm, 1.4*cm, 1.4*cm, 7.8*cm], repeatRows=1)
    t_pp.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("FONTNAME",   (0,1),(-1,-1), FONT_REGULAR),
        ("FONTNAME",   (1,1),(4,-1), "Courier"),
        ("ALIGN",      (1,0),(4,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_pp)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # РАЗДЕЛ 8 — ARXIV
    # ════════════════════════════════════════════════════════════
    story.append(Paragraph("10. Как опубликовать результаты на arXiv", S["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "Платформа Drosophila Brain Explorer спроектирована для научной работы. "
        "Каждый эксперимент сохраняет полный JSON параметров — это обеспечивает воспроизводимость. "
        "Ниже — стратегия превращения работы с платформой в публикацию.",
        S["body"]))

    story.append(Paragraph("Структура статьи (шаблон для arXiv)", S["h2"]))
    arxiv_data = [
        ["Раздел", "Содержание", "Используйте в платформе"],
        ["Abstract", "Кратко: модель, гипотеза, результат, значимость", "—"],
        ["Introduction", "Обзор FlyWire коннектома, LIF модели, задача статьи", "Ссылка на Shiu et al. 2024"],
        ["Methods", "Параметры модели (полная таблица), FlyWire IDs нейронов, n_run, статистика", "JSON из каждого эксперимента"],
        ["Results", "Firing rates по условиям, p-values, графики firing rate", "Экспорт из ResultsViewer + ComparePanel"],
        ["Discussion", "Биологическая интерпретация, ограничения (нейропептиды!), следующие шаги", "Статусы гипотез + notes"],
        ["Data availability", "Коннектом: doi:10.17617/3.CZODIW; Код: github.com/zeniv/drosophila-brain-explorer", "README.md репозитория"],
    ]
    t_arxiv = Table(arxiv_data, colWidths=[2.8*cm, 7*cm, 6.6*cm], repeatRows=1)
    t_arxiv.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), C_DARK),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), FONT_BOLD),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("FONTNAME",   (0,1),(-1,-1), FONT_REGULAR),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_GRAY_L]),
        ("GRID",       (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(t_arxiv)
    story.append(spacer(10))

    story.append(Paragraph("Цитирование", S["h2"]))
    story.append(Paragraph("Обязательно цитировать в любой публикации с использованием платформы:", S["body"]))
    story.append(Paragraph(
        'Shiu P.K. et al. "A Drosophila computational brain model reveals sensorimotor processing." '
        'Nature 634, 210–218 (2024). https://doi.org/10.1038/s41586-024-07763-9',
        S["code"]))
    story.append(Paragraph(
        "Dorkenwald S. et al. (FlyWire Consortium). The full adult fly brain connectome. "
        "bioRxiv (2023). https://doi.org/10.1101/2023.06.27.546246",
        S["code"]))

    story.append(Paragraph("Стратегия повышения цитируемости", S["h2"]))
    cit_tips = [
        ("Онлайн-демо в статье", "Укажите URL платформы (после деплоя на сервер) в разделе Data availability — "
         "читатели смогут воспроизвести результаты за клик, что увеличивает цитирование."),
        ("Software paper (JOSS)", "Платформа может быть отдельной публикацией в Journal of Open Source Software — "
         "это добавит ещё одну статью с независимым цитированием."),
        ("Новые гипотезы", "Гипотезы H5 и H6 (parameter space) не изучены в оригинальной статье — "
         "это novelty для самостоятельной публикации."),
        ("Воспроизводимость", "Полный JSON каждого эксперимента — это reproducibility statement, "
         "высоко ценимый рецензентами Nature Methods, eLife, PLoS Computational Biology."),
        ("Preprint стратегия", "Выложить на bioRxiv до submission в журнал — это ускоряет цитирование "
         "на 6–18 месяцев (время рецензирования)."),
    ]
    for title, text in cit_tips:
        story.append(Paragraph(f"<b>{title}:</b> {text}", S["bullet"]))

    story.append(spacer(12))
    story.append(thin_rule())
    story.append(spacer(6))

    story.append(Paragraph(
        "Drosophila Brain Explorer  |  github.com/zeniv/drosophila-brain-explorer  |  "
        "Основано на: Shiu et al., Nature 2024  |  Данные: doi:10.17617/3.CZODIW",
        S["caption"]))

    doc.build(story)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    out = "F:/work/code/dro/Drosophila_Brain_Explorer_Guide.pdf"
    build_pdf(out)
