"""
Jenerik dışa aktarma (export) modülü — Milestone ERP
Herhangi bir liste verisini xlsx veya pdf olarak üretir.

Kullanım:
    from export_utils import liste_xlsx, liste_pdf
    headers = ['Sipariş No', 'Müşteri', 'Tutar']
    rows = [['SIP-1', 'Anka', '1000'], ['SIP-2', 'Beta', '2000']]
    return liste_xlsx('Siparişler', headers, rows, dosya_adi='siparisler')
    return liste_pdf('Siparişler', headers, rows, dosya_adi='siparisler')
"""
import io
from datetime import date


def _make_response(data_bytes, dosya_adi, content_type, inline=False):
    from flask import make_response
    resp = make_response(data_bytes)
    resp.headers['Content-Type'] = content_type
    # inline=True → tarayıcıda aç (PDF için); inline=False → indir (Excel için)
    yerlesim = 'inline' if inline else 'attachment'
    resp.headers['Content-Disposition'] = f'{yerlesim}; filename="{dosya_adi}"'
    return resp


def liste_xlsx(baslik, headers, rows, dosya_adi='liste', sayisal_sutunlar=None):
    """
    headers: ['Sütun1', 'Sütun2', ...]
    rows: [[deger1, deger2, ...], ...]
    sayisal_sutunlar: sağa yaslanacak/sayı formatı uygulanacak sütun indeksleri (0-tabanlı)
    """
    sayisal_sutunlar = sayisal_sutunlar or []
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise RuntimeError('Excel (.xlsx) çıktısı için "openpyxl" paketi kurulu olmalı. '
                           'Kurulum: pip install openpyxl')
    wb = Workbook()
    ws = wb.active
    ws.title = (baslik or 'Liste')[:31]

    n_col = max(1, len(headers))
    # Başlık satırı
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_col)
    c = ws.cell(row=1, column=1, value=baslik)
    c.font = Font(bold=True, size=14, color='1E3A5F')
    c.alignment = Alignment(horizontal='left')
    # Tarih satırı
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_col)
    t = ws.cell(row=2, column=1, value=f'Oluşturma: {date.today().strftime("%d.%m.%Y")}')
    t.font = Font(size=9, color='888888')

    # Sütun başlıkları
    header_row = 4
    thin = Side(style='thin', color='DDDDDD')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for ci, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=ci, value=h)
        cell.font = Font(bold=True, color='FFFFFF', size=10)
        cell.fill = PatternFill('solid', start_color='1E3A5F')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Veri satırları
    r = header_row + 1
    for row in rows:
        for ci, val in enumerate(row, start=1):
            # Güvenli değer: None → boş, diğer her şey string (openpyxl uyumsuz tipleri önle)
            guvenli = '' if val is None else (val if isinstance(val, (int, float, str)) else str(val))
            cell = ws.cell(row=r, column=ci, value=guvenli)
            cell.border = border
            cell.font = Font(size=10)
            if (ci - 1) in sayisal_sutunlar:
                cell.alignment = Alignment(horizontal='right')
            else:
                cell.alignment = Alignment(horizontal='left')
        # Zebra
        if (r - header_row) % 2 == 0:
            for ci in range(1, n_col + 1):
                ws.cell(row=r, column=ci).fill = PatternFill('solid', start_color='F7F5F0')
        r += 1

    # Sütun genişlikleri (içeriğe göre)
    for ci in range(1, n_col + 1):
        maxlen = len(str(headers[ci - 1])) if ci - 1 < len(headers) else 10
        for row in rows:
            if ci - 1 < len(row):
                maxlen = max(maxlen, len(str(row[ci - 1] if row[ci - 1] is not None else '')))
        ws.column_dimensions[get_column_letter(ci)].width = min(max(maxlen + 3, 10), 50)

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    if not dosya_adi.endswith('.xlsx'):
        dosya_adi += '.xlsx'
    return _make_response(
        bio.getvalue(), dosya_adi,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def _turkce_font_kaydet():
    """Türkçe karakterleri destekleyen fontu kaydeder. Döner: (normal_font, bold_font)."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    # Olası font yolları (Linux/Pardus, Windows)
    normal_yollar = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/local/lib/python3.12/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\arial.ttf',
        'C:\\Windows\\Fonts\\tahoma.ttf',
    ]
    bold_yollar = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        'C:\\Windows\\Fonts\\arialbd.ttf',
        'C:\\Windows\\Fonts\\tahomabd.ttf',
    ]
    try:
        normal = next((p for p in normal_yollar if os.path.exists(p)), None)
        bold = next((p for p in bold_yollar if os.path.exists(p)), None)
        if normal:
            if 'TR' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('TR', normal))
            if bold and 'TR-Bold' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('TR-Bold', bold))
            return 'TR', ('TR-Bold' if bold else 'TR')
    except Exception:
        pass
    return 'Helvetica', 'Helvetica-Bold'


def liste_pdf(baslik, headers, rows, dosya_adi='liste', sayisal_sutunlar=None):
    """PDF tablo üretir (reportlab). Türkçe karakter destekli."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
    except ImportError:
        raise RuntimeError('PDF çıktısı için "reportlab" paketi kurulu olmalı. '
                           'Kurulum: pip install reportlab')

    font_normal, font_bold = _turkce_font_kaydet()
    sayisal_sutunlar = sayisal_sutunlar or []
    bio = io.BytesIO()
    # Çok sütun varsa yatay sayfa
    yatay = len(headers) > 5
    sayfa = landscape(A4) if yatay else A4
    doc = SimpleDocTemplate(bio, pagesize=sayfa,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            leftMargin=12 * mm, rightMargin=12 * mm)
    styles = getSampleStyleSheet()
    baslik_stil = ParagraphStyle('Baslik', parent=styles['Title'], fontSize=15, fontName=font_bold,
                                 textColor=colors.HexColor('#1E3A5F'), alignment=TA_LEFT, spaceAfter=4)
    tarih_stil = ParagraphStyle('Tarih', parent=styles['Normal'], fontSize=8, fontName=font_normal,
                                textColor=colors.HexColor('#888888'), spaceAfter=10)

    elemanlar = [
        Paragraph(baslik or 'Liste', baslik_stil),
        Paragraph(f'Oluşturma: {date.today().strftime("%d.%m.%Y")}', tarih_stil),
        Spacer(1, 4),
    ]

    # Hücre içeriklerini Paragraph yap (uzun metin kayması için)
    hucre_stil = ParagraphStyle('Hucre', parent=styles['Normal'], fontSize=8, leading=10, fontName=font_normal)
    hucre_sag = ParagraphStyle('HucreSag', parent=hucre_stil, alignment=2)  # sağ
    head_stil = ParagraphStyle('Head', parent=styles['Normal'], fontSize=8, fontName=font_bold,
                               textColor=colors.white, leading=10)

    data = [[Paragraph(str(h), head_stil) for h in headers]]
    for row in rows:
        satir = []
        for ci, val in enumerate(row):
            stil = hucre_sag if ci in sayisal_sutunlar else hucre_stil
            satir.append(Paragraph(str(val if val is not None else ''), stil))
        data.append(satir)

    tablo = Table(data, repeatRows=1)
    tablo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F5F0')]),
    ]))
    elemanlar.append(tablo)
    doc.build(elemanlar)
    bio.seek(0)
    if not dosya_adi.endswith('.pdf'):
        dosya_adi += '.pdf'
    return _make_response(bio.getvalue(), dosya_adi, 'application/pdf', inline=True)
