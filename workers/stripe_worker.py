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
            
            stripe_customer_id = self.stripe_service.create_item(name, email)
            
            if stripe_customer_id:
                self.customer_repo.add_integration(
                    customer_id=customer_id,
                    integration_type='stripe',
                    external_id=stripe_customer_id
                )
                print(f"Created Stripe customer for {name} ({email})")
        except Exception as e:
            print(f"Error handling customer created event: {e}")
    
    def _handle_customer_updated(self, event):
        """Handle customer updated event"""
        try:
            customer_data = event.get('customer', {})
            customer_id = customer_data.get('id')
            name = customer_data.get('name')
            email = customer_data.get('email')
            
            integration = self.customer_repo.get_integration(customer_id, 'stripe')
            if integration:
                stripe_customer_id = integration.external_id
                self.stripe_service.update_item(stripe_customer_id, name, email)
                print(f"Updated Stripe customer for {name} ({email})")
        except Exception as e:
            print(f"Error handling customer updated event: {e}")
    
    def _handle_customer_deleted(self, event):
        """Handle customer deleted event"""
        try:
            customer_id = event.get('customer_id')
            
            integration = self.customer_repo.get_integration(customer_id, 'stripe')
            if integration:
                stripe_customer_id = integration.external_id
                self.stripe_service.delete_item(stripe_customer_id)
                print(f"Deleted Stripe customer for customer_id {customer_id}")
        except Exception as e:
            print(f"Error handling customer deleted event: {e}")