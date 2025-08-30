"""
Fetch all active NFL players from NFL.com API (free)
"""
import requests
import pandas as pd
from typing import List, Dict


def get_nfl_players(season: int = 2024) -> List[Dict]:
    """
    Get all NFL players from NFL.com API
    This is the most comprehensive free source
    """
    players = []
    
    # NFL.com roster endpoint
    base_url = "https://api.nfl.com/v1/rosterplayers"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; FantasyBot/1.0)',
        'Accept': 'application/json'
    }
    
    # Get all 32 NFL teams
    teams = get_nfl_teams()
    
    for team_abbr in teams:
        try:
            # NFL API endpoint for team rosters
            url = f"{base_url}?team={team_abbr}&season={season}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            team_data = response.json()
            team_players = parse_nfl_roster(team_data, team_abbr)
            players.extend(team_players)
            
        except requests.RequestException as e:
            print(f"Error fetching {team_abbr} roster: {e}")
            continue
    
    return players


def get_nfl_teams() -> List[str]:
    """Get all 32 NFL team abbreviations"""
    return [
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
        'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
    ]


def parse_nfl_roster(roster_data: Dict, team_abbr: str) -> List[Dict]:
    """Parse NFL.com roster response"""
    players = []
    
    for player_data in roster_data.get('players', []):
        try:
            player = {
                'nfl_id': player_data.get('id'),
                'name': f"{player_data.get('firstName', '')} {player_data.get('lastName', '')}".strip(),
                'first_name': player_data.get('firstName', ''),
                'last_name': player_data.get('lastName', ''),
                'position': player_data.get('position', ''),
                'team': team_abbr,
                'jersey_number': player_data.get('jerseyNumber', ''),
                'height': player_data.get('height', ''),
                'weight': player_data.get('weight', ''),
                'age': player_data.get('age', ''),
                'experience': player_data.get('experience', ''),
                'college': player_data.get('college', ''),
                'status': player_data.get('status', 'ACT'),
                'rookie_year': player_data.get('rookieYear', '')
            }
            players.append(player)
            
        except Exception as e:
            print(f"Error parsing player: {e}")
            continue
    
    return players


def get_sleeper_players() -> List[Dict]:
    """
    Alternative: Sleeper API (very comprehensive, free)
    Sleeper maintains an excellent player database
    """
    try:
        url = "https://api.sleeper.app/v1/players/nfl"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyBot/1.0)'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        players_dict = response.json()
        players = []
        
        for player_id, player_data in players_dict.items():
            if player_data.get('active', False):  # Only active players
                player = {
                    'sleeper_id': player_id,
                    'name': f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip(),
                    'first_name': player_data.get('first_name', ''),
                    'last_name': player_data.get('last_name', ''),
                    'position': player_data.get('position', ''),
                    'team': player_data.get('team', ''),
                    'jersey_number': player_data.get('number', ''),
                    'height': player_data.get('height', ''),
                    'weight': player_data.get('weight', ''),
                    'age': player_data.get('age', ''),
                    'college': player_data.get('college', ''),
                    'rookie_year': player_data.get('rookie_year', ''),
                    'years_exp': player_data.get('years_exp', 0),
                    'fantasy_positions': player_data.get('fantasy_positions', []),
                    'injury_status': player_data.get('injury_status', ''),
                    'depth_chart_position': player_data.get('depth_chart_position', ''),
                    'depth_chart_order': player_data.get('depth_chart_order', ''),
                }
                players.append(player)
        
        return players
        
    except Exception as e:
        print(f"Sleeper API error: {e}")
        return []


if __name__ == '__main__':
    print("Fetching NFL players...")
    
    # Method 1: NFL.com
    print("Trying NFL.com API...")
    nfl_players = get_nfl_players(2024)
    print(f"NFL.com: {len(nfl_players)} players")
    
    # Method 2: Sleeper (most comprehensive)
    print("Trying Sleeper API...")
    sleeper_players = get_sleeper_players()
    print(f"Sleeper: {len(sleeper_players)} players")
    
    # Use Sleeper if available (most complete), otherwise NFL.com
    if sleeper_players:
        players_df = pd.DataFrame(sleeper_players)
        players_df.to_csv('all_nfl_players_sleeper.csv', index=False)
        players_df.to_json('all_nfl_players_sleeper.json', orient='records')
        print("Saved Sleeper data to all_nfl_players_sleeper.*")
    elif nfl_players:
        players_df = pd.DataFrame(nfl_players)
        players_df.to_csv('all_nfl_players_nfl.csv', index=False)
        players_df.to_json('all_nfl_players_nfl.json', orient='records')
        print("Saved NFL.com data to all_nfl_players_nfl.*")
    
    print(f"Sample players:")
    print(players_df.head())
