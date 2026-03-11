import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

# Kafka broker configurations
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'transactions_topic'

def create_producer():
    """Create and return a Kafka Producer instance."""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"Successfully connected to Kafka Broker at {KAFKA_BROKER}")
            return producer
        except Exception as e:
            print(f"Failed to connect to Kafka Broker: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def generate_transaction():
    """Generate a mock transaction record."""
    transaction_types = ['purchase', 'refund', 'transfer', 'deposit']
    return {
        'transaction_id': str(uuid.uuid4()),
        'user_id': fake.uuid4()[:8],
        'amount': round(random.uniform(5.0, 1500.0), 2),
        'transaction_type': random.choice(transaction_types),
        'transaction_timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    producer = create_producer()
    print(f"Starting to produce messages to topic '{TOPIC_NAME}'...")
    
    try:
        while True:
            transaction = generate_transaction()
            # Send message to Kafka
            producer.send(TOPIC_NAME, transaction)
            print(f"Sent: {transaction}")
            
            # Flush the producer buffer
            producer.flush()
            
            # Wait a bit before sending the next one
            time.sleep(random.uniform(0.5, 2.0))
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
