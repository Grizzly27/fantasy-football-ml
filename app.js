const DATA_URL = './data.json';

let players = [];
let draftedStack = []; // stack for undo
let filter = 'ALL';
let search = '';
let currentSort = 'score';
let currentSecondarySort = '';
let sortAscending = false;

const playersList = document.getElementById('playersList');
const playersRemaining = document.getElementById('playersRemaining');
const lastUpdated = document.getElementById('lastUpdated');
const undoBtn = document.getElementById('undoBtn');
const searchInput = document.getElementById('searchInput');
const primarySortSelect = document.getElementById('primarySort');
const secondarySortSelect = document.getElementById('secondarySort');
const sortAsc = document.getElementById('sortAsc');
const sortDesc = document.getElementById('sortDesc');

function getInjuryColor(injury) {
  const status = injury?.toLowerCase() || 'healthy';
  switch(status) {
    case 'healthy': return '#30D158';
    case 'questionable': return '#FF9500';
    case 'doubtful': return '#FF9500';
    case 'out': return '#FF3B30';
    default: return '#30D158';
  }
}

function getConfidenceLevel(score, tier) {
  // Calculate confidence based on ML score and tier
  let confidence = 75; // Base confidence
  
  // Adjust for tier (higher tier = more confidence in that tier range)
  switch(tier) {
    case 1: confidence = Math.min(95, 85 + (score - 95) * 2); break;
    case 2: confidence = Math.min(90, 80 + (score - 85) * 1.5); break;
    case 3: confidence = Math.min(85, 75 + (score - 75) * 1.2); break;
    case 4: confidence = Math.min(80, 70 + (score - 65) * 1); break;
    default: confidence = Math.min(75, 60 + (score - 50) * 0.8);
  }
  
  confidence = Math.max(50, Math.round(confidence));
  
  const color = confidence >= 85 ? '#30D158' : 
                confidence >= 75 ? '#FF9500' : 
                confidence >= 65 ? '#FF9500' : '#FF3B30';
                
  return { level: confidence, color };
}

function sortPlayers(playersArray, primary, secondary = null, ascending = false) {
  return [...playersArray].sort((a, b) => {
    let primaryCompare = compareValues(a[primary], b[primary], ascending);
    if (primaryCompare !== 0 || !secondary) return primaryCompare;
    return compareValues(a[secondary], b[secondary], ascending);
  });
}

function compareValues(aVal, bVal, ascending) {
  // Handle null/undefined values
  if (aVal == null && bVal == null) return 0;
  if (aVal == null) return ascending ? -1 : 1;
  if (bVal == null) return ascending ? 1 : -1;
  
  if (typeof aVal === 'string') {
    return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
  }
  return ascending ? aVal - bVal : bVal - aVal;
}

async function loadData(){
  try{
    const res = await fetch(DATA_URL);
    players = await res.json();
    players.sort((a,b)=>b.score-a.score);
    hydrateFromLocal();
    render();
    
    // Update hero stats with formatted time
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
    lastUpdated.textContent = timeStr;
    
    // Load model metrics
    try {
      const metricsRes = await fetch('./ml_output/metrics.json');
      const metrics = await metricsRes.json();
      const avgRMSE = ((metrics.rf + metrics.xgb + metrics.lgb) / 3).toFixed(2);
      document.getElementById('modelAccuracy').textContent = `Ensemble RMSE: ${avgRMSE}`;
    } catch(e) {
      console.log('Could not load metrics:', e);
    }
    
  }catch(err){
    console.error('Failed loading data',err);
    // fallback: try localStorage data
    const raw = localStorage.getItem('ff_data');
    if(raw){players = JSON.parse(raw);} else {players = []}
    render();
  }
}

function hydrateFromLocal(){
  const drafted = JSON.parse(localStorage.getItem('ff_drafted')||'[]');
  if(drafted.length){
    // mark drafted
    for(const id of drafted){
      const p = players.find(x=>x.id===id);
      if(p){p._drafted=true}
    }
    draftedStack = drafted.slice();
  }
}

function saveDrafted(){
  const ids = players.filter(p=>p._drafted).map(p=>p.id);
  localStorage.setItem('ff_drafted',JSON.stringify(ids));
}

