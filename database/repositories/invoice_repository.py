# from sqlalchemy.orm import Session
# from database.models import Invoice
# from catalogue_repository import CatalogRepository

# # Invoice Repository
# class InvoiceRepository(CatalogRepository):
#     def __init__(self, session: Session):
#         super().__init__(session, Invoice)
    
#     def get_by_customer(self, customer_id):
#         """Get invoices for a customer"""
#         return self.session.query(Invoice).filter(Invoice.customer_id == customer_id).all()