# workers/stripe_worker.py
from services.kafka_service import KafkaService
from services.stripe_service import StripeService
from database.repositories.customer_repository import CustomerRepository
from database.models import Session as DBSession
import threading

class StripeWorker:
    def __init__(self):
        self.kafka_service = KafkaService()
        self.stripe_service = StripeService()
        self.db_session = DBSession()
        self.customer_repo = CustomerRepository(self.db_session)
        self.consumer = self.kafka_service.get_consumer('customer_outward_sync', 'stripe_worker')
        self.running = False
    
    def start(self):
        """Start the worker"""
        self.running = True
        thread = threading.Thread(target=self.process_messages)
        thread.daemon = True
        thread.start()
        print("Stripe worker started")
        return thread
    
    def stop(self):
        """Stop the worker"""
        self.running = False
    
    def process_messages(self):
        """Process messages from the Kafka queue"""
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                event = message.value
                event_type = event.get('event_type')
                
                if event_type == 'customer_created':
                    self._handle_customer_created(event)
                elif event_type == 'customer_updated':
                    self._handle_customer_updated(event)
                elif event_type == 'customer_deleted':
                    self._handle_customer_deleted(event)
        except Exception as e:
            print(f"Error processing messages: {e}")
    
    def _handle_customer_created(self, event):
        """Handle customer created event"""
        try:
            customer_data = event.get('customer', {})
            customer_id = customer_data.get('id')
            name = customer_data.get('name')
            email = customer_data.get('email')
            
            stripe_customer_id = self.stripe_service.create_item(name=name, email=email)
            
            if stripe_customer_id:
                if self.customer_repo.get_integration(catalog_id=customer_id, integration_type='stripe'):
                    print(f"Stripe customer already exists for {name} ({email})")
                else:
                    self.customer_repo.add_integration(
                        item_id=customer_id,
                        integration_type='stripe',
                        integration_id=stripe_customer_id
                    )
                    print(f"Created and linked Stripe customer {stripe_customer_id} for {name} ({email})")
        except Exception as e:
            print(f"Error handling customer created event: {e}")
    
    def _handle_customer_updated(self, event):
        """Handle customer updated event"""
        try:
            customer_data = event.get('customer', {})
            customer_id = customer_data.get('id')
            name = customer_data.get('name')
            email = customer_data.get('email')
            
            integration = self.customer_repo.get_integration(catalog_id=customer_id, integration_type='stripe')
            if integration:
                stripe_customer_id = integration.integration_id
                self.stripe_service.update_item(stripe_customer_id, name, email)
                print(f"Updated Stripe customer for {name} ({email})")
        except Exception as e:
            print(f"Error handling customer updated event: {e}")
    
    def _handle_customer_deleted(self, event):
        """Handle customer deleted event"""
        try:
            # In the customer_api.py, we're sending the Stripe ID, not the local customer ID
            stripe_id = event.get('customer_id')
            
            if not stripe_id:
                print("Error: Missing Stripe ID in customer deletion event")
                return
                
            print(f"Processing deletion for Stripe customer ID: {stripe_id}")
            
            # First delete from Stripe using the Stripe ID directly
            delete_result = self.stripe_service.delete_item(stripe_id)
            
            if delete_result:
                print(f"Successfully deleted customer from Stripe: {stripe_id}")
                
                # Now find and delete the integration record by Stripe ID
                integration = self.customer_repo.get_integration(
                    integration_id=stripe_id,  # Use integration_id parameter instead of catalog_id
                    integration_type='stripe'
                )
                
                if integration:
                    self.customer_repo.delete_integration(integration.id)
                    print(f"Successfully deleted integration record (ID: {integration.id})")
                else:
                    print(f"No integration record found for Stripe ID: {stripe_id} (may have been cascade deleted)")
            else:
                print(f"Failed to delete customer from Stripe: {stripe_id}")
                
        except Exception as e:
            import traceback
            print(f"Error handling customer deletion event: {e}")
            print(traceback.format_exc())