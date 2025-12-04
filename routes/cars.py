"""
Car inventory management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.car import Car
from models.document import Document
from database import db
from datetime import datetime
from sqlalchemy import or_, and_

bp = Blueprint('cars', __name__, url_prefix='/cars')

@bp.route('/')
@login_required
def list_cars():
    """List all cars with filtering"""
    page = request.args.get('page', 1, type=int)
    # Per-page selector (defaults to 20, safe bounds 5-200)
    per_page = request.args.get('per_page', 20, type=int)
    try:
        per_page = max(5, min(per_page, 200))
    except Exception:
        per_page = 20
    status = request.args.get('status', '')
    make = request.args.get('make', '')
    search = request.args.get('search', '')
    import_country = request.args.get('import_country', '')
    
    query = Car.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if make:
        query = query.filter_by(make=make)
    if import_country:
        query = query.filter_by(import_country=import_country)
    if search:
        query = query.filter(
            or_(
                Car.vin.ilike(f'%{search}%'),
                Car.model.ilike(f'%{search}%'),
                Car.registration_number.ilike(f'%{search}%')
            )
        )
    
    cars = query.order_by(Car.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique makes for filter dropdown
    makes = db.session.query(Car.make).distinct().order_by(Car.make).all()
    makes = [m[0] for m in makes]
    
    # Preserve current query params for pagination links
    # Build a dict of current filters excluding page
    current_params = {
        'status': status,
        'make': make,
        'search': search,
        'import_country': import_country,
        'per_page': per_page,
        'view': request.args.get('view', '')
    }
    return render_template('cars/list.html', cars=cars, makes=makes, current_params=current_params)

@bp.route('/<int:car_id>')
@login_required
def view_car(car_id):
    """View car details"""
    car = Car.query.get_or_404(car_id)
    return render_template('cars/view.html', car=car)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_car():
    """Add new car to inventory"""
    if request.method == 'POST':
        try:
            vin = request.form.get('vin').upper()
            
            # Check if VIN already exists
            existing_car = Car.query.filter_by(vin=vin).first()
            if existing_car:
                flash(f'En bil med VIN {vin} findes allerede i systemet. <a href="{url_for("cars.view_car", car_id=existing_car.id)}" class="alert-link">Vis bilen</a>', 'warning')
                return render_template('cars/add.html')
            
            ad_url = request.form.get('ad_url')
            car = Car(
                vin=vin,
                make=request.form.get('make'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                color=request.form.get('color'),
                mileage=int(request.form.get('mileage', 0)),
                fuel_type=request.form.get('fuel_type'),
                transmission=request.form.get('transmission'),
                import_country=request.form.get('import_country'),
                supplier=request.form.get('supplier'),
                dealer_name=request.form.get('dealer_name'),
                dealer_location=request.form.get('dealer_location'),
                distance_km=int(request.form.get('distance_km', 0)) if request.form.get('distance_km') else None,
                import_date=datetime.strptime(request.form.get('import_date'), '%Y-%m-%d').date() if request.form.get('import_date') else None,
                purchase_price=float(request.form.get('purchase_price')),
                purchase_currency=request.form.get('purchase_currency', 'DKK'),
                discount=float(request.form.get('discount', 0)),
                transport_cost=float(request.form.get('transport_cost', 0)),
                customs_cost=float(request.form.get('customs_cost', 0)),
                preparation_cost=float(request.form.get('preparation_cost', 0)),
                other_costs=float(request.form.get('other_costs', 0)),
                selling_price=float(request.form.get('selling_price', 0)) if request.form.get('selling_price') else None,
                dealer_price=float(request.form.get('dealer_price', 0)) if request.form.get('dealer_price') else None,
                private_price=float(request.form.get('private_price', 0)) if request.form.get('private_price') else None,
                status=request.form.get('status', 'ordered'),
                equipment=request.form.get('equipment'),
                condition_notes=request.form.get('condition_notes')
            )
            # Optional registration number: treat empty as None to avoid UNIQUE conflicts on ''
            regnum = request.form.get('registration_number')
            if regnum and regnum.strip():
                car.registration_number = regnum.strip()
            
            db.session.add(car)
            db.session.commit()
            # Store ad URL as a document for easy access, if provided
            if ad_url:
                try:
                    doc = Document(
                        car_id=car.id,
                        name='Annonce Link',
                        document_type='ad_link',
                        filename=ad_url,
                        file_path=ad_url,
                        mime_type='text/uri-list',
                        description='Direkte link til annoncen'
                    )
                    db.session.add(doc)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            
            flash(f'Bil {car.make} {car.model} tilføjet succesfuldt', 'success')
            return redirect(url_for('cars.view_car', car_id=car.id))
        
        except Exception as e:
            db.session.rollback()
            import traceback
            error_msg = str(e)
            if 'UNIQUE constraint failed: cars.vin' in error_msg:
                flash(f'VIN nummeret findes allerede i systemet. Kontroller at bilen ikke er tilføjet tidligere.', 'danger')
            else:
                flash(f'Fejl ved tilføjelse af bil: {error_msg}', 'danger')
    
    return render_template('cars/add.html')

@bp.route('/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """Edit car details"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            car.vin = request.form.get('vin').upper()
            car.make = request.form.get('make')
            car.model = request.form.get('model')
            car.year = int(request.form.get('year'))
            car.color = request.form.get('color')
            car.mileage = int(request.form.get('mileage', 0))
            car.fuel_type = request.form.get('fuel_type')
            car.transmission = request.form.get('transmission')
            car.import_country = request.form.get('import_country')
            car.supplier = request.form.get('supplier')
            car.dealer_name = request.form.get('dealer_name')
            car.dealer_location = request.form.get('dealer_location')
            
            if request.form.get('distance_km'):
                car.distance_km = int(request.form.get('distance_km'))
            
            if request.form.get('import_date'):
                car.import_date = datetime.strptime(request.form.get('import_date'), '%Y-%m-%d').date()
            
            car.purchase_price = float(request.form.get('purchase_price'))
            car.discount = float(request.form.get('discount', 0))
            car.transport_cost = float(request.form.get('transport_cost', 0))
            car.customs_cost = float(request.form.get('customs_cost', 0))
            car.preparation_cost = float(request.form.get('preparation_cost', 0))
            car.other_costs = float(request.form.get('other_costs', 0))
            
            if request.form.get('selling_price'):
                car.selling_price = float(request.form.get('selling_price'))
            if request.form.get('dealer_price'):
                car.dealer_price = float(request.form.get('dealer_price'))
            if request.form.get('private_price'):
                car.private_price = float(request.form.get('private_price'))
            
            car.status = request.form.get('status')
            car.equipment = request.form.get('equipment')
            car.condition_notes = request.form.get('condition_notes')
            # Optional registration number: treat empty as None to avoid UNIQUE conflicts on ''
            regnum = request.form.get('registration_number')
            car.registration_number = regnum.strip() if regnum and regnum.strip() else None
            
            db.session.commit()
            
            flash('Bil opdateret succesfuldt', 'success')
            return redirect(url_for('cars.view_car', car_id=car.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl ved opdatering: {str(e)}', 'danger')
    
    return render_template('cars/edit.html', car=car)

@bp.route('/<int:car_id>/delete', methods=['POST'])
@login_required
def delete_car(car_id):
    """Delete car from inventory"""
    if not current_user.is_admin():
        flash('Du har ikke tilladelse til at slette biler', 'danger')
        return redirect(url_for('cars.list_cars'))
    
    car = Car.query.get_or_404(car_id)
    
    try:
        db.session.delete(car)
        db.session.commit()
        flash('Bil slettet succesfuldt', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('cars.list_cars'))

@bp.route('/<int:car_id>/add-note', methods=['POST'])
@login_required
def add_note(car_id):
    """Add a quick note to a car"""
    car = Car.query.get_or_404(car_id)
    note_content = request.form.get('note_content', '').strip()
    
    if note_content:
        from datetime import datetime
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
        new_note = f"[{timestamp}] {current_user.full_name}: {note_content}"
        
        if car.condition_notes:
            car.condition_notes = f"{new_note}\n\n{car.condition_notes}"
        else:
            car.condition_notes = new_note
        
        try:
            db.session.commit()
            flash('Note tilføjet', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fejl: {str(e)}', 'danger')
    
    return redirect(url_for('cars.view_car', car_id=car_id))


@bp.route('/<int:car_id>/update-process', methods=['POST'])
@login_required
def update_process(car_id):
    """Update process checklist item"""
    car = Car.query.get_or_404(car_id)
    
    step = request.form.get('step')
    checked = request.form.get('checked') == 'true'
    
    valid_steps = ['inquiry', 'ordered', 'kaufvertrag', 'gelangen', 'hjemtagelse', 'payment', 'in_transit', 'delivered']
    
    if step not in valid_steps:
        return jsonify({'success': False, 'error': 'Invalid step'}), 400
    
    try:
        # Update the appropriate field
        setattr(car, f'process_{step}_done', checked)
        
        # Set date if checking, clear if unchecking
        if checked:
            setattr(car, f'process_{step}_date', datetime.now())
        else:
            setattr(car, f'process_{step}_date', None)
        
        db.session.commit()
        
        # Return the formatted date
        date_str = datetime.now().strftime('%d-%m-%Y - kl. %H:%M') if checked else 'Afventer'
        
        return jsonify({
            'success': True, 
            'checked': checked,
            'date': date_str
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:car_id>/update-notes', methods=['POST'])
@login_required
def update_notes(car_id):
    """Update process notes for a car"""
    car = Car.query.get_or_404(car_id)
    
    notes = request.form.get('notes', '')
    
    try:
        car.process_notes = notes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Noter gemt'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:car_id>/update-market-price', methods=['POST'])
@login_required
def update_market_price(car_id):
    """Update market price from Bilbasen"""
    car = Car.query.get_or_404(car_id)
    
    market_price = request.form.get('market_price', '')
    
    try:
        if market_price:
            car.market_price = float(market_price)
            car.market_price_updated = datetime.now()
        else:
            car.market_price = None
            car.market_price_updated = None
        
        db.session.commit()
        
        # Beregn prissammenligning
        total_cost = float(car.total_cost() or 0)
        mkt_price = float(car.market_price or 0)
        difference = mkt_price - total_cost if mkt_price else 0
        diff_percent = (difference / mkt_price * 100) if mkt_price > 0 else 0
        
        return jsonify({
            'success': True,
            'market_price': mkt_price,
            'total_cost': total_cost,
            'difference': difference,
            'difference_percent': round(diff_percent, 1),
            'updated': car.market_price_updated.strftime('%d-%m-%Y %H:%M') if car.market_price_updated else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:car_id>/upload-document', methods=['POST'])
@login_required
def upload_document(car_id):
    """Upload a file or add a link to a car"""
    import os
    from werkzeug.utils import secure_filename
    
    car = Car.query.get_or_404(car_id)
    
    try:
        # Check if it's a file upload or a link
        if 'file_upload' in request.files and request.files['file_upload'].filename:
            file = request.files['file_upload']
            filename = secure_filename(file.filename)
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads', 'cars', str(car_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create document record
            doc = Document(
                car_id=car.id,
                name=request.form.get('file_name') or filename,
                document_type=request.form.get('file_type', 'other'),
                filename=filename,
                file_path=f'/{file_path}',
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type,
                uploaded_by_id=current_user.id
            )
            db.session.add(doc)
            db.session.commit()
            flash('Fil uploadet succesfuldt', 'success')
            
        elif request.form.get('link_url'):
            # Add link
            link_url = request.form.get('link_url')
            link_name = request.form.get('link_name') or 'Link'
            
            doc = Document(
                car_id=car.id,
                name=link_name,
                document_type='ad_link',
                filename=link_url,
                file_path=link_url,
                mime_type='text/uri-list',
                uploaded_by_id=current_user.id
            )
            db.session.add(doc)
            db.session.commit()
            flash('Link tilføjet succesfuldt', 'success')
        else:
            flash('Ingen fil eller link valgt', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl: {str(e)}', 'danger')
    
    return redirect(url_for('cars.view_car', car_id=car_id))


@bp.route('/document/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    """Download a document"""
    import os
    from flask import send_file
    
    doc = Document.query.get_or_404(doc_id)
    
    # If it's a link, redirect to it
    if doc.document_type == 'ad_link':
        return redirect(doc.file_path)
    
    # Otherwise, serve the file
    file_path = doc.file_path.lstrip('/')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=doc.filename)
    else:
        flash('Fil ikke fundet', 'danger')
        return redirect(url_for('cars.view_car', car_id=doc.car_id))


@bp.route('/<int:car_id>/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(car_id, doc_id):
    """Delete a document or link"""
    import os
    
    car = Car.query.get_or_404(car_id)
    doc = Document.query.get_or_404(doc_id)
    
    if doc.car_id != car.id:
        flash('Ugyldigt dokument', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))
    
    try:
        # Delete physical file if it exists
        if doc.document_type != 'ad_link' and doc.file_path:
            file_path = doc.file_path.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(doc)
        db.session.commit()
        flash('Dokument slettet', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fejl ved sletning: {str(e)}', 'danger')
    
    return redirect(url_for('cars.view_car', car_id=car_id))

@bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for car statistics"""
    total = Car.query.count()
    available = Car.query.filter_by(status='available').count()
    sold = Car.query.filter_by(status='sold').count()
    in_transit = Car.query.filter_by(status='in_transit').count()
    
    return jsonify({
        'total': total,
        'available': available,
        'sold': sold,
        'in_transit': in_transit
    })

@bp.route('/parse-ad', methods=['POST'])
@login_required
def parse_ad():
    """Parse advertisement image/PDF or URL and extract car data"""
    from utils.ocr_parser import AdParser
    
    # Check for URL first
    ad_url = request.form.get('ad_url')
    if ad_url:
        try:
            data = AdParser.parse_url(ad_url)
            if 'error' in data:
                return jsonify({'error': data['error']}), 500
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Check for file upload
    if 'ad_image' not in request.files:
        return jsonify({'error': 'Ingen fil eller URL angivet'}), 400
    
    file = request.files['ad_image']
    
    if file.filename == '':
        return jsonify({'error': 'Ingen fil valgt'}), 400
    
    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'pdf'}
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Ugyldig filtype. Brug PNG, JPG, PDF eller andre billedformater'}), 400
    
    try:
        # Parse the advertisement
        data = AdParser.parse_from_upload(file)
        
        if 'error' in data:
            return jsonify({'error': data['error']}), 500
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
