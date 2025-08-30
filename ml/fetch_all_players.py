"""
Fetch all active NFL players from Yahoo Fantasy API
"""
import os
from ml.yahoo_client import YahooOAuthClient
from ml.yahoo_utils import get_player_stats
import pandas as pd


def get_all_yahoo_players(client: YahooOAuthClient, season=2024):
    """
    Get all active NFL players from Yahoo Fantasy API
    Note: Yahoo requires specific player IDs or game context
    """
    # Yahoo approach: get players from a specific league or game
    game_key = f"nfl.{season}"
    
    # Method 1: Get players from league rosters (requires league access)
    # Method 2: Get players from game stats (broader access)
    
    # This is a simplified example - Yahoo typically requires iterating through
    # team rosters or using specific player search endpoints
    
    try:
        # Example endpoint - actual implementation depends on Yahoo API structure
        path = f"/game/{game_key}/players?format=json"
        response = client.get(path)
        return parse_yahoo_players(response)
    except Exception as e:
        print(f"Yahoo API error: {e}")
        return []


def parse_yahoo_players(response):
    """Parse Yahoo API response to extract player data"""
    players = []
    # Yahoo returns nested XML-like JSON structure
    # This is a template - adjust based on actual response structure
    
    fantasy_content = response.get('fantasy_content', {})
    game = fantasy_content.get('game', {})
    player_list = game.get('players', {})
    
    # Navigate Yahoo's nested structure
    for player_data in player_list.get('player', []):
        if isinstance(player_data, dict):
            player = {
                'yahoo_id': player_data.get('player_key'),
                'name': player_data.get('name', {}).get('full', ''),
                'position': player_data.get('display_position', ''),
                'team': player_data.get('editorial_team_abbr', ''),
                'status': player_data.get('status', ''),
                'injury_note': player_data.get('injury_note', '')
            }
            players.append(player)
    
    return players


if __name__ == '__main__':
    # Requires valid Yahoo OAuth tokens
    client = YahooOAuthClient()
    players = get_all_yahoo_players(client)
    df = pd.DataFrame(players)
    print(f"Found {len(players)} players")
    print(df.head())
