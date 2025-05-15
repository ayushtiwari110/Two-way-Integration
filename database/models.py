from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

# Base class for any catalog item (Customer, Invoice, etc.)
class CatalogItem(Base):
    __tablename__ = 'catalog_items'
    
    id = Column(Integer, primary_key=True)
    catalog_type = Column(String, nullable=False)  # 'customer', 'invoice', etc.
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    __mapper_args__ = {
        'polymorphic_identity': 'catalog_item',
        'polymorphic_on': catalog_type
    }

class Customer(CatalogItem):
    __tablename__ = 'customers'
    
    id = Column(Integer, ForeignKey('catalog_items.id'), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    integrations = relationship("CatalogIntegration", back_populates="catalog_item")
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

# Database setup
engine = create_engine('sqlite:///customer_sync.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
    
# # Potentially extendable to other systems within our product (e.g., Invoice Catalog)
# class Invoice(CatalogItem):
#     __tablename__ = 'invoices'
#    
#     id = Column(Integer, ForeignKey('catalog_items.id'), primary_key=True)
#     customer_id = Column(Integer, ForeignKey('customers.id'))
#     customer_name = Column(String, nullable=False)
#     amount = Column(Numeric(10, 2), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(String, nullable=False)
#     due_date = Column(DateTime, nullable=True)
#
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "customer_id": self.customer_id,
#             "customer_name": self.customer_name,
#             "amount": self.amount,
#             "description": self.description,
#             "status": self.status,
#             "due_date": self.due_date,
#             "created_at": self.created_at.isoformat() if self.created_at else None,
#             "updated_at": self.updated_at.isoformat() if self.updated_at else None
#         }
#
#     customer = relationship("Customer")
#     integrations = relationship("CatalogIntegration", back_populates="catalog_item")
#    
#     __mapper_args__ = {
#         'polymorphic_identity': 'invoice',
#     }
#
# # This class can be used to manage integrations with multiple external systems
# class CatalogIntegration(Base):
#     __tablename__ = 'catalog_integrations'
    
#     id = Column(Integer, primary_key=True)
#     catalog_item_id = Column(Integer, ForeignKey('catalog_items.id'))
#     integration_type = Column(String, nullable=False)  # e.g., 'salesforce', 'hubspot'
#     integration_id = Column(String, nullable=False)  # Unique ID from the integration system
#     created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
#     catalog_item = relationship("CatalogItem", back_populates="integrations")
    
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "catalog_item_id": self.catalog_item_id,
#             "integration_type": self.integration_type,
#             "integration_id": self.integration_id,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }
#     __mapper_args__ = {
#         'polymorphic_identity': 'catalog_integration',
#     }