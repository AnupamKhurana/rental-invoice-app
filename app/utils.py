"""Utility functions for the rental invoicing application.

Includes PDF generation with Indian accounting compliance.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
import re
from config import Config
from app import db


def validate_pan(pan):
    """Validate PAN format."""
    if not pan:
        return False
    pattern = Config.PAN_PATTERN
    return bool(re.match(pattern, pan.upper()))


def validate_gstin(gstin):
    """Validate GSTIN format."""
    if not gstin:
        return True  # Optional field
    pattern = Config.GSTIN_PATTERN
    return bool(re.match(pattern, gstin.upper()))


def validate_aadhaar(aadhaar):
    """Validate Aadhaar format."""
    if not aadhaar:
        return True  # Optional field
    return bool(re.match(r'^\d{12}$', aadhaar))


def format_currency(amount, symbol='₹'):
    """Format amount as Indian currency."""
    if amount is None:
        return f"{symbol} 0.00"
    return f"{symbol} {amount:,.2f}"


def format_date_indian(date_obj):
    """Format date in Indian style (DD-MM-YYYY)."""
    if date_obj:
        return date_obj.strftime('%d-%m-%Y')
    return ''


def generate_invoice_pdf(invoice, landlord):
    """Generate PDF invoice following Indian accounting standards.
    
    Args:
        invoice: Invoice object
        landlord: Landlord object (owner)
        
    Returns:
        Path to generated PDF file
    """
    
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{invoice.invoice_number}_{timestamp}.pdf"
    filepath = os.path.join(Config.INVOICE_UPLOAD_FOLDER, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom font-based styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#000000'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#000000'),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333'),
        leftIndent=2
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#000000'),
        leftIndent=2
    )
    
    small_text_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.HexColor('#666666'),
        spaceAfter=4
    )
    
    content = []
    
    # ========== HEADER SECTION ==========
    # Title
    content.append(Paragraph("RENTAL INVOICE", title_style))
    content.append(Spacer(1, 6))
    
    # Invoice number and date - right aligned
    invoice_header = [
        ["Invoice No:", invoice.invoice_number],
        ["Invoice Date:", format_date_indian(invoice.invoice_date)],
        ["Due Date:", format_date_indian(invoice.due_date)],
        ["Billing Period:", f"{invoice.billing_month}/{invoice.billing_year}"],
    ]
    
    invoice_header_table = Table(invoice_header, colWidths=[4*cm, 6*cm])
    invoice_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    content.append(invoice_header_table)
    content.append(Spacer(1, 12))
    
    # ========== PARTIES SECTION ==========
    parties_data = [
        [
            Paragraph("FROM (Landlord):", label_style),
            Paragraph("TO (Tenant):", label_style)
        ],
        [
            Paragraph(landlord.name, value_style),
            Paragraph(invoice.lease.tenant.name, value_style)
        ],
        [
            Paragraph(landlord.address.replace('\n', '<br/>&nbsp;'), value_style),
            Paragraph(invoice.lease.tenant.address.replace('\n', '<br/>&nbsp;'), value_style)
        ],
        [
            Paragraph(f"PAN: {landlord.pan}", small_text_style),
            Paragraph(f"PAN: {invoice.lease.tenant.pan}", small_text_style)
        ],
        [
            Paragraph(f"GSTIN: {landlord.gstin or 'Not Registered'}", small_text_style),
            Paragraph(f"GSTIN: {invoice.lease.tenant.gstin or 'Not Registered'}", small_text_style)
        ],
        [
            Paragraph(f"Phone: {landlord.phone}", small_text_style),
            Paragraph(f"Phone: {invoice.lease.tenant.phone}", small_text_style)
        ],
    ]
    
    parties_table = Table(parties_data, colWidths=[7*cm, 7*cm])
    parties_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(parties_table)
    content.append(Spacer(1, 16))
    
    # ========== PROPERTY SECTION ==========
    property_info = invoice.lease.property
    property_data = [
        [Paragraph("PROPERTY DETAILS:", header_style)],
        [f"Property Name: {property_info.property_name}"],
        [f"Property Address: {property_info.get_full_address()}"],
        [f"Property Type: {property_info.property_type.title()}"],
        [f"Lease Agreement: {invoice.lease.agreement_number}"],
        [f"Lease Period: {format_date_indian(invoice.lease.start_date)} to {format_date_indian(invoice.lease.end_date)}"],
    ]
    
    property_table = Table(property_data, colWidths=[14*cm])
    property_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(property_table)
    content.append(Spacer(1, 16))
    
    # ========== CHARGES TABLE ==========
    charges_data = [
        ["S.No.", "Description", "Amount (₹)"],
        [1, "Basic Rent", format_currency(invoice.basic_rent)],
        [2, "Maintenance Charges", format_currency(invoice.maintenance_charges)],
        [3, "Parking Charges", format_currency(invoice.parking_charges)],
        [4, "Electricity Charges", format_currency(invoice.electricity_charges)],
        [5, "Water Charges", format_currency(invoice.water_charges)],
        [6, "Other Charges", format_currency(invoice.other_charges)],
    ]
    
    # Add GST if applicable
    if invoice.gst_amount > 0:
        gst_rate = invoice.lease.gst_rate
        charges_data.append([7, f"GST ({gst_rate}%)", format_currency(invoice.gst_amount)])
    
    charges_data.append(["", "SUBTOTAL", format_currency(invoice.subtotal)])
    
    # Add TDS if applicable
    if invoice.tds_amount > 0:
        tds_rate = invoice.lease.tds_rate
        charges_data.append(["", f"Less: TDS ({tds_rate}%)", f"- {format_currency(invoice.tds_amount)}"])
        charges_data.append(["", "NET PAYABLE", format_currency(invoice.amount_after_tds)])
    else:
        charges_data.append(["", "TOTAL AMOUNT", format_currency(invoice.total_amount)])
    
    charges_table = Table(charges_data, colWidths=[0.8*cm, 9*cm, 3.7*cm])
    charges_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUND', (0, 1), (-1, -2), colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#000000')),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#FFFFFF')),
        ('BACKGROUND', (2, -1), (2, -1), colors.HexColor('#000000')),
        ('TEXTCOLOR', (2, -1), (2, -1), colors.HexColor('#FFFFFF')),
        ('FONTSIZE', (1, -1), (2, -1), 10),
    ]))
    content.append(charges_table)
    content.append(Spacer(1, 20))
    
    # ========== PAYMENT DETAILS ==========
    payment_data = [
        ["Payment Status:", invoice.payment_status.upper()],
        ["Payment Mode:", invoice.payment_mode if invoice.payment_mode else "Not Paid"],
    ]
    if invoice.payment_date:
        payment_data.append(["Payment Date:", format_date_indian(invoice.payment_date)])
    
    payment_table = Table(payment_data, colWidths=[5*cm, 8*cm])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(payment_table)
    content.append(Spacer(1, 24))
    
    # ========== BANK DETAILS ==========
    # Note: Bank details can be added to Landlord model in future
    # For now, showing placeholder
    bank_data = [
        ["PAYMENT INFORMATION:"],
        ["Please make payments to the landlord's registered bank account."],
        ["Contact the landlord for bank account details."],
    ]
    
    bank_table = Table(bank_data, colWidths=[14*cm])
    bank_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(bank_table)
    content.append(Spacer(1, 24))
    
    # ========== COMPLIANCE NOTES ==========
    notes = [
        "• This invoice is generated in compliance with Indian accounting standards.",
        "• TDS deduction as per Section 194-IB of Income Tax Act applies where applicable.",
        "• GST charged as per applicable GST laws for rental properties.",
        "• Payment should be made within the due date to avoid late fees.",
        "• For any queries, please contact the landlord.",
        "• This is a computer-generated invoice and does not require a signature.",
    ]
    
    for note in notes:
        content.append(Paragraph(note, small_text_style))
    
    content.append(Spacer(1, 12))
    
    # ========== FOOTER ==========
    footer_text = f"Page {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    content.append(Paragraph(footer_text, small_text_style))
    
    # Build PDF
    doc.build(content)
    
    # Update invoice record
    invoice.pdf_filename = filename
    db.session.commit()
    
    return filepath


def calculate_tds(lease, rent_amount):
    """Calculate TDS as per Section 194-IB.
    
    TDS is applicable when:
    - Payer is individual/HUF
    - Rent exceeds ₹50,000 per month
    - Rate is 5%
    """
    if lease.tds_applicable and rent_amount > 50000:
        return rent_amount * (lease.tds_rate / 100)
    return 0.0


def calculate_gst(lease, rent_amount):
    """Calculate GST on rent.
    
    GST is typically applicable for:
    - Commercial properties at 18%
    - Residential properties above certain threshold
    """
    if lease.gst_applicable:
        return rent_amount * (lease.gst_rate / 100)
    return 0.0


def get_next_invoice_number(landlord_id):
    """Generate next invoice number."""
    from app.models import Invoice
    
    prefix = f"{Config.INVOICE_PREFIX}-{landlord_id}-"
    
    # Get last invoice number
    last_invoice = Invoice.query.filter(
        Invoice.invoice_number.startswith(prefix)
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract number part and increment
        num_part = last_invoice.invoice_number.split('-')[-1]
        next_num = int(num_part) + 1
    else:
        next_num = 1
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}"


def print_ruby_note():
    """Print note about Ruby implementation for verification."""
    print("""
    ============================================================================
    INDIAN RENTAL INVOICING APPLICATION - COMPLIANCE NOTES
    ============================================================================
    
    This application follows Indian tax and accounting compliance:
    
    1. GST (Goods and Services Tax)
       - Commercial properties: 18% GST applicable
       - Residential properties: GST applicable if landlord's turnover > ₹20 lakhs
       
    2. TDS (Tax Deducted at Source) - Section 194-IB
       - Applicable when rent > ₹50,000 per month
       - Rate: 5% for individuals/HUF
       - No TAN required for individuals
       
    3. PAN Validation
       - Format: AAAAN0000A (e.g., ABCDE1234F)
       - Mandatory for both landlord and tenant
       
    4. GSTIN Validation
       - Format: 2-digit state code + 10-digit PAN + Entity code + Check digit
       - Optional (only if GST registered)
       
    5. Invoice Requirements (as per Indian law)
       - Unique invoice number
       - Date of issue
       - Supplier and recipient details with PAN
       - Description of service
       - Tax breakdown
       - Total amount
       
    6. RERA Compliance
       - Registration number field included for properties
       - Required for commercial complexes
       
    7. Audit Trail
       - All actions logged for compliance
       - Timestamp and user tracking
    
    ============================================================================
    """)
