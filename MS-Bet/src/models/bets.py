import strawberry
from strawberry.federation import Schema
from src.MBManager import publish_bet_on_notification_exchange

@strawberry.type
class Bet:
    id: strawberry.ID
    user_id: strawberry.ID
    match_id: strawberry.ID
    amount: float
    odds: float
    status: str
    
@strawberry.type
class Query:
    @strawberry.field
    def get_bet(self, id: strawberry.ID) -> Bet:
        # Placeholder implementation
        return Bet(
            id=id,
            user_id="1",
            match_id="101",
            amount=100.0,
            odds=2.5,
            status="pending"
        )
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_bet(self, user_id: strawberry.ID, match_id: strawberry.ID, amount: float, odds: float) -> Bet:
        print("Création du pari dans la bdd")
        return Bet(
            id="1",
            user_id=user_id,
            match_id=match_id,
            amount=amount,
            odds=odds,
            status="pending"
        )
bet_schema = Schema(query=Query, mutation=Mutation)