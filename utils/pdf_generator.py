import io
import os
import datetime
import qrcode
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from config import Config

_ASSET_CACHE = {}

def _get_asset_path(filename):
    """Find asset path in static/assets or fallback to BASE_DIR with in-memory caching."""
    if filename in _ASSET_CACHE:
        return _ASSET_CACHE[filename]
    base_dir = Config.BASE_DIR
    p1 = os.path.join(base_dir, "static", "assets", filename)
    if os.path.exists(p1):
        _ASSET_CACHE[filename] = p1
        return p1
    p2 = os.path.join(base_dir, "public", "templates", filename)
    if os.path.exists(p2):
        _ASSET_CACHE[filename] = p2
        return p2
    p3 = os.path.join(base_dir, filename)
    if os.path.exists(p3):
        _ASSET_CACHE[filename] = p3
        return p3
    _ASSET_CACHE[filename] = None
    return None

def draw_offer_letter_canvas(canvas_obj, doc):
    """Vector canvas background for Offer Letter (A4 Portrait: 595.27 x 841.89 pt)."""
    canvas_obj.saveState()
    w, h = doc.pagesize

    # Outer Navy Blue Border
    canvas_obj.setStrokeColor(colors.HexColor('#0B3D91'))
    canvas_obj.setLineWidth(3)
    canvas_obj.rect(18, 18, w - 36, h - 36)

    # Inner Gold Accent Line
    canvas_obj.setStrokeColor(colors.HexColor('#D97706'))
    canvas_obj.setLineWidth(1)
    canvas_obj.rect(22, 22, w - 44, h - 44)

    # Top Header Blue Bar
    canvas_obj.setFillColor(colors.HexColor('#0B3D91'))
    canvas_obj.rect(22, h - 38, w - 44, 16, fill=1, stroke=0)

    # Header Bar Text
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawString(32, h - 33, "WEBINTERN PLATFORM — OFFICIAL INTERNSHIP OFFER")
    canvas_obj.drawRightString(w - 32, h - 33, "VERIFIED VIRTUAL PROGRAM")

    # Bottom Footer Bar
    canvas_obj.setFillColor(colors.HexColor('#082B66'))
    canvas_obj.rect(22, 22, w - 44, 24, fill=1, stroke=0)

    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawString(32, 29, "www.webintern.in | Support: webinternsupport@gmail.com")
    canvas_obj.drawRightString(w - 32, 29, "Ministry of MSME Recognized Framework")

    canvas_obj.restoreState()

def draw_certificate_canvas(canvas_obj, doc, verify_url=None, cert_id=None, date_str=None):
    """Vector canvas background for Certificate (A4 Landscape: 841.89 x 595.27 pt)."""
    canvas_obj.saveState()
    w, h = doc.pagesize

    # Outer Dark Navy Border
    canvas_obj.setStrokeColor(colors.HexColor('#0B3D91'))
    canvas_obj.setLineWidth(5)
    canvas_obj.rect(16, 16, w - 32, h - 32)

    # Inner Gold Border
    canvas_obj.setStrokeColor(colors.HexColor('#D97706'))
    canvas_obj.setLineWidth(1.5)
    canvas_obj.rect(22, 22, w - 44, h - 44)

    # Corner Decorative Squares
    corner_size = 14
    canvas_obj.setFillColor(colors.HexColor('#0B3D91'))
    canvas_obj.rect(22, h - 22 - corner_size, corner_size, corner_size, fill=1, stroke=0)
    canvas_obj.rect(w - 22 - corner_size, h - 22 - corner_size, corner_size, corner_size, fill=1, stroke=0)
    canvas_obj.rect(22, 22, corner_size, corner_size, fill=1, stroke=0)
    canvas_obj.rect(w - 22 - corner_size, 22, corner_size, corner_size, fill=1, stroke=0)

    # Bottom Certificate ID bar text
    canvas_obj.setFillColor(colors.HexColor('#4B5563'))
    canvas_obj.setFont('Helvetica-Bold', 8)
    if cert_id:
        canvas_obj.drawString(35, 30, f"Certificate ID: {cert_id}")
    if date_str:
        canvas_obj.drawRightString(w - 35, 30, f"Issue Date: {date_str}")

    canvas_obj.restoreState()

