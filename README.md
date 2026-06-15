# 🏠 Indian Rental Invoicing Application

A comprehensive rental management application designed for Indian landlords, compliant with GST laws, TDS regulations, and Indian accounting standards.

## ✨ Features

### Core Functionality
- **Tenant Management** - Store and manage tenant details with PAN/Aadhaar
- **Landlord Management** - Multiple landlord support with GST registration
- **Property Management** - Track residential, commercial, and industrial properties
- **Lease Agreements** - Create and manage lease agreements with tax settings
- **Invoice Generation** - Professional PDF invoices with Indian accounting format

### Tax Compliance
- **GST Calculation** - Automatic GST calculation (18% standard for commercial)
- **TDS Deduction** - Section 194-IB TDS compliance (5% for rent > ₹50,000)
- **PAN Validation** - Built-in PAN format validation
- **GSTIN Validation** - GSTIN format validation
- **Audit Trail** - Complete audit logging for compliance

### Indian Standards
- RERA registration support
- Indian date format (DD-MM-YYYY)
- Indian currency formatting (₹)
- All Indian states dropdown
- UTR/NEFT/RTGS payment tracking

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Installation & Setup

### 1. Navigate to the project folder
```bash
cd rental-invoice-app
```

### 2. Activate virtual environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```cmd
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application

**With sample data:**
```bash
python run.py --seed
```

**Without sample data:**
```bash
python run.py
```

### 5. Access the application
Open your browser and navigate to:
```
http://localhost:5000
```

## 🔐 Default Login (with sample data)

```
Email: rajesh.kumar@example.com
Password: password123
```

## 📁 Project Structure

```
rental-invoice-app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes.py            # Route blueprints
│   ├── utils.py             # Utility functions (PDF generation)
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── auth/
│       ├── main/
│       ├── tenant/
│       ├── landlord/
│       ├── property/
│       ├── lease/
│       └── invoice/
├── uploads/
│   ├── documents/           # Document uploads
│   └── invoices/            # Generated PDF invoices
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── venv/                    # Virtual environment
```

## 🎯 Usage Guide

### 1. Register/Login
- New users should register with PAN and optionally GSTIN
- Existing users can login

### 2. Add Tenants
- Navigate to Tenants → Add New Tenant
- Fill in tenant details including PAN (mandatory)

### 3. Add Properties
- Navigate to Properties → Add New Property
- Enter property details including address
- Select property type (residential/commercial/industrial)

### 4. Create Lease Agreement
- Navigate to Leases → Create New Lease
- Select tenant and property
- Enter lease terms and financial details
- Configure GST and TDS settings

### 5. Generate Invoice
- Go to Lease → View → Create Invoice
- Enter billing period and charges
- System automatically calculates GST and TDS
- Download professional PDF invoice

## 🇮🇳 Tax Compliance Details

### GST (Goods and Services Tax)
- **Commercial Properties**: 18% GST applicable
- **Residential Properties**: Exempt unless landlord's turnover > ₹20 lakhs
- GSTIN validation included

### TDS (Tax Deducted at Source) - Section 194-IB
- **Applicable When**: Monthly rent > ₹50,000
- **Rate**: 5%
- **Who**: Individuals/HUF paying rent
- **No TAN Required**: For individuals under 194-IB

### PAN (Permanent Account Number)
- Mandatory for both landlord and tenant
- Format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)
- Built-in validation

## 📊 Invoice Features

The generated PDF invoices include:
- Professional Indian format
- Landlord and tenant details with PAN/GSTIN
- Complete charges breakdown
- GST calculation (if applicable)
- TDS deduction (if applicable)
- Net payable amount
- Payment tracking
- Compliance notes

## 🔧 Configuration

Edit `config.py` for custom settings:

```python
# GST Settings
GST_RATE_COMMERCIAL = 18.0  # Default 18%
GST_THRESHOLD = 2000000     # ₹20 lakhs

# TDS Settings
TDS_RATE_194IB = 5.0        # 5%
TDS_THRESHOLD_194IB = 50000 # ₹50,000
```

## 📝 Sample Data

Run with `--seed` flag to populate sample data:
```bash
python run.py --seed
```

This creates:
- 1 Landlord (GST registered)
- 2 Tenants
- 2 Properties (1 residential, 1 commercial)
- 2 Lease Agreements
- 3 Invoices (1 paid, 2 pending)

## 🛠️ Technologies Used

- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **ReportLab** - PDF generation
- **WTForms** - Form handling
- **Flask-Login** - User authentication

## 📞 Support

For issues or questions:
1. Check the console for error messages
2. Verify PAN/GSTIN formats
3. Ensure virtual environment is activated

## 📄 License

MIT License - Free for personal and commercial use

---

**Made with ❤️ for Indian Landlords** 🇮🇳

*Following Indian accounting standards and tax laws*
