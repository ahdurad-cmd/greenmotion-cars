"""
Authentication routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models.user import User
from database import db
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Ugyldigt brugernavn eller adgangskode', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Din konto er deaktiveret', 'danger')
            return redirect(url_for('auth.login'))
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        
        flash(f'Velkommen tilbage, {user.full_name}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Du er nu logget ud', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html')

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Nuværende adgangskode er forkert', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('Nye adgangskoder matcher ikke', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('Adgangskode skal være mindst 6 tegn', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Adgangskode opdateret succesfuldt', 'success')
    return redirect(url_for('auth.profile'))

@bp.route('/init-db')
def init_db():
    """Initialize database tables"""
    try:
        # Import all models to register them with SQLAlchemy
        from models.user import User
        from models.car import Car
        from models.customer import Customer
        from models.sale import Sale
        from models.logistics import Logistics
        from models.document import Document
        from models.invoice import Invoice, InvoiceItem
        from models.calendar_event import CalendarEvent
        from models.company_settings import CompanySettings
        
        db.create_all()
        return "Database tables created!"
    except Exception as e:
        import traceback
        return f"Error: {str(e)}\n\n{traceback.format_exc()}", 500

@bp.route('/setup-admin')
def setup_admin():
    """Create initial admin user - only works if no users exist"""
    try:
        # Import all models to register them with SQLAlchemy
        from models.user import User as UserModel
        from models.car import Car
        from models.customer import Customer
        from models.sale import Sale
        from models.logistics import Logistics
        from models.document import Document
        from models.invoice import Invoice, InvoiceItem
        from models.calendar_event import CalendarEvent
        from models.company_settings import CompanySettings
        
        # Ensure tables exist FIRST
        db.create_all()
        db.session.commit()
        
        # Now check if any user exists
        existing = UserModel.query.first()
        if existing is not None:
            return "Admin already exists", 403
        
        # Create admin user
        admin = UserModel(
            username='admin',
            email='ahdurad@gmail.com',
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('GreenMotion2025!')
        
        db.session.add(admin)
        db.session.commit()
        
        return "Admin user created! Username: admin, Password: GreenMotion2025!"
    except Exception as e:
        db.session.rollback()
        import traceback
        return f"Error: {str(e)}\n\n{traceback.format_exc()}", 500