def generate_offer_letter_pdf(
    student_name,
    internship_title,
    date_str,
    save_id=None,
    company_name="WEBINTERN",
    start_date=None,
    end_date=None,
    duration="4 Weeks",
    location="Virtual / Remote",
    skills_tools=None,
    tasks_projects=None,
    offer_id=None,
    college_name=None,
    department=None,
    mentor_name=None
):
    """Generate Offer Letter PDF (A4 Portrait) using ReportLab flowables with zero text collision."""
    buffer = io.BytesIO()
    page_w, page_h = 595.27, 841.89  # Portrait A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_w, page_h),
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_title = ParagraphStyle(
        'OfferTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0B3D91'),
        alignment=0,
        spaceAfter=4
    )

    style_meta = ParagraphStyle(
        'OfferMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4B5563'),
        alignment=2
    )

    style_salutation = ParagraphStyle(
        'OfferSalutation',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#082B66'),
        spaceBefore=10,
        spaceAfter=8
    )

    style_body = ParagraphStyle(
        'OfferBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )

    style_table_label = ParagraphStyle(
        'TableLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0B3D91')
    )

    style_table_val = ParagraphStyle(
        'TableVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#111827')
    )

    style_bullet = ParagraphStyle(
        'OfferBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=12,
        spaceAfter=4
    )

    story = []

    eff_offer_id = offer_id or f"WI-OFFER-2026-{(save_id[:6] if save_id else '1001').upper()}"
    eff_start = start_date or date_str
    eff_end = end_date or "4 Weeks from Start Date"
    eff_college = college_name or "Recognized College / University"
    eff_dept = department or "Engineering / Science / Management"
    eff_mentor = mentor_name or "Dr. A. K. Sharma (Technical Director)"

    # Header Row with Logos
    logo_path = _get_asset_path("logo.png")
    msme_path = _get_asset_path("msme-logo.png")

    logo_img = Image(logo_path, width=80, height=80) if logo_path else Paragraph("<b>WEBINTERN</b>", style_title)



    msme_img = Image(msme_path, width=130, height=45) if msme_path else Paragraph("<b>MSME Govt of India</b>", style_meta)

    header_table = Table([[logo_img, msme_img]], colWidths=[300, 223])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Divider line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0B3D91'), spaceAfter=12))

    # Title & Meta Table
    title_p = Paragraph("OFFER OF VIRTUAL INTERNSHIP", style_title)
    meta_p = Paragraph(f"<b>Ref No:</b> {eff_offer_id}<br/><b>Date:</b> {date_str}", style_meta)

    title_table = Table([[title_p, meta_p]], colWidths=[320, 203])
    title_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(title_table)
    story.append(Spacer(1, 10))

    # Recipient Block
    story.append(Paragraph(f"To,<br/><b>{student_name}</b>", style_salutation))
    story.append(Paragraph(f"Institution: <b>{eff_college}</b><br/>Department / Specialization: <b>{eff_dept}</b>", ParagraphStyle('SubInfo', parent=styles['Normal'], fontSize=9.5, textColor=colors.HexColor('#4B5563'), spaceAfter=10)))

    # Main Body Text - Section 1: Offer Announcement
    body_text_1 = f"""
    We are pleased to extend this formal offer of a Virtual Internship to you for the <b>{internship_title}</b> program at <b>{company_name}</b>. Based on your application credentials and academic background at <b>{eff_college}</b>, we are confident that your participation in our 2026 cohort will foster significant technical growth and practical development experience.
    """
    story.append(Paragraph(body_text_1.strip(), style_body))

    # Section 2: Program Schedule & Directives (Paragraph prose instead of grid table)
    body_text_2 = f"""
    Your internship is scheduled to commence on <b>{eff_start}</b> and will conclude on <b>{eff_end}</b>, covering a total program duration of <b>{duration}</b> in a <b>{location}</b> format. Throughout this period, you will be assigned to the <b>{eff_dept}</b> track under the guidance and technical supervision of <b>{eff_mentor}</b>.
    """
    story.append(Paragraph(body_text_2.strip(), style_body))
    story.append(Spacer(1, 4))

    # Section 3: Scope of Work & Responsibilities
    story.append(Paragraph("<b>Scope of Work & Technical Deliverables:</b>", ParagraphStyle('SecHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0B3D91'), spaceAfter=6)))
    resp_bullets = [
        f"Complete weekly practical project assignments and modules in {internship_title}.",
        "Submit required technical documentations, architecture diagrams, and source code deliverables prior to evaluation deadlines.",
        "Engage in technical assessment reviews and implement feedback provided by assigned industry mentors.",
        "Maintain academic integrity, confidentiality, and professional code standards in all submitted project work."
    ]
    for b in resp_bullets:
        story.append(Paragraph(f"• {b}", style_bullet))

    story.append(Spacer(1, 8))

    # Section 4: Terms & Certification Eligibility
    story.append(Paragraph("<b>Terms & Certification Eligibility:</b>", ParagraphStyle('SecHead2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0B3D91'), spaceAfter=4)))
    terms_text = f"""
    This virtual internship is an intensive skill-enhancement framework. Upon successful completion and evaluation of all required weekly deliverables and verification, <b>{company_name}</b> will award you an official, authenticated <b>Internship Completion Certificate</b> equipped with a unique Certificate ID and QR code verification link. You are expected to maintain strict confidentiality regarding all proprietary project resources and materials provided during the internship.
    """
    story.append(Paragraph(terms_text.strip(), style_body))

    story.append(Spacer(1, 14))

    # Signature & Verification Badge Block
    badge_path = _get_asset_path("verified-seal.png")
    sig_path = _get_asset_path("signature.png")
    sig_img = Image(sig_path, width=145, height=55) if sig_path else Paragraph("<i>Authorized Signature</i>", styles['Normal'])

    sig_text = Paragraph("""
    <b>Authorized Representative</b><br/>
    <b>Founding Board / Authorized Signatory</b><br/>
    WEBINTERN Virtual Learning Platform
    """, style_body)

    sig_box = Table([[sig_img], [sig_text]], colWidths=[240])
    sig_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    badge_img = Image(badge_path, width=82, height=82) if badge_path else Paragraph("<b>VERIFIED</b>", style_table_label)
    badge_label = Paragraph("<font color='#0B3D91'><b>VERIFIED INTERNSHIP</b></font><br/><font size=7.5 color='#4B5563'>Official Authenticated Seal</font>", ParagraphStyle('OfferBadgeSub', parent=styles['Normal'], alignment=1, leading=10, spaceBefore=3))
    
    badge_box = Table([[badge_img], [badge_label]], colWidths=[160])
    badge_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    footer_table = Table([[sig_box, badge_box]], colWidths=[350, 173])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(footer_table)

    doc.build(story, onFirstPage=draw_offer_letter_canvas, onLaterPages=draw_offer_letter_canvas)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    if save_id:
        try:
            os.makedirs(Config.GENERATED_OFFERS_DIR, exist_ok=True)
            out_file = os.path.join(Config.GENERATED_OFFERS_DIR, f"offer_{save_id}.pdf")
            with open(out_file, 'wb') as f:
                f.write(pdf_bytes)
        except Exception as e:
            print(f"Warning: Failed to save offer PDF: {e}")

    return pdf_bytes

