"""
Import logistics tracking routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models.logistics import LogisticsEntry
from models.car import Car
from database import db
from datetime import datetime

bp = Blueprint('logistics', __name__, url_prefix='/logistics')

@bp.route('/')
@login_required
def list_logistics():
    """List all logistics entries"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = LogisticsEntry.query
    
    if status:
        query = query.filter_by(status=status)
    
    entries = query.order_by(LogisticsEntry.estimated_arrival).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('logistics/list.html', entries=entries)

@bp.route('/<int:logistics_id>')
@login_required
def view_logistics(logistics_id):
    """View logistics entry details"""
    entry = LogisticsEntry.query.get_or_404(logistics_id)
    return render_template('logistics/view.html', entry=entry)

@bp.route('/add/<int:car_id>', methods=['GET', 'POST'])
@login_required
def add_logistics(car_id):
    """Add logistics entry for a car"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            entry = LogisticsEntry(
                car_id=car_id,
                transport_company=request.form.get('transport_company'),
                tracking_number=request.form.get('tracking_number'),
                pickup_date=datetime.strptime(request.form.get('pickup_date'), '%Y-%m-%d').date() if request.form.get('pickup_date') else None,
                estimated_arrival=datetime.strptime(request.form.get('estimated_arrival'), '%Y-%m-%d').date() if request.form.get('estimated_arrival') else None,
                origin_location=request.form.get('origin_location'),
                destination_location=request.form.get('destination_location'),
                status=request.form.get('status', 'scheduled'),
                shipping_cost=float(request.form.get('shipping_cost', 0)) if request.form.get('shipping_cost') else None,
                insurance_cost=float(request.form.get('insurance_cost', 0)) if request.form.get('insurance_cost') else None,
                notes=request.form.get('notes')
            )
            
            # Update car status
            if entry.status == 'picked_up' or entry.status == 'in_transit':
                car.status = 'in_transit'
            
            db.session.add(entry)
            db.session.commit()
            
            flash('Logistik information tilføjet', 'success')
            return redirect(url_for('logistics.view_logistics', logistics_id=entry.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl: {str(e)}', 'danger')
    
    return render_template('logistics/add.html', car=car)

@bp.route('/<int:logistics_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_logistics(logistics_id):
    """Edit logistics entry"""
    entry = LogisticsEntry.query.get_or_404(logistics_id)
    
    if request.method == 'POST':
        try:
            entry.transport_company = request.form.get('transport_company')
            entry.tracking_number = request.form.get('tracking_number')
            
            if request.form.get('pickup_date'):
                entry.pickup_date = datetime.strptime(request.form.get('pickup_date'), '%Y-%m-%d').date()
            if request.form.get('estimated_arrival'):
                entry.estimated_arrival = datetime.strptime(request.form.get('estimated_arrival'), '%Y-%m-%d').date()
            if request.form.get('actual_arrival'):
                entry.actual_arrival = datetime.strptime(request.form.get('actual_arrival'), '%Y-%m-%d').date()
            
            entry.origin_location = request.form.get('origin_location')
            entry.destination_location = request.form.get('destination_location')
            entry.current_location = request.form.get('current_location')
            entry.status = request.form.get('status')
            
            entry.shipping_documents = request.form.get('shipping_documents') == 'on'
            entry.customs_cleared = request.form.get('customs_cleared') == 'on'
            entry.inspection_completed = request.form.get('inspection_completed') == 'on'
            
            if request.form.get('shipping_cost'):
                entry.shipping_cost = float(request.form.get('shipping_cost'))
            if request.form.get('insurance_cost'):
                entry.insurance_cost = float(request.form.get('insurance_cost'))
            
            entry.notes = request.form.get('notes')
            
            # Update car status based on logistics status
            if entry.status == 'picked_up' or entry.status == 'in_transit':
                entry.car.status = 'in_transit'
            elif entry.status == 'arrived':
                entry.car.status = 'arrived'
            elif entry.status == 'delivered':
                entry.car.status = 'in_preparation'
            
            db.session.commit()
            
            flash('Logistik information opdateret', 'success')
            return redirect(url_for('logistics.view_logistics', logistics_id=entry.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl: {str(e)}', 'danger')
    
    return render_template('logistics/edit.html', entry=entry)

@bp.route('/tracking')
@login_required
def tracking_overview():
    """Overview of all shipments in transit"""
    in_transit = LogisticsEntry.query.filter(
        LogisticsEntry.status.in_(['picked_up', 'in_transit', 'customs'])
    ).order_by(LogisticsEntry.estimated_arrival).all()
    
    # Separate delayed shipments
    delayed = [entry for entry in in_transit if entry.is_delayed()]
    on_time = [entry for entry in in_transit if not entry.is_delayed()]
    
    return render_template('logistics/tracking.html', 
                         delayed=delayed,
                         on_time=on_time)
