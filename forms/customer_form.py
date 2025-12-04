"""
Customer form with CSRF protection
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

class CustomerForm(FlaskForm):
    """Form for creating and editing customers"""
    
    # Type
    customer_type = SelectField('Kundetype', choices=[
        ('dealer', 'Forhandler'),
        ('private', 'Privat')
    ], validators=[DataRequired(message='Kundetype er påkrævet')])
    
    # Basic information
    name = StringField('Navn', validators=[
        DataRequired(message='Navn er påkrævet'),
        Length(max=120)
    ])
    
    contact_person = StringField('Kontaktperson', validators=[
        Optional(),
        Length(max=120)
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email er påkrævet'),
        Email(message='Indtast en gyldig email'),
        Length(max=120)
    ])
    
    phone = StringField('Telefon', validators=[
        DataRequired(message='Telefon er påkrævet'),
        Length(max=20)
    ])
    
    secondary_phone = StringField('Sekundær telefon', validators=[
        Optional(),
        Length(max=20)
    ])
    
    # Business information (for dealers)
    cvr = StringField('CVR nummer', validators=[
        Optional(),
        Length(max=20)
    ])
    
    company_name = StringField('Firmanavn', validators=[
        Optional(),
        Length(max=120)
    ])
    
    # Address
    address = StringField('Adresse', validators=[
        Optional(),
        Length(max=200)
    ])
    
    postal_code = StringField('Postnummer', validators=[
        Optional(),
        Length(max=10)
    ])
    
    city = StringField('By', validators=[
        Optional(),
        Length(max=100)
    ])
    
    country = StringField('Land', validators=[
        Optional(),
        Length(max=50)
    ], default='Danmark')
    
    # Financial (for dealers)
    credit_limit = DecimalField('Kreditgrænse', validators=[
        Optional(),
        NumberRange(min=0, message='Kreditgrænse skal være positiv')
    ], places=2, default=0)
    
    payment_terms = IntegerField('Betalingsbetingelser (dage)', validators=[
        Optional(),
        NumberRange(min=0, max=365, message='Indtast gyldige betalingsbetingelser')
    ], default=14)
    
    discount_percentage = DecimalField('Rabatprocent', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Rabat skal være mellem 0 og 100')
    ], places=2, default=0)
    
    # Status
    is_active = BooleanField('Aktiv', default=True)
    
    rating = SelectField('Vurdering', choices=[
        ('', 'Ingen vurdering'),
        ('1', '⭐ (1)'),
        ('2', '⭐⭐ (2)'),
        ('3', '⭐⭐⭐ (3)'),
        ('4', '⭐⭐⭐⭐ (4)'),
        ('5', '⭐⭐⭐⭐⭐ (5)')
    ], validators=[Optional()], coerce=lambda x: int(x) if x else None)
    
    # Notes
    notes = TextAreaField('Noter', validators=[Optional()])
    preferences = TextAreaField('Præferencer', validators=[Optional()])
