"""
Logging configuration for GreenMotion Cars CRM
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Set log level from config or environment
    log_level_name = os.environ.get('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Remove existing handlers
    app.logger.handlers = []
    
    # File handler for general logs
    file_handler = RotatingFileHandler(
        'logs/greenmotion.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    # File handler for errors only
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(pathname)s:%(lineno)d: %(message)s\n'
        'Traceback:\n%(exc_info)s'
    ))
    error_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_handler)
    
    # Console handler for development
    if app.config['DEBUG']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    # Set application log level
    app.logger.setLevel(log_level)
    
    # Log startup
    app.logger.info('='*50)
    app.logger.info('GreenMotion Cars CRM Starting')
    app.logger.info(f'Environment: {app.config.get("ENV", "unknown")}')
    app.logger.info(f'Debug Mode: {app.config["DEBUG"]}')
    app.logger.info('='*50)
    
    return app.logger
