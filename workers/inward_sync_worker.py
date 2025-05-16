# workers/inward_sync_worker.py
from services.kafka_service import KafkaService
from database.repositories.customer_repository import CustomerRepository
from database.models import Session as DBSession, Customer
import threading

class InwardSyncWorker:
    def __init__(self):
        self.kafka_service = KafkaService()
        self.db_session = DBSession()
        self.customer_repo = CustomerRepository(self.db_session)
        self.consumer = self.kafka_service.get_consumer('customer_inward_sync', 'inward_sync_worker')
        self.running = False
    
    def start(self):
        """Start the worker"""
        self.running = True
        thread = threading.Thread(target=self.process_messages)
        thread.daemon = True
        thread.start()
        print("Inward sync worker started")
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
                # Stripe's customer updated and created events
                if event_type == 'customer.updated' or event_type == 'customer.created':
                    self._handle_stripe_customer_updated(event)
                elif event_type == 'customer.deleted':
                    self._handle_stripe_customer_deleted(event)
                else:
                    print(f"Unknown event type in inward_sync_worker: {event_type}")
        except Exception as e:
            print(f"Error processing messages: {e}")
    
    def _handle_stripe_customer_updated(self, event):
        """Handle Stripe customer updated event"""
        try:
            stripe_customer = event.get('stripe_customer', {})
            stripe_id = stripe_customer.get('id')
            name = stripe_customer.get('name')
            email = stripe_customer.get('email')
            
            if not email:
                print(f"Missing email for Stripe customer {stripe_id}")
                return
            
            # Find if this customer already exists in our system
            existing_customer = self.db_session.query(Customer).filter(
                Customer.name == name,
                Customer.email == email,
            ).first()
            
            if existing_customer:
                # Customer exists, update it
                customer = self.customer_repo.get(existing_customer.id)
                if customer:
                    customer = self.customer_repo.update(customer.id, name=name, email=email)
                    print(f"Updated customer {customer.id} from Stripe")
            else:
                # Customer doesn't exist, check by email
                customer = self.customer_repo.get_by_email(email)
                
                if customer:
                    # Update customer and add integration
                    customer = self.customer_repo.update(customer.id, name=name, email=email)
                    self.customer_repo.add_integration(
                        item_id=customer.id,
                        integration_type='stripe',
                        integration_id=stripe_id
                    )
                    print(f"Linked existing customer {customer.id} to Stripe customer {stripe_id}")
                else:
                    # Create new customer and add integration
                    customer = self.customer_repo.create(name=name, email=email)
                    self.customer_repo.add_integration(
                        item_id=customer.id,
                        integration_type='stripe',
                        integration_id=stripe_id
                    )
                    print(f"Created new customer {customer.id} from Stripe customer {stripe_id}")
        except Exception as e:
            print(f"Error handling Stripe customer update: {e}")
    
    def _handle_stripe_customer_deleted(self, event):
        """Handle Stripe customer deleted event"""
        try:
            stripe_customer = event.get('stripe_customer', {})
            stripe_id = stripe_customer.get('id')
            
            if not stripe_id:
                print("Missing Stripe ID for deleted customer")
                return
            
            # Find the customer in our system
            integration = self.customer_repo.get_integration(integration_id=stripe_id, integration_type='stripe')
            
            if integration:
                # Remove the customer's integration to stripe
                self.customer_repo.delete_integration(integration.id)
                print(f"Deleted integration for customer {integration.catalog_item_id} from Stripe")
                # Optionally, delete the customer from our system
                # self.customer_repo.delete(integration.catalog_item_id)
                # print(f"Deleted customer {integration.catalog_item_id} from our system")
            else:
                print(f"No matching customer found for Stripe ID {stripe_id}")
        except Exception as e:
            print(f"Error handling Stripe customer deletion: {e}")