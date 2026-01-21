from fastapi import Depends, FastAPI, HTTPException
from dotenv import load_dotenv
import strawberry
from strawberry.fastapi import GraphQLRouter
from src.models.bets import bet_schema
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import get_db_session, engine, Base
from src.MBManager import start_consuming

async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI()
async def get_context(db: AsyncSession = Depends(get_db_session)):
    return {
        "db": db,
    }
graphql_app = GraphQLRouter(bet_schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
async def on_startup():
    await init_tables()
    import threading
    threading.Thread(target=start_consuming, daemon=True).start()
 