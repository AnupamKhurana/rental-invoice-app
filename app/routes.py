"""Route blueprints for the rental invoicing application."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
import re
import os
from config import Config
from app import db
from app.models import Landlord, Tenant, Property, LeaseAgreement, Invoice, TenantDocument, AuditLog

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
tenant_bp = Blueprint('tenant', __name__)
landlord_bp = Blueprint('landlord', __name__)
property_bp = Blueprint('property', __name__)
lease_bp = Blueprint('lease', __name__)
invoice_bp = Blueprint('invoice', __name__)


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Landlord login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        landlord = Landlord.query.filter_by(email=email).first()
        
        if landlord and landlord.check_password(password):
            login_user(landlord, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Landlord registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        pan = request.form.get('pan')
        gstin = request.form.get('gstin') or ''
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not phone or not address or not pan:
            flash('All required fields must be filled', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('auth/register.html')
        
        # PAN validation
        if not re.match(Config.PAN_PATTERN, pan.upper()):
            flash('Invalid PAN format', 'error')
            return render_template('auth/register.html')
        
        # GSTIN validation (if provided)
        if gstin and not re.match(Config.GSTIN_PATTERN, gstin.upper()):
            flash('Invalid GSTIN format', 'error')
            return render_template('auth/register.html')
        
        # Check duplicates
        if Landlord.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        if Landlord.query.filter_by(pan=pan.upper()).first():
            flash('PAN already registered', 'error')
            return render_template('auth/register.html')
        
        # Create landlord
        landlord = Landlord(
            name=name,
            email=email,
            phone=phone,
            address=address,
            pan=pan.upper(),
            gstin=gstin.upper() if gstin else None,
            is_gst_registered=bool(gstin)
        )
        landlord.set_password(password)
        
        db.session.add(landlord)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ============================================================================
# MAIN ROUTES
# ============================================================================

@main_bp.route('/')
def index():
    """Dashboard/home page."""
    if current_user.is_authenticated:
        return render_template('main/dashboard.html', user=current_user)
    return render_template('main/index.html')


@main_bp.route('/summary')
@login_required
def summary():
    """Summary dashboard - shows all data for all logged-in users."""
    # Get statistics (all data shared)
    properties_count = Property.query.count()
    tenants_count = Tenant.query.count()
    active_leases = LeaseAgreement.query.filter_by(is_active=True).count()
    
    # Financial summary (all invoices)
    from sqlalchemy import func
    total_invoices = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
    
    paid_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.payment_status == 'paid'
    ).scalar() or 0
    
    pending_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.payment_status != 'paid'
    ).scalar() or 0
    
    return render_template('main/summary.html', 
                         properties_count=properties_count,
                         tenants_count=tenants_count,
                         active_leases=active_leases,
                         total_invoices=total_invoices,
                         paid_invoices=paid_invoices,
                         pending_invoices=pending_invoices)


# ============================================================================
# LANDLORD ROUTES
# ============================================================================

@landlord_bp.route('/list')
@login_required
def list_landlords():
    """List all landlords (admin view)."""
    landlords = Landlord.query.all()
    return render_template('landlord/list.html', landlords=landlords)


@landlord_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_landlord():
    """Add new landlord."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        pan = request.form.get('pan')
        gstin = request.form.get('gstin') or ''
        
        # Validation
        if not all([name, email, phone, address, pan]):
            flash('All required fields must be filled', 'error')
            return render_template('landlord/add.html')
        
        # PAN validation
        if not re.match(Config.PAN_PATTERN, pan.upper()):
            flash('Invalid PAN format', 'error')
            return render_template('landlord/add.html')
        
        # GSTIN validation
        if gstin and not re.match(Config.GSTIN_PATTERN, gstin.upper()):
            flash('Invalid GSTIN format', 'error')
            return render_template('landlord/add.html')
        
        # Check duplicates
        if Landlord.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('landlord/add.html')
        
        landlord = Landlord(
            name=name,
            email=email,
            phone=phone,
            address=address,
            pan=pan.upper(),
            gstin=gstin.upper() if gstin else None,
            is_gst_registered=bool(gstin)
        )
        landlord.set_password('default123')  # Default password, should change
        
        db.session.add(landlord)
        db.session.commit()
        
        # Log audit
        log_audit('create', 'Landlord', landlord.id)
        
        flash('Landlord added successfully', 'success')
        return redirect(url_for('landlord.list_landlords'))
    
    return render_template('landlord/add.html')


