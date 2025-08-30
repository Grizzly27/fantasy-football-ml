from urllib.parse import quote_plus
from .yahoo_client import YahooOAuthClient


def get_league_meta(client: YahooOAuthClient, game_code: str, season: int):
    # Example: /game/{game_key}/leagues
    path = f"/game/{quote_plus(game_code)}/leagues;season={season}?format=json"
    return client.get(path)


def get_team_roster(client: YahooOAuthClient, team_key: str):
    # team_key e.g. "nfl.l.123456.t.1"
    path = f"/team/{quote_plus(team_key)}/roster?format=json"
    return client.get(path)


def get_player_stats(client: YahooOAuthClient, player_ids, season=None, week=None):
    ids = ','.join(map(str,player_ids))
    path = f"/player/{quote_plus(ids)}/stats?format=json"
    params = {}
    if season: params['season'] = season
    if week: params['week'] = week
    return client.get(path, params=params)


def get_matchups(client: YahooOAuthClient, league_key: str, week=None):
    path = f"/league/{quote_plus(league_key)}/scoreboard?format=json"
    params = {}
    if week: params['week'] = week
    return client.get(path, params=params)
