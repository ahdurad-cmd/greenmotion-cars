# GreenMotion Cars CRM System

Et komplet CRM system til bilimportforretning med håndtering af lager, kunder, salg og logistik.

## Features

### 🚗 Billagerstyring
- Detaljeret bilregistrering med VIN, mærke, model, årgang
- Import fra Sverige og Tyskland
- Omkostningssporing (indkøb, transport, told, klargøring)
- Statussporing: Bestilt → Undervejs → Ankommet → Klar → Solgt
- Prisstyrking for forhandlere og private

### 👥 Kundestyring
- Separate kategorier for forhandlere og privatkunder
- CVR-registrering for forhandlere
- Kreditgrænser og betalingsvilkår
- Kommunikationslog
- Købshistorik

### 💰 Salgspipeline
- Lead-håndtering
- Tilbudsgenerering
- Kontraktstyring
- Betalingssporing
- Fortjenstberegning

### 🚚 Import & Logistik
- Transportsporing
- Toldstatus
- Ankomstsopfølgning
- Leverandørstyring

### 📊 Rapporter & Analytics
- Real-time dashboard
- Lageroversigt
- Salgsrapporter
- Kunderapporter
- Fortjenstanalyse

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.0
- **Database**: SQLite (dev), PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5, JavaScript
- **Icons**: Bootstrap Icons

## Installation

### 1. Klon eller download projektet

```bash
cd "Greenmotion Cars"
```

### 2. Opret virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # På macOS/Linux
# eller
venv\Scripts\activate  # På Windows
```

### 3. Installer dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialiser database

```bash
python init_db.py
```

Dette opretter databasen og følgende brugere:
- **Admin**: username=`admin`, password=`admin123`
- **Sales**: username=`sales`, password=`sales123`

### 5. Kør applikationen

```bash
python app.py
```

Åbn browseren på: **http://localhost:5001**

## Login Credentials

Efter initialisering kan du logge ind med:
- **Admin**: username=`admin`, password=`admin123`
- **Sales**: username=`sales`, password=`sales123`

## Projekt Struktur

```
Greenmotion Cars/
├── app.py                 # Hovedapplikation
├── config.py              # Konfiguration
├── init_db.py            # Database initialisering
├── requirements.txt      # Python dependencies
├── models/               # Database modeller
│   ├── user.py
│   ├── car.py
│   ├── customer.py
│   ├── sale.py
│   ├── logistics.py
│   └── document.py
├── routes/               # Route handlers
│   ├── auth.py
│   ├── cars.py
│   ├── customers.py
│   ├── sales.py
│   ├── logistics.py
│   ├── reports.py
│   └── admin.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── cars/
│   ├── customers/
│   ├── sales/
│   ├── logistics/
│   ├── reports/
│   └── admin/
└── static/              # Statiske filer
    ├── css/
    ├── js/
    └── uploads/
```

## Brugerroller

- **Admin**: Fuld adgang til alle funktioner inklusive brugeradministration
- **Manager**: Adgang til alle forretningsfunktioner
- **Sales**: Adgang til salg, kunder, og biler
- **User**: Begrænset læseadgang

## Konfiguration

Kopier `.env.example` til `.env` og tilpas indstillingerne:

```bash
cp .env.example .env
```

Rediger `.env`:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///greenmotion.db
# eller til PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/greenmotion
```

## Produktion

For produktionsbrug:

1. Skift til PostgreSQL database
2. Sæt `FLASK_ENV=production`
3. Generer stærk SECRET_KEY
4. Brug WSGI server (f.eks. Gunicorn)
5. Konfigurer HTTPS

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Support

For spørgsmål eller problemer, kontakt systemadministrator.

## Licens

Proprietær software til GreenMotion Cars.

---

**GreenMotion Cars CRM System** © 2025
