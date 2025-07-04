# services/stripe_service.py
import stripe
from services.integration_service import CatalogIntegrationService
from config import STRIPE_API_KEY

# Stripe Integration Service
class StripeService(CatalogIntegrationService):
    
    def __init__(self):
        super().__init__('customer')
        stripe.api_key = STRIPE_API_KEY
    
    def create_item(self, name, email):
        """Create a customer in Stripe"""
        try:
            customer = stripe.Customer.create(
                name=name,
                email=email
            )
            return customer.id
        except Exception as e:
            print(f"Error creating Stripe customer: {e}")
            return None
    
    def update_item(self, integration_id, name, email):
        """Update a customer in Stripe"""
        try:
            update_params = {}
            if name:
                update_params['name'] = name
            if email:
                update_params['email'] = email
                
            if update_params:
                customer = stripe.Customer.modify(
                    id=integration_id,
                    **update_params
                )
                return customer
            return None
        except Exception as e:
            print(f"Error updating Stripe customer: {e}")
            return None
    
    def delete_item(self, integration_id):
        """Delete a customer in Stripe"""
        try:
            return stripe.Customer.delete(integration_id)
        except Exception as e:
            print(f"Error deleting Stripe customer: {e}")
            return None
    
    def get_items(self, limit, starting_after):
        """Get customers from Stripe"""
        try:
            params = {"limit": limit}
            if starting_after:
                params["starting_after"] = starting_after
            
            return stripe.Customer.list(**params)
        except Exception as e:
            print(f"Error fetching Stripe customers: {e}")
            return None
    
    def get_item(self, integration_id):
        """Get a specific customer from Stripe"""
        try:
            return stripe.Customer.retrieve(integration_id)
        except Exception as e:
            print(f"Error fetching Stripe customer: {e}")
            return None