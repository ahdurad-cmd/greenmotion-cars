"""
Database initialization script
Creates initial admin user and sample data
"""
from app import create_app
from database import db
from models.user import User
from models.car import Car
from models.customer import Customer
from datetime import datetime, date

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin user exists
        if not User.query.filter_by(username='admin').first():
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@greenmotion.dk',
                full_name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create a regular user
            user = User(
                username='sales',
                email='sales@greenmotion.dk',
                full_name='Sales User',
                role='sales',
                is_active=True
            )
            user.set_password('sales123')
            db.session.add(user)
            
            db.session.commit()
            print("✓ Users created successfully")
            print("  Admin: username='admin', password='admin123'")
            print("  Sales: username='sales', password='sales123'")
        else:
            print("Admin user already exists")
        
        # Add sample data if database is empty
        if Car.query.count() == 0:
            print("\nAdding sample data...")
            
            # Sample cars
            sample_cars = [
                {
                    'vin': 'WBA3B3G55DNP69139',
                    'make': 'BMW',
                    'model': '320d',
                    'year': 2020,
                    'color': 'Sort',
                    'mileage': 85000,
                    'fuel_type': 'Diesel',
                    'transmission': 'Automatisk',
                    'import_country': 'Tyskland',
                    'supplier': 'Deutsche Auto GmbH',
                    'import_date': date(2024, 11, 15),
                    'purchase_price': 185000,
                    'transport_cost': 8500,
                    'customs_cost': 12000,
                    'preparation_cost': 5000,
                    'dealer_price': 235000,
                    'private_price': 249000,
                    'status': 'available'
                },
                {
                    'vin': 'YV1CZ59H7X2123456',
                    'make': 'Volvo',
                    'model': 'V60',
                    'year': 2019,
                    'color': 'Hvid',
                    'mileage': 95000,
                    'fuel_type': 'Diesel',
                    'transmission': 'Automatisk',
                    'import_country': 'Sverige',
                    'supplier': 'Svensk Bil AB',
                    'import_date': date(2024, 12, 1),
                    'purchase_price': 165000,
                    'transport_cost': 6000,
                    'customs_cost': 9500,
                    'preparation_cost': 4500,
                    'dealer_price': 205000,
                    'private_price': 219000,
                    'status': 'available'
                },
                {
                    'vin': 'WVWZZZ3CZHE123456',
                    'make': 'Volkswagen',
                    'model': 'Passat',
                    'year': 2021,
                    'color': 'Grå',
                    'mileage': 45000,
                    'fuel_type': 'Diesel',
                    'transmission': 'Automatisk',
                    'import_country': 'Tyskland',
                    'supplier': 'Auto Import Deutschland',
                    'import_date': date(2024, 11, 20),
                    'purchase_price': 195000,
                    'transport_cost': 8000,
                    'customs_cost': 11000,
                    'preparation_cost': 4000,
                    'dealer_price': 245000,
                    'private_price': 259000,
                    'status': 'in_preparation'
                }
            ]
            
            for car_data in sample_cars:
                car = Car(**car_data)
                db.session.add(car)
            
            # Sample customers
            sample_customers = [
                {
                    'customer_type': 'dealer',
                    'name': 'Biler A/S',
                    'company_name': 'Biler A/S',
                    'cvr': '12345678',
                    'contact_person': 'Peter Jensen',
                    'email': 'peter@bileras.dk',
                    'phone': '+45 12345678',
                    'address': 'Autovej 10',
                    'postal_code': '2000',
                    'city': 'Frederiksberg',
                    'credit_limit': 500000,
                    'payment_terms': 30,
                    'discount_percentage': 5
                },
                {
                    'customer_type': 'private',
                    'name': 'Lars Nielsen',
                    'email': 'lars@example.com',
                    'phone': '+45 87654321',
                    'address': 'Hjemvej 5',
                    'postal_code': '2100',
                    'city': 'København Ø'
                }
            ]
            
            for customer_data in sample_customers:
                customer = Customer(**customer_data)
                db.session.add(customer)
            
            db.session.commit()
            print("✓ Sample data added successfully")
        
        print("\n✓ Database initialization complete!")
        print("\nYou can now run the application with: flask run")

if __name__ == '__main__':
    init_database()
