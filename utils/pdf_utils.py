import os
from datetime import datetime
try:
    from reportlab.lib.pagesizes import A6, A4, landscape
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

def format_rupiah(amount):
    return f"Rp {int(amount):,.0f}".replace(",", ".")

def cetak_tiket_pdf(tiket_data: dict, output_path: str) -> bool:
    if not HAS_REPORTLAB:
        return False
    doc = SimpleDocTemplate(
        output_path,
        pagesize=(80*mm, 160*mm),
        leftMargin=5*mm, rightMargin=5*mm,
        topMargin=5*mm, bottomMargin=5*mm,
        title=f"Tiket FerryBook {tiket_data.get('nomor_tiket','')}".strip(),
        author="FerryBook", subject="Tiket Penyeberangan"
    )
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('title', fontSize=12, fontName='Helvetica-Bold',
                                  alignment=TA_CENTER, textColor=colors.HexColor('#003366'))
    subtitle_style = ParagraphStyle('sub', fontSize=8, fontName='Helvetica',
                                     alignment=TA_CENTER, textColor=colors.grey)
    normal = ParagraphStyle('norm', fontSize=8, fontName='Helvetica',
                             alignment=TA_LEFT, leading=12)
    bold_c = ParagraphStyle('boldc', fontSize=9, fontName='Helvetica-Bold',
                              alignment=TA_CENTER, textColor=colors.HexColor('#003366'))
    small_c = ParagraphStyle('smallc', fontSize=7, fontName='Helvetica',
                               alignment=TA_CENTER, textColor=colors.grey)

    story.append(Paragraph("FERRYBOOK", title_style))
    story.append(Paragraph("Sistem Reservasi Tiket Kapal Feri", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366')))
    story.append(Spacer(1, 3*mm))

    data = [
        ["No. Tiket", tiket_data.get('nomor_tiket','')],
        ["Rute", f"{tiket_data.get('asal','')} → {tiket_data.get('tujuan','')}"],
        ["Kapal", tiket_data.get('nama_kapal','')],
        ["Tanggal", tiket_data.get('tanggal','')],
        ["Berangkat", tiket_data.get('jam_berangkat','')],
        ["Nama", tiket_data.get('nama_penumpang','')],
        ["ID", tiket_data.get('no_identitas','')],
    ]
    if tiket_data.get('tipe_tiket') == 'kendaraan':
        data.append(["Kendaraan", tiket_data.get('jenis_kendaraan','')])
        data.append(["No. Polisi", tiket_data.get('no_polisi','')])
    else:
        data.append(["Penumpang", f"{tiket_data.get('jumlah_penumpang',1)} orang"])

    t = Table(data, colWidths=[25*mm, 45*mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0),(-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0),(-1,-1), 8),
        ('FONTNAME', (0,0),(0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0),(0,-1), colors.HexColor('#003366')),
        ('ROWBACKGROUNDS', (0,0),(-1,-1), [colors.HexColor('#F0F4FF'), colors.white]),
        ('GRID', (0,0),(-1,-1), 0.25, colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366')))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"TOTAL: {format_rupiah(tiket_data.get('total_harga',0))}", bold_c))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M')}", small_c))
    story.append(Paragraph(f"Petugas: {tiket_data.get('nama_petugas','')}", small_c))
    story.append(Spacer(1, 2*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, lineCap='round', dash=[2,2]))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("Tiket ini adalah bukti pembayaran yang sah.", small_c))
    story.append(Paragraph("Harap simpan hingga tiba di tujuan.", small_c))

    doc.build(story)
    return True

def cetak_laporan_manifes_pdf(tikets: list, judul: str, output_path: str) -> bool:
    if not HAS_REPORTLAB:
        return False
    doc_title = f"Laporan Manifes FerryBook - {judul}".strip()
    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4),
                             leftMargin=12*mm, rightMargin=12*mm,
                             topMargin=14*mm, bottomMargin=14*mm,
                             title=doc_title, author="FerryBook",
                             subject="Laporan Manifes Penumpang")
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('h1', fontSize=16, leading=20, spaceAfter=6,
                                  fontName='Helvetica-Bold',
                                  alignment=TA_CENTER, textColor=colors.HexColor('#003366'))
    sub_style = ParagraphStyle('sub', fontSize=11, leading=14, fontName='Helvetica',
                               alignment=TA_CENTER, textColor=colors.grey)
    story.append(Paragraph("FERRYBOOK - LAPORAN MANIFES", title_style))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(judul, sub_style))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#003366')))
    story.append(Spacer(1, 3*mm))

    header = ["No. Tiket", "Nama Penumpang", "ID", "Rute", "Kapal", "Tanggal", "Jam", "Tipe", "Jml", "Total"]
    rows = [header]
    total_pendapatan = 0
    for i, t in enumerate(tikets, 1):
        rows.append([
            t.get('nomor_tiket',''),
            t.get('nama_penumpang',''),
            t.get('no_identitas',''),
            f"{t.get('asal','')}→{t.get('tujuan','')}",
            t.get('nama_kapal',''),
            t.get('tanggal',''),
            t.get('jam_berangkat',''),
            t.get('tipe_tiket','').capitalize(),
            str(t.get('jumlah_penumpang',1)),
            format_rupiah(t.get('total_harga',0)),
        ])
        total_pendapatan += t.get('total_harga', 0)

    col_widths = [42*mm, 40*mm, 26*mm, 34*mm, 34*mm, 22*mm, 14*mm, 18*mm, 11*mm, 26*mm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0),(-1,0), colors.white),
        ('FONTNAME', (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0),(-1,-1), 7),
        ('FONTNAME', (0,1),(-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1),(-1,-1), [colors.HexColor('#EEF2FF'), colors.white]),
        ('GRID', (0,0),(-1,-1), 0.25, colors.HexColor('#AAAAAA')),
        ('TOPPADDING', (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
        ('ALIGN', (0,0),(-1,-1), 'LEFT'),
        ('ALIGN', (-1,0),(-1,-1), 'RIGHT'),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366')))
    story.append(Paragraph(
        f"Total Tiket: {len(tikets)}  |  Total Pendapatan: {format_rupiah(total_pendapatan)}",
        ParagraphStyle('footer', fontSize=10, fontName='Helvetica-Bold',
                       alignment=TA_RIGHT, textColor=colors.HexColor('#003366'))
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        ParagraphStyle('ts', fontSize=8, fontName='Helvetica', alignment=TA_RIGHT, textColor=colors.grey)
    ))
    doc.build(story)
    return True
