# 🏠 Indian Rental Invoicing & Property Tax Management

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![ReportLab](https://img.shields.io/badge/PDF_Engine-ReportLab-00599C?style=for-the-badge)](https://www.reportlab.com/)
[![Tax Compliance](https://img.shields.io/badge/Compliance-GST_%26_TDS_194--IB-007A3D?style=for-the-badge)](https://incometaxindia.gov.in)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A comprehensive rental management and automated invoicing platform engineered specifically for **Indian landlords, property managers, and co-working operators**. Fully compliant with **GST laws**, **Section 194-IB TDS regulations**, **RERA**, and standard Indian financial accounting practices.

---

## ✨ Features & Capabilities

### 🏢 Property & Lease Lifecycle
- **Multi-Property Categorization**: Manage Residential, Commercial, and Industrial units with location metadata.
- **Tenant & Landlord KYC**: Record and validate PAN cards, Aadhaar, and GSTIN certificates with regex validation.
- **Configurable Lease Contracts**: Set security deposit thresholds, escalation clauses, billing cycles, and automated tax applicability.

### 🇮🇳 Indian Tax & Legal Compliance
- **Automated GST Calculation**: Auto-applies standard 18% GST for commercial properties, with turnover threshold rules.
- **Section 194-IB TDS Handling**: Computes 5% TDS deduction when monthly rent exceeds ₹50,000 for individual/HUF tenants.
- **Format Validation**: Strict client- and server-side verification for PAN (`[A-Z]{5}[0-9]{4}[A-Z]`) and GSTIN formats.
- **Payment Reconciliation**: Tracks NEFT, RTGS, IMPS, UPI, and UTR transaction reference numbers.
- **RERA Compliance Notes**: Standard clause attachments and tenant verification audit trails.

### 📄 Professional PDF Invoice Generation
- High-fidelity PDF generation via ReportLab adhering to Indian accounting formats.
- Displays INR currency symbols (`₹`), Indian numbering comma grouping (e.g. ₹1,50,000), state codes, and HSN/SAC codes.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | [Flask](https://flask.palletsprojects.com/) (Application Factory Pattern) |
| **ORM & Database** | [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) + SQLite / PostgreSQL |
| **Authentication** | [Flask-Login](https://flask-login.readthedocs.io/) (Session management & RBAC) |
| **Form Validation** | [WTForms](https://wtforms.readthedocs.io/) |
| **PDF Generation Engine**| [ReportLab](https://www.reportlab.com/) |

---

## 📂 Directory Structure

```text
rental-invoice-app/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # SQLAlchemy models (Landlord, Tenant, Property, Lease, Invoice)
│   ├── routes.py            # Blueprint route definitions
│   ├── utils.py             # ReportLab PDF invoice rendering engine
│   └── templates/           # Modular Jinja2 templates (auth, landlord, tenant, property, lease, invoice)
├── uploads/
│   ├── documents/           # Uploaded tenant verification IDs
│   └── invoices/            # Generated PDF invoices
├── config.py                # Tax slabs, TDS thresholds, and security secrets
├── run.py                   # App entrypoint (supports `--seed` flag)
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone & Enter Repository
```bash
git clone https://github.com/AnupamKhurana/rental-invoice-app.git
cd rental-invoice-app
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Launch with Sample Data
Populate realistic sample landlords, tenants, leases, and pending/paid invoices:
```bash
python run.py --seed
```

*(Or run without sample data for a clean slate: `python run.py`)*

### 4. Access Dashboard
Navigate to: **`http://localhost:5000`**

**Default Seed Credentials:**
- **Email:** `rajesh.kumar@example.com`
- **Password:** `password123`

---

## 📊 Indian Tax Compliance Rules Reference

| Tax Mechanism | Threshold / Conditions | Rate / Treatment |
| :--- | :--- | :--- |
| **Commercial GST** | Any registered commercial lease | Standard **18%** (CGST 9% + SGST 9% or IGST 18%) |
| **Residential GST** | Exempt for individual tenants; taxable if registered business tenant | Exempt / Reverse Charge |
| **TDS Sec 194-IB** | Rent exceeds **₹50,000/month** (Tenant is Individual / HUF) | **5%** deducted by tenant; TAN not required |
| **PAN Verification** | Mandatory for all active rental agreements | Built-in format validator |

---

## 🔧 Customizing Tax Slabs

Tax parameters can be customized in `config.py`:
```python
GST_RATE_COMMERCIAL = 18.0   # Default commercial rate (%)
GST_THRESHOLD = 2000000      # ₹20 Lakhs turnover threshold
TDS_RATE_194IB = 5.0         # 5% TDS rate
TDS_THRESHOLD_194IB = 50000  # ₹50,000 monthly rent threshold
```

---

## 📄 License

This project is licensed under the MIT License - free for personal and commercial property management.
