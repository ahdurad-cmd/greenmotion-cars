"""
Sales pipeline and transaction routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.sale import Sale
from models.car import Car
from models.customer import Customer
from database import db
from datetime import datetime

bp = Blueprint('sales', __name__, url_prefix='/sales')

def generate_sale_number():
    """Generate unique sale number"""
    last_sale = Sale.query.order_by(Sale.id.desc()).first()
    if last_sale:
        last_num = int(last_sale.sale_number.split('-')[1])
        return f'SALE-{last_num + 1:06d}'
    return 'SALE-000001'

@bp.route('/')
@login_required
def list_sales():
    """List all sales"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Sale.query
    
    if status:
        query = query.filter_by(status=status)
    
    sales = query.order_by(Sale.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('sales/list.html', sales=sales)

@bp.route('/<int:sale_id>')
@login_required
def view_sale(sale_id):
    """View sale details"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/view.html', sale=sale)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    """Create new sale"""
    if request.method == 'POST':
        try:
            car_id = int(request.form.get('car_id'))
            customer_id = int(request.form.get('customer_id'))
            
            car = Car.query.get_or_404(car_id)
            customer = Customer.query.get_or_404(customer_id)
            
            # Determine price based on customer type
            if customer.is_dealer() and car.dealer_price:
                list_price = car.dealer_price
            elif customer.is_private() and car.private_price:
                list_price = car.private_price
            else:
                list_price = car.selling_price or car.total_cost() * 1.2
            
            sale = Sale(
                sale_number=generate_sale_number(),
                car_id=car_id,
                customer_id=customer_id,
                salesperson_id=current_user.id,
                list_price=list_price,
                offered_price=float(request.form.get('offered_price')) if request.form.get('offered_price') else list_price,
                status=request.form.get('status', 'lead'),
                notes=request.form.get('notes')
            )
            
            # Mark car as reserved if sale is progressing
            if sale.status in ['offer_sent', 'negotiation', 'contract_signed']:
                car.status = 'reserved'
            
            db.session.add(sale)
            db.session.commit()
            
            flash(f'Salg {sale.sale_number} oprettet succesfuldt', 'success')
            return redirect(url_for('sales.view_sale', sale_id=sale.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved oprettelse af salg: {str(e)}', 'danger')
    
    # Get available cars and customers for form
    cars = Car.query.filter(Car.status.in_(['available', 'reserved'])).all()
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    
    return render_template('sales/add.html', cars=cars, customers=customers)

@bp.route('/<int:sale_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sale(sale_id):
    """Edit sale details"""
    sale = Sale.query.get_or_404(sale_id)
    
    if request.method == 'POST':
        try:
            old_status = sale.status
            
            sale.status = request.form.get('status')
            
            if request.form.get('offered_price'):
                sale.offered_price = float(request.form.get('offered_price'))
            
            if request.form.get('discount_amount'):
                sale.discount_amount = float(request.form.get('discount_amount'))
            
            if request.form.get('final_price'):
                sale.final_price = float(request.form.get('final_price'))
            
            sale.payment_method = request.form.get('payment_method')
            sale.payment_status = request.form.get('payment_status')
            
            if request.form.get('amount_paid'):
                sale.amount_paid = float(request.form.get('amount_paid'))
            
            sale.notes = request.form.get('notes')
            sale.terms_conditions = request.form.get('terms_conditions')
            
            # Update dates based on status
            if sale.status == 'offer_sent' and not sale.offer_date:
                sale.offer_date = datetime.utcnow()
            elif sale.status == 'contract_signed' and not sale.contract_date:
                sale.contract_date = datetime.utcnow()
            elif sale.status == 'completed' and not sale.completed_date:
                sale.completed_date = datetime.utcnow()
                sale.car.status = 'sold'
                sale.car.sold_date = datetime.utcnow()
            
            # Update car status
            if sale.status in ['offer_sent', 'negotiation', 'contract_signed', 'payment_pending']:
                if sale.car.status == 'available':
                    sale.car.status = 'reserved'
            elif sale.status == 'cancelled':
                if sale.car.status == 'reserved':
                    sale.car.status = 'available'
            
            db.session.commit()
            
            flash('Salg opdateret succesfuldt', 'success')
            return redirect(url_for('sales.view_sale', sale_id=sale.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved opdatering: {str(e)}', 'danger')
    
    return render_template('sales/edit.html', sale=sale)

@bp.route('/<int:sale_id>/payment', methods=['POST'])
@login_required
def record_payment(sale_id):
    """Record payment for sale"""
    sale = Sale.query.get_or_404(sale_id)
    
    try:
        amount = float(request.form.get('amount'))
        
        sale.amount_paid = float(sale.amount_paid or 0) + amount
        
        if sale.is_fully_paid():
            sale.payment_status = 'paid'
            sale.payment_date = datetime.utcnow()
            
            if sale.status == 'payment_pending':
                sale.status = 'completed'
                sale.completed_date = datetime.utcnow()
                sale.car.status = 'sold'
                sale.car.sold_date = datetime.utcnow()
        else:
            sale.payment_status = 'partial'
        
        db.session.commit()
        
        flash(f'Betaling på {amount:,.2f} DKK registreret', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved registrering af betaling: {str(e)}', 'danger')
    
    return redirect(url_for('sales.view_sale', sale_id=sale_id))

@bp.route('/pipeline')
@login_required
def pipeline():
    """Sales pipeline view"""
    leads = Sale.query.filter_by(status='lead').order_by(Sale.created_at.desc()).all()
    offers = Sale.query.filter_by(status='offer_sent').order_by(Sale.offer_date.desc()).all()
    negotiations = Sale.query.filter_by(status='negotiation').order_by(Sale.created_at.desc()).all()
    contracts = Sale.query.filter_by(status='contract_signed').order_by(Sale.contract_date.desc()).all()
    pending = Sale.query.filter_by(status='payment_pending').order_by(Sale.created_at.desc()).all()
    
    return render_template('sales/pipeline.html',
                         leads=leads,
                         offers=offers,
                         negotiations=negotiations,
                         contracts=contracts,
                         pending=pending)

@bp.route('/pipeline/update', methods=['POST'])
@login_required
def update_pipeline_status():
    """Update sale status from pipeline drag-and-drop"""
    try:
        data = request.get_json()
        sale_id = data.get('sale_id')
        new_status = data.get('status')
        
        sale = Sale.query.get_or_404(sale_id)
        
        # Validate status transition if needed
        # For now, allow any transition
        
        old_status = sale.status
        sale.status = new_status
        
        # Update dates based on status
        if new_status == 'offer_sent' and not sale.offer_date:
            sale.offer_date = datetime.utcnow()
        elif new_status == 'contract_signed' and not sale.contract_date:
            sale.contract_date = datetime.utcnow()
        elif new_status == 'completed' and not sale.completed_date:
            sale.completed_date = datetime.utcnow()
            sale.car.status = 'sold'
            sale.car.sold_date = datetime.utcnow()
            
        # Update car status
        if new_status in ['offer_sent', 'negotiation', 'contract_signed', 'payment_pending']:
            if sale.car.status == 'available':
                sale.car.status = 'reserved'
        elif new_status == 'cancelled':
            if sale.car.status == 'reserved':
                sale.car.status = 'available'
                
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
