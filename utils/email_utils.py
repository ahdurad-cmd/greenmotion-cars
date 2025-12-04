"""
Email utilities for sending notifications
"""
from flask import current_app, render_template, url_for
from flask_mail import Message
from app import mail
import logging

logger = logging.getLogger(__name__)

def send_email(subject, recipients, html_body, text_body=None, sender=None):
    """
    Send an email
    
    Args:
        subject: Email subject
        recipients: List of recipient email addresses
        html_body: HTML content
        text_body: Plain text content (optional)
        sender: Sender email (optional, uses config default)
    """
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            body=text_body,
            sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        logger.info(f'Email sent to {recipients}: {subject}')
        return True
    except Exception as e:
        logger.error(f'Failed to send email to {recipients}: {str(e)}')
        return False

def send_welcome_email(customer):
    """Send welcome email to new customer"""
    subject = 'Velkommen til GreenMotion Cars!'
    html_body = render_template('email/welcome.html', customer=customer)
    return send_email(subject, customer.email, html_body)

def send_sale_notification(sale, recipients):
    """Send notification about new sale"""
    subject = f'Nyt Salg: #{sale.sale_number}'
    html_body = render_template('email/sale_notification.html', sale=sale)
    return send_email(subject, recipients, html_body)

def send_reminder_email(recipient_email, recipient_name, message, reminder_details, 
                       action_required=None, deadline=None, action_url=None):
    """Send reminder email"""
    subject = 'Påmindelse fra GreenMotion Cars'
    html_body = render_template(
        'email/reminder.html',
        recipient_name=recipient_name,
        message=message,
        reminder_details=reminder_details,
        action_required=action_required,
        deadline=deadline,
        action_url=action_url
    )
    return send_email(subject, recipient_email, html_body)

def send_payment_reminder(sale):
    """Send payment reminder for a sale"""
    customer = sale.customer
    return send_reminder_email(
        recipient_email=customer.email,
        recipient_name=customer.name,
        message=f'Dette er en venlig påmindelse om udestående betaling for salg #{sale.sale_number}.',
        reminder_details=f'Resterende beløb: {sale.remaining_payment():,.2f} kr.',
        action_required='Venligst gennemfør betaling hurtigst muligt.',
        deadline=None,
        action_url=url_for('sales.sale_detail', id=sale.id, _external=True)
    )

def send_inspection_reminder(car):
    """Send reminder about upcoming car inspection"""
    # This would typically go to an admin or the person responsible
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@greenmotioncars.dk')
    
    return send_reminder_email(
        recipient_email=admin_email,
        recipient_name='Administrator',
        message=f'Bilen {car.make} {car.model} (VIN: {car.vin}) har snart udløbende syn.',
        reminder_details=f'Syn udløber: {car.inspection_valid_until.strftime("%d-%m-%Y") if car.inspection_valid_until else "Ukendt"}',
        action_required='Book syn snarest muligt.',
        deadline=car.inspection_valid_until,
        action_url=url_for('cars.car_detail', id=car.id, _external=True)
    )
