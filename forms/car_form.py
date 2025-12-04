"""
Car form with CSRF protection
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class CarForm(FlaskForm):
    """Form for creating and editing cars"""
    
    # Basic information
    vin = StringField('VIN', validators=[
        DataRequired(message='VIN er påkrævet'),
        Length(max=17, message='VIN må være max 17 tegn')
    ])
    make = StringField('Mærke', validators=[
        DataRequired(message='Mærke er påkrævet'),
        Length(max=50)
    ])
    model = StringField('Model', validators=[
        DataRequired(message='Model er påkrævet'),
        Length(max=100)
    ])
    year = IntegerField('År', validators=[
        DataRequired(message='År er påkrævet'),
        NumberRange(min=1900, max=2100, message='Indtast et gyldigt år')
    ])
    color = StringField('Farve', validators=[Optional(), Length(max=50)])
    mileage = IntegerField('Kilometerstand', validators=[
        Optional(),
        NumberRange(min=0, message='Kilometerstand skal være positiv')
    ])
    
    fuel_type = SelectField('Brændstof', choices=[
        ('', 'Vælg brændstof'),
        ('Benzin', 'Benzin'),
        ('Diesel', 'Diesel'),
        ('Elektrisk', 'Elektrisk'),
        ('Hybrid', 'Hybrid'),
        ('Plugin Hybrid', 'Plugin Hybrid')
    ], validators=[Optional()])
    
    transmission = SelectField('Transmission', choices=[
        ('', 'Vælg transmission'),
        ('Manuel', 'Manuel'),
        ('Automatisk', 'Automatisk')
    ], validators=[Optional()])
    
    # Import information
    import_country = SelectField('Importland', choices=[
        ('', 'Vælg land'),
        ('Tyskland', 'Tyskland'),
        ('Sverige', 'Sverige'),
        ('Danmark', 'Danmark'),
        ('Norge', 'Norge'),
        ('Holland', 'Holland'),
        ('Belgien', 'Belgien')
    ], validators=[DataRequired(message='Importland er påkrævet')])
    
    supplier = StringField('Leverandør', validators=[Optional(), Length(max=100)])
    dealer_name = StringField('Forhandler', validators=[Optional(), Length(max=100)])
    dealer_location = StringField('Lokation', validators=[Optional(), Length(max=100)])
    distance_km = IntegerField('Afstand (km)', validators=[
        Optional(),
        NumberRange(min=0, message='Afstand skal være positiv')
    ])
    import_date = DateField('Importdato', validators=[Optional()], format='%Y-%m-%d')
    
    # Pricing
    purchase_price = DecimalField('Købspris', validators=[
        DataRequired(message='Købspris er påkrævet'),
        NumberRange(min=0, message='Købspris skal være positiv')
    ], places=2)
    
    purchase_currency = SelectField('Valuta', choices=[
        ('DKK', 'DKK'),
        ('EUR', 'EUR'),
        ('SEK', 'SEK')
    ], validators=[DataRequired(message='Valuta er påkrævet')])
    
    discount = DecimalField('Rabat', validators=[
        Optional(),
        NumberRange(min=0, message='Rabat skal være positiv')
    ], places=2, default=0)
    
    # Costs
    transport_cost = DecimalField('Transportomkostninger', validators=[
        Optional(),
        NumberRange(min=0, message='Omkostninger skal være positive')
    ], places=2, default=0)
    
    customs_cost = DecimalField('Toldafgifter', validators=[
        Optional(),
        NumberRange(min=0, message='Omkostninger skal være positive')
    ], places=2, default=0)
    
    preparation_cost = DecimalField('Klargøringsomkostninger', validators=[
        Optional(),
        NumberRange(min=0, message='Omkostninger skal være positive')
    ], places=2, default=0)
    
    other_costs = DecimalField('Andre omkostninger', validators=[
        Optional(),
        NumberRange(min=0, message='Omkostninger skal være positive')
    ], places=2, default=0)
    
    # Selling prices
    selling_price = DecimalField('Salgspris', validators=[
        Optional(),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    dealer_price = DecimalField('Forhandlerpris', validators=[
        Optional(),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    private_price = DecimalField('Privatpris', validators=[
        Optional(),
        NumberRange(min=0, message='Pris skal være positiv')
    ], places=2)
    
    # Status
    status = SelectField('Status', choices=[
        ('ordered', 'Bestilt'),
        ('in_transit', 'Under transport'),
        ('arrived', 'Ankommet'),
        ('in_preparation', 'Under klargøring'),
        ('available', 'Tilgængelig'),
        ('reserved', 'Reserveret'),
        ('sold', 'Solgt')
    ], validators=[DataRequired(message='Status er påkrævet')])
    
    # Details
    equipment = TextAreaField('Udstyr', validators=[Optional()])
    condition_notes = TextAreaField('Tilstandsnoter', validators=[Optional()])
    service_history = TextAreaField('Servicehistorik', validators=[Optional()])
    
    # Registration
    registration_number = StringField('Registreringsnummer', validators=[
        Optional(),
        Length(max=20)
    ])
    first_registration = DateField('Førstegangsregistrering', validators=[Optional()], format='%Y-%m-%d')
    inspection_date = DateField('Sidste syn', validators=[Optional()], format='%Y-%m-%d')
    inspection_valid_until = DateField('Syn gyldig til', validators=[Optional()], format='%Y-%m-%d')