function render(){
  let visible = players.filter(p=>!p._drafted)
    .filter(p=>filter==='ALL' || p.pos===filter)
    .filter(p=>p.name.toLowerCase().includes(search));

  // Apply sorting
  visible = sortPlayers(visible, currentSort, currentSecondarySort, sortAscending);

  playersList.innerHTML = '';
  for(const p of visible){
    const card = document.createElement('div');
    card.className = 'player-card';
    card.setAttribute('data-id',p.id);
    card.setAttribute('data-tier',p.tier);
    card.setAttribute('data-position',p.pos);
    card.setAttribute('data-team',p.team);

    // Draft button
    const btn = document.createElement('button');
    btn.className = 'draft-btn';
    btn.title = 'Mark as drafted';
    btn.innerHTML = '✕';
    btn.addEventListener('click',()=>markDrafted(p.id,card));

    // Card content
    const content = document.createElement('div');
    content.className = 'card-content';

    // Player header
    const header = document.createElement('div');
    header.className = 'player-header';

    const playerInfo = document.createElement('div');
    playerInfo.className = 'player-info';

    // Player name row with team logo
    const nameRow = document.createElement('div');
    nameRow.className = 'player-name-row';
    
    const teamLogo = document.createElement('img');
    teamLogo.className = 'team-logo';
    teamLogo.src = window.TeamLogos ? window.TeamLogos.getTeamLogo(p.team) : '';
    teamLogo.alt = p.team;
    teamLogo.onerror = function() {
      this.style.display = 'none';
    };

    const name = document.createElement('h3');
    name.className = 'player-name';
    name.textContent = p.name;

    nameRow.appendChild(teamLogo);
    nameRow.appendChild(name);

    const meta = document.createElement('div');
    meta.className = 'player-meta';

    const posBadge = document.createElement('span');
    posBadge.className = 'pos-badge';
    posBadge.textContent = p.pos;

    const teamBadge = document.createElement('span');
    teamBadge.className = 'team-badge';
    teamBadge.textContent = p.team;

    const tierIndicator = document.createElement('span');
    tierIndicator.className = `tier-indicator tier-${p.tier}`;
    tierIndicator.textContent = `TIER ${p.tier}`;

    const byeWeek = document.createElement('span');
    byeWeek.className = 'bye-week';
    byeWeek.textContent = `BYE: ${p.bye_week || 'TBD'}`;

    const injuryStatus = document.createElement('span');
    injuryStatus.className = `injury-status ${p.injury?.toLowerCase() || 'healthy'}`;
    injuryStatus.innerHTML = `<span style="color: ${getInjuryColor(p.injury)}">●</span> ${p.injury || 'Healthy'}`;

    meta.appendChild(posBadge);
    meta.appendChild(teamBadge);
    meta.appendChild(tierIndicator);
    meta.appendChild(byeWeek);
    meta.appendChild(injuryStatus);

    playerInfo.appendChild(nameRow);
    playerInfo.appendChild(meta);

    // Score section
    const scoreSection = document.createElement('div');
    scoreSection.className = 'score-section';

    const mlScore = document.createElement('div');
    mlScore.className = 'ml-score tooltip';
    mlScore.textContent = p.score.toFixed(1);
    mlScore.setAttribute('data-tooltip', 'ML Ensemble Score: RF + XGBoost + LightGBM average prediction');

    const scoreLabel = document.createElement('div');
    scoreLabel.className = 'score-label';
    scoreLabel.textContent = 'ML Score';

    scoreSection.appendChild(mlScore);
    scoreSection.appendChild(scoreLabel);

    header.appendChild(playerInfo);
    header.appendChild(scoreSection);

    // Enhanced stats grid
    const statsExpanded = document.createElement('div');
    statsExpanded.className = 'player-stats-expanded';

    // Primary stats row
    const primaryStats = document.createElement('div');
    primaryStats.className = 'stat-row primary-stats';

    const projStat = document.createElement('div');
    projStat.className = 'stat-item tooltip';
    projStat.setAttribute('data-tooltip', 'Projected fantasy points per game based on 2024 season data');
    projStat.innerHTML = `
      <div class="stat-value">${p.proj}</div>
      <div class="stat-label">Proj PPG</div>
    `;

    const adpStat = document.createElement('div');
    adpStat.className = 'stat-item tooltip';
    adpStat.setAttribute('data-tooltip', 'Average Draft Position across fantasy platforms');
    adpStat.innerHTML = `
      <div class="stat-value">${p.adp}</div>
      <div class="stat-label">ADP</div>
    `;

    const consistencyStat = document.createElement('div');
    consistencyStat.className = 'stat-item tooltip';
    consistencyStat.setAttribute('data-tooltip', 'Week-to-week consistency rating (1-10 scale)');
    consistencyStat.innerHTML = `
      <div class="stat-value">${p.consistency_rating}</div>
      <div class="stat-label">Consistency</div>
    `;

    primaryStats.appendChild(projStat);
    primaryStats.appendChild(adpStat);
    primaryStats.appendChild(consistencyStat);

    // Secondary stats row
    const secondaryStats = document.createElement('div');
    secondaryStats.className = 'stat-row secondary-stats';

    const ceilingStat = document.createElement('div');
    ceilingStat.className = 'stat-item tooltip';
    ceilingStat.setAttribute('data-tooltip', 'Best case scenario weekly projection');
    ceilingStat.innerHTML = `
      <div class="stat-value">${p.ceiling_projection}</div>
      <div class="stat-label">Ceiling</div>
    `;

    const floorStat = document.createElement('div');
    floorStat.className = 'stat-item tooltip';
    floorStat.setAttribute('data-tooltip', 'Worst case scenario weekly projection');
    floorStat.innerHTML = `
      <div class="stat-value">${p.floor_projection}</div>
      <div class="stat-label">Floor</div>
    `;

    const redzoneStat = document.createElement('div');
    redzoneStat.className = 'stat-item tooltip';
    redzoneStat.setAttribute('data-tooltip', 'Red zone touches/targets per game');
    redzoneStat.innerHTML = `
      <div class="stat-value">${p.redzone_touches}</div>
      <div class="stat-label">RZ Touches</div>
    `;

    secondaryStats.appendChild(ceilingStat);
    secondaryStats.appendChild(floorStat);
    secondaryStats.appendChild(redzoneStat);

    statsExpanded.appendChild(primaryStats);
    statsExpanded.appendChild(secondaryStats);

    // Expandable advanced stats
    const expandBtn = document.createElement('button');
    expandBtn.className = 'expand-stats-btn';
    expandBtn.textContent = 'More Stats ▼';
    
    const advancedStats = document.createElement('div');
    advancedStats.className = 'advanced-stats hidden';
    
    const advancedRow = document.createElement('div');
    advancedRow.className = 'stat-row';
    
    const lastSeasonStat = document.createElement('div');
    lastSeasonStat.className = 'stat-item';
    lastSeasonStat.innerHTML = `
      <div class="stat-value">${p.last_season_points}</div>
      <div class="stat-label">2024 Points</div>
    `;
    
    const sosStat = document.createElement('div');
    sosStat.className = 'stat-item';
    sosStat.innerHTML = `
      <div class="stat-value">${p.strength_of_schedule}</div>
      <div class="stat-label">SOS</div>
    `;
    
    const ageStat = document.createElement('div');
    ageStat.className = 'stat-item';
    ageStat.innerHTML = `
      <div class="stat-value">${p.age}</div>
      <div class="stat-label">Age</div>
    `;
    
    advancedRow.appendChild(lastSeasonStat);
    advancedRow.appendChild(sosStat);
    advancedRow.appendChild(ageStat);
    advancedStats.appendChild(advancedRow);
    
    // Toggle functionality
    expandBtn.addEventListener('click', () => {
      const isHidden = advancedStats.classList.contains('hidden');
      advancedStats.classList.toggle('hidden');
      expandBtn.textContent = isHidden ? 'Less Stats ▲' : 'More Stats ▼';
    });

    content.appendChild(header);
    content.appendChild(statsExpanded);
    content.appendChild(expandBtn);
    content.appendChild(advancedStats);

    card.appendChild(btn);
    card.appendChild(content);

    playersList.appendChild(card);
  }
  
  const remaining = players.filter(p=>!p._drafted).length;
  const drafted = players.filter(p=>p._drafted).length;
  
  playersRemaining.textContent = `${remaining} players remaining`;
  document.getElementById('draftedCount').textContent = `${drafted} drafted`;
}

function markDrafted(id,card){
  // debounce double clicks
  if(card._animating) return;
  card._animating=true;
  const p = players.find(x=>x.id===id);
  if(!p) return;
  p._drafted = true;
  draftedStack.push(id);
  saveDrafted();

  // Enhanced animation
  card.classList.add('removing');
  setTimeout(()=>{
    render();
    card._animating=false;
  },300);
}

undoBtn.addEventListener('click',()=>{
  const last = draftedStack.pop();
  if(!last) return;
  const p = players.find(x=>x.id===last);
  if(p){p._drafted=false; saveDrafted(); render();}
});

// filters
document.querySelectorAll('.position-tab').forEach(b=>b.addEventListener('click',e=>{
  document.querySelectorAll('.position-tab').forEach(x=>x.classList.remove('active'));
  e.target.classList.add('active');
  filter = e.target.dataset.pos;
  render();
}));

searchInput.addEventListener('input',e=>{search = e.target.value.toLowerCase(); render();});

// init
loadData();

// expose for debugging
window.__ff = {players,render};
