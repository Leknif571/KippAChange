import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.database import get_db_session, init_db
from app.models import Sport, Competition, Team, Match
from app.models.match import MatchStatus


async def seed():
    """Crée les données de test pour MS-Calendar"""
    print("🚀 Initialisation de la base de données...", flush=True)
    await init_db()

    async with get_db_session() as session:
        # Vérifier si des données existent déjà
        q = await session.execute(select(Sport))
        existing_sport = q.scalar_one_or_none()
        
        if existing_sport:
            q2 = await session.execute(select(Match))
            matches = q2.scalars().all()
            print(f"⚠️  Données déjà présentes: {len(matches)} match(s)", flush=True)
            
            if len(matches) > 0:
                print("🔄 Pour recréer les données, lance d'abord: python -m app.scripts.reset_data", flush=True)
                return
            else:
                print("🔄 Sport existe mais pas de matchs, on continue le seed...", flush=True)

        # 1. Créer le sport Football
        print("⚽ Création du sport Football...", flush=True)
        football = Sport(
            name="Football",
            code="FOOTBALL",
            description="Football / Soccer",
            is_active=True
        )
        session.add(football)
        await session.commit()
        await session.refresh(football)

        # 2. Créer les compétitions
        print("🏆 Création des compétitions...", flush=True)
        competitions_data = [
            ("FIFA World Cup 2026", "WC_2026", "International", "2026"),
            ("UEFA Champions League", "UCL", "Europe", "2025-2026"),
            ("Ligue 1", "L1", "France", "2025-2026"),
        ]
        competitions = []
        for name, code, country, season in competitions_data:
            comp = Competition(
                name=name,
                code=code,
                country=country,
                season=season,
                sport_id=football.id,
                is_active=True
            )
            session.add(comp)
            competitions.append(comp)
        await session.commit()
        for c in competitions:
            await session.refresh(c)

        # 3. Créer les équipes
        print("👕 Création des équipes...", flush=True)
        teams_data = [
            ("France", "FRA", "France"),
            ("Germany", "GER", "Germany"),
            ("Spain", "ESP", "Spain"),
            ("England", "ENG", "England"),
            ("Portugal", "POR", "Portugal"),
            ("Italy", "ITA", "Italy"),
            ("Brazil", "BRA", "Brazil"),
            ("Argentina", "ARG", "Argentina"),
            ("Netherlands", "NED", "Netherlands"),
            ("Belgium", "BEL", "Belgium"),
            ("Paris Saint-Germain", "PSG", "France"),
            ("Real Madrid", "RMA", "Spain"),
            ("FC Barcelona", "BAR", "Spain"),
            ("Manchester City", "MCI", "England"),
            ("Bayern Munich", "BAY", "Germany"),
            ("Olympique de Marseille", "OM", "France"),
        ]
        teams = {}
        for name, code, country in teams_data:
            t = Team(
                name=name,
                short_name=code,
                code=code,
                country=country,
                sport_id=football.id
            )
            session.add(t)
            teams[code] = t
        await session.commit()
        for t in teams.values():
            await session.refresh(t)

        # 4. Créer les matchs
        print("📅 Création des matchs...", flush=True)
        now = datetime.now(timezone.utc)
        
        matches_data = [
            # World Cup 2026
            (competitions[0].id, teams["FRA"].id, teams["GER"].id, now + timedelta(days=5, hours=20), "Stade de France", "Groupe A", None, None, None),
            (competitions[0].id, teams["ESP"].id, teams["ENG"].id, now + timedelta(days=6, hours=18), "Wembley Stadium", "Groupe B", None, None, None),
            (competitions[0].id, teams["POR"].id, teams["ITA"].id, now + timedelta(days=7, hours=20), "Estádio da Luz", "Groupe C", None, None, None),
            (competitions[0].id, teams["BRA"].id, teams["ARG"].id, now + timedelta(days=8, hours=21), "Maracanã", "Groupe D", None, None, None),
            (competitions[0].id, teams["NED"].id, teams["BEL"].id, now + timedelta(days=9, hours=18), "Johan Cruyff Arena", "Groupe E", None, None, None),
            
            # Champions League - avec cotes (pariables)
            (competitions[1].id, teams["PSG"].id, teams["RMA"].id, now + timedelta(days=3, hours=21), "Parc des Princes", "Huitièmes - Aller", 2.10, 3.40, 3.20),
            (competitions[1].id, teams["BAR"].id, teams["MCI"].id, now + timedelta(days=4, hours=21), "Camp Nou", "Huitièmes - Aller", 2.80, 3.30, 2.50),
            (competitions[1].id, teams["BAY"].id, teams["PSG"].id, now + timedelta(days=10, hours=21), "Allianz Arena", "Huitièmes - Retour", 1.85, 3.60, 4.00),
            
            # Ligue 1 - avec cotes (pariables)
            (competitions[2].id, teams["PSG"].id, teams["OM"].id, now + timedelta(days=2, hours=21), "Parc des Princes", "Journée 22", 1.45, 4.50, 6.00),
        ]

        for comp_id, home_id, away_id, mdate, venue, rnd, home_odds, draw_odds, away_odds in matches_data:
            is_bettable = home_odds is not None
            m = Match(
                competition_id=comp_id,
                home_team_id=home_id,
                away_team_id=away_id,
                match_date=mdate,
                status=MatchStatus.SCHEDULED,
                venue=venue,
                round=rnd,
                home_odds=home_odds,
                draw_odds=draw_odds,
                away_odds=away_odds,
                is_bettable=is_bettable
            )
            session.add(m)

        await session.commit()

        # Résumé
        q_matches = await session.execute(select(Match))
        all_matches = q_matches.scalars().all()
        bettable = [m for m in all_matches if m.is_bettable]
        
        print(f"\n✅ Seed terminé avec succès !", flush=True)
        print(f"   - {len(teams)} équipes créées", flush=True)
        print(f"   - {len(competitions)} compétitions créées", flush=True)
        print(f"   - {len(all_matches)} matchs créés ({len(bettable)} pariables)", flush=True)


def main():
    asyncio.run(seed())


if __name__ == "__main__":
    main()

#commande à lancer pour appliquer le script et générer les données de test
#python -m app.scripts.seed_data.py

#les requetes grphql pour tester 
# query {
#   getUpcomingMatches(daysAhead: 14, limit: 10) {
#     id
#     matchDate
#     homeTeam { name }
#     awayTeam { name }
#     competition { name }
#     homeOdds
#     drawOdds
#     awayOdds
#     isBettable
#   }
# }
# mutation {
#   setMatchOdds(matchId: 1, homeOdds: 1.85, drawOdds: 3.40, awayOdds: 4.20) {
#     id
#     homeTeam { name }
#     awayTeam { name }
#     homeOdds
#     drawOdds
#     awayOdds
#     isBettable
#   }
# }
# query {
#   getBettableMatches(limit: 10) {
#     id
#     matchDate
#     homeTeam { name }
#     awayTeam { name }
#     homeOdds
#     drawOdds
#     awayOdds
#     isBettable
#   }
# }