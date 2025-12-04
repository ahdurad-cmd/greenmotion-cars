"""
Models package initialization
"""
from models.user import User
from models.car import Car
from models.customer import Customer
from models.sale import Sale
from models.logistics import LogisticsEntry
from models.document import Document, Communication

__all__ = [
    'User',
    'Car', 
    'Customer',
    'Sale',
    'LogisticsEntry',
    'Document',
    'Communication'
]
