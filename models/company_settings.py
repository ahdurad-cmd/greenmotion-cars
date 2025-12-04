"""
Company settings model for invoice configuration
"""
from datetime import datetime
from database import db

class CompanySettings(db.Model):
    """Company information for invoices"""
    __tablename__ = 'company_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Company info
    company_name = db.Column(db.String(200), nullable=False, default='GreenMotion Cars')
    company_address = db.Column(db.String(200))
    company_postal_code = db.Column(db.String(10))
    company_city = db.Column(db.String(100))
    company_country = db.Column(db.String(50), default='Danmark')
    
    # Contact info
    company_phone = db.Column(db.String(20))
    company_email = db.Column(db.String(120))
    company_website = db.Column(db.String(200))
    
    # Business registration
    company_cvr = db.Column(db.String(20))
    company_vat = db.Column(db.String(20))
    
    # Bank details
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    bank_reg_number = db.Column(db.String(20))
    bank_swift = db.Column(db.String(20))
    bank_iban = db.Column(db.String(50))
    account_holder = db.Column(db.String(200))
    payment_note = db.Column(db.String(200))
    
    # Invoice settings
    default_payment_terms = db.Column(db.Integer, default=14)
    default_vat_rate = db.Column(db.Numeric(5, 2), default=25)
    invoice_footer_text = db.Column(db.Text)
    
    # Logo (optional - can be added later)
    logo_path = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_settings():
        """Get company settings, create default if not exists"""
        settings = CompanySettings.query.first()
        if not settings:
            settings = CompanySettings(
                company_name='GreenMotion Cars',
                company_country='Danmark',
                default_payment_terms=14,
                default_vat_rate=25
            )
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def __repr__(self):
        return f'<CompanySettings {self.company_name}>'
