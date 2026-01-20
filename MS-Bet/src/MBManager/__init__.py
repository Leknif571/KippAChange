import json
import os,pika
import time
from dotenv import load_dotenv
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path) 
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_BET_EXCHANGE = os.getenv("RABBITMQ_BET_EXCHANGE")
RABBITMQ_NOTIFICATION_EXCHANGE = os.getenv("RABBITMQ_NOTIFICATION_EXCHANGE")
RABBITMQ_BET_QUEUE = os.getenv("RABBITMQ_BET_QUEUE")
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )
connection = get_rabbitmq_connection()
channel = connection.channel()
channel.exchange_declare(exchange=RABBITMQ_BET_EXCHANGE, exchange_type='fanout')
connection.close()

def publish_bet_on_notification_exchange(message: dict):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.basic_publish(exchange=RABBITMQ_NOTIFICATION_EXCHANGE, routing_key='', body=json.dumps(message))
        print("Message publié sur l'exchange de notification :", message, flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la publication du message : {e}")
        return False

def create_bet(bet_data: dict):
    print(f"Création du pari avec les données : {bet_data}", flush=True)
    

def start_consuming():
    def callback(ch, method, properties, body):
        body_received = json.loads(body)
        print(" [x] Pari reçu :", body_received['data'], flush=True)
        time.sleep(2)
        create_bet(body_received['data'])
        publish_bet_on_notification_exchange({"event": "bet_created", "data": body_received['data']})

        

    connection = get_rabbitmq_connection()
    channel = connection.channel()
    result = channel.queue_declare(queue=RABBITMQ_BET_QUEUE, exclusive=False)
    queue_name = result.method.queue
    channel.queue_bind(exchange=RABBITMQ_BET_EXCHANGE, queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f" [*] En attente de messages sur l'exchange '{RABBITMQ_BET_EXCHANGE}' (queue: {queue_name})...", flush=True)
    channel.start_consuming() 
    connection.close()