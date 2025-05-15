# services/kafka_service.py
from kafka import KafkaProducer, KafkaConsumer
import json
from config import KAFKA_BOOTSTRAP_SERVERS

class KafkaService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_message(self, topic, message):
        """Send a message to a Kafka topic"""
        try:
            future = self.producer.send(topic, message)
            self.producer.flush()
            return future.get(timeout=60)
        except Exception as e:
            print(f"Error sending message to Kafka: {e}")
            return None
    
    def get_consumer(self, topic, group_id):
        """Get a Kafka consumer for a specific topic"""
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id,
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        except Exception as e:
            print(f"Error creating Kafka consumer: {e}")
            return None