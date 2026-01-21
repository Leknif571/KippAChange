import strawberry
from strawberry.federation import Schema
from sqlalchemy import Column, Integer, String, Float, select
from . import Base
from sqlalchemy.ext.asyncio import AsyncSession
from src.MBManager import publish_bet_on_notification_exchange, publish_add_amount_on_wallet_exchange

class BetModel(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    match_id = Column(String, index=True)
    wallet_id = Column(String, index=True)
    amount = Column(Float)
    odds = Column(Float)
    bet_result = Column(String, default="pending")
    status = Column(String, default="pending")

@strawberry.type
class Bet:
    id: strawberry.ID
    user_id: strawberry.ID
    match_id: strawberry.ID
    wallet_id: strawberry.ID
    amount: float
    odds: float
    bet_result: str
    status: str
    
@strawberry.type
class Query:
    @strawberry.field
    async def get_bet(self, id: strawberry.ID, info: strawberry.Info) -> Bet:
        db: AsyncSession = info.context["db"]
        try:
            bet_id_int = int(id)
        except ValueError:
            return None
        query = select(BetModel).where(BetModel.id == bet_id_int)
        result = await db.execute(query)
        db_bet = result.scalars().first()
        if not db_bet:
            return None
        return Bet(
            id=strawberry.ID(str(db_bet.id)),
            user_id=strawberry.ID(db_bet.user_id),
            match_id=strawberry.ID(db_bet.match_id),
            wallet_id=strawberry.ID(db_bet.wallet_id),
            amount=db_bet.amount,
            odds=db_bet.odds,
            bet_result=db_bet.bet_result,
            status=db_bet.status
        )
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_bet(
        self, 
        user_id: strawberry.ID,
        wallet_id: strawberry.ID, 
        match_id: strawberry.ID, 
        amount: float, 
        odds: float, 
        bet_result: str, 
        info: strawberry.Info
    ) -> Bet:
        request = info.context["request"]
        
        # Récupération de la session asynchrone
        db: AsyncSession = info.context["db"]

        user_age = request.headers.get("x-user-age")
        if user_age and int(user_age) < 18:
            print(user_age)
            raise Exception("User is underaged")

        db_bet = BetModel(
            user_id=user_id,
            match_id=match_id,
            wallet_id=wallet_id,
            amount=amount,
            odds=odds,
            bet_result=bet_result,
            status="pending"
        )

        try:
            db.add(db_bet)
            await db.commit()
            await db.refresh(db_bet)
        except Exception as e:
            await db.rollback()
            raise Exception(f"Erreur DB: {str(e)}")

        publish_bet_on_notification_exchange({"pattern":"bet_created", "data":{"user_id":db_bet.user_id, "match_id":db_bet.match_id}})
        publish_add_amount_on_wallet_exchange({"pattern":"bet_created","data":{"wallet_id":db_bet.wallet_id, "amount":db_bet.amount}})
        
        return Bet(
            id=strawberry.ID(str(db_bet.id)),
            user_id=strawberry.ID(db_bet.user_id),
            match_id=strawberry.ID(db_bet.match_id),
            wallet_id=strawberry.ID(db_bet.wallet_id),
            amount=db_bet.amount,
            odds=db_bet.odds,
            bet_result=db_bet.bet_result,
            status=db_bet.status
        )
bet_schema = Schema(query=Query, mutation=Mutation)