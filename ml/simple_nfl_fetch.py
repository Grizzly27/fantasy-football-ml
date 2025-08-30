"""
Simple working script to get NFL players from Sleeper API
Sleeper is the most reliable free source for NFL player data
"""
import requests
import pandas as pd
import json
from pathlib import Path


def get_all_nfl_players_sleeper():
    """
    Get all active NFL players from Sleeper API
    This is the most reliable free source
    """
    print("🏈 Fetching NFL players from Sleeper API...")
    
    try:
        url = "https://api.sleeper.app/v1/players/nfl"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; FantasyDraftBot/1.0)'}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print("✅ Successfully fetched player data")
        players_dict = response.json()
        
        # Convert to list of active players
        players = []
        active_count = 0
        
        for player_id, data in players_dict.items():
            # Only include active players
            if not data.get('active', False):
                continue
                
            # Skip players without teams (free agents/inactive)
            if not data.get('team'):
                continue
            
            active_count += 1
            
            # Create player record
            fantasy_pos = data.get('fantasy_positions', [])
            fantasy_pos_str = ','.join(fantasy_pos) if fantasy_pos else ''
            
            player = {
                'player_id': player_id,
                'name': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'position': data.get('position', ''),
                'team': data.get('team', ''),
                'jersey_number': data.get('number', ''),
                'height': data.get('height', ''),
                'weight': data.get('weight', 0),
                'age': data.get('age', 0),
                'college': data.get('college', ''),
                'rookie_year': data.get('rookie_year', 0),
                'years_exp': data.get('years_exp', 0),
                'fantasy_positions': fantasy_pos_str,
                'injury_status': data.get('injury_status', ''),
                'depth_chart_position': data.get('depth_chart_position', ''),
                'depth_chart_order': data.get('depth_chart_order', 0),
                'active': data.get('active', False)
            }
            players.append(player)
        
        print(f"✅ Processed {active_count} active players")
        
        # Convert to DataFrame
        df = pd.DataFrame(players)
        
        # Clean and filter
        df = df[df['position'].isin(['QB', 'RB', 'WR', 'TE', 'K', 'DEF'])].copy()
        df = df.sort_values(['team', 'position', 'name']).reset_index(drop=True)
        
        # Save files
        Path('data').mkdir(exist_ok=True)
        df.to_csv('data/nfl_players_sleeper.csv', index=False)
        df.to_json('data/nfl_players_sleeper.json', orient='records')
        
        print(f"💾 Saved {len(df)} fantasy-relevant players to data/")
        
        # Print summary
        print(f"\n📊 Player Summary:")
        print(f"Total Fantasy Players: {len(df)}")
        print("\nBy Position:")
        for pos, count in df['position'].value_counts().items():
            print(f"  {pos}: {count}")
        
        print(f"\nBy Team (sample):")
        for team, count in df['team'].value_counts().head(10).items():
            print(f"  {team}: {count}")
        
        print(f"\n📋 Sample Players:")
        sample = df[['name', 'position', 'team', 'age', 'years_exp']].head(15)
        print(sample.to_string(index=False))
        
        return df
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == '__main__':
    players_df = get_all_nfl_players_sleeper()
    
    if players_df is not None:
        print(f"\n🎉 Success! {len(players_df)} players ready for ML pipeline")
    else:
        print("❌ Failed to fetch player data")
