from sqlalchemy.orm import Session
from database.models import CatalogIntegration

# Generic repository pattern for different Catalog types (Customer, Invoice, etc.)
class CatalogRepository:
    """Generic repository for catalog items"""
    
    def __init__(self, session: Session, item_class):
        self.session = session
        self.item_class = item_class
    
    def create(self, name, email):
        """Create a new catalog item"""
        item = self.item_class(name=name, email=email)
        self.session.add(item)
        self.session.commit()
        print(f"Created {self.item_class.__name__} with name: {name}, email: {email}")
        
        return item
    
    def update(self, item_id, name=None, email=None):
        """Update a catalog item"""
        item = self.session.query(self.item_class).filter(self.item_class.id == item_id).first()
        if not item:
            print(f"{self.item_class.__name__} with ID {item_id} not found.")
            return None
        
        if name is not None:
            item.name = name
        if email is not None:
            item.email = email
                
        self.session.commit()
        return item
    
    def delete(self, item_id):
        """Delete a catalog item"""
        item = self.session.query(self.item_class).filter(self.item_class.id == item_id).first()
        if not item:
            print(f"{self.item_class.__name__} with ID {item_id} not found.")
            return False
        
        self.session.delete(item)
        self.session.commit()
        return True
    
    def get(self, item_id):
        """Get a catalog item by ID"""
        return self.session.query(self.item_class).filter(self.item_class.id == item_id).first()
    
    def get_all(self):
        """Get all catalog items"""
        return self.session.query(self.item_class).all()
    
    def add_integration(self, item_id, integration_type, integration_id):
        """Add integration information for a catalog item"""
        integration = CatalogIntegration(
            catalog_item_id=item_id,
            integration_type=integration_type,
            integration_id=integration_id,
        )
        self.session.add(integration)
        self.session.commit()
        return integration
    
    def get_integration(self, integration_id=None, catalog_id=None, integration_type='stripe'):
        """Get a catalog item by its external integration ID"""
        if catalog_id:
            return self.session.query(CatalogIntegration).filter(
                CatalogIntegration.catalog_item_id == catalog_id,
                CatalogIntegration.integration_type == integration_type
            ).first()
        return self.session.query(CatalogIntegration).filter(
            CatalogIntegration.integration_id == integration_id,
            CatalogIntegration.integration_type == integration_type
        ).first()
        
    def get_all_integrations(self, integration_type='stripe'):
        """Get all integrations for a specific type"""
        return self.session.query(CatalogIntegration).filter(
            CatalogIntegration.integration_type == integration_type
        ).all()
    
    def delete_integration(self, integration_id):
        """Delete a catalog item integration"""
        integration = self.session.query(CatalogIntegration).filter(
            CatalogIntegration.id == integration_id
        ).first()
        if not integration:
            print(f"Integration with ID {integration_id} not found.")
            return False
        
        self.session.delete(integration)
        self.session.commit()
        return True