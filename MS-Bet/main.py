from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.MBManager import start_consuming
import logging

app = FastAPI()
@app.on_event("startup")
def startup_event():
    import threading
    threading.Thread(target=start_consuming, daemon=True).start()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FastAPI avec RabbitMQ et dotenv !"}
 