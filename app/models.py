"""Database models for Indian Rental Invoicing Application.

This module contains all the database models following Indian accounting
standards, GST laws, and compliance requirements.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Landlord(UserMixin, db.Model):
    """Landlord model - Property owner with GST/TDS compliance fields."""
    
    __tablename__ = 'landlords'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pan = db.Column(db.String(10), unique=True, nullable=False)  # Permanent Account Number
    gstin = db.Column(db.String(15), unique=True, nullable=True)  # GST Identification Number
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_gst_registered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='landlord', lazy=True, cascade='all, delete-orphan')
    leases = db.relationship('LeaseAgreement', backref='landlord', lazy=True)
    # Invoices accessed through leases - no direct relationship needed

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Landlord {self.name}>'


class Tenant(db.Model):
    """Tenant model - Renter details with compliance fields."""
    
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pan = db.Column(db.String(10), unique=True, nullable=False)
    gstin = db.Column(db.String(15), unique=True, nullable=True)
    aadhaar = db.Column(db.String(12), nullable=True)  # Optional for verification
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    employer_name = db.Column(db.String(150), nullable=True)
    employer_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leases = db.relationship('LeaseAgreement', backref='tenant', lazy=True)
    documents = db.relationship('TenantDocument', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'


class Property(db.Model):
    """Property model - Rental property details."""
    
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'), nullable=True)
    
    # Property identification
    property_name = db.Column(db.String(150), nullable=False)
    property_code = db.Column(db.String(20), unique=True, nullable=False)  # Internal reference
    property_type = db.Column(db.String(20), nullable=False)  # residential, commercial, industrial
    
    # Address details
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    landmark = db.Column(db.String(200), nullable=True)
    
    # Property details
    flat_number = db.Column(db.String(20), nullable=True)
    building_name = db.Column(db.String(100), nullable=True)
    total_area_sqft = db.Column(db.Float, nullable=True)
    carpet_area_sqft = db.Column(db.Float, nullable=True)
    number_of_rooms = db.Column(db.Integer, nullable=True)
    number_of_bathrooms = db.Column(db.Integer, nullable=True)
    floor_number = db.Column(db.Integer, nullable=True)
    total_floors = db.Column(db.Integer, nullable=True)
    parking_available = db.Column(db.Boolean, default=False)
    furnished = db.Column(db.Boolean, default=False)
    
    # RERA registration (if applicable)
    rera_registration_number = db.Column(db.String(50), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_rented = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leases = db.relationship('LeaseAgreement', backref='property', lazy=True)
    
    def get_full_address(self):
        """Return full formatted address."""
        parts = [self.address_line1, self.address_line2, 
                 self.city, self.state, self.pincode]
        return ', '.join(str(p) for p in parts if p)
    
    def __repr__(self):
        return f'<Property {self.property_name}>'


class LeaseAgreement(db.Model):
    """Lease Agreement model - Links landlord, property, and tenant.
    
    Contains lease terms, rental amounts, and compliance details.
    """
    
    __tablename__ = 'lease_agreements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Agreement identification
    agreement_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Lease terms
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    notice_period_days = db.Column(db.Integer, default=30)
    
    # Financial terms
    monthly_rent = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, default=0.0)
    maintenance_charges = db.Column(db.Float, default=0.0)
    parking_charges = db.Column(db.Float, default=0.0)
    
    # GST details
    gst_applicable = db.Column(db.Boolean, default=False)
    gst_rate = db.Column(db.Float, default=0.0)
    
    # TDS details (Section 194-IB)
    tds_applicable = db.Column(db.Boolean, default=False)
    tds_rate = db.Column(db.Float, default=5.0)  # 5% for individuals/HUF
    
    # Advance rent (if any)
    advance_rent_months = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, terminated, expired
    
    # Additional terms
    terms_and_conditions = db.Column(db.Text, nullable=True)
    special_conditions = db.Column(db.Text, nullable=True)
    
    # Signatures
    signed_by_landlord = db.Column(db.Boolean, default=False)
    signed_by_tenant = db.Column(db.Boolean, default=False)
    witness_name = db.Column(db.String(100), nullable=True)
    witness_signature = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='lease', lazy=True)
    
    def total_monthly_amount(self):
        """Calculate total monthly amount before taxes."""
        return self.monthly_rent + self.maintenance_charges + self.parking_charges
    
    def get_gst_amount(self):
        """Calculate GST amount."""
        if self.gst_applicable:
            return self.monthly_rent * (self.gst_rate / 100)
        return 0.0
    
    def get_tds_amount(self):
        """Calculate TDS amount."""
        if self.tds_applicable and self.monthly_rent > 50000:
            return self.monthly_rent * (self.tds_rate / 100)
        return 0.0
    
    def __repr__(self):
        return f'<LeaseAgreement {self.agreement_number}>'


class Invoice(db.Model):
    """Invoice model - Rental invoice with GST compliance.
    
    Follows Indian invoicing standards with proper tax breakdown.
    """
    
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    lease_id = db.Column(db.Integer, db.ForeignKey('lease_agreements.id'), nullable=False)
    
    # Invoice identification
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Dates
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date, nullable=True)  # When actually paid
    
    # Period
    billing_month = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    billing_year = db.Column(db.Integer, nullable=False)
    
    # Amount breakdown (following Indian accounting)
    basic_rent = db.Column(db.Float, nullable=False)
    maintenance_charges = db.Column(db.Float, default=0.0)
    parking_charges = db.Column(db.Float, default=0.0)
    electricity_charges = db.Column(db.Float, default=0.0)
    water_charges = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    
    # Tax amounts
    gst_amount = db.Column(db.Float, default=0.0)
    tds_amount = db.Column(db.Float, default=0.0)
    
    # Totals
    subtotal = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # After GST
    amount_after_tds = db.Column(db.Float, default=0.0)  # Net to landlord
    
    # Payment details
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, partial
    payment_mode = db.Column(db.String(20), nullable=True)
    cheque_number = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    utr_number = db.Column(db.String(50), nullable=True)  # For NEFT/RTGS
    
    # Notes
    remarks = db.Column(db.Text, nullable=True)
    
    # PDF storage
    pdf_filename = db.Column(db.String(200), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_totals(self):
        """Calculate invoice totals."""
        self.subtotal = (self.basic_rent + self.maintenance_charges + 
                        self.parking_charges + self.electricity_charges + 
                        self.water_charges + self.other_charges)
        self.total_amount = self.subtotal + self.gst_amount
        self.amount_after_tds = self.total_amount - self.tds_amount
    
    def mark_as_paid(self, payment_mode=None, payment_date=None, **kwargs):
        """Mark invoice as paid."""
        self.payment_status = 'paid'
        self.payment_date = payment_date or datetime.now().date()
        if payment_mode:
            self.payment_mode = payment_mode
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.payment_status == 'paid':
            return False
        return datetime.now().date() > self.due_date
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class TenantDocument(db.Model):
    """Documents uploaded by/for tenant - ID proofs, agreements, etc."""
    
    __tablename__ = 'tenant_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    document_type = db.Column(db.String(50), nullable=False)  # pan, aadhaar, agreement, etc.
    document_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TenantDocument {self.document_name}>'


class AuditLog(db.Model):
    """Audit log for compliance tracking."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, view
    model_name = db.Column(db.String(50), nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    user_type = db.Column(db.String(20), nullable=True)  # landlord, admin
    old_values = db.Column(db.Text, nullable=True)
    new_values = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.model_name}>'
