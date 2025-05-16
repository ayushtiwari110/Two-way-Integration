from abc import ABC, abstractmethod

class CatalogIntegrationService(ABC):
    """Abstract base class for catalog integration with external services"""
    
    def __init__(self, entity_type):
        """Initialize with entity type ('customer', 'invoice', etc.)"""
        self.entity_type = entity_type
    
    @abstractmethod
    def create_item(self, name, email):
        """Create an item in the external service"""
        pass
    
    @abstractmethod
    def update_item(self, integration_id, name=None, email=None):   
        """Update an item in the external service"""
        pass
    
    @abstractmethod
    def delete_item(self, integration_id):
        """Delete an item in the external service"""
        pass
    
    @abstractmethod
    def get_items(self, limit=100, starting_after=None):
        """Get items from the external service"""
        pass
    
    @abstractmethod
    def get_item(self, integration_id):
        """Get a specific item from the external service"""
        pass