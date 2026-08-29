# Backend Project Structure

## Overview
Complete FastAPI backend for the 痔漏辅助诊疗系统 (Anorectal TCM Clinic Management System).

## File Count
- **39 Python files** created
- **Complete working backend** with all modules implemented

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, CORS, router registration
│   ├── config.py                  # Settings with pydantic-settings
│   ├── database.py                # Async SQLAlchemy engine & session
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py            # JWT, password hashing, get_current_user
│   │
│   ├── models/                    # SQLAlchemy 2.0 models with UUID PKs
│   │   ├── __init__.py
│   │   ├── tenant.py              # Multi-tenant base
│   │   ├── user.py                # Users with roles
│   │   ├── patient.py             # Patient records
│   │   ├── consultation.py        # Consultation, Prescription, Followup
│   │   ├── image.py               # Clinical images with AI results
│   │   ├── billing.py             # ChargeItem, Bill, BillItem, BillPayment, DailyRevenue
│   │   ├── inventory.py           # Medicine, MedicineBatch, StockTransaction, StockAlert
│   │   └── knowledge.py           # AnorectalHerb, Formula, Case, PreventionGuide
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── patient.py
│   │   ├── billing.py
│   │   ├── inventory.py
│   │   └── vision.py
│   │
│   ├── services/                  # AI services
│   │   ├── __init__.py
│   │   ├── vision_ai.py           # Qwen-VL-Max multimodal image analysis
│   │   └── deepseek_service.py   # DeepSeek text-based syndrome differentiation
│   │
│   └── api/
│       └── v1/
│           ├── __init__.py
│           ├── auth.py            # Login, register, /me
│           ├── patients.py        # Patient CRUD
│           ├── consultations.py   # Consultation CRUD + AI diagnosis trigger
│           ├── billing.py         # Bills, payments, revenue stats
│           ├── inventory.py       # Medicine stock management
│           ├── vision.py          # Image analysis endpoint
│           ├── knowledge.py       # TCM knowledge base queries
│           ├── stats.py           # Dashboard statistics
│           ├── uploads.py         # File upload/download
│           └── followup.py        # Followup scheduling
│
├── scripts/
│   ├── init_demo.py               # Create demo tenant & users
│   ├── seed_knowledge.py          # Seed herbs, formulas, cases
│   └── seed_charge_items.py       # Seed charge items
│
├── requirements.txt               # All dependencies
├── Dockerfile                     # Production container
├── .env.example                   # Environment variables template
├── README.md                      # Complete documentation
└── STRUCTURE.md                   # This file
```

## Key Features Implemented

### 1. Multi-Tenant Architecture
- All tables have `tenant_id` foreign key
- JWT includes tenant context
- All queries automatically scoped by tenant

### 2. AI-Powered Diagnosis
- **Qwen-VL-Max**: Multimodal image analysis for anorectal lesions
  - Detailed prompt covering disease identification, TCM syndrome differentiation, treatment recommendations
  - Supports: hemorrhoid, fissure, abscess, fistula, prolapse, eczema, condyloma, tongue
- **DeepSeek**: Text-based TCM syndrome differentiation
  - Eight principles, organ differentiation, qi-blood-fluid analysis
  - Generates: diagnosis, syndrome, treatment principle, prescriptions

### 3. Business Management
- **Patients**: Full CRUD with search
- **Consultations**: Medical records with AI analysis integration
- **Billing**: Charge items, bills, payments, revenue tracking
- **Inventory**: Medicine stock in/out, batch tracking, expiry alerts
- **Followup**: Scheduling, reminders, completion tracking

### 4. Knowledge Base
- **Herbs**: Anorectal TCM herbs database
- **Formulas**: Classical and modern prescriptions
- **Cases**: Clinical case studies
- **Prevention**: Disease-specific prevention guides

### 5. Statistics & Analytics
- Dashboard overview (patients, consultations, revenue, alerts)
- Trends analysis (daily consultations, daily revenue)
- Disease distribution
- Inventory alerts

## Database Models

### Core Tables
- `tenants` - Clinics/organizations
- `users` - Staff with roles (admin/doctor/assistant/cashier)
- `patients` - Patient demographics and medical history
- `consultations` - Visit records with symptoms, diagnosis, treatment
- `prescriptions` - TCM prescriptions linked to consultations
- `followups` - Scheduled followup visits
- `images` - Clinical images with AI analysis results stored in JSONB

### Business Tables
- `charge_items` - Fee schedule
- `bills`, `bill_items`, `bill_payments` - Billing system
- `daily_revenue` - Aggregated daily statistics
- `medicines`, `medicine_batches` - Inventory
- `stock_transactions`, `stock_alerts` - Stock movements and warnings

### Knowledge Base Tables
- `anorectal_herbs` - TCM herbs for anorectal diseases
- `anorectal_formulas` - Classical and modern formulas
- `anorectal_cases` - Case studies
- `prevention_guides` - Prevention and postop care

All tables use UUID primary keys and have proper indexes on tenant_id and frequently queried fields.

## API Endpoints

### Authentication `/api/v1/auth`
- POST `/login` - User login
- POST `/register` - New tenant registration (creates both tenant and admin user)
- GET `/me` - Current user profile
- PUT `/me` - Update profile
- POST `/change-password` - Password change

### Patients `/api/v1/patients`
- GET `/` - List with pagination, search by name/phone, filter by gender
- POST `/` - Create patient
- GET `/{id}` - Patient details
- PUT `/{id}` - Update patient
- DELETE `/{id}` - Delete patient

### Consultations `/api/v1/consultations`
- GET `/` - List with filters (patient, disease type, status)
- POST `/` - Create consultation
- GET `/{id}` - Consultation details
- PUT `/{id}` - Update consultation
- POST `/{id}/ai-diagnosis` - Trigger AI syndrome differentiation
- DELETE `/{id}` - Delete consultation

### Vision AI `/api/v1/vision`
- POST `/analyze-image` - Upload base64 image for AI analysis
- GET `/history/{patient_id}` - Patient image analysis history
- POST `/compare` - Compare before/after images

### Billing `/api/v1/billing`
- GET `/charge-items` - List charge items (with category filter)
- POST `/charge-items` - Create charge item
- PUT `/charge-items/{id}` - Update charge item
- GET `/bills` - List bills (with patient, status, date filters)
- GET `/bills/{id}` - Bill details with items and payments
- POST `/bills` - Create bill
- POST `/payments` - Record payment
- GET `/revenue` - Revenue statistics (with date range)

### Inventory `/api/v1/inventory`
- GET `/medicines` - List medicines (search, category, low_stock filter)
- POST `/medicines` - Add medicine
- GET `/medicines/{id}` - Medicine details
- PUT `/medicines/{id}` - Update medicine
- POST `/stock-in` - Record stock in (creates batch)
- POST `/stock-out` - Record stock out
- GET `/batches/{medicine_id}` - List batches for medicine
- GET `/alerts` - Stock alerts (low stock, expiring, expired)
- PUT `/alerts/{id}/resolve` - Resolve alert
- GET `/stats` - Inventory statistics

### Knowledge Base `/api/v1/knowledge`
- GET `/herbs` - List herbs (search, category filter)
- GET `/herbs/{id}` - Herb details
- GET `/formulas` - List formulas (search, syndrome, disease, type filters)
- GET `/formulas/{id}` - Formula details
- GET `/formulas/recommend/{disease_type}` - Recommend formulas
- GET `/cases` - List cases (disease type, search)
- GET `/cases/{id}` - Case details
- GET `/prevention` - Prevention guides (disease type filter)
- GET `/prevention/{id}` - Guide details

### Statistics `/api/v1/stats`
- GET `/overview` - Dashboard overview (patients, consultations, revenue, inventory alerts)
- GET `/trends` - Trends for past N days

### Uploads `/api/v1/uploads`
- POST `/image` - Upload image file
- POST `/document` - Upload document (PDF, Word)
- GET `/files/{tenant_id}/{filename}` - Download file
- DELETE `/files/{tenant_id}/{filename}` - Delete file

### Followup `/api/v1/followup`
- GET `/` - List followups (filters: patient, status, upcoming)
- POST `/` - Schedule followup
- GET `/today` - Today's followups
- GET `/overdue` - Overdue followups
- GET `/{id}` - Followup details
- PUT `/{id}` - Update followup
- POST `/{id}/complete` - Mark as completed
- POST `/{id}/cancel` - Cancel followup

## Environment Variables

Required configuration in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/zhilou_db

# AI Services
DEEPSEEK_API_KEY=sk-xxxxx
QWEN_API_KEY=sk-xxxxx

# JWT
SECRET_KEY=your-secret-key

# Optional
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
SENTRY_DSN=
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `.env` file

3. Run development server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Initialize demo data:
   ```bash
   python scripts/init_demo.py
   python scripts/seed_knowledge.py
   python scripts/seed_charge_items.py
   ```

5. Access API docs: http://localhost:8000/docs

## Docker Deployment

```bash
docker build -t zhilou-backend .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e DEEPSEEK_API_KEY=... \
  -e QWEN_API_KEY=... \
  zhilou-backend
```

## Notes

- All async/await patterns properly implemented
- UUID primary keys throughout
- Multi-tenant isolation on all queries
- Comprehensive error handling with HTTP status codes
- Chinese language responses for clinical context
- AI prompts optimized for anorectal TCM diagnosis
- No placeholders - all code is complete and working
