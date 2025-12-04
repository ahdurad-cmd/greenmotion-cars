from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database import db
from models.calendar_event import CalendarEvent
from models.car import Car
from models.customer import Customer
from models.sale import Sale
from datetime import datetime, timedelta
from calendar import monthrange

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

@calendar_bp.route('/')
@login_required
def index():
    # Get current month or requested month
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get all events for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    events = CalendarEvent.query.filter(
        CalendarEvent.event_date >= start_date,
        CalendarEvent.event_date < end_date
    ).order_by(CalendarEvent.event_date, CalendarEvent.start_time).all()
    
    # Group events by date for efficient template lookup
    events_by_date = {}
    for e in events:
        key = e.event_date.isoformat()
        events_by_date.setdefault(key, []).append(e)
    
    # Generate calendar data
    first_day_weekday = start_date.weekday()  # 0 = Monday
    days_in_month = monthrange(year, month)[1]
    
    # Calculate previous and next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar/index.html',
                         events=events,
                         events_by_date=events_by_date,
                         year=year,
                         month=month,
                         first_day_weekday=first_day_weekday,
                         days_in_month=days_in_month,
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year,
                         today=datetime.now().date())

@calendar_bp.route('/day/<date>')
@login_required
def day_view(date):
    event_date = datetime.strptime(date, '%Y-%m-%d').date()
    events = CalendarEvent.query.filter_by(event_date=event_date).order_by(CalendarEvent.start_time).all()
    return render_template('calendar/day.html', date=event_date, events=events)

@calendar_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        
        event = CalendarEvent(
            title=request.form['title'],
            description=request.form.get('description'),
            event_date=event_date,
            event_type=request.form.get('event_type', 'note'),
            location=request.form.get('location'),
            user_id=current_user.id,
            is_all_day=bool(request.form.get('is_all_day'))
        )
        
        # Set times if not all day
        if not event.is_all_day:
            if request.form.get('start_time'):
                event.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
            if request.form.get('end_time'):
                event.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Link to car, customer, or sale if provided
        if request.form.get('car_id'):
            event.car_id = request.form['car_id']
        if request.form.get('customer_id'):
            event.customer_id = request.form['customer_id']
        if request.form.get('sale_id'):
            event.sale_id = request.form['sale_id']
        
        db.session.add(event)
        db.session.commit()
        
        flash('Begivenhed oprettet!', 'success')
        return redirect(url_for('calendar.index'))
    
    # Get data for dropdowns
    cars = Car.query.filter_by(status='available').all()
    customers = Customer.query.all()
    sales = Sale.query.filter(Sale.status.in_(['lead', 'offer_sent', 'negotiation'])).all()
    
    # Get date from query param if provided
    default_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    return render_template('calendar/add.html', 
                         cars=cars, 
                         customers=customers, 
                         sales=sales,
                         default_date=default_date)

@calendar_bp.route('/<int:event_id>')
@login_required
def view_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    return render_template('calendar/view.html', event=event)

@calendar_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    
    # Check permission
    if event.user_id != current_user.id and current_user.role not in ['admin', 'manager']:
        flash('Du har ikke tilladelse til at redigere denne begivenhed.', 'danger')
        return redirect(url_for('calendar.view_event', event_id=event_id))
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form.get('description')
        event.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        event.event_type = request.form.get('event_type', 'note')
        event.location = request.form.get('location')
        event.is_all_day = bool(request.form.get('is_all_day'))
        
        if not event.is_all_day:
            if request.form.get('start_time'):
                event.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
            if request.form.get('end_time'):
                event.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        else:
            event.start_time = None
            event.end_time = None
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Begivenhed opdateret!', 'success')
        return redirect(url_for('calendar.view_event', event_id=event_id))
    
    return render_template('calendar/edit.html', event=event)

@calendar_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    
    if event.user_id != current_user.id and current_user.role not in ['admin', 'manager']:
        flash('Du har ikke tilladelse til at slette denne begivenhed.', 'danger')
        return redirect(url_for('calendar.view_event', event_id=event_id))
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Begivenhed slettet!', 'success')
    return redirect(url_for('calendar.index'))

@calendar_bp.route('/api/events')
@login_required
def api_events():
    """API endpoint for getting events as JSON"""
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = CalendarEvent.query
    if start:
        query = query.filter(CalendarEvent.event_date >= datetime.strptime(start, '%Y-%m-%d').date())
    if end:
        query = query.filter(CalendarEvent.event_date <= datetime.strptime(end, '%Y-%m-%d').date())
    
    events = query.all()
    
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'date': e.event_date.isoformat(),
        'start_time': e.start_time.strftime('%H:%M') if e.start_time else None,
        'end_time': e.end_time.strftime('%H:%M') if e.end_time else None,
        'type': e.event_type,
        'user': e.user.username
    } for e in events])
