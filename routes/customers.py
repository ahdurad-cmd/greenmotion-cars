"""
Customer management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.customer import Customer
from models.document import Communication
from database import db
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('customers', __name__, url_prefix='/customers')

@bp.route('/')
@login_required
def list_customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    customer_type = request.args.get('type', '')
    search = request.args.get('search', '')
    
    query = Customer.query
    
    # Apply filters
    if customer_type:
        query = query.filter_by(customer_type=customer_type)
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.company_name.ilike(f'%{search}%'),
                Customer.cvr.ilike(f'%{search}%')
            )
        )
    
    customers = query.order_by(Customer.name).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('customers/list.html', customers=customers)

@bp.route('/<int:customer_id>')
@login_required
def view_customer(customer_id):
    """View customer details"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Get customer communications
    communications = customer.communications.order_by(Communication.created_at.desc()).limit(10).all()
    
    # Get customer sales
    sales = customer.sales.order_by('created_at desc').limit(10).all()
    
    return render_template('customers/view.html', 
                         customer=customer,
                         communications=communications,
                         sales=sales)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    """Add new customer"""
    if request.method == 'POST':
        try:
            customer = Customer(
                customer_type=request.form.get('customer_type'),
                name=request.form.get('name'),
                contact_person=request.form.get('contact_person'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                secondary_phone=request.form.get('secondary_phone'),
                cvr=request.form.get('cvr') if request.form.get('cvr') else None,
                company_name=request.form.get('company_name'),
                address=request.form.get('address'),
                postal_code=request.form.get('postal_code'),
                city=request.form.get('city'),
                country=request.form.get('country', 'Danmark'),
                credit_limit=float(request.form.get('credit_limit', 0)) if request.form.get('credit_limit') else 0,
                payment_terms=int(request.form.get('payment_terms', 14)),
                discount_percentage=float(request.form.get('discount_percentage', 0)) if request.form.get('discount_percentage') else 0,
                notes=request.form.get('notes'),
                preferences=request.form.get('preferences')
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash(f'Kunde {customer.name} tilføjet succesfuldt', 'success')
            return redirect(url_for('customers.view_customer', customer_id=customer.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved tilføjelse af kunde: {str(e)}', 'danger')
    
    return render_template('customers/add.html')

@bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """Edit customer details"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        try:
            customer.customer_type = request.form.get('customer_type')
            customer.name = request.form.get('name')
            customer.contact_person = request.form.get('contact_person')
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.secondary_phone = request.form.get('secondary_phone')
            customer.cvr = request.form.get('cvr') if request.form.get('cvr') else None
            customer.company_name = request.form.get('company_name')
            customer.address = request.form.get('address')
            customer.postal_code = request.form.get('postal_code')
            customer.city = request.form.get('city')
            customer.country = request.form.get('country')
            
            if request.form.get('credit_limit'):
                customer.credit_limit = float(request.form.get('credit_limit'))
            customer.payment_terms = int(request.form.get('payment_terms', 14))
            if request.form.get('discount_percentage'):
                customer.discount_percentage = float(request.form.get('discount_percentage'))
            
            customer.notes = request.form.get('notes')
            customer.preferences = request.form.get('preferences')
            customer.rating = int(request.form.get('rating')) if request.form.get('rating') else None
            
            db.session.commit()
            
            flash('Kunde opdateret succesfuldt', 'success')
            return redirect(url_for('customers.view_customer', customer_id=customer.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved opdatering: {str(e)}', 'danger')
    
    return render_template('customers/edit.html', customer=customer)

@bp.route('/<int:customer_id>/add-communication', methods=['POST'])
@login_required
def add_communication(customer_id):
    """Add communication log entry"""
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        communication = Communication(
            customer_id=customer_id,
            user_id=current_user.id,
            communication_type=request.form.get('communication_type'),
            subject=request.form.get('subject'),
            content=request.form.get('content'),
            direction=request.form.get('direction', 'outbound')
        )
        
        customer.last_contact = datetime.utcnow()
        
        db.session.add(communication)
        db.session.commit()
        
        flash('Kommunikation tilføjet', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl: {str(e)}', 'danger')
    
    return redirect(url_for('customers.view_customer', customer_id=customer_id))

@bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Delete customer"""
    if not current_user.is_admin():
        flash('Du har ikke tilladelse til at slette kunder', 'danger')
        return redirect(url_for('customers.list_customers'))
    
    customer = Customer.query.get_or_404(customer_id)
    
    if customer.sales.count() > 0:
        flash('Kan ikke slette kunde med eksisterende salg', 'danger')
        return redirect(url_for('customers.view_customer', customer_id=customer_id))
    
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Kunde slettet succesfuldt', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('customers.list_customers'))
