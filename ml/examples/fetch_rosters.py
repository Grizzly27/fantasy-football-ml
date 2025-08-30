"""Example: fetch team roster and convert to pandas DataFrame"""
import os
import pandas as pd
from ml.yahoo_client import YahooOAuthClient
from ml.yahoo_utils import get_team_roster


def parse_roster_response(resp):
    # This parser is conservative; inspect resp structure and adapt
    players = []
    # Yahoo often nests under fantasy_content -> team -> roster -> 0 -> players -> 0 -> player
    fc = resp.get('fantasy_content', {})
    team = fc.get('team', {})
    roster = team.get('roster', {})
    # find player lists under roster
    # naive traversal
    def walk(d):
        if isinstance(d, dict):
            for k,v in d.items():
                if k == 'player':
                    if isinstance(v, list):
                        for p in v:
                            players.append(p)
                    else:
                        players.append(v)
                else:
                    walk(v)
        elif isinstance(d, list):
            for item in d:
                walk(item)
    walk(roster)
    # flatten player entries
    out = []
    for p in players:
        pid = p.get('player_key') or p.get('player_id') or p.get('player_id')
        name = p.get('name', {}).get('full') if isinstance(p.get('name'), dict) else p.get('name')
        pos = p.get('display_position') or p.get('position')
        team = p.get('editorial_team_abbr') or p.get('team')
        out.append({'player_key':pid,'name':name,'pos':pos,'team':team})
    return out


def main():
    client = YahooOAuthClient()
    # Set your team_key here
    team_key = os.getenv('YAHOO_TEAM_KEY') or 'nfl.l.123456.t.1'
    resp = get_team_roster(client, team_key)
    rows = parse_roster_response(resp)
    df = pd.DataFrame(rows)
    print(df.head())

if __name__ == '__main__':
    main()
