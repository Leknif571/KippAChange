"""
Script pour créer des données de test pour le microservice MS-Calendar
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Forcer la sortie en UTF-8 sous Windows (évite UnicodeEncodeError pour les emojis)
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Ajouter le dossier src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy import select
from app.database import get_db_session
from app.models import Sport, Competition, Team, Match
from app.models.match import MatchStatus


async def get_or_create(session, model, defaults=None, **kwargs):
    q = await session.execute(select(model).filter_by(**kwargs))
    instance = q.scalar_one_or_none()
    if instance:
        return instance
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def create_test_data():
    """Créer des données de test complètes (idempotent)"""
    
    print("🌱 Création des données de test...")
    
    async with get_db_session() as session:
        football = await get_or_create(session, Sport, name="Football", code="FOOTBALL",
                                       defaults={"description": "Football / Soccer", "is_active": True})
        print(f"   ✅ {football.name} (ID: {football.id})")

        world_cup = await get_or_create(session, Competition, code="WC_EU",
                                        defaults={"name": "FIFA World Cup - Europe", "country": "Europe", "season": "2026", "sport_id": football.id, "is_active": True})

        print(f"   ✅ {world_cup.name} (ID: {world_cup.id})")

        def make_team_kwargs(name, short_name, code, logo_url, country, sport_id):
            return {"name": name, "short_name": short_name, "code": code, "logo_url": logo_url, "country": country, "sport_id": sport_id}

        teams_data = [
            make_team_kwargs("France", "FRA", "FRA", "https://example.com/fra.png", "France", football.id),
            make_team_kwargs("Germany", "GER", "GER", "https://example.com/ger.png", "Germany", football.id),
            make_team_kwargs("Spain", "ESP", "ESP", "https://example.com/esp.png", "Spain", football.id),
            make_team_kwargs("England", "ENG", "ENG", "https://example.com/eng.png", "England", football.id),
            make_team_kwargs("Portugal", "POR", "POR", "https://example.com/por.png", "Portugal", football.id),
            make_team_kwargs("Netherlands", "NED", "NED", "https://example.com/ned.png", "Netherlands", football.id),
            make_team_kwargs("Italy", "ITA", "ITA", "https://example.com/ita.png", "Italy", football.id),
            make_team_kwargs("Belgium", "BEL", "BEL", "https://example.com/bel.png", "Belgium", football.id),
            make_team_kwargs("Switzerland", "SUI", "SUI", "https://example.com/sui.png", "Switzerland", football.id),
            make_team_kwargs("Croatia", "CRO", "CRO", "https://example.com/cro.png", "Croatia", football.id),
        ]

        created_teams = []
        for t in teams_data:
            team = await get_or_create(session, Team, code=t["code"], defaults=t)
            created_teams.append(team)
        print(f"   ✅ {len(created_teams)} équipes nationales créées/confirmées")

        # 5. Matches — Coupe du Monde (Europe) : matchs tests
        now = datetime.utcnow()
        match_specs = [
            # (competition_id, home_id, away_id, match_date, status, venue, round, home_odds, draw_odds, away_odds)
            (world_cup.id, created_teams[0].id, created_teams[1].id, now + timedelta(days=5, hours=18), MatchStatus.SCHEDULED, "Stade de France", "Groupe A", 1.95, 3.20, 3.40),  # France vs Germany
            (world_cup.id, created_teams[2].id, created_teams[3].id, now + timedelta(days=6, hours=20), MatchStatus.SCHEDULED, "Wembley", "Groupe B", 2.10, 3.10, 3.30),        # Spain vs England
            (world_cup.id, created_teams[4].id, created_teams[5].id, now + timedelta(days=7, hours=16), MatchStatus.SCHEDULED, "Estádio da Luz", "Groupe C", 2.50, 3.30, 2.70),# Portugal vs Netherlands
            (world_cup.id, created_teams[6].id, created_teams[7].id, now + timedelta(days=8, hours=19), MatchStatus.SCHEDULED, "San Siro", "Groupe D", 2.40, 3.20, 2.90),      # Italy vs Belgium
            (world_cup.id, created_teams[8].id, created_teams[9].id, now + timedelta(days=9, hours=18), MatchStatus.SCHEDULED, "St. Jakob-Park", "Groupe E", 2.80, 3.10, 2.60),# Switzerland vs Croatia
            # un match en live pour test
            (world_cup.id, created_teams[0].id, created_teams[2].id, now - timedelta(minutes=30), MatchStatus.LIVE, "Stade Olympique", "Groupe F", 1.90, 3.40, 4.00),    # France vs Spain (live)
        ]

        for comp_id, home_id, away_id, mdate, status, venue, round_, home_odds, draw_odds, away_odds in match_specs:
            q = await session.execute(select(Match).filter_by(competition_id=comp_id, home_team_id=home_id, away_team_id=away_id, match_date=mdate))
            existing = q.scalar_one_or_none()
            if existing:
                continue
            m = Match(
                competition_id=comp_id,
                home_team_id=home_id,
                away_team_id=away_id,
                match_date=mdate,
                status=status,
                venue=venue,
                round=round_,
                home_odds=home_odds,
                draw_odds=draw_odds,
                away_odds=away_odds,
                score_home= (1 if status == MatchStatus.LIVE else 0),
                score_away= (0 if status == MatchStatus.LIVE else 0)
            )
            session.add(m)
        await session.commit()

        print(f"   ✅ seed terminé (idempotent)")

    print("\n✅ Données de test créées/confirmées avec succès !\n")
    print("🚀 Testez l'API GraphQL sur http://127.0.0.1:8000/graphql")


if __name__ == "__main__":
    asyncio.run(create_test_data())
