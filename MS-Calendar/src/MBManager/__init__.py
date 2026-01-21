import json
import os
import pika
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
RABBITMQ_CALENDAR_EXCHANGE = os.getenv("RABBITMQ_CALENDAR_EXCHANGE", "calendar_exchange")
RABBITMQ_BET_EXCHANGE = os.getenv("RABBITMQ_BET_EXCHANGE", "bet_exchange")
RABBITMQ_CALENDAR_QUEUE = os.getenv("RABBITMQ_CALENDAR_QUEUE", "calendar_queue")
RABBITMQ_MATCH_FINISHED_QUEUE = os.getenv("RABBITMQ_MATCH_FINISHED_QUEUE", "match_finished_queue")


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )


def init_exchanges_and_queues():
    """Initialise les exchanges et queues au démarrage de MS-Calendar"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Déclarer les exchanges
        channel.exchange_declare(exchange=RABBITMQ_CALENDAR_EXCHANGE, exchange_type='fanout', durable=True)
        channel.exchange_declare(exchange=RABBITMQ_BET_EXCHANGE, exchange_type='fanout', durable=True)

        # Déclarer les queues
        channel.queue_declare(queue=RABBITMQ_CALENDAR_QUEUE, durable=True)
        channel.queue_declare(queue=RABBITMQ_MATCH_FINISHED_QUEUE, durable=True)

        # Lier les queues aux exchanges
        channel.queue_bind(exchange=RABBITMQ_CALENDAR_EXCHANGE, queue=RABBITMQ_CALENDAR_QUEUE)
        channel.queue_bind(exchange=RABBITMQ_BET_EXCHANGE, queue=RABBITMQ_MATCH_FINISHED_QUEUE)

        print(f"[Calendar] Exchanges et queues initialisés", flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"[Calendar] Erreur init RabbitMQ: {e}", flush=True)
        return False


def publish_match_bettable(match_data: dict):
    """Publie un message quand un match devient pariable"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        message = {
            "event": "match_bettable",
            "data": match_data
        }
        channel.basic_publish(
            exchange=RABBITMQ_BET_EXCHANGE,
            routing_key='',
            body=json.dumps(message)
        )
        print(f"[Calendar] Match pariable publié: {match_data.get('id')}", flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"[Calendar] Erreur publication match_bettable: {e}", flush=True)
        return False


def publish_match_finished(match_result_data: dict):
    """
    Publie un message quand un match est terminé avec son résultat.
    MS-Bet écoute cette queue pour traiter les paris.
    """
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Déclarer la queue si elle n'existe pas
        channel.queue_declare(queue=RABBITMQ_MATCH_FINISHED_QUEUE, durable=True)
        
        message = {
            "event": "match_finished",
            "data": match_result_data
        }
        
        # Publier directement sur la queue (sans exchange)
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_MATCH_FINISHED_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2, 
            )
        )
        
        print(f"[Calendar] Match terminé publié: {match_result_data.get('match_id')} - Résultat: {match_result_data.get('result')}", flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"[Calendar] Erreur publication match_finished: {e}", flush=True)
        return False