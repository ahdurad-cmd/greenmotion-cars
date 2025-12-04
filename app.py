"""
GreenMotion Cars CRM System
Main application entry point
"""
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import login_required
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache
from datetime import datetime
import os

# Import configuration and logging
from config import config
from logging_config import setup_logging

# Initialize extensions
mail = Mail()
cache = Cache()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    app.logger.info(f'GreenMotion Cars CRM starting in {config_name} mode')
    @app.route('/dashboard')
    def dashboard():
        try:
            from models.car import Car
            from sqlalchemy import desc
            recent = Car.query.order_by(desc(getattr(Car, 'updated_at', getattr(Car, 'id')))).limit(10).all()
            kpis = {
                'inventory_count': Car.query.count(),
                'pipeline_open': Car.query.filter(getattr(Car, 'stage', '') != 'Sold').count() if hasattr(Car, 'stage') else recent and len(recent) or 0
            }
        except Exception:
            recent = []
            kpis = {'inventory_count': 0, 'pipeline_open': 0}
        return render_template('dashboard.html', kpis=kpis, recent=recent)

    @app.route('/search')
    def search():
        query = request.args.get('q', '').strip()
        results = {
            'cars': [],
            'customers': [],
            'docs': []
        }
        try:
            from models.car import Car
            if query:
                results['cars'] = Car.query.filter(
                    (Car.make.ilike(f"%{query}%")) |
                    (Car.model.ilike(f"%{query}%")) |
                    (Car.vin.ilike(f"%{query}%"))
                ).limit(25).all()
        except Exception:
            pass
        return render_template('search.html', q=query, results=results)
    # Setup logging
    setup_logging(app)
    app.logger.info(f'GreenMotion Cars CRM starting in {config_name} mode')
    
    # Initialize extensions
    from database import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Import blueprints
    from routes import auth, cars, customers, sales, logistics, reports, admin, calendar, invoices
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(cars.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(sales.bp)
    app.register_blueprint(logistics.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(calendar.calendar_bp)
    app.register_blueprint(invoices.bp)
    
    @app.route('/')
    @login_required
    def index():
        """Dashboard homepage"""
        from models.car import Car
        from models.customer import Customer
        from models.sale import Sale
        from models.user import User
    
        # Get statistics
        total_cars = Car.query.count()
        available_cars = Car.query.filter_by(status='available').count()
        total_customers = Customer.query.count()
        active_sales = Sale.query.filter(Sale.status.in_(['lead', 'offer_sent', 'negotiation', 'contract_signed', 'payment_pending'])).count()
    
        # Get recent cars for dashboard
        recent_cars = Car.query.order_by(Car.updated_at.desc()).limit(10).all()
    
        # Get recent sales
        recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
        
        # Get users for sidebar
        users = User.query.order_by(User.full_name).limit(5).all()
    
        return render_template('dashboard.html',
                             total_cars=total_cars,
                             available_cars=available_cars,
                             total_customers=total_customers,
                             active_sales=active_sales,
                             recent=recent_cars,
                             recent_sales=recent_sales,
                             users=users)
    
    @app.context_processor
    def inject_now():
        """Make datetime available in templates"""
        return {'now': datetime.utcnow()}
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            from database import db
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    return app

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        app.logger.warning(f'Page not found: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        app.logger.warning(f'Forbidden access attempt: {request.url}')
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        from database import db
        db.session.rollback()
        app.logger.error(f'Server error: {str(error)}', exc_info=True)
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        from database import db
        db.session.rollback()
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        
        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': str(error) if app.debug else 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from database import db
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
