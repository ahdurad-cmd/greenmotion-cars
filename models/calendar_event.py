from database import db
from datetime import datetime

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    event_type = db.Column(db.String(50))  # meeting, delivery, inspection, note, other
    location = db.Column(db.String(200))
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='calendar_events')
    
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'))
    car = db.relationship('Car', backref='calendar_events')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', backref='calendar_events')
    
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    sale = db.relationship('Sale', backref='calendar_events')
    
    # Metadata
    is_all_day = db.Column(db.Boolean, default=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalendarEvent {self.title} on {self.event_date}>'
