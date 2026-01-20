from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Remplacez par votre URL de connexion PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/kippachange_db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Factory pour créer des sessions asynchrones
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

# Dépendance pour récupérer la session DB (sera utilisée dans le contexte Strawberry)
async def get_db_session():
    async with async_session() as session:
        yield session