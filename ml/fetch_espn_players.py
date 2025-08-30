"""
Fetch all active NFL players from ESPN API (free, no auth)
"""
import requests
import pandas as pd
from typing import List, Dict


def get_espn_players(season: int = 2024) -> List[Dict]:
    """
    Get all NFL players from ESPN API
    ESPN has a public API that doesn't require authentication
    """
    players = []
    
    # ESPN's fantasy API endpoint for NFL players
    base_url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{season}"
    
    # Get all teams first
    teams_url = f"{base_url}/segments/0/leagues/0"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyBot/1.0)'}
    
    try:
        # ESPN method 1: Get player universe
        players_url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/players"
        params = {
            'view': 'players_wl',
            'limit': 2000,  # Adjust as needed
        }
        
        response = requests.get(players_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        for player_data in data.get('players', []):
            player = parse_espn_player(player_data)
            if player:
                players.append(player)
                
    except requests.RequestException as e:
        print(f"ESPN API error: {e}")
        # Fallback: try position-by-position
        players = get_espn_players_by_position(season)
    
    return players


def parse_espn_player(player_data: Dict) -> Dict:
    """Parse ESPN player data structure"""
    try:
        player_info = player_data.get('player', {})
        
        return {
            'espn_id': player_info.get('id'),
            'name': player_info.get('fullName', ''),
            'first_name': player_info.get('firstName', ''),
            'last_name': player_info.get('lastName', ''),
            'position': get_position_name(player_info.get('defaultPositionId', 0)),
            'team': get_team_name(player_info.get('proTeamId', 0)),
            'jersey_number': player_info.get('jersey', ''),
            'active': player_info.get('active', True),
            'injury_status': player_info.get('injuryStatus', 'ACTIVE')
        }
    except Exception as e:
        print(f"Error parsing player: {e}")
        return None


def get_position_name(position_id: int) -> str:
    """Convert ESPN position ID to readable name"""
    position_map = {
        1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 
        5: 'K', 16: 'D/ST', 17: 'LB', 18: 'DT',
        19: 'DE', 20: 'CB', 21: 'S', 22: 'DT', 23: 'DE'
    }
    return position_map.get(position_id, 'UNK')


def get_team_name(team_id: int) -> str:
    """Convert ESPN team ID to abbreviation"""
    # ESPN team ID mapping (partial)
    team_map = {
        1: 'ATL', 2: 'BUF', 3: 'CHI', 4: 'CIN', 5: 'CLE', 6: 'DAL',
        7: 'DEN', 8: 'DET', 9: 'GB', 10: 'TEN', 11: 'IND', 12: 'KC',
        13: 'LV', 14: 'LAR', 15: 'MIA', 16: 'MIN', 17: 'NE', 18: 'NO',
        19: 'NYG', 20: 'NYJ', 21: 'PHI', 22: 'ARI', 23: 'PIT', 24: 'LAC',
        25: 'SF', 26: 'SEA', 27: 'TB', 28: 'WSH', 29: 'CAR', 30: 'JAX',
        33: 'BAL', 34: 'HOU'
    }
    return team_map.get(team_id, 'FA')  # FA = Free Agent


def get_espn_players_by_position(season: int) -> List[Dict]:
    """Fallback method: get players by position"""
    players = []
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
    
    for pos in positions:
        try:
            url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/players"
            params = {
                'view': 'players_wl',
                'limit': 500,
                'filter': f'{{"filterActive":true,"filterPosition":["{pos}"]}}'
            }
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyBot/1.0)'}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            for player_data in data.get('players', []):
                player = parse_espn_player(player_data)
                if player:
                    players.append(player)
                    
        except Exception as e:
            print(f"Error fetching {pos} players: {e}")
    
    return players


if __name__ == '__main__':
    players = get_espn_players(2024)
    df = pd.DataFrame(players)
    print(f"Found {len(players)} active NFL players")
    print(df.head())
    
    # Save to file
    df.to_csv('espn_players.csv', index=False)
    df.to_json('espn_players.json', orient='records')
