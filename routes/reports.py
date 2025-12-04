"""
Reports and analytics routes
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from models.car import Car
from models.customer import Customer
from models.sale import Sale
from database import db
from sqlalchemy import func, extract
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def dashboard():
    """Main reports dashboard"""
    return render_template('reports/dashboard.html')

@bp.route('/inventory')
@login_required
def inventory_report():
    """Inventory analysis report"""
    # Total inventory value
    total_value = db.session.query(func.sum(Car.purchase_price + 
                                            Car.transport_cost + 
                                            Car.customs_cost + 
                                            Car.preparation_cost + 
                                            Car.other_costs)).filter(Car.status != 'sold').scalar() or 0
    
    # Cars by status
    by_status = db.session.query(
        Car.status,
        func.count(Car.id).label('count')
    ).group_by(Car.status).all()
    
    # Cars by make
    by_make = db.session.query(
        Car.make,
        func.count(Car.id).label('count'),
        func.avg(Car.mileage).label('avg_mileage')
    ).group_by(Car.make).order_by(func.count(Car.id).desc()).all()
    
    # Cars by import country
    by_country = db.session.query(
        Car.import_country,
        func.count(Car.id).label('count')
    ).group_by(Car.import_country).all()
    
    # Average time to sell
    sold_cars = Car.query.filter(Car.status == 'sold', Car.sold_date.isnot(None)).all()
    avg_days_to_sell = 0
    if sold_cars:
        total_days = sum([(car.sold_date - car.created_at).days for car in sold_cars])
        avg_days_to_sell = total_days / len(sold_cars)
    
    return render_template('reports/inventory.html',
                         total_value=total_value,
                         by_status=by_status,
                         by_make=by_make,
                         by_country=by_country,
                         avg_days_to_sell=avg_days_to_sell)

@bp.route('/sales')
@login_required
def sales_report():
    """Sales performance report"""
    # Date range filter
    period = request.args.get('period', '30')  # days
    start_date = datetime.utcnow() - timedelta(days=int(period))
    
    # Total sales
    total_sales = Sale.query.filter(
        Sale.status == 'completed',
        Sale.completed_date >= start_date
    ).count()
    
    # Total revenue
    total_revenue = db.session.query(
        func.sum(Sale.final_price)
    ).filter(
        Sale.status == 'completed',
        Sale.completed_date >= start_date
    ).scalar() or 0
    
    # Total profit
    completed_sales = Sale.query.filter(
        Sale.status == 'completed',
        Sale.completed_date >= start_date
    ).all()
    
    total_profit = sum([sale.profit() or 0 for sale in completed_sales])
    
    # Average profit margin
    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Sales by salesperson
    by_salesperson = db.session.query(
        Sale.salesperson_id,
        func.count(Sale.id).label('count'),
        func.sum(Sale.final_price).label('revenue')
    ).filter(
        Sale.status == 'completed',
        Sale.completed_date >= start_date
    ).group_by(Sale.salesperson_id).all()
    
    # Sales pipeline
    pipeline_counts = db.session.query(
        Sale.status,
        func.count(Sale.id).label('count'),
        func.sum(Sale.offered_price).label('potential_value')
    ).filter(Sale.status != 'completed', Sale.status != 'cancelled').group_by(Sale.status).all()
    
    # Sales by month (last 12 months)
    monthly_sales = db.session.query(
        extract('year', Sale.completed_date).label('year'),
        extract('month', Sale.completed_date).label('month'),
        func.count(Sale.id).label('count'),
        func.sum(Sale.final_price).label('revenue')
    ).filter(
        Sale.status == 'completed',
        Sale.completed_date >= datetime.utcnow() - timedelta(days=365)
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return render_template('reports/sales.html',
                         total_sales=total_sales,
                         total_revenue=total_revenue,
                         total_profit=total_profit,
                         avg_margin=avg_margin,
                         by_salesperson=by_salesperson,
                         pipeline_counts=pipeline_counts,
                         monthly_sales=monthly_sales,
                         period=period)

@bp.route('/customers')
@login_required
def customer_report():
    """Customer analysis report"""
    # Total customers
    total_customers = Customer.query.count()
    dealers = Customer.query.filter_by(customer_type='dealer').count()
    private = Customer.query.filter_by(customer_type='private').count()
    
    # Top customers by revenue
    top_customers = db.session.query(
        Customer.id,
        Customer.name,
        Customer.customer_type,
        func.count(Sale.id).label('purchase_count'),
        func.sum(Sale.final_price).label('total_revenue')
    ).join(Sale).filter(
        Sale.status == 'completed'
    ).group_by(Customer.id, Customer.name, Customer.customer_type).order_by(
        func.sum(Sale.final_price).desc()
    ).limit(20).all()
    
    # Customer acquisition by month
    monthly_customers = db.session.query(
        extract('year', Customer.created_at).label('year'),
        extract('month', Customer.created_at).label('month'),
        func.count(Customer.id).label('count')
    ).filter(
        Customer.created_at >= datetime.utcnow() - timedelta(days=365)
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return render_template('reports/customers.html',
                         total_customers=total_customers,
                         dealers=dealers,
                         private=private,
                         top_customers=top_customers,
                         monthly_customers=monthly_customers)

@bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    # Current month
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    stats = {
        'inventory': {
            'total': Car.query.count(),
            'available': Car.query.filter_by(status='available').count(),
            'in_transit': Car.query.filter_by(status='in_transit').count(),
            'sold_this_month': Car.query.filter(Car.sold_date >= month_start).count()
        },
        'sales': {
            'active': Sale.query.filter(Sale.status.in_(['lead', 'offer_sent', 'negotiation', 'contract_signed', 'payment_pending'])).count(),
            'completed_this_month': Sale.query.filter(Sale.completed_date >= month_start).count(),
            'revenue_this_month': db.session.query(func.sum(Sale.final_price)).filter(Sale.completed_date >= month_start).scalar() or 0
        },
        'customers': {
            'total': Customer.query.count(),
            'new_this_month': Customer.query.filter(Customer.created_at >= month_start).count()
        }
    }
    
    return jsonify(stats)
