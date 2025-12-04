"""
Document model for file management
"""
from datetime import datetime
from database import db

class Document(db.Model):
    """Document storage and management"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys (optional - document can belong to car or sale)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), index=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), index=True)
    
    # Document information
    name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False, index=True)
    # invoice, contract, import_docs, registration, inspection, photo, other
    
    # File information
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(100))
    
    # Metadata
    description = db.Column(db.Text)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_by = db.relationship('User', backref='uploaded_documents')
    
    def __repr__(self):
        return f'<Document {self.name} ({self.document_type})>'


class Communication(db.Model):
    """Communication log for customer interactions"""
    __tablename__ = 'communications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), index=True)
    
    # Communication details
    communication_type = db.Column(db.String(30), nullable=False, index=True)
    # email, phone, meeting, note
    
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    
    # Metadata
    direction = db.Column(db.String(20))  # inbound, outbound
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='communications')
    
    def __repr__(self):
        return f'<Communication {self.communication_type} - {self.subject}>'
