from abc import ABC, abstractmethod

class CatalogIntegrationService(ABC):
    """Abstract base class for catalog integration with external services"""
    
    def __init__(self, entity_type):
        """Initialize with entity type ('customer', 'invoice', etc.)"""
        self.entity_type = entity_type
    
    @abstractmethod
    def create_item(self, **kwargs):
        """Create an item in the external service"""
        pass
    
    @abstractmethod
    def update_item(self, **kwargs):
        """Update an item in the external service"""
        pass
    
    @abstractmethod
    def delete_item(self, **kwargs):
        """Delete an item in the external service"""
        pass
    
    @abstractmethod
    def get_items(self, **kwargs):
        """Get items from the external service"""
        pass