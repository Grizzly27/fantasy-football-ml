"""
Master script to fetch all active NFL players from multiple sources
Priority: Sleeper API > ESPN API > NFL.com > Yahoo Fantasy
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
import json
from pathlib import Path


def fetch_all_nfl_players(season: int = 2024, output_dir: str = "data") -> pd.DataFrame:
    """
    Fetch all NFL players using the best available source
    Returns a comprehensive DataFrame with all active players
    """
    
    print(f"🏈 Fetching all active NFL players for {season} season...")
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Try sources in order of preference
    sources = [
        ("Sleeper API", fetch_sleeper_players),
        ("ESPN API", fetch_espn_players),  
        ("NFL.com API", fetch_nfl_players),
    ]
    
    players_df = None
    
    for source_name, fetch_func in sources:
        print(f"\n🔄 Trying {source_name}...")
        try:
            players = fetch_func(season)
            if players:
                players_df = pd.DataFrame(players)
                print(f"✅ {source_name}: Found {len(players)} players")
                
                # Save raw data
                filename = source_name.lower().replace(" ", "_").replace(".", "")
                players_df.to_csv(output_path / f"nfl_players_{filename}.csv", index=False)
                players_df.to_json(output_path / f"nfl_players_{filename}.json", orient='records')
                
                break
            else:
                print(f"❌ {source_name}: No data returned")
                
        except Exception as e:
            print(f"❌ {source_name}: Error - {e}")
    
    if players_df is None:
        print("❌ All sources failed. Using fallback data...")
        players_df = create_fallback_data()
    
    # Clean and standardize the data
    players_df = clean_player_data(players_df)
    
    # Save final cleaned data
    players_df.to_csv(output_path / "nfl_players_clean.csv", index=False)
    players_df.to_json(output_path / "nfl_players_clean.json", orient='records')
    
    print(f"\n🎉 Final dataset: {len(players_df)} players")
    print(f"💾 Saved to: {output_path}/nfl_players_clean.*")
    
    # Print summary stats
    print_player_summary(players_df)
    
    return players_df


def fetch_sleeper_players(season: int = 2024) -> List[Dict]:
    """Sleeper has the most comprehensive NFL player database"""
    url = "https://api.sleeper.app/v1/players/nfl"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyDraftBot/1.0)'}
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    players_dict = response.json()
    players = []
    
    for player_id, data in players_dict.items():
        # Filter for active players only
        if not data.get('active', False):
            continue
            
        # Skip players without teams (free agents might be inactive)
        if not data.get('team'):
            continue
            
        player = {
            'player_id': player_id,
            'name': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'position': data.get('position', ''),
            'team': data.get('team', ''),
            'jersey_number': data.get('number'),
            'height': data.get('height', ''),
            'weight': data.get('weight'),
            'age': data.get('age'),
            'college': data.get('college', ''),
            'rookie_year': data.get('rookie_year'),
            'years_exp': data.get('years_exp', 0),
            'fantasy_positions': ','.join(data.get('fantasy_positions', [])),
            'injury_status': data.get('injury_status', 'Healthy'),
            'depth_chart_position': data.get('depth_chart_position'),
            'depth_chart_order': data.get('depth_chart_order'),
            'search_full_name': data.get('search_full_name', ''),
            'source': 'sleeper'
        }
        players.append(player)
    
    return players


def fetch_espn_players(season: int = 2024) -> List[Dict]:
    """ESPN Fantasy API - good fallback option"""
    players = []
    
    # ESPN positions to fetch
    positions = [1, 2, 3, 4, 5, 16]  # QB, RB, WR, TE, K, D/ST
    
    for position_id in positions:
        try:
            url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{}/players".format(season)
            params = {
                'view': 'players_wl',
                'limit': 1000,
            }
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyDraftBot/1.0)'}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            for player_data in data.get('players', []):
                player_info = player_data.get('player', {})
                
                # Filter by position
                if player_info.get('defaultPositionId') != position_id:
                    continue
                
                player = {
                    'player_id': f"espn_{player_info.get('id')}",
                    'name': player_info.get('fullName', ''),
                    'first_name': player_info.get('firstName', ''),
                    'last_name': player_info.get('lastName', ''),
                    'position': get_espn_position_name(player_info.get('defaultPositionId', 0)),
                    'team': get_espn_team_name(player_info.get('proTeamId', 0)),
                    'jersey_number': player_info.get('jersey'),
                    'active': player_info.get('active', True),
                    'injury_status': player_info.get('injuryStatus', 'ACTIVE'),
                    'source': 'espn'
                }
                players.append(player)
                
        except Exception as e:
            print(f"ESPN position {position_id} error: {e}")
            continue
    
    return players


def fetch_nfl_players(season: int = 2024) -> List[Dict]:
    """NFL.com API - official but sometimes limited"""
    players = []
    teams = [
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
        'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
    ]
    
    for team in teams:
        try:
            # NFL.com roster endpoint (this URL may need adjustment)
            url = f"https://www.nfl.com/api/roster/team/{team}"
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyDraftBot/1.0)'}
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            team_data = response.json()
            
            for player_data in team_data.get('players', []):
                player = {
                    'player_id': f"nfl_{player_data.get('id')}",
                    'name': f"{player_data.get('firstName', '')} {player_data.get('lastName', '')}".strip(),
                    'first_name': player_data.get('firstName', ''),
                    'last_name': player_data.get('lastName', ''),
                    'position': player_data.get('position', ''),
                    'team': team,
                    'jersey_number': player_data.get('jerseyNumber'),
                    'height': player_data.get('height'),
                    'weight': player_data.get('weight'),
                    'college': player_data.get('college', ''),
                    'source': 'nfl'
                }
                players.append(player)
                
        except Exception as e:
            print(f"NFL team {team} error: {e}")
            continue
    
    return players


def get_espn_position_name(position_id: int) -> str:
    """Convert ESPN position ID to name"""
    mapping = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'D/ST'}
    return mapping.get(position_id, 'UNK')


def get_espn_team_name(team_id: int) -> str:
    """Convert ESPN team ID to abbreviation"""
    mapping = {
        1: 'ATL', 2: 'BUF', 3: 'CHI', 4: 'CIN', 5: 'CLE', 6: 'DAL',
        7: 'DEN', 8: 'DET', 9: 'GB', 10: 'TEN', 11: 'IND', 12: 'KC',
        13: 'LV', 14: 'LAR', 15: 'MIA', 16: 'MIN', 17: 'NE', 18: 'NO',
        19: 'NYG', 20: 'NYJ', 21: 'PHI', 22: 'ARI', 23: 'PIT', 24: 'LAC',
        25: 'SF', 26: 'SEA', 27: 'TB', 28: 'WAS', 29: 'CAR', 30: 'JAX',
        33: 'BAL', 34: 'HOU'
    }
    return mapping.get(team_id, 'FA')


def clean_player_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize player data"""
    # Remove duplicates based on name and team
    df = df.drop_duplicates(subset=['name', 'team'], keep='first')
    
    # Clean names
    df['name'] = df['name'].str.strip()
    df['first_name'] = df['first_name'].fillna('').str.strip()
    df['last_name'] = df['last_name'].fillna('').str.strip()
    
    # Standardize positions
    df['position'] = df['position'].fillna('UNK').str.upper()
    
    # Clean teams
    df['team'] = df['team'].fillna('FA').str.upper()
    
    # Only fantasy-relevant positions
    fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST', 'DEF']
    df = df[df['position'].isin(fantasy_positions)]
    
    # Sort by team and position
    df = df.sort_values(['team', 'position', 'name']).reset_index(drop=True)
    
    return df


