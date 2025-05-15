from sqlalchemy.orm import Session
from models import CatalogItem, Customer, Invoice, CatalogIntegration

# Generic repository pattern for different Catalog types (Customer, Invoice, etc.)
class CatalogRepository:
    """Generic repository for catalog items"""
    
    def __init__(self, session: Session, item_class):
        self.session = session
        self.item_class = item_class
    
    def create(self, **kwargs):
        """Create a new catalog item"""
        item = self.item_class(**kwargs)
        self.session.add(item)
        self.session.commit()
        return item
    
    def update(self, item_id, **kwargs):
        """Update a catalog item"""
        item = self.session.query(self.item_class).filter(self.item_class.id == item_id).first()
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
                
        self.session.commit()
        return item
    
    def delete(self, item_id):
        """Delete a catalog item"""
        item = self.session.query(self.item_class).filter(self.item_class.id == item_id).first()
        if not item:
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