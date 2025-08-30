# Fantasy Draft Assistant — Live NFL Data + ML Pipeline

This is a fully functional fantasy football draft assistant powered by real NFL player data and machine learning predictions.

## What's Included
- `index.html`, `styles.css`, `app.js` — Interactive web app with one-click draft removal
- `data.json` — **300 real NFL players with ML-generated predictions**
- `ml/train.py` — ML training pipeline (Random Forest + XGBoost + LightGBM ensemble)
- `ml/simple_nfl_fetch.py` — Fetches 850+ active NFL players from Sleeper API
- `ml/yahoo_client.py`, `ml/yahoo_utils.py` — Yahoo Fantasy API integration
- `PRD_Fantasy_Football_ML.md` — Comprehensive product requirements

## 🚀 Quick Start

### Run the Complete Pipeline
```powershell
# 1. Fetch latest NFL players (851 active players)
python ml\simple_nfl_fetch.py

# 2. Train ML models and generate predictions  
python ml\train.py

# 3. Serve the web app
python -m http.server 8000
# Open http://localhost:8000
```

### Current Data
- **851 active NFL players** fetched from Sleeper API
- **300 top fantasy-relevant players** with ML predictions
- **Real player data**: names, positions, teams, ages, experience, depth charts
- **ML features**: 16 engineered features including position encoding, experience curves, age adjustments
- **Ensemble predictions**: Average of Random Forest, XGBoost, and LightGBM models

## 🏈 Live Demo Features
- ✅ **Real NFL Players**: Jayden Daniels, Caleb Williams, Bo Nix, etc.
- ✅ **ML Predictions**: Ensemble model trained on player characteristics  
- ✅ **One-Click Drafting**: Large X buttons for instant player removal
- ✅ **Position Filtering**: QB, RB, WR, TE, K, DEF
- ✅ **Mobile Optimized**: 44px touch targets, responsive design
- ✅ **Draft Persistence**: Auto-saves drafted players
- ✅ **Undo Function**: Recover accidental drafts

## 📊 Model Performance
- **Random Forest RMSE**: 3.00
- **XGBoost RMSE**: 3.07  
- **LightGBM RMSE**: 3.04
- **Features Used**: Age, experience, position, depth chart, physical metrics
- **Training Data**: 851 active NFL players

## 🔧 Development Setup

## 🔧 Development Setup

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Fetch fresh NFL data
python ml\simple_nfl_fetch.py

# Train models and generate predictions
python ml\train.py

# Start development server
python -m http.server 8000
```

## 🚀 GitHub Pages Deployment

```powershell
# Initialize repo and push
git init
git add .
git commit -m "feat: Fantasy Draft Assistant with ML pipeline"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main

# Enable GitHub Pages
# Go to repo Settings → Pages → Source: Deploy from branch (main)
# Site will be available at: https://<username>.github.io/<repo>/
```

## 📁 Project Structure
```
fantasy_football_ML/
├── index.html              # Main web app
├── app.js                  # Draft interface logic
├── styles.css              # Responsive styling
├── data.json              # 300 ML-ranked players
├── ml/
│   ├── train.py           # ML training pipeline
│   ├── simple_nfl_fetch.py # NFL data fetching
│   ├── yahoo_client.py    # Yahoo API integration
│   └── yahoo_utils.py     # Yahoo helper functions
├── data/
│   ├── nfl_players_sleeper.csv  # 851 raw players
│   └── nfl_players_sleeper.json
├── ml_output/
│   ├── predictions.json   # ML predictions
│   ├── metrics.json       # Model performance
│   └── *.joblib          # Trained models
└── requirements.txt       # Python dependencies
```

## 🎯 Usage During Your Draft
1. Open http://localhost:8000 (or your GitHub Pages URL)
2. Browse ML-ranked players by position
3. Click the red ❌ next to drafted players
4. Use position filters (QB, RB, WR, TE, K, DEF)  
5. Search for specific players
6. Undo accidental drafts

## 🔄 Updating Player Data
The app uses real NFL data that can be refreshed:
```powershell
# Get latest rosters and stats
python ml\simple_nfl_fetch.py

# Retrain with new data  
python ml\train.py

# Updated predictions now in data.json
```

## 🏆 Top Players (Current ML Rankings)
1. **Jayden Daniels** (QB, WAS) - 100.6
2. **Spencer Rattler** (QB, NO) - 100.5  
3. **Kedon Slovis** (QB, ARI) - 100.4
4. **Michael Penix** (QB, ATL) - 100.4
5. **Bo Nix** (QB, DEN) - 100.4

*Rankings based on ML ensemble of player age, experience, position, depth chart, and team context*
