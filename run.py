"""Main entry point for the Indian Rental Invoicing Application.

This script initializes and runs the Flask application.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Landlord, Tenant, Property, LeaseAgreement, Invoice
from app.utils import print_ruby_note


def seed_sample_data():
    """Seed database with sample data for testing."""
    
    with create_app().app_context():
        # Check if data already exists
        if Landlord.query.first():
            print("Sample data already exists. Skipping seed.")
            return
        
        print("Seeding sample data...")
        
        # Create sample landlord
        landlord = Landlord(
            name="Rajesh Kumar",
            email="rajesh.kumar@example.com",
            phone="9876543210",
            address="123, MG Road, Koramangala, Bangalore, Karnataka - 560034",
            pan="ABCDE1234F",
            gstin="29ABCDE1234F1Z5",
            is_gst_registered=True
        )
        landlord.set_password("password123")
        db.session.add(landlord)
        db.session.flush()
        
        # Create sample tenants
        tenant1 = Tenant(
            name="Priya Sharma",
            email="priya.sharma@example.com",
            phone="9876543211",
            address="456, Park Street, Kolkata, West Bengal - 700016",
            pan="PQRST5678G",
            employer_name="Tech Solutions Pvt Ltd",
            employer_address="123, Cyber City, Gurgaon"
        )
        
        tenant2 = Tenant(
            name="Amit Patel",
            email="amit.patel@example.com",
            phone="9876543212",
            address="789, Nehru Place, New Delhi - 110019",
            pan="UVWXY9012H",
            employer_name="Financial Services Ltd"
        )
        
        db.session.add_all([tenant1, tenant2])
        db.session.flush()
        
        # Create sample properties
        property1 = Property(
            landlord_id=None,
            property_name="Apartment 301, Sunshine Heights",
            property_code="PROP-1-20240101000001",
            property_type="residential",
            address_line1="45, Brigade Road",
            address_line2="Near Metro Station",
            city="Bangalore",
            state="Karnataka",
            pincode="560025",
            flat_number="301",
            building_name="Sunshine Heights",
            total_area_sqft=1200,
            carpet_area_sqft=1000,
            number_of_rooms=2,
            number_of_bathrooms=2,
            furnished=True,
            parking_available=True
        )
        
        property2 = Property(
            landlord_id=None,
            property_name="Office Space - 4th Floor",
            property_code="PROP-1-20240101000002",
            property_type="commercial",
            address_line1="78, Commercial Street",
            address_line2="Business District",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            total_area_sqft=2500,
            carpet_area_sqft=2200,
            parking_available=True
        )
        
        db.session.add_all([property1, property2])
        db.session.flush()
        
        # Create sample lease agreements
        lease1 = LeaseAgreement(
            landlord_id=None,
            tenant_id=tenant1.id,
            property_id=property1.id,
            agreement_number="LEA-1-202401011200",
            start_date=datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-12-01", "%Y-%m-%d").date(),
            monthly_rent=25000.00,
            security_deposit=50000.00,
            maintenance_charges=2000.00,
            gst_applicable=False,
            tds_applicable=False
        )
        
        lease2 = LeaseAgreement(
            landlord_id=None,
            tenant_id=tenant2.id,
            property_id=property2.id,
            agreement_number="LEA-1-202401011201",
            start_date=datetime.strptime("2024-01-15", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
            monthly_rent=75000.00,
            security_deposit=150000.00,
            maintenance_charges=5000.00,
            parking_charges=1500.00,
            gst_applicable=True,
            gst_rate=18.0,
            tds_applicable=True,
            tds_rate=5.0
        )
        
        db.session.add_all([lease1, lease2])
        db.session.flush()
        
        # Create sample invoices
        
        invoice1 = Invoice(
            lease_id=lease1.id,
            invoice_number="INV-1-20240101120000",
            invoice_date=datetime.now().date() - timedelta(days=30),
            due_date=datetime.now().date() - timedelta(days=15),
            billing_month="2024-01",
            billing_year=2024,
            basic_rent=25000.00,
            maintenance_charges=2000.00,
            subtotal=27000.00,
            total_amount=27000.00,
            amount_after_tds=27000.00,
            payment_status="paid",
            payment_mode="upi",
            payment_date=datetime.now().date() - timedelta(days=16)
        )
        
        invoice2 = Invoice(
            lease_id=lease2.id,
            invoice_number="INV-1-20240101120001",
            invoice_date=datetime.now().date() - timedelta(days=20),
            due_date=datetime.now().date() - timedelta(days=5),
            billing_month="2024-01",
            billing_year=2024,
            basic_rent=75000.00,
            maintenance_charges=5000.00,
            parking_charges=1500.00,
            gst_amount=13500.00,  # 18% of 75000
            subtotal=81500.00,
            total_amount=95000.00,
            tds_amount=3750.00,  # 5% of 75000
            amount_after_tds=91250.00,
            payment_status="pending"
        )
        
        invoice3 = Invoice(
            lease_id=lease1.id,
            invoice_number="INV-1-20240101120002",
            invoice_date=datetime.now().date() - timedelta(days=10),
            due_date=datetime.now().date() + timedelta(days=10),
            billing_month="2024-02",
            billing_year=2024,
            basic_rent=25000.00,
            maintenance_charges=2000.00,
            subtotal=27000.00,
            total_amount=27000.00,
            amount_after_tds=27000.00,
            payment_status="pending"
        )
        
        db.session.add_all([invoice1, invoice2, invoice3])
        db.session.commit()
        
        print("Sample data seeded successfully!")
        print("\nLogin credentials:")
        print(f"Email: {landlord.email}")
        print("Password: password123")


def main():
    """Main function to run the application."""
    
    # Print application info
    print("=" * 70)
    print("🏠 INDIAN RENTAL INVOICING APPLICATION")
    print("=" * 70)
    print("\nA comprehensive rental management solution compliant with:")
    print("• Goods and Services Tax (GST) Act")
    print("• Tax Deducted at Source (TDS) - Section 194-IB")
    print("• Indian Accounting Standards")
    print("• Real Estate (Regulation and Development) Act (RERA)")
    print("\n" + "=" * 70)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--seed':
            print("\n🌱 Seeding sample data...")
            seed_sample_data()
            return
        elif sys.argv[1] == '--info':
            print_ruby_note()
            return
    
    # Create and run app
    app = create_app()
    
    print("\n🚀 Starting application...")
    print("\n📌 Access the application at:")
    print("   http://localhost:5000")
    print("\n💡 Features:")
    print("   • Tenant Management")
    print("   • Property Management")
    print("   • Lease Agreements")
    print("   • GST & TDS Compliance")
    print("   • Professional Invoice PDF Generation")
    print("\n" + "=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


if __name__ == '__main__':
    main()