def generate_certificate_pdf(
    student_name,
    internship_title,
    date_str,
    cert_id,
    is_verified=True,
    college_name=None,
    department=None,
    guide_name=None,
    project_name=None,
    duration="4 Weeks",
    start_date=None,
    end_date=None,
    company_name="WEBINTERN",
    verification_url=None
):
    """Generate Certificate PDF (A4 Landscape) using ReportLab flowables with zero text collision."""
    buffer = io.BytesIO()
    page_w, page_h = 841.89, 595.27  # Landscape A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_w, page_h),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Landscape Styles
    style_cert_title = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0B3D91'),
        alignment=1,
        spaceAfter=4
    )

    style_subtitle = ParagraphStyle(
        'CertSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#6B7280'),
        alignment=1,
        spaceAfter=10
    )

    style_name = ParagraphStyle(
        'CertName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor('#082B66'),
        alignment=1,
        spaceAfter=10
    )

    style_clause = ParagraphStyle(
        'CertClause',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1F2937'),
        alignment=1,
        spaceAfter=14
    )

    style_table_lbl = ParagraphStyle(
        'CTableLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0B3D91')
    )

    style_table_txt = ParagraphStyle(
        'CTableTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#111827')
    )

    story = []

    eff_college = college_name or "Recognized College / University"
    eff_dept = department or "Engineering / Science / Management"
    eff_guide = guide_name or "Dr. A. K. Sharma (Technical Director)"
    eff_project = project_name or f"{internship_title} Capstone Project"
    eff_start = start_date or date_str
    eff_end = end_date or date_str
    eff_url = verification_url or f"https://webintern.in/verify/{cert_id}"

    # Header Row (Logos)
    logo_path = _get_asset_path("logo.png")
    msme_path = _get_asset_path("msme-logo.png")

    logo_img = Image(logo_path, width=85, height=85) if logo_path else Paragraph("<b>WEBINTERN</b>", style_cert_title)


    msme_img = Image(msme_path, width=130, height=45) if msme_path else Paragraph("<b>MSME Govt of India</b>", style_subtitle)


    header_table = Table([[logo_img, msme_img]], colWidths=[400, 370])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Certificate Main Headers
    story.append(Paragraph("INTERNSHIP COMPLETION CERTIFICATE", style_cert_title))
    story.append(Paragraph("THIS IS TO CERTIFY THAT", style_subtitle))

    # Candidate Name (Central Visual Focal Element)
    story.append(Paragraph(student_name.upper(), style_name))

    # Decorative Line Under Name
    story.append(HRFlowable(width="60%", thickness=1.5, color=colors.HexColor('#D97706'), spaceAfter=12))

    # Certification Statement Clause (Paragraph Prose 1)
    clause_text_1 = f"""
    student of <b>{eff_college}</b> (Department of <b>{eff_dept}</b>), has successfully completed a <b>{duration}</b> Virtual Internship in <b>{internship_title}</b> with <b>{company_name}</b> from <b>{eff_start}</b> to <b>{eff_end}</b>.
    """
    story.append(Paragraph(clause_text_1.strip(), style_clause))
    story.append(Spacer(1, 4))

    # Capstone & Performance Proclamation (Paragraph Prose 2 - replacing grid table)
    clause_text_2 = f"""
    During this tenure, the candidate demonstrated exceptional technical proficiency, problem-solving aptitude, and professional dedication in completing the <b>{eff_project}</b> and fulfilling all required module assessments under the guidance of <b>{eff_guide}</b>.
    """
    style_clause_2 = ParagraphStyle('CertClause2', parent=style_clause, fontSize=10, leading=15, textColor=colors.HexColor('#374151'), spaceAfter=14)
    story.append(Paragraph(clause_text_2.strip(), style_clause_2))
    story.append(Spacer(1, 10))

    # Bottom Footer Column Layout (Gold Badge + Signature + QR Code)
    badge_path = _get_asset_path("verified-seal.png")
    sig_path = _get_asset_path("signature.png")

    badge_img = Image(badge_path, width=82, height=82) if badge_path else Paragraph("<b>VERIFIED</b>", style_subtitle)
    badge_label = Paragraph("<font color='#0B3D91'><b>VERIFIED INTERNSHIP</b></font><br/><font size=7.5 color='#4B5563'>Official Authenticated Seal</font>", ParagraphStyle('CertBadgeSub', parent=styles['Normal'], alignment=1, leading=10, spaceBefore=3))
    badge_box = Table([[badge_img], [badge_label]], colWidths=[150])
    badge_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    sig_img = Image(sig_path, width=145, height=55) if sig_path else Paragraph("<i>Signature</i>", styles['Normal'])
    sig_block = Table([[sig_img], [Paragraph("<b>Authorized Representative</b><br/>Founding Board, WEBINTERN", style_table_txt)]], colWidths=[200])
    sig_block.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

    # QR Code Generation
    qr_cell = None
    try:
        qr = qrcode.QRCode(box_size=3, border=1)
        qr.add_data(eff_url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="#0B3D91", back_color="white")
        img_buffer = io.BytesIO()
        img_qr.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_cell = Image(img_buffer, width=55, height=55)
    except Exception as e:
        print(f"[QR Gen Error]: {e}")
        qr_cell = Paragraph("<b>Scan QR</b>", style_subtitle)

    qr_block = Table([[qr_cell], [Paragraph("<font size=7 color='#4B5563'>Scan to Verify Certificate</font>", style_table_txt)]], colWidths=[150])
    qr_block.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

    footer_table = Table([[badge_box, sig_block, qr_block]], colWidths=[170, 430, 170])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    story.append(footer_table)

    def _draw_canvas(c, d):
        draw_certificate_canvas(c, d, verify_url=eff_url, cert_id=cert_id, date_str=date_str)

    doc.build(story, onFirstPage=_draw_canvas, onLaterPages=_draw_canvas)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    if cert_id:
        try:
            os.makedirs(Config.GENERATED_CERTIFICATES_DIR, exist_ok=True)
            clean_cert_id = str(cert_id).replace('/', '_')
            out_file = os.path.join(Config.GENERATED_CERTIFICATES_DIR, f"certificate_{clean_cert_id}.pdf")
            with open(out_file, 'wb') as f:
                f.write(pdf_bytes)
        except Exception as e:
            print(f"Warning: Failed to save certificate PDF: {e}")

    return pdf_bytes
