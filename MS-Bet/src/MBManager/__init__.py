import json
import os,pika,asyncio
from sqlalchemy import select
from src.models import async_session
from dotenv import load_dotenv
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path) 
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_BET_EXCHANGE = os.getenv("RABBITMQ_BET_EXCHANGE")
RABBITMQ_NOTIFICATION_QUEUE = os.getenv("RABBITMQ_NOTIFICATION_QUEUE")
RABBITMQ_MATCH_FINISHED_QUEUE = os.getenv("RABBITMQ_MATCH_FINISHED_QUEUE")
RABBITMQ_WALLET_QUEUE = os.getenv("RABBITMQ_WALLET_QUEUE")
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
    
def publish_add_amount_on_wallet_exchange(data: dict):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key=RABBITMQ_WALLET_QUEUE, body=json.dumps(data))
        print("Message publié sur l'exchange wallet :", data, flush=True)
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la publication du message : {e}")
        return False

async def process_match_result(match_id: str, final_result: str):
    from src.models.bets import BetModel
    async with async_session() as db:
        try:
            query = select(BetModel).where(
                BetModel.match_id == match_id,
                BetModel.status != "FINISHED"
            )
            result = await db.execute(query)
            bets = result.scalars().all()

            if not bets:
                print("Aucun pari en attente pour ce match.")
                return
            count_won = 0
            count_lost = 0
            for bet in bets:
                if bet.bet_result == final_result:
                    bet.status = "won"
                    count_won += 1
                    pattern = "bet_won"
                    publish_add_amount_on_wallet_exchange({"pattern":pattern,"data": {"wallet_id": bet.wallet_id, "amount": bet.amount * bet.odds}})
                else:
                    bet.status = "lost"
                    count_lost += 1
                    pattern = "bet_lost"
                
                publish_bet_on_notification_exchange({"pattern":pattern, "data":{"user_id":"Unknown", "match_id":match_id}})
            await db.commit()
            print(f"Mise à jour terminée : {count_won} gagnés, {count_lost} perdus.")
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des paris : {e}")
            await db.rollback()

def match_updated_callback(ch, method, properties, body):
    print("Message reçu (Résultat de match) :", body.decode(), flush=True)
    
    try:
        data = json.loads(body.decode())

        match_id = data['data'].get('match_id')
        result = data['data'].get('final_result')
        if match_id and result:
            asyncio.run(process_match_result(str(match_id), str(result)))
        else:
            print("Message invalide : match_id ou result manquant")
    except json.JSONDecodeError:
        print("Erreur : Le message n'est pas un JSON valide")
    except Exception as e:
        print(f"Erreur inattendue dans le callback : {e}")
        
    
def start_consuming():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_MATCH_FINISHED_QUEUE, durable=True)
    channel.basic_consume(queue=RABBITMQ_MATCH_FINISHED_QUEUE, on_message_callback=match_updated_callback, auto_ack=True)
    print("En attente de messages dans la file d'attente des paris...", flush=True)
    channel.start_consuming()
    