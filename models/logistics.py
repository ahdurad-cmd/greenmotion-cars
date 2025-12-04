"""
Logistics model for tracking import and transport
"""
from datetime import datetime
from database import db

class LogisticsEntry(db.Model):
    """Logistics tracking for car imports"""
    __tablename__ = 'logistics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False, index=True)
    
    # Transport information
    transport_company = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100), index=True)
    
    # Dates
    pickup_date = db.Column(db.Date)
    estimated_arrival = db.Column(db.Date, index=True)
    actual_arrival = db.Column(db.Date)
    
    # Location
    origin_location = db.Column(db.String(200))
    destination_location = db.Column(db.String(200))
    current_location = db.Column(db.String(200))
    
    # Status
    status = db.Column(db.String(30), nullable=False, default='scheduled', index=True)
    # scheduled, picked_up, in_transit, customs, arrived, delivered
    
    # Documents
    shipping_documents = db.Column(db.Boolean, default=False)
    customs_cleared = db.Column(db.Boolean, default=False)
    inspection_completed = db.Column(db.Boolean, default=False)
    
    # Costs
    shipping_cost = db.Column(db.Numeric(10, 2))
    insurance_cost = db.Column(db.Numeric(10, 2))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_delayed(self):
        """Check if shipment is delayed"""
        if self.estimated_arrival and not self.actual_arrival:
            return datetime.now().date() > self.estimated_arrival
        return False
    
    def days_in_transit(self):
        """Calculate days in transit"""
        if self.pickup_date:
            end_date = self.actual_arrival or datetime.now().date()
            return (end_date - self.pickup_date).days
        return None
    
    def __repr__(self):
        return f'<LogisticsEntry {self.tracking_number} ({self.status})>'
