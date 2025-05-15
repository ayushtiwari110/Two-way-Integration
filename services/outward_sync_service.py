# services/outward_sync_service.py
from services.kafka_service import KafkaService

class OutwardSyncService:
    def __init__(self, kafka_service: KafkaService):
        self.kafka_service = kafka_service
        self.outward_topic = 'customer_outward_sync'
    
    def queue_create_event(self, customer):
        """Queue a customer creation event"""
        message = {
            'event_type': 'customer_created',
            'customer': customer.to_dict()
        }
        return self.kafka_service.send_message(self.outward_topic, message)
    
    def queue_update_event(self, customer):
        """Queue a customer update event"""
        message = {
            'event_type': 'customer_updated',
            'customer': customer.to_dict()
        }
        return self.kafka_service.send_message(self.outward_topic, message)
    
    def queue_delete_event(self, customer_id):
        """Queue a customer deletion event"""
        message = {
            'event_type': 'customer_deleted',
            'customer_id': customer_id
        }
        return self.kafka_service.send_message(self.outward_topic, message)