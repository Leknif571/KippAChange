from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import strawberry
from strawberry.fastapi import GraphQLRouter
from src.models.bets import bet_schema
import logging

app = FastAPI()
graphql_app = GraphQLRouter(bet_schema)
app.include_router(graphql_app, prefix="/graphql")

app.get("/health")
def health_check():
    return {"status": "ok"}
 