@landlord_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_landlord(id):
    """Edit landlord details."""
    landlord = Landlord.query.get_or_404(id)
    
    if request.method == 'POST':
        landlord.name = request.form.get('name')
        landlord.email = request.form.get('email')
        landlord.phone = request.form.get('phone')
        landlord.address = request.form.get('address')
        landlord.pan = request.form.get('pan').upper()
        gstin = request.form.get('gstin') or ''
        landlord.gstin = gstin.upper() if gstin else None
        landlord.is_gst_registered = bool(gstin)
        landlord.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_audit('update', 'Landlord', landlord.id)
        
        flash('Landlord updated successfully', 'success')
        return redirect(url_for('landlord.list_landlords'))
    
    return render_template('landlord/edit.html', landlord=landlord)


@landlord_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_landlord(id):
    """Delete landlord."""
    landlord = Landlord.query.get_or_404(id)
    
    if landlord.properties or landlord.invoices:
        flash('Cannot delete landlord with associated data', 'error')
    else:
        log_audit('delete', 'Landlord', landlord.id)
        db.session.delete(landlord)
        db.session.commit()
        flash('Landlord deleted successfully', 'success')
    
    return redirect(url_for('landlord.list_landlords'))


# ============================================================================
# TENANT ROUTES
# ============================================================================

@tenant_bp.route('/list')
@login_required
def list_tenants():
    """List all tenants (shared across all users)."""
    tenants = Tenant.query.all()
    return render_template('tenant/list.html', tenants=tenants)


