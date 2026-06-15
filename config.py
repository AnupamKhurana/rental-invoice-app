import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration with Indian rental invoicing specifics."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'indian-rental-invoice-dev-key-2024'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///rental_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folders
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DOCUMENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'documents')
    INVOICE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'invoices')
    
    # Max upload size (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    
    # Allowed file extensions
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    
    # GST Settings (India)
    GST_RATE_COMMERCIAL = 18.0  # Commercial property GST rate
    GST_RATE_RESIDENTIAL = 0.0  # Residential property - typically no GST unless > threshold
    GST_THRESHOLD = 2000000  # GST registration threshold (₹20 lakhs)
    
    # TDS Settings (Section 194-IB)
    TDS_RATE_194IB = 5.0  # TDS rate for individuals/HUF paying rent > ₹50,000
    TDS_THRESHOLD_194IB = 50000  # TDS applicable if rent > ₹50,000 per month
    
    # PAN Validation Pattern
    PAN_PATTERN = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    # GSTIN Validation Pattern
    GSTIN_PATTERN = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    
    # Invoice Settings
    INVOICE_PREFIX = 'INV'
    INVOICE_PADDING = 8  # Number of digits for invoice number
    
    # Indian States for dropdowns
    STATES = [
        ('', 'Select State'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chandigarh', 'Chandigarh'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Puducherry', 'Puducherry'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
    ]
    
    # Property Types
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ]
    
    # Lease Types
    LEASE_TYPES = [
        ('monthly', 'Month-to-Month'),
        ('fixed_11', '11 Months (Fixed)'),
        ('fixed_12', '12 Months (Fixed)'),
        ('fixed_24', '24 Months (Fixed)'),
        ('fixed_36', '36 Months (Fixed)'),
        ('other', 'Other'),
    ]
    
    # Payment Modes
    PAYMENT_MODES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('rtgs', 'RTGS'),
        ('imps', 'IMPS'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    ]


def create_folders():
    """Create required upload folders."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.DOCUMENT_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.INVOICE_UPLOAD_FOLDER, exist_ok=True)


# Create folders on import
create_folders()
