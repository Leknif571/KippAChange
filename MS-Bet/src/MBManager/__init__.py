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
RABBITMQ_NOTIFICATION_QUEUE = os.getenv("RABBITMQ_NOTIFICATION_QUEUE")
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
        channel.basic_publish(exchange='', routing_key=RABBITMQ_NOTIFICATION_QUEUE, body=json.dumps(message))
        print("Message publié sur l'exchange de notification :", message, flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la publication du message : {e}")
        return False

def create_bet(bet_data: dict):
    print(f"Création du pari avec les données : {bet_data}", flush=True)
    