@tenant_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    """Add new tenant."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        pan = request.form.get('pan')
        gstin = request.form.get('gstin') or ''
        aadhaar = request.form.get('aadhaar') or ''
        emergency_contact_name = request.form.get('emergency_contact_name') or ''
        emergency_contact_phone = request.form.get('emergency_contact_phone') or ''
        employer_name = request.form.get('employer_name') or ''
        employer_address = request.form.get('employer_address') or ''
        
        # Validation
        if not all([name, email, phone, address, pan]):
            flash('All required fields must be filled', 'error')
            return render_template('tenant/add.html')
        
        # PAN validation
        if not re.match(Config.PAN_PATTERN, pan.upper()):
            flash('Invalid PAN format', 'error')
            return render_template('tenant/add.html')
        
        # GSTIN validation
        if gstin and not re.match(Config.GSTIN_PATTERN, gstin.upper()):
            flash('Invalid GSTIN format', 'error')
            return render_template('tenant/add.html')
        
        # Aadhaar validation (12 digits)
        if aadhaar and not re.match(r'^\d{12}$', aadhaar):
            flash('Invalid Aadhaar format (must be 12 digits)', 'error')
            return render_template('tenant/add.html')
        
        # Check duplicates
        if Tenant.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('tenant/add.html')
        
        tenant = Tenant(
            name=name,
            email=email,
            phone=phone,
            address=address,
            pan=pan.upper(),
            gstin=gstin.upper() if gstin else None,
            aadhaar=aadhaar,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            employer_name=employer_name,
            employer_address=employer_address
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        log_audit('create', 'Tenant', tenant.id)
        
        flash('Tenant added successfully', 'success')
        return redirect(url_for('tenant.list_tenants'))
    
    return render_template('tenant/add.html')


@tenant_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tenant(id):
    """Edit tenant details."""
    tenant = Tenant.query.get_or_404(id)
    
    if request.method == 'POST':
        tenant.name = request.form.get('name')
        tenant.email = request.form.get('email')
        tenant.phone = request.form.get('phone')
        tenant.address = request.form.get('address')
        tenant.pan = request.form.get('pan').upper()
        gstin = request.form.get('gstin') or ''
        tenant.gstin = gstin.upper() if gstin else None
        aadhaar = request.form.get('aadhaar') or ''
        tenant.aadhaar = aadhaar
        tenant.emergency_contact_name = request.form.get('emergency_contact_name') or ''
        tenant.emergency_contact_phone = request.form.get('emergency_contact_phone') or ''
        tenant.employer_name = request.form.get('employer_name') or ''
        tenant.employer_address = request.form.get('employer_address') or ''
        tenant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_audit('update', 'Tenant', tenant.id)
        
        flash('Tenant updated successfully', 'success')
        return redirect(url_for('tenant.list_tenants'))
    
    return render_template('tenant/edit.html', tenant=tenant)


@tenant_bp.route('/view/<int:id>')
@login_required
def view_tenant(id):
    """View tenant details."""
    tenant = Tenant.query.get_or_404(id)
    leases = LeaseAgreement.query.filter_by(tenant_id=tenant.id).all()
    return render_template('tenant/view.html', tenant=tenant, leases=leases)


@tenant_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_tenant(id):
    """Delete tenant."""
    tenant = Tenant.query.get_or_404(id)
    
    if tenant.leases or tenant.invoices:
        flash('Cannot delete tenant with associated data', 'error')
    else:
        log_audit('delete', 'Tenant', tenant.id)
        db.session.delete(tenant)
        db.session.commit()
        flash('Tenant deleted successfully', 'success')
    
    return redirect(url_for('tenant.list_tenants'))


# ============================================================================
# PROPERTY ROUTES
# ============================================================================

@property_bp.route('/list')
@login_required
def list_properties():
    """List all properties (shared across all users)."""
    properties = Property.query.all()
    return render_template('property/list.html', properties=properties)


@property_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_property():
    """Add new property (shared across all users)."""
    if request.method == 'POST':
        property_name = request.form.get('property_name')
        property_type = request.form.get('property_type')
        address_line1 = request.form.get('address_line1')
        address_line2 = request.form.get('address_line2') or ''
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        flat_number = request.form.get('flat_number') or ''
        building_name = request.form.get('building_name') or ''
        
        # Generate property code
        from datetime import datetime
        prop_code = f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Validation
        if not all([property_name, property_type, address_line1, city, state, pincode]):
            flash('All required fields must be filled', 'error')
            return render_template('property/add.html')
        
        property_obj = Property(
            landlord_id=None,
            property_name=property_name,
            property_code=prop_code,
            property_type=property_type,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode,
            flat_number=flat_number,
            building_name=building_name,
            total_area_sqft=float(request.form.get('total_area_sqft') or 0),
            carpet_area_sqft=float(request.form.get('carpet_area_sqft') or 0),
            number_of_rooms=int(request.form.get('number_of_rooms') or 0),
            number_of_bathrooms=int(request.form.get('number_of_bathrooms') or 0),
            parking_available=request.form.get('parking_available') == 'on',
            furnished=request.form.get('furnished') == 'on'
        )
        
        db.session.add(property_obj)
        db.session.commit()
        
        log_audit('create', 'Property', property_obj.id)
        
        flash('Property added successfully', 'success')
        return redirect(url_for('property.list_properties'))
    
    return render_template('property/add.html', states=Config.STATES)


@property_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    """Edit property details (shared across all users)."""
    property_obj = Property.query.get_or_404(id)
    
    if request.method == 'POST':
        property_obj.property_name = request.form.get('property_name')
        property_obj.property_type = request.form.get('property_type')
        property_obj.address_line1 = request.form.get('address_line1')
        property_obj.address_line2 = request.form.get('address_line2') or ''
        property_obj.city = request.form.get('city')
        property_obj.state = request.form.get('state')
        property_obj.pincode = request.form.get('pincode')
        property_obj.flat_number = request.form.get('flat_number') or ''
        property_obj.building_name = request.form.get('building_name') or ''
        property_obj.total_area_sqft = float(request.form.get('total_area_sqft') or 0)
        property_obj.carpet_area_sqft = float(request.form.get('carpet_area_sqft') or 0)
        property_obj.number_of_rooms = int(request.form.get('number_of_rooms') or 0)
        property_obj.number_of_bathrooms = int(request.form.get('number_of_bathrooms') or 0)
        property_obj.parking_available = request.form.get('parking_available') == 'on'
        property_obj.furnished = request.form.get('furnished') == 'on'
        property_obj.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_audit('update', 'Property', property_obj.id)
        
        flash('Property updated successfully', 'success')
        return redirect(url_for('property.list_properties'))
    
    return render_template('property/edit.html', property=property_obj, states=Config.STATES)


@property_bp.route('/view/<int:id>')
@login_required
def view_property(id):
    """View property details (shared across all users)."""
    property_obj = Property.query.get_or_404(id)
    leases = LeaseAgreement.query.filter_by(property_id=id).all()
    
    return render_template('property/view.html', property=property_obj, leases=leases)


@property_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_property(id):
    """Delete property (shared across all users)."""
    property_obj = Property.query.get_or_404(id)
    
    if property_obj.leases:
        flash('Cannot delete property with active leases', 'error')
    else:
        log_audit('delete', 'Property', property_obj.id)
        db.session.delete(property_obj)
        db.session.commit()
        flash('Property deleted successfully', 'success')
    
    return redirect(url_for('property.list_properties'))


# ============================================================================
# LEASE AGREEMENT ROUTES
# ============================================================================

@lease_bp.route('/list')
@login_required
def list_leases():
    """List all lease agreements (shared across all users)."""
    leases = LeaseAgreement.query.all()
    return render_template('lease/list.html', leases=leases)


@lease_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_lease():
    """Create new lease agreement (shared across all users)."""
    if request.method == 'POST':
        tenant_id = request.form.get('tenant_id')
        property_id = request.form.get('property_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        monthly_rent = float(request.form.get('monthly_rent'))
        security_deposit = float(request.form.get('security_deposit') or 0)
        maintenance_charges = float(request.form.get('maintenance_charges') or 0)
        parking_charges = float(request.form.get('parking_charges') or 0)
        
        # Generate agreement number
        from datetime import datetime
        agreement_num = f"LEA-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Validation
        if not all([tenant_id, property_id, start_date, end_date]):
            flash('All required fields must be filled', 'error')
            return render_template('lease/add.html')
        
        # Check property exists
        property_obj = Property.query.get_or_404(property_id)
        
        lease = LeaseAgreement(
            landlord_id=None,
            tenant_id=tenant_id,
            property_id=property_id,
            agreement_number=agreement_num,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            monthly_rent=monthly_rent,
            security_deposit=security_deposit,
            maintenance_charges=maintenance_charges,
            parking_charges=parking_charges,
            gst_applicable=request.form.get('gst_applicable') == 'on',
            gst_rate=float(request.form.get('gst_rate') or 18.0),
            tds_applicable=request.form.get('tds_applicable') == 'on',
            tds_rate=float(request.form.get('tds_rate') or 5.0)
        )
        
        db.session.add(lease)
        db.session.commit()
        
        log_audit('create', 'LeaseAgreement', lease.id)
        
        flash('Lease agreement created successfully', 'success')
        return redirect(url_for('lease.list_leases'))
    
    # Get tenants and properties for dropdowns (all data shared)
    tenants = Tenant.query.all()
    properties = Property.query.all()
    
    return render_template('lease/add.html', tenants=tenants, properties=properties)


@lease_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lease(id):
    """Edit lease agreement (shared across all users)."""
    lease = LeaseAgreement.query.get_or_404(id)
    
    if request.method == 'POST':
        lease.tenant_id = request.form.get('tenant_id')
        lease.property_id = request.form.get('property_id')
        lease.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        lease.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        lease.monthly_rent = float(request.form.get('monthly_rent'))
        lease.security_deposit = float(request.form.get('security_deposit') or 0)
        lease.maintenance_charges = float(request.form.get('maintenance_charges') or 0)
        lease.parking_charges = float(request.form.get('parking_charges') or 0)
        lease.gst_applicable = request.form.get('gst_applicable') == 'on'
        lease.gst_rate = float(request.form.get('gst_rate') or 18.0)
        lease.tds_applicable = request.form.get('tds_applicable') == 'on'
        lease.tds_rate = float(request.form.get('tds_rate') or 5.0)
        lease.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_audit('update', 'LeaseAgreement', lease.id)
        
        flash('Lease agreement updated successfully', 'success')
        return redirect(url_for('lease.list_leases'))
    
    tenants = Tenant.query.all()
    properties = Property.query.all()
    
    return render_template('lease/edit.html', lease=lease, tenants=tenants, properties=properties)


@lease_bp.route('/view/<int:id>')
@login_required
def view_lease(id):
    """View lease agreement details (shared across all users)."""
    lease = LeaseAgreement.query.get_or_404(id)
    
    invoices = Invoice.query.filter_by(lease_id=id).order_by(Invoice.invoice_date.desc()).all()
    
    return render_template('lease/view.html', lease=lease, invoices=invoices)


@lease_bp.route('/terminate/<int:id>', methods=['POST'])
@login_required
def terminate_lease(id):
    """Terminate lease agreement (shared across all users)."""
    lease = LeaseAgreement.query.get_or_404(id)
    
    lease.is_active = False
    lease.status = 'terminated'
    lease.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_audit('terminate', 'LeaseAgreement', lease.id)
    
    flash('Lease agreement terminated', 'success')
    return redirect(url_for('lease.list_leases'))


# ============================================================================
# INVOICE ROUTES
# ============================================================================

@invoice_bp.route('/list')
@login_required
def list_invoices():
    """List all invoices (shared across all users)."""
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    return render_template('invoice/list.html', invoices=invoices)


@invoice_bp.route('/add/<int:lease_id>', methods=['GET', 'POST'])
@login_required
def add_invoice(lease_id):
    """Create new invoice (shared across all users)."""
    lease = LeaseAgreement.query.get_or_404(lease_id)
    
    if request.method == 'POST':
        billing_month = request.form.get('billing_month')  # YYYY-MM
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        
        # Extract year from billing_month
        billing_year = int(billing_month[:4])
        
        # Generate invoice number
        from datetime import datetime
        invoice_num = f"{Config.INVOICE_PREFIX}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get amounts from form or use lease defaults
        basic_rent = float(request.form.get('basic_rent') or lease.monthly_rent)
        maintenance = float(request.form.get('maintenance_charges') or lease.maintenance_charges)
        parking = float(request.form.get('parking_charges') or lease.parking_charges)
        electricity = float(request.form.get('electricity_charges') or 0)
        water = float(request.form.get('water_charges') or 0)
        other = float(request.form.get('other_charges') or 0)
        
        # Calculate GST
        gst_amount = 0
        if lease.gst_applicable:
            gst_amount = basic_rent * (lease.gst_rate / 100)
        
        # Calculate TDS
        tds_amount = 0
        if lease.tds_applicable and basic_rent > 50000:
            tds_amount = basic_rent * (lease.tds_rate / 100)
        
        # Calculate totals
        subtotal = basic_rent + maintenance + parking + electricity + water + other
        total_amount = subtotal + gst_amount
        amount_after_tds = total_amount - tds_amount
        
        invoice = Invoice(
            lease_id=lease_id,
            invoice_number=invoice_num,
            invoice_date=datetime.strptime(invoice_date, '%Y-%m-%d').date(),
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date(),
            billing_month=billing_month,
            billing_year=billing_year,
            basic_rent=basic_rent,
            maintenance_charges=maintenance,
            parking_charges=parking,
            electricity_charges=electricity,
            water_charges=water,
            other_charges=other,
            gst_amount=gst_amount,
            tds_amount=tds_amount,
            subtotal=subtotal,
            total_amount=total_amount,
            amount_after_tds=amount_after_tds
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        log_audit('create', 'Invoice', invoice.id)
        
        flash('Invoice created successfully', 'success')
        return redirect(url_for('invoice.view_invoice', invoice_id=invoice.id))
    
    return render_template('invoice/add.html', lease=lease)


@invoice_bp.route('/view/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    """View invoice details (shared across all users)."""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    return render_template('invoice/view.html', invoice=invoice)


@invoice_bp.route('/mark-paid/<int:invoice_id>', methods=['POST'])
@login_required
def mark_paid(invoice_id):
    """Mark invoice as paid (shared across all users)."""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    payment_mode = request.form.get('payment_mode')
    cheque_number = request.form.get('cheque_number') or ''
    bank_name = request.form.get('bank_name') or ''
    utr_number = request.form.get('utr_number') or ''
    
    invoice.mark_as_paid(
        payment_mode=payment_mode,
        payment_date=datetime.now().date(),
        cheque_number=cheque_number,
        bank_name=bank_name,
        utr_number=utr_number
    )
    
    db.session.commit()
    
    log_audit('mark_paid', 'Invoice', invoice.id)
    
    flash('Invoice marked as paid', 'success')
    return redirect(url_for('invoice.view_invoice', invoice_id=invoice.id))


@invoice_bp.route('/download-pdf/<int:invoice_id>')
@login_required
def download_pdf(invoice_id):
    """Download invoice as PDF (shared across all users)."""
    from app.utils import generate_invoice_pdf
    
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Find any landlord for PDF generation
    landlord = Landlord.query.first()
    
    pdf_path = generate_invoice_pdf(invoice, landlord)
    
    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name=f"{invoice.invoice_number}.pdf")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log_audit(action, model_name, model_id, old_values=None, new_values=None):
    """Log audit trail."""
    audit = AuditLog(
        action=action,
        model_name=model_name,
        model_id=model_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        user_type='landlord' if current_user.is_authenticated else None,
        old_values=old_values,
        new_values=new_values
    )
    db.session.add(audit)
    db.session.commit()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_DOCUMENT_EXTENSIONS
