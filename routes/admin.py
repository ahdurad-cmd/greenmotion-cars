"""
Admin routes for system administration
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User
from models.company_settings import CompanySettings
from database import db
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Du har ikke tilladelse til at få adgang til denne side', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=request.form.get('username')).first():
                flash('Brugernavn er allerede i brug', 'danger')
                return redirect(url_for('admin.add_user'))
            
            if User.query.filter_by(email=request.form.get('email')).first():
                flash('Email er allerede i brug', 'danger')
                return redirect(url_for('admin.add_user'))
            
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                full_name=request.form.get('full_name'),
                role=request.form.get('role', 'user'),
                is_active=request.form.get('is_active', 'on') == 'on'
            )
            
            user.set_password(request.form.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Bruger {user.username} oprettet succesfuldt', 'success')
            return redirect(url_for('admin.list_users'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved oprettelse af bruger: {str(e)}', 'danger')
    
    return render_template('admin/add_user.html')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Check if email is being changed and is unique
            new_email = request.form.get('email')
            if new_email != user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Email er allerede i brug', 'danger')
                    return redirect(url_for('admin.edit_user', user_id=user_id))
                user.email = new_email
            
            user.full_name = request.form.get('full_name')
            user.role = request.form.get('role')
            user.is_active = request.form.get('is_active', 'off') == 'on'
            
            # Only update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            
            flash('Bruger opdateret succesfuldt', 'success')
            return redirect(url_for('admin.list_users'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved opdatering: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    if user_id == current_user.id:
        flash('Du kan ikke slette din egen bruger', 'danger')
        return redirect(url_for('admin.list_users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Bruger slettet succesfuldt', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_users'))

@bp.route('/company-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def company_settings():
    """Edit company settings for invoices - now shows all companies"""
    companies = CompanySettings.query.order_by(CompanySettings.company_name).all()
    
    return render_template('admin/company_settings.html', companies=companies)

@bp.route('/companies')
@login_required
@admin_required
def list_companies():
    """List all companies"""
    companies = CompanySettings.query.order_by(CompanySettings.company_name).all()
    return render_template('admin/companies.html', companies=companies)

@bp.route('/companies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_company():
    """Add new company"""
    if request.method == 'POST':
        try:
            company = CompanySettings(
                company_name=request.form.get('company_name'),
                company_address=request.form.get('company_address'),
                company_postal_code=request.form.get('company_postal_code'),
                company_city=request.form.get('company_city'),
                company_country=request.form.get('company_country', 'Danmark'),
                company_phone=request.form.get('company_phone'),
                company_email=request.form.get('company_email'),
                company_cvr=request.form.get('company_cvr'),
                company_vat=request.form.get('company_vat'),
                bank_name=request.form.get('bank_name'),
                bank_iban=request.form.get('bank_iban'),
                bank_swift=request.form.get('bank_swift'),
                account_holder=request.form.get('account_holder')
            )
            db.session.add(company)
            db.session.commit()
            flash(f'Firma {company.company_name} oprettet', 'success')
            return redirect(url_for('admin.list_companies'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl: {str(e)}', 'danger')
    
    return render_template('admin/company_form.html', company=None)

@bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(company_id):
    """Edit company"""
    company = CompanySettings.query.get_or_404(company_id)
    
    if request.method == 'POST':
        try:
            company.company_name = request.form.get('company_name')
            company.company_address = request.form.get('company_address')
            company.company_postal_code = request.form.get('company_postal_code')
            company.company_city = request.form.get('company_city')
            company.company_country = request.form.get('company_country', 'Danmark')
            company.company_phone = request.form.get('company_phone')
            company.company_email = request.form.get('company_email')
            company.company_cvr = request.form.get('company_cvr')
            company.company_vat = request.form.get('company_vat')
            company.bank_name = request.form.get('bank_name')
            company.bank_iban = request.form.get('bank_iban')
            company.bank_swift = request.form.get('bank_swift')
            company.account_holder = request.form.get('account_holder')
            
            db.session.commit()
            flash(f'Firma {company.company_name} opdateret', 'success')
            return redirect(url_for('admin.list_companies'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl: {str(e)}', 'danger')
    
    return render_template('admin/company_form.html', company=company)

@bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    """Delete company"""
    company = CompanySettings.query.get_or_404(company_id)
    
    try:
        company_name = company.company_name
        db.session.delete(company)
        db.session.commit()
        flash(f'Firma {company_name} slettet', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_companies'))

