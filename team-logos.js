// NFL Team Logo System
const TEAM_LOGOS = {
  // AFC East
  'BUF': 'https://a.espncdn.com/i/teamlogos/nfl/500/buf.png',
  'MIA': 'https://a.espncdn.com/i/teamlogos/nfl/500/mia.png',
  'NE': 'https://a.espncdn.com/i/teamlogos/nfl/500/ne.png',
  'NYJ': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
  
  // AFC North
  'BAL': 'https://a.espncdn.com/i/teamlogos/nfl/500/bal.png',
  'CIN': 'https://a.espncdn.com/i/teamlogos/nfl/500/cin.png',
  'CLE': 'https://a.espncdn.com/i/teamlogos/nfl/500/cle.png',
  'PIT': 'https://a.espncdn.com/i/teamlogos/nfl/500/pit.png',
  
  // AFC South
  'HOU': 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png',
  'IND': 'https://a.espncdn.com/i/teamlogos/nfl/500/ind.png',
  'JAX': 'https://a.espncdn.com/i/teamlogos/nfl/500/jax.png',
  'TEN': 'https://a.espncdn.com/i/teamlogos/nfl/500/ten.png',
  
  // AFC West
  'DEN': 'https://a.espncdn.com/i/teamlogos/nfl/500/den.png',
  'KC': 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png',
  'LV': 'https://a.espncdn.com/i/teamlogos/nfl/500/lv.png',
  'LAC': 'https://a.espncdn.com/i/teamlogos/nfl/500/lac.png',
  
  // NFC East
  'DAL': 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png',
  'NYG': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png',
  'PHI': 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png',
  'WAS': 'https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png',
  
  // NFC North
  'CHI': 'https://a.espncdn.com/i/teamlogos/nfl/500/chi.png',
  'DET': 'https://a.espncdn.com/i/teamlogos/nfl/500/det.png',
  'GB': 'https://a.espncdn.com/i/teamlogos/nfl/500/gb.png',
  'MIN': 'https://a.espncdn.com/i/teamlogos/nfl/500/min.png',
  
  // NFC South
  'ATL': 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png',
  'CAR': 'https://a.espncdn.com/i/teamlogos/nfl/500/car.png',
  'NO': 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png',
  'TB': 'https://a.espncdn.com/i/teamlogos/nfl/500/tb.png',
  
  // NFC West
  'ARI': 'https://a.espncdn.com/i/teamlogos/nfl/500/ari.png',
  'LAR': 'https://a.espncdn.com/i/teamlogos/nfl/500/lar.png',
  'SF': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
  'SEA': 'https://a.espncdn.com/i/teamlogos/nfl/500/sea.png',
  
  // Fallback for unknown teams
  'FA': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiM2ZTZlNzMiLz4KPHRleHQgeD0iNTAlIiB5PSI1NSUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWkiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5GQTwvdGV4dD4KPC9zdmc+',
  'UNK': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiM4Njg2OGIiLz4KPHR2eHQgeD0iNTAlIiB5PSI1NSUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWkiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj4/PC90ZXh0Pgo8L3N2Zz4='
};

// Team color mappings for additional styling
const TEAM_COLORS = {
  'ARI': '#97233F', 'ATL': '#A71930', 'BAL': '#241773', 'BUF': '#00338D',
  'CAR': '#0085CA', 'CHI': '#0B162A', 'CIN': '#FB4F14', 'CLE': '#311D00',
  'DAL': '#003594', 'DEN': '#FB4F14', 'DET': '#0076B6', 'GB': '#203731',
  'HOU': '#03202F', 'IND': '#002C5F', 'JAX': '#006778', 'KC': '#E31837',
  'LV': '#000000', 'LAC': '#0080C6', 'LAR': '#003594', 'MIA': '#008E97',
  'MIN': '#4F2683', 'NE': '#002244', 'NO': '#D3BC8D', 'NYG': '#0B2265',
  'NYJ': '#125740', 'PHI': '#004C54', 'PIT': '#FFB612', 'SF': '#AA0000',
  'SEA': '#002244', 'TB': '#D50A0A', 'TEN': '#0C2340', 'WAS': '#5A1414'
};

// Function to get team logo with fallback
function getTeamLogo(team) {
  return TEAM_LOGOS[team] || TEAM_LOGOS['UNK'];
}

// Function to get team primary color
function getTeamColor(team) {
  return TEAM_COLORS[team] || '#6e6e73';
}

// Export for use in main app
window.TeamLogos = {
  getTeamLogo,
  getTeamColor,
  TEAM_LOGOS,
  TEAM_COLORS
};
