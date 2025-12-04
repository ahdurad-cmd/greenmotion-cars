# GreenMotion Cars CRM - Quick Start Guide

## 🚀 Getting Started with New Features

### 1. Environment Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Copy environment file
cp .env.example .env

# Edit with your settings
nano .env
```

### 2. Configure Email (Optional but Recommended)

Edit `.env` file:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@greenmotioncars.dk
ADMIN_EMAIL=admin@greenmotioncars.dk
```

**Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate
4. Copy password to `.env`

### 3. Database Migrations

```bash
# Migrations are already initialized!
# To create a migration after model changes:
flask db migrate -m "Your migration message"

# Apply migrations:
flask db upgrade

# Check migration status:
flask db current
```

### 4. Start the Application

```bash
# Development mode (default)
python app.py

# Or use Flask CLI
flask run
```

**Access:**
- Main app: http://localhost:5001
- Health check: http://localhost:5001/health

### 5. Check Logs

```bash
# View application logs
tail -f logs/app.log

# View error logs only
tail -f logs/error.log
```

---

## 🎯 Using New Features

### Send Welcome Email

```python
from utils.email_utils import send_welcome_email
from models.customer import Customer

# When creating a new customer
customer = Customer(name="Test Customer", email="test@example.com")
db.session.add(customer)
db.session.commit()

# Send welcome email
send_welcome_email(customer)
```

### Cache Expensive Queries

```python
from utils.cache_utils import cached
from models.car import Car

@cached(timeout=300)  # Cache for 5 minutes
def get_available_cars():
    return Car.query.filter_by(status='available').all()
```

### Use Forms with CSRF Protection

```python
from forms import CarForm

@app.route('/cars/add', methods=['GET', 'POST'])
@login_required
def add_car():
    form = CarForm()
    
    if form.validate_on_submit():
        car = Car(
            vin=form.vin.data,
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            # ... other fields
        )
        db.session.add(car)
        db.session.commit()
        flash('Bil tilføjet!', 'success')
        return redirect(url_for('cars.list_cars'))
    
    return render_template('car_form.html', form=form)
```

**In template:**
```html
<form method="POST">
    {{ form.hidden_tag() }}  <!-- CSRF token -->
    
    {{ form.vin.label }}
    {{ form.vin(class="form-control") }}
    {% if form.vin.errors %}
        <div class="text-danger">{{ form.vin.errors[0] }}</div>
    {% endif %}
    
    <button type="submit">Gem</button>
</form>
```

---

## 📊 Health Monitoring

Check system health:
```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-29T10:30:00"
}
```

---

## 🔍 Troubleshooting

### Issue: ImportError for new packages

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Database migration errors

**Solution:**
```bash
# Reset migrations (CAUTION: Development only!)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Issue: Email not sending

**Check:**
1. SMTP settings in `.env`
2. App-specific password for Gmail
3. Firewall not blocking port 587
4. Check logs: `tail -f logs/error.log`

### Issue: Cache not working

**For Redis (Production):**
```bash
# Install Redis
brew install redis  # Mac
sudo apt install redis  # Ubuntu

# Start Redis
redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
```

**For Development:**
```env
# Use simple cache (no Redis needed)
CACHE_TYPE=simple
```

---

## 📁 File Structure

```
GreenMotion Cars/
├── app.py                    # Main application (ENHANCED)
├── config.py                 # Configuration (NEW)
├── logging_config.py         # Logging setup (NEW)
├── requirements.txt          # Updated dependencies
├── .env.example             # Environment template (UPDATED)
├── .env                     # Your settings (create this)
│
├── forms/                   # NEW - WTForms
│   ├── __init__.py
│   ├── car_form.py
│   ├── customer_form.py
│   └── sale_form.py
│
├── utils/                   # Enhanced utilities
│   ├── email_utils.py       # NEW - Email functions
│   └── cache_utils.py       # NEW - Caching decorators
│
├── templates/
│   ├── email/              # NEW - Email templates
│   │   ├── welcome.html
│   │   ├── sale_notification.html
│   │   └── reminder.html
│   └── errors/             # NEW - Error pages
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
│
├── migrations/             # Flask-Migrate (auto-generated)
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── logs/                   # Auto-created for logs
│   ├── app.log
│   └── error.log
│
└── docs/
    ├── IMPROVEMENTS_IMPLEMENTED.md
    └── QUICK_START.md       # This file
```

---

## 🎓 Learning Resources

### Database Migrations
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

### WTForms
- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
- [WTForms Documentation](https://wtforms.readthedocs.io/)

### Flask-Mail
- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)

### Caching
- [Flask-Caching Documentation](https://flask-caching.readthedocs.io/)

---

## ✅ Verification Checklist

Run these checks to verify everything is working:

- [ ] Application starts without errors: `python app.py`
- [ ] Health check responds: `curl http://localhost:5001/health`
- [ ] Logs are being created in `logs/` directory
- [ ] Database migrations initialized: `flask db current`
- [ ] Forms load with CSRF tokens
- [ ] Email configuration is set (if using emails)
- [ ] All routes are accessible
- [ ] Error pages display correctly (try `/nonexistent`)

---

## 🆘 Support

If you encounter issues:

1. **Check logs**: `tail -f logs/error.log`
2. **Verify environment**: Check `.env` file
3. **Test database**: Run health check endpoint
4. **Dependencies**: `pip list` to verify installations
5. **Python version**: Ensure Python 3.10+

---

## 🎉 You're Ready!

Your GreenMotion Cars CRM is now equipped with:
- ✅ Professional configuration management
- ✅ Structured logging
- ✅ Database version control
- ✅ Email notifications
- ✅ CSRF protection
- ✅ Caching system
- ✅ Error handling

**Happy coding!** 🚗💚

---

**Last Updated**: 2025-01-29  
**Version**: 2.0.0
