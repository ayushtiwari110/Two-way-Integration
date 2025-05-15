# repositories/catalog_repository.py
from sqlalchemy.orm import Session
from database.models import Customer
from database.repositories.catalogue_repository import CatalogRepository

# Customer Repository
class CustomerRepository(CatalogRepository):
    def __init__(self, session: Session):
        super().__init__(session, Customer)
    
    def get_by_email(self, email):
        """Get a customer by email"""
        return self.session.query(Customer).filter(Customer.email == email).first()

    def get_customer_by_integration(self, integration_id, integration_type):
        """Get a customer through their external integration ID"""
        integration = self.get_integration(integration_id, integration_type)
        if integration:
            return self.get_by_id(integration.catalog_item_id)
        return None