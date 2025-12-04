"""
Invoice routes for managing invoices
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from functools import wraps
from database import db
from models.invoice import Invoice, InvoiceLineItem
from models.customer import Customer
from models.sale import Sale
from models.car import Car
from models.company_settings import CompanySettings

bp = Blueprint('invoices', __name__, url_prefix='/invoices')

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Kun administratorer har adgang til fakturaer', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_invoice_number():
    """Generate unique invoice number"""
    today = datetime.utcnow()
    prefix = f"INV-{today.year}-"
    
    # Find last invoice number for this year
    last_invoice = Invoice.query.filter(
        Invoice.invoice_number.like(f"{prefix}%")
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract number and increment
        last_num = int(last_invoice.invoice_number.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"

@bp.route('/')
@login_required
@admin_required
def list_invoices():
    """List all invoices"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Invoice.query
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(
            db.or_(
                Invoice.invoice_number.ilike(f'%{search}%'),
                Invoice.customer_name.ilike(f'%{search}%')
            )
        )
    
    # Pagination
    invoices = query.order_by(Invoice.invoice_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calculate statistics
    stats = {
        'total': Invoice.query.count(),
        'draft': Invoice.query.filter_by(status='draft').count(),
        'sent': Invoice.query.filter_by(status='sent').count(),
        'paid': Invoice.query.filter_by(status='paid').count(),
        'overdue': Invoice.query.filter(
            Invoice.status.in_(['sent']),
            Invoice.due_date < datetime.utcnow().date()
        ).count()
    }
    
    return render_template('invoices/list.html', 
                         invoices=invoices, 
                         stats=stats,
                         status_filter=status_filter,
                         search=search)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_invoice():
    """Create new invoice"""
    if request.method == 'POST':
        try:
            # Get default settings
            settings = CompanySettings.get_settings()
            
            # Determine invoice number (allow manual override)
            manual_number = (request.form.get('invoice_number') or '').strip()
            inv_number = manual_number if manual_number else generate_invoice_number()

            # Create invoice with initial zero values
            invoice = Invoice(
                invoice_number=inv_number,
                customer_id=request.form.get('customer_id') or None,
                customer_name=request.form.get('customer_name'),
                customer_email=request.form.get('customer_email'),
                customer_phone=request.form.get('customer_phone'),
                customer_address=request.form.get('customer_address'),
                customer_cvr=request.form.get('customer_cvr'),
                invoice_date=datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d').date(),
                payment_terms=int(request.form.get('payment_terms', settings.default_payment_terms)),
                vat_rate=float(request.form.get('vat_rate', settings.default_vat_rate)),
                purchase_currency=request.form.get('purchase_currency', 'DKK'),
                notes=request.form.get('notes'),
                internal_notes=request.form.get('internal_notes'),
                status='draft',
                subtotal=0,
                vat_amount=0,
                total_amount=0,
                issuing_company_id=(request.form.get('issuing_company_id') or None)
            )
            
            # Calculate due date
            invoice.due_date = invoice.invoice_date + timedelta(days=invoice.payment_terms)
            
            db.session.add(invoice)
            db.session.flush()  # Get invoice ID
            
            # Add line items
            descriptions = request.form.getlist('line_description[]')
            quantities = request.form.getlist('line_quantity[]')
            unit_prices = request.form.getlist('line_unit_price[]')
            discounts = request.form.getlist('line_discount[]')
            
            for i, desc in enumerate(descriptions):
                if desc.strip():
                    # Parse values, allow empty for text lines
                    qty = quantities[i].strip() if i < len(quantities) else ''
                    price = unit_prices[i].strip() if i < len(unit_prices) else ''
                    disc = discounts[i].strip() if i < len(discounts) else '0'
                    
                    line_item = InvoiceLineItem(
                        invoice_id=invoice.id,
                        description=desc,
                        quantity=float(qty) if qty else 0,
                        unit_price=float(price) if price else 0,
                        discount_percentage=float(disc) if disc else 0,
                        sort_order=i
                    )
                    db.session.add(line_item)
            
            # Calculate totals from line items
            db.session.flush()
            invoice.calculate_totals()
            
            db.session.commit()
            flash(f'Faktura {invoice.invoice_number} oprettet!', 'success')
            return redirect(url_for('invoices.invoice_detail', id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved oprettelse af faktura: {str(e)}', 'danger')
    
    # GET request
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    settings = CompanySettings.get_settings()
    companies = CompanySettings.query.order_by(CompanySettings.company_name).all()
    # Determine default company (prefer one named like 'GreenMotion')
    default_company_id = None
    for c in companies:
        if c.company_name and 'greenmotion' in c.company_name.lower():
            default_company_id = c.id
            break
    today = datetime.utcnow().date()
    
    return render_template('invoices/create.html', 
                         customers=customers,
                         settings=settings,
                         companies=companies,
                         default_company_id=default_company_id,
                         today=today)

@bp.route('/<int:id>')
@login_required
@admin_required
def invoice_detail(id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(id)
    line_items = invoice.line_items.order_by(InvoiceLineItem.sort_order).all()
    
    return render_template('invoices/detail.html', 
                         invoice=invoice,
                         line_items=line_items)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_invoice(id):
    """Edit invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status == 'paid':
        flash('Kan ikke redigere en betalt faktura', 'warning')
        return redirect(url_for('invoices.invoice_detail', id=id))
    
    if request.method == 'POST':
        try:
            # Update invoice
            manual_number = (request.form.get('invoice_number') or '').strip()
            if manual_number:
                invoice.invoice_number = manual_number
            invoice.customer_id = request.form.get('customer_id') or None
            invoice.customer_name = request.form.get('customer_name')
            invoice.customer_email = request.form.get('customer_email')
            invoice.customer_phone = request.form.get('customer_phone')
            invoice.customer_address = request.form.get('customer_address')
            invoice.customer_postal_code = request.form.get('customer_postal_code')
            invoice.customer_city = request.form.get('customer_city')
            invoice.customer_country = request.form.get('customer_country', 'Danmark')
            invoice.customer_cvr = request.form.get('customer_cvr')
            invoice.invoice_date = datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d').date()
            invoice.payment_terms = int(request.form.get('payment_terms', 14))
            invoice.vat_rate = float(request.form.get('vat_rate', 25))
            invoice.purchase_currency = request.form.get('purchase_currency', invoice.purchase_currency or 'DKK')
            invoice.notes = request.form.get('notes')
            invoice.internal_notes = request.form.get('internal_notes')
            invoice.issuing_company_id = request.form.get('issuing_company_id') or None
            
            # Recalculate due date
            invoice.due_date = invoice.invoice_date + timedelta(days=invoice.payment_terms)
            
            # Delete existing line items
            InvoiceLineItem.query.filter_by(invoice_id=invoice.id).delete()
            
            # Add new line items
            descriptions = request.form.getlist('line_description[]')
            quantities = request.form.getlist('line_quantity[]')
            unit_prices = request.form.getlist('line_unit_price[]')
            discounts = request.form.getlist('line_discount[]')
            
            for i, desc in enumerate(descriptions):
                if desc.strip():
                    # Parse values, allow empty for text lines
                    qty = quantities[i].strip() if i < len(quantities) else ''
                    price = unit_prices[i].strip() if i < len(unit_prices) else ''
                    disc = discounts[i].strip() if i < len(discounts) else '0'
                    
                    line_item = InvoiceLineItem(
                        invoice_id=invoice.id,
                        description=desc,
                        quantity=float(qty) if qty else 0,
                        unit_price=float(price) if price else 0,
                        discount_percentage=float(disc) if disc else 0,
                        sort_order=i
                    )
                    db.session.add(line_item)
            
            # Calculate totals
            db.session.flush()
            invoice.calculate_totals()
            
            db.session.commit()
            flash(f'Faktura {invoice.invoice_number} opdateret!', 'success')
            return redirect(url_for('invoices.invoice_detail', id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved opdatering: {str(e)}', 'danger')
    
    # GET request
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    line_items = invoice.line_items.order_by(InvoiceLineItem.sort_order).all()
    companies = CompanySettings.query.order_by(CompanySettings.company_name).all()
    
    return render_template('invoices/edit.html', 
                         invoice=invoice,
                         line_items=line_items,
                         customers=customers,
                         companies=companies)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_invoice(id):
    """Delete invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status == 'paid':
        flash('Kan ikke slette en betalt faktura', 'danger')
        return redirect(url_for('invoices.invoice_detail', id=id))
    
    try:
        invoice_number = invoice.invoice_number
        db.session.delete(invoice)
        db.session.commit()
        flash(f'Faktura {invoice_number} slettet', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('invoices.list_invoices'))

@bp.route('/<int:id>/status/<status>', methods=['POST'])
@login_required
@admin_required
def update_status(id, status):
    """Update invoice status"""
    invoice = Invoice.query.get_or_404(id)
    
    valid_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
    if status not in valid_statuses:
        flash('Ugyldig status', 'danger')
        return redirect(url_for('invoices.invoice_detail', id=id))
    
    invoice.status = status
    
    if status == 'sent' and not invoice.sent_at:
        invoice.sent_at = datetime.utcnow()
    elif status == 'paid':
        invoice.payment_date = datetime.utcnow().date()
    
    db.session.commit()
    flash(f'Status opdateret til: {status}', 'success')
    
    return redirect(url_for('invoices.invoice_detail', id=id))

@bp.route('/<int:id>/print')
@login_required
@admin_required
def print_invoice(id):
    """Print-friendly invoice view"""
    invoice = Invoice.query.get_or_404(id)
    line_items = invoice.line_items.order_by(InvoiceLineItem.sort_order).all()
    settings = CompanySettings.get_settings()
    selected_company = None
    if invoice.issuing_company_id:
        selected_company = CompanySettings.query.get(invoice.issuing_company_id)
    
    return render_template('invoices/print.html', 
                         invoice=invoice,
                         line_items=line_items,
                         settings=settings,
                         selected_company=selected_company)

@bp.route('/api/customer/<int:customer_id>')
@login_required
@admin_required
def get_customer_info(customer_id):
    """API endpoint to get customer info for autofill"""
    customer = Customer.query.get_or_404(customer_id)
    
    return jsonify({
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address,
        'postal_code': customer.postal_code,
        'city': customer.city,
        'country': customer.country,
        'cvr': customer.cvr,
        'payment_terms': customer.payment_terms if customer.is_dealer() else 14
    })
