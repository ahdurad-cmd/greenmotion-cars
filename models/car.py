"""
Car model for vehicle inventory management
"""
from datetime import datetime
from database import db

class Car(db.Model):
    """Car inventory model"""
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False, index=True)
    
    # Basic information
    make = db.Column(db.String(50), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    color = db.Column(db.String(50))
    mileage = db.Column(db.Integer)
    fuel_type = db.Column(db.String(30))  # Benzin, Diesel, Elektrisk, Hybrid
    transmission = db.Column(db.String(30))  # Manuel, Automatisk
    
    # Import information
    import_country = db.Column(db.String(50), nullable=False, index=True)  # Sverige, Tyskland
    supplier = db.Column(db.String(100))
    dealer_name = db.Column(db.String(100))  # Forhandlerens navn
    dealer_location = db.Column(db.String(100))  # By hvor bilen ligger
    distance_km = db.Column(db.Integer)  # Afstand fra Aalborg i km
    import_date = db.Column(db.Date, index=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_currency = db.Column(db.String(3), default='DKK')
    discount = db.Column(db.Numeric(10, 2), default=0)  # Rabat på købspris
    
    # Costs
    transport_cost = db.Column(db.Numeric(10, 2), default=0)  # Transport
    transport_surcharge = db.Column(db.Numeric(10, 2), default=0)  # Transporttillæg
    customs_cost = db.Column(db.Numeric(10, 2), default=0)  # Grøn Vejafgift
    invoice_fee = db.Column(db.Numeric(10, 2), default=0)  # Fakturagebyr (i EUR)
    preparation_cost = db.Column(db.Numeric(10, 2), default=0)
    other_costs = db.Column(db.Numeric(10, 2), default=0)
    expedition_fee = db.Column(db.Numeric(10, 2), default=0)  # Ekspeditionsgebyr
    
    # Pricing
    selling_price = db.Column(db.Numeric(10, 2))
    dealer_price = db.Column(db.Numeric(10, 2))
    private_price = db.Column(db.Numeric(10, 2))
    
    # Status
    status = db.Column(db.String(30), nullable=False, default='ordered', index=True)
    # ordered, in_transit, arrived, in_preparation, available, reserved, sold
    
    # Details
    equipment = db.Column(db.Text)  # Udstyrsliste
    condition_notes = db.Column(db.Text)  # Tilstandsnoter
    service_history = db.Column(db.Text)
    
    # Registration
    registration_number = db.Column(db.String(20), unique=True, index=True)
    first_registration = db.Column(db.Date)
    inspection_date = db.Column(db.Date)
    inspection_valid_until = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_date = db.Column(db.DateTime)
    
    # Process Checklist (for timeline tracking)
    process_inquiry_done = db.Column(db.Boolean, default=False)
    process_inquiry_date = db.Column(db.DateTime)
    process_ordered_done = db.Column(db.Boolean, default=False)
    process_ordered_date = db.Column(db.DateTime)
    process_kaufvertrag_done = db.Column(db.Boolean, default=False)
    process_kaufvertrag_date = db.Column(db.DateTime)
    process_gelangen_done = db.Column(db.Boolean, default=False)
    process_gelangen_date = db.Column(db.DateTime)
    process_hjemtagelse_done = db.Column(db.Boolean, default=False)
    process_hjemtagelse_date = db.Column(db.DateTime)
    process_payment_done = db.Column(db.Boolean, default=False)
    process_payment_date = db.Column(db.DateTime)
    process_in_transit_done = db.Column(db.Boolean, default=False)
    process_in_transit_date = db.Column(db.DateTime)
    process_delivered_done = db.Column(db.Boolean, default=False)
    process_delivered_date = db.Column(db.DateTime)
    
    # Process Notes
    process_notes = db.Column(db.Text)  # Notes for process/status section
    
    # Market comparison (Bilbasen)
    market_price = db.Column(db.Numeric(10, 2))  # Markedspris fra Bilbasen
    market_price_updated = db.Column(db.DateTime)  # Hvornår blev prisen opdateret
    
    # Relationships
    documents = db.relationship('Document', backref='car', lazy='dynamic', cascade='all, delete-orphan')
    logistics = db.relationship('LogisticsEntry', backref='car', lazy='dynamic', cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='car', lazy='dynamic')
    
    def net_purchase_price(self):
        """Calculate net purchase price (excluding VAT) based on import country"""
        gross_price = float(self.purchase_price or 0)
        discount = float(self.discount or 0)
        
        # Apply discount first
        price_after_discount = gross_price - discount
        
        # Determine VAT rate based on import country
        vat_rate = 0
        if self.import_country:
            country = self.import_country.lower()
            if 'tyskland' in country or 'germany' in country:
                vat_rate = 0.19  # 19% German VAT
            elif 'sverige' in country or 'sweden' in country:
                vat_rate = 0.25  # 25% Swedish VAT
        
        # Calculate net price (remove VAT)
        if vat_rate > 0:
            net_price = price_after_discount / (1 + vat_rate)
        else:
            net_price = price_after_discount
        
        return net_price
    
    def net_price_dkk(self):
        """Calculate net purchase price in DKK"""
        rate = 1.0
        if self.purchase_currency and self.purchase_currency.upper() == 'EUR':
            rate = 7.4685
        elif self.purchase_currency and self.purchase_currency.upper() == 'SEK':
            rate = 0.685
        
        return self.net_purchase_price() * rate
    
    def total_additional_costs(self):
        """Calculate total additional costs in DKK (excluding purchase price)"""
        # Invoice fee is in EUR, convert to DKK
        invoice_fee_dkk = float(self.invoice_fee or 0) * 7.4685
        
        return (float(self.transport_cost or 0) + 
                float(self.transport_surcharge or 0) +
                float(self.customs_cost or 0) + 
                invoice_fee_dkk +
                float(self.preparation_cost or 0) + 
                float(self.other_costs or 0))
    
    def total_cost(self):
        """Calculate total cost of car using net purchase price"""
        return self.net_price_dkk() + self.total_additional_costs()
    
    def profit_margin(self, selling_price=None):
        """Calculate profit margin"""
        price = selling_price or self.selling_price
        if not price:
            return None
        return float(price) - self.total_cost()
    
    def profit_percentage(self, selling_price=None):
        """Calculate profit percentage"""
        margin = self.profit_margin(selling_price)
        if margin is None:
            return None
        total = self.total_cost()
        if total == 0:
            return None
        return (margin / total) * 100
    
    @property
    def parsed_notes(self):
        """Parse condition_notes into a list of dicts"""
        if not self.condition_notes:
            return []
        
        notes = []
        # Split by double newline as used in add_note
        raw_notes = self.condition_notes.split('\n\n')
        
        for raw_note in raw_notes:
            if not raw_note.strip():
                continue
                
            # Try to parse format: "[dd-mm-yyyy HH:MM] User Name: Content"
            try:
                # Find the first closing bracket
                close_bracket = raw_note.find(']')
                if close_bracket == -1:
                    notes.append({'content': raw_note, 'user': 'System', 'date': '', 'initials': 'S'})
                    continue
                    
                date_str = raw_note[1:close_bracket]
                
                # Find the first colon after the bracket
                colon = raw_note.find(':', close_bracket)
                if colon == -1:
                    user = "Ukendt"
                    content = raw_note[close_bracket+1:].strip()
                else:
                    user = raw_note[close_bracket+1:colon].strip()
                    content = raw_note[colon+1:].strip()
                
                notes.append({
                    'date': date_str,
                    'user': user,
                    'content': content,
                    'initials': ''.join([n[0] for n in user.split() if n])[:2].upper()
                })
            except Exception:
                notes.append({'content': raw_note, 'user': 'System', 'date': '', 'initials': 'S'})
                
        return notes

    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.vin})>'
