# repositories/catalog_repository.py
from sqlalchemy.orm import Session
from models import Customer
from catalogue_repository import CatalogRepository

# Customer Repository
class CustomerRepository(CatalogRepository):
    def __init__(self, session: Session):
        super().__init__(session, Customer)
    
    def get_by_email(self, email):
        """Get a customer by email"""
        return self.session.query(Customer).filter(Customer.email == email).first()