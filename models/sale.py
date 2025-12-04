"""
Sale model for managing sales pipeline and transactions
"""
from datetime import datetime
from database import db

class Sale(db.Model):
    """Sales pipeline and transaction model"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Status
    status = db.Column(db.String(30), nullable=False, default='lead', index=True)
    # lead, offer_sent, negotiation, contract_signed, payment_pending, completed, cancelled
    
    # Pricing
    list_price = db.Column(db.Numeric(10, 2), nullable=False)
    offered_price = db.Column(db.Numeric(10, 2))
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    final_price = db.Column(db.Numeric(10, 2))
    
    # Payment
    payment_method = db.Column(db.String(30))  # bank_transfer, financing, cash
    payment_status = db.Column(db.String(30), default='pending')  # pending, partial, paid
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    
    # Dates
    lead_date = db.Column(db.DateTime, default=datetime.utcnow)
    offer_date = db.Column(db.DateTime)
    contract_date = db.Column(db.DateTime)
    payment_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    # Details
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='sale', lazy='dynamic', cascade='all, delete-orphan')
    
    def remaining_payment(self):
        """Calculate remaining payment amount"""
        if self.final_price:
            return float(self.final_price) - float(self.amount_paid or 0)
        return 0
    
    def is_fully_paid(self):
        """Check if sale is fully paid"""
        return self.remaining_payment() <= 0
    
    def profit(self):
        """Calculate profit from this sale"""
        if self.final_price and hasattr(self, 'car') and self.car:
            return float(self.final_price) - self.car.total_cost()
        return None
    
    def __repr__(self):
        return f'<Sale {self.sale_number} ({self.status})>'
