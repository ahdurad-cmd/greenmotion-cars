"""
Customer model for dealer and private customer management
"""
from datetime import datetime
from database import db

class Customer(db.Model):
    """Customer model for dealers and private buyers"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type
    customer_type = db.Column(db.String(20), nullable=False, index=True)  # dealer, private
    
    # Basic information
    name = db.Column(db.String(120), nullable=False, index=True)
    contact_person = db.Column(db.String(120))  # For dealers
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    secondary_phone = db.Column(db.String(20))
    
    # Business information (for dealers)
    cvr = db.Column(db.String(20), unique=True, index=True)  # CVR nummer
    company_name = db.Column(db.String(120), index=True)
    
    # Address
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    country = db.Column(db.String(50), default='Danmark')
    
    # Financial
    credit_limit = db.Column(db.Numeric(10, 2), default=0)  # For dealers
    payment_terms = db.Column(db.Integer, default=14)  # Days (for dealers)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)  # For dealers
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Integer)  # 1-5 stars
    
    # Notes
    notes = db.Column(db.Text)
    preferences = db.Column(db.Text)  # Customer preferences (makes, models, etc.)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact = db.Column(db.DateTime)
    
    # Relationships
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')
    communications = db.relationship('Communication', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    def total_purchases(self):
        """Calculate total number of purchases"""
        return self.sales.filter_by(status='completed').count()
    
    def total_revenue(self):
        """Calculate total revenue from this customer"""
        total = 0
        for sale in self.sales.filter_by(status='completed').all():
            if sale.final_price:
                total += float(sale.final_price)
        return total
    
    def is_dealer(self):
        """Check if customer is a dealer"""
        return self.customer_type == 'dealer'
    
    def is_private(self):
        """Check if customer is a private buyer"""
        return self.customer_type == 'private'
    
    def __repr__(self):
        return f'<Customer {self.name} ({self.customer_type})>'
