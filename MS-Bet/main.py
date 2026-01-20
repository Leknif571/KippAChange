from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import strawberry
from src.MBManager import start_consuming
from strawberry.fastapi import GraphQLRouter
from src.models.bets import bet_schema
import logging

app = FastAPI()
graphql_app = GraphQLRouter(bet_schema)
app.include_router(graphql_app, prefix="/graphql")

app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    import threading
    threading.Thread(target=start_consuming, daemon=True).start()
 