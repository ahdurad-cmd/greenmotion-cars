"""
Sale form with CSRF protection
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, DateTimeField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class SaleForm(FlaskForm):
    """Form for creating and editing sales"""
    
    # Sale number (auto-generated usually, but allow manual input for imports)
    sale_number = StringField('Salgsnummer', validators=[
        DataRequired(message='Salgsnummer er påkrævet'),
        Length(max=50)
    ])
    
    # Foreign keys (these would be SelectFields populated with actual data)
    car_id = SelectField('Bil', validators=[
        DataRequired(message='Bil er påkrævet')
    ], coerce=int)
    
    customer_id = SelectField('Kunde', validators=[
        DataRequired(message='Kunde er påkrævet')
    ], coerce=int)
    
    salesperson_id = SelectField('Sælger', validators=[
        DataRequired(message='Sælger er påkrævet')
    ], coerce=int)
    
    # Status
    status = SelectField('Status', choices=[
        ('lead', 'Lead'),
        ('offer_sent', 'Tilbud sendt'),
        ('negotiation', 'Forhandling'),
        ('contract_signed', 'Kontrakt underskrevet'),
        ('payment_pending', 'Afventer betaling'),
        ('completed', 'Gennemført'),
        ('cancelled', 'Annulleret')
    ], validators=[DataRequired(message='Status er påkrævet')])
    
    # Pricing
    list_price = DecimalField('Listepris', validators=[
        DataRequired(message='Listepris er påkrævet'),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    offered_price = DecimalField('Tilbudt pris', validators=[
        Optional(),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    discount_amount = DecimalField('Rabatbeløb', validators=[
        Optional(),
        NumberRange(min=0, message='Rabat skal være positiv')
    ], places=2, default=0)
    
    final_price = DecimalField('Endelig pris', validators=[
        Optional(),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    # Payment
    payment_method = SelectField('Betalingsmetode', choices=[
        ('', 'Vælg betalingsmetode'),
        ('bank_transfer', 'Bankoverførsel'),
        ('financing', 'Finansiering'),
        ('cash', 'Kontant'),
        ('leasing', 'Leasing')
    ], validators=[Optional()])
    
    payment_status = SelectField('Betalingsstatus', choices=[
        ('pending', 'Afventer'),
        ('partial', 'Delvis betalt'),
        ('paid', 'Betalt')
    ], validators=[DataRequired(message='Betalingsstatus er påkrævet')])
    
    amount_paid = DecimalField('Betalt beløb', validators=[
        Optional(),
        NumberRange(min=0, message='Beløb skal være positivt')
    ], places=2, default=0)
    
    # Dates
    lead_date = DateTimeField('Lead dato', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    offer_date = DateTimeField('Tilbudsdato', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    contract_date = DateTimeField('Kontraktdato', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    payment_date = DateTimeField('Betalingsdato', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    delivery_date = DateTimeField('Leveringsdato', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    
    # Details
    notes = TextAreaField('Noter', validators=[Optional()])
    terms_conditions = TextAreaField('Vilkår og betingelser', validators=[Optional()])