def create_fallback_data() -> pd.DataFrame:
    """Create minimal fallback data if all APIs fail"""
    fallback_players = [
        {'name': 'Josh Allen', 'position': 'QB', 'team': 'BUF', 'source': 'fallback'},
        {'name': 'Lamar Jackson', 'position': 'QB', 'team': 'BAL', 'source': 'fallback'},
        {'name': 'Christian McCaffrey', 'position': 'RB', 'team': 'SF', 'source': 'fallback'},
        {'name': 'Derrick Henry', 'position': 'RB', 'team': 'TEN', 'source': 'fallback'},
        {'name': 'Davante Adams', 'position': 'WR', 'team': 'LV', 'source': 'fallback'},
        {'name': 'Tyreek Hill', 'position': 'WR', 'team': 'MIA', 'source': 'fallback'},
        {'name': 'Travis Kelce', 'position': 'TE', 'team': 'KC', 'source': 'fallback'},
        {'name': 'Mark Andrews', 'position': 'TE', 'team': 'BAL', 'source': 'fallback'},
    ]
    return pd.DataFrame(fallback_players)


def print_player_summary(df: pd.DataFrame):
    """Print summary statistics"""
    print("\n📊 Player Summary:")
    print(f"Total Players: {len(df)}")
    print("\nBy Position:")
    print(df['position'].value_counts().to_string())
    print("\nBy Team (top 10):")
    print(df['team'].value_counts().head(10).to_string())


if __name__ == '__main__':
    # Fetch all players
    players_df = fetch_all_nfl_players(2024, "data")
    
    # Show sample
    print("\n📋 Sample Players:")
    print(players_df[['name', 'position', 'team', 'source']].head(20).to_string(index=False))
