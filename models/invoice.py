"""
Invoice model for managing invoices
"""
from datetime import datetime, timedelta
from database import db

class Invoice(db.Model):
    """Invoice model for billing customers"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys (optional - can create invoice without linking to sale/customer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, index=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True, index=True)
    # Issuing company selection
    issuing_company_id = db.Column(db.Integer, db.ForeignKey('company_settings.id'), nullable=True, index=True)
    
    # Manual customer info (if not linked to customer)
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.String(200))
    customer_postal_code = db.Column(db.String(10))
    customer_city = db.Column(db.String(100))
    customer_country = db.Column(db.String(50), default='Danmark')
    customer_cvr = db.Column(db.String(20))
    
    # Invoice details
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    payment_terms = db.Column(db.Integer, default=14)  # Days
    
    # Status
    status = db.Column(db.String(30), nullable=False, default='draft', index=True)
    # draft, sent, paid, overdue, cancelled
    
    # Payment
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    
    # Amounts
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    vat_rate = db.Column(db.Numeric(5, 2), default=25)  # Percentage
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    # Currency (ISO code): DKK, EUR, SEK
    purchase_currency = db.Column(db.String(3), nullable=False, default='DKK', index=True)
    
    # Notes
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('Customer', backref=db.backref('invoices', lazy='dynamic'))
    sale = db.relationship('Sale', backref=db.backref('invoices', lazy='dynamic'))
    line_items = db.relationship('InvoiceLineItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    issuing_company = db.relationship('CompanySettings', backref=db.backref('invoices', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        super(Invoice, self).__init__(**kwargs)
        if not self.due_date and self.invoice_date:
            self.due_date = self.invoice_date + timedelta(days=self.payment_terms)
    
    def calculate_totals(self):
        """Calculate subtotal, VAT, and total from line items"""
        self.subtotal = sum(item.total() for item in self.line_items)
        self.vat_amount = float(self.subtotal) * (float(self.vat_rate) / 100)
        self.total_amount = float(self.subtotal) + self.vat_amount
    
    def get_customer_name(self):
        """Get customer name from linked customer or manual entry"""
        if self.customer:
            return self.customer.name
        return self.customer_name or 'Ukendt kunde'
    
    def get_customer_address_lines(self):
        """Get formatted customer address"""
        if self.customer:
            return [
                self.customer.address or '',
                f"{self.customer.postal_code or ''} {self.customer.city or ''}".strip(),
                self.customer.country or 'Danmark'
            ]
        return [
            self.customer_address or '',
            f"{self.customer_postal_code or ''} {self.customer_city or ''}".strip(),
            self.customer_country or 'Danmark'
        ]
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status == 'paid':
            return False
        return datetime.utcnow().date() > self.due_date
    
    def days_until_due(self):
        """Calculate days until due date"""
        delta = self.due_date - datetime.utcnow().date()
        return delta.days
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} ({self.status})>'


class InvoiceLineItem(db.Model):
    """Invoice line items"""
    __tablename__ = 'invoice_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False, index=True)
    
    # Line item details
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    # Ordering
    sort_order = db.Column(db.Integer, default=0)
    
    # Optional link to car
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=True)
    
    def total(self):
        """Calculate line item total after discount"""
        subtotal = float(self.quantity) * float(self.unit_price)
        discount = subtotal * (float(self.discount_percentage) / 100)
        return subtotal - discount
    
    def __repr__(self):
        return f'<InvoiceLineItem {self.description[:30]}>'
