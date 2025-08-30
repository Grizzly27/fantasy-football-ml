import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from joblib import dump

ROOT = Path(__file__).resolve().parents[1]
DATA_IN = ROOT / 'data' / 'nfl_players_sleeper.csv'
OUT_DIR = ROOT / 'ml_output'
OUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load real NFL player data from Sleeper API"""
    if DATA_IN.exists():
        df = pd.read_csv(DATA_IN)
        print(f"Loaded {len(df)} players from Sleeper data")
        return df
    else:
        # Fallback to sample data if sleeper data not available
        with open(ROOT / 'data.json','r',encoding='utf-8') as f:
            data = json.load(f)
        print("Using fallback sample data")
        return pd.DataFrame(data)


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    """Create features from real NFL player data"""
    X = df.copy()
    
    # Handle missing values first
    X['age'] = pd.to_numeric(X['age'], errors='coerce').fillna(25)
    X['years_exp'] = pd.to_numeric(X['years_exp'], errors='coerce').fillna(0)  
    X['weight'] = pd.to_numeric(X['weight'], errors='coerce').fillna(200)
    X['depth_chart_order'] = pd.to_numeric(X['depth_chart_order'], errors='coerce').fillna(2)
    
    # Position encoding (one-hot)
    X['pos_rb'] = (X['position']=='RB').astype(int)
    X['pos_wr'] = (X['position']=='WR').astype(int) 
    X['pos_qb'] = (X['position']=='QB').astype(int)
    X['pos_te'] = (X['position']=='TE').astype(int)
    X['pos_k'] = (X['position']=='K').astype(int)
    X['pos_def'] = (X['position']=='DEF').astype(int)
    
    # Experience-based features
    X['is_rookie'] = (X['years_exp'] == 0).astype(int)
    X['is_veteran'] = (X['years_exp'] >= 5).astype(int)
    X['prime_age'] = ((X['age'] >= 24) & (X['age'] <= 29)).astype(int)
    
    # Depth chart features (starter vs backup)
    X['is_starter'] = (X['depth_chart_order'] == 1).astype(int)
    X['is_backup'] = (X['depth_chart_order'] == 2).astype(int)
    
    # Physical features
    X['weight_norm'] = X['weight'] / 250  # Normalize weight
    X['age_exp_ratio'] = X['age'] / (X['years_exp'] + 1)  # Age efficiency
    
    # Create synthetic target based on multiple factors
    # This is a placeholder - in real scenario you'd use historical fantasy points
    base_score = 50
    
    # Position scoring adjustments
    pos_multipliers = {'QB': 1.2, 'RB': 1.1, 'WR': 1.0, 'TE': 0.9, 'K': 0.6, 'DEF': 0.7}
    pos_scores = X['position'].map(pos_multipliers).fillna(0.5) * 40
    
    # Experience bonus (peaks around 3-7 years)
    exp_bonus = np.where(X['years_exp'] < 3, X['years_exp'] * 5,
                np.where(X['years_exp'] <= 7, 15 + (X['years_exp'] - 3) * 2,
                        23 - (X['years_exp'] - 7) * 1))
    
    # Age penalty (decline after 30)
    age_penalty = np.where(X['age'] <= 30, 0, (X['age'] - 30) * -2)
    
    # Depth chart bonus (starters get big boost)
    depth_bonus = np.where(X['depth_chart_order'] == 1, 20,
                  np.where(X['depth_chart_order'] == 2, 5, 0))
    
    # Add some controlled randomness for variation
    np.random.seed(42)
    random_factor = np.random.normal(0, 5, len(X))
    
    y = base_score + pos_scores + exp_bonus + age_penalty + depth_bonus + random_factor
    y = np.clip(y, 0, 100)  # Keep scores between 0-100
    
    # Select feature columns
    feature_cols = ['age', 'years_exp', 'weight_norm', 'depth_chart_order', 'age_exp_ratio',
                   'pos_rb', 'pos_wr', 'pos_qb', 'pos_te', 'pos_k', 'pos_def',
                   'is_rookie', 'is_veteran', 'prime_age', 'is_starter', 'is_backup']
    
    X_features = X[feature_cols].fillna(0)
    
    return X_features, y


def train_and_eval(X,y):
    """Train ensemble models and evaluate performance"""
    # Use cross-validation for better evaluation
    tscv = TimeSeriesSplit(n_splits=3)
    rmses = {}
    models = {}

    for name, Model in [('rf', RandomForestRegressor), ('xgb', XGBRegressor), ('lgb', LGBMRegressor)]:
        fold_rmse = []
        model = None
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            
            # Train model with better parameters
            if name == 'rf':
                model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
            elif name == 'xgb':
                model = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
            else:  # lgb
                model = LGBMRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1)
            
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            fold_rmse.append(rmse)
        
        rmses[name] = float(np.mean(fold_rmse))
        models[name] = model  # Keep the last trained model
        
        # Save the final model trained on all data
        final_scaler = StandardScaler()
        X_scaled = final_scaler.fit_transform(X)
        model.fit(X_scaled, y)
        
        dump(model, OUT_DIR / f'{name}.joblib')
        dump(final_scaler, OUT_DIR / f'{name}_scaler.joblib')

    return rmses


if __name__ == '__main__':
    print("🏈 Loading NFL player data...")
    df = load_data()
    print(f"✅ Loaded {len(df)} players")
    
    print("🔧 Creating features...")
    X, y = featurize(df)
    print(f"✅ Created {X.shape[1]} features for {len(X)} players")
    
    print("🤖 Training ensemble models...")
    rmses = train_and_eval(X, y)
    
    print("📊 Saving metrics...")
    with open(OUT_DIR / 'metrics.json', 'w', encoding='utf-8') as f:
        json.dump(rmses, f, indent=2)
    
    print("🎯 Generating predictions...")
    # Reload models and generate final predictions for all players
    from joblib import load
    
    # Load trained models and scalers
    rf_model = load(OUT_DIR / 'rf.joblib')
    xgb_model = load(OUT_DIR / 'xgb.joblib') 
    lgb_model = load(OUT_DIR / 'lgb.joblib')
    
    rf_scaler = load(OUT_DIR / 'rf_scaler.joblib')
    xgb_scaler = load(OUT_DIR / 'xgb_scaler.joblib')
    lgb_scaler = load(OUT_DIR / 'lgb_scaler.joblib')
    
    # Generate ensemble predictions
    rf_pred = rf_model.predict(rf_scaler.transform(X))
    xgb_pred = xgb_model.predict(xgb_scaler.transform(X)) 
    lgb_pred = lgb_model.predict(lgb_scaler.transform(X))
    
    # Ensemble average
    ensemble_pred = (rf_pred + xgb_pred + lgb_pred) / 3.0
    
    # Set random seed for reproducible enhanced stats
    np.random.seed(42)
    
    # Prepare output for the web app with enhanced stats
    output_players = []
    for idx, row in df.iterrows():
        if idx < len(ensemble_pred):  # Safety check
            injury_status = row.get('injury_status', 'Healthy')
            if isinstance(injury_status, str):
                injury_display = injury_status[:10] or 'Healthy'
            else:
                injury_display = 'Healthy'
            
            # Handle NaN values for depth chart
            depth_order = row.get('depth_chart_order', 2)
            if pd.isna(depth_order):
                depth_order = 2
                
            # Calculate enhanced stats
            base_proj = float(ensemble_pred[idx] * 0.8)
            age = int(row.get('age', 25)) if not pd.isna(row.get('age', 25)) else 25
            years_exp = int(row.get('years_exp', 0)) if not pd.isna(row.get('years_exp', 0)) else 0
            
            # Calculate ADP based on score (higher score = lower/better ADP)
            normalized_score = (ensemble_pred[idx] - ensemble_pred.min()) / (ensemble_pred.max() - ensemble_pred.min())
            adp = round(300 - (normalized_score * 280), 1)  # Range from ~20 to 300
            
            # Calculate consistency rating (0-10) based on age and experience
            consistency = min(10, max(1, 
                (years_exp * 1.5) + 
                (8 if 25 <= age <= 29 else 6 if age < 25 else max(2, 8 - (age - 29)))
            ))
            
            # Calculate ceiling and floor (variance based on consistency)
            variance = 11 - consistency  # Higher consistency = lower variance
            ceiling = base_proj + (variance * 2.5)
            floor = max(0, base_proj - (variance * 2))
            
            # Position-specific stats
            if row.get('position') in ['RB', 'QB']:
                carries = round(max(0, 20 - (depth_order * 8) + np.random.normal(0, 3)), 1)
                targets = round(max(0, 3 + np.random.normal(0, 2)), 1)
            elif row.get('position') in ['WR', 'TE']:
                carries = 0.0
                targets = round(max(0, 8 - (depth_order * 2) + np.random.normal(0, 2)), 1)
            else:
                carries = 0.0
                targets = 0.0
            
            # Red zone opportunities (based on position and depth)
            if row.get('position') in ['RB', 'TE']:
                redzone_touches = round(max(0, 3 - depth_order + np.random.normal(0, 0.5)), 1)
            elif row.get('position') == 'WR':
                redzone_touches = round(max(0, 2.5 - depth_order + np.random.normal(0, 0.5)), 1)
            else:
                redzone_touches = round(max(0, 1 + np.random.normal(0, 0.3)), 1)
            
            # Strength of schedule (random between 0.7-1.3, 1.0 = average)
            sos = round(0.7 + (np.random.random() * 0.6), 2)
            
            # Bye week (random between 4-14)
            bye_week = int(4 + (np.random.random() * 11))
            
            # Last season points (based on current projection with variance)
            last_season = round(base_proj * 17 + np.random.normal(0, 30), 1)  # 17 games
            last_season = max(0, last_season)
            
            player = {
                'id': idx + 1,
                'name': row.get('name', 'Unknown Player'),
                'pos': row.get('position', 'UNK'),
                'team': row.get('team', 'FA'),
                'score': round(float(ensemble_pred[idx]), 1),
                'proj': round(base_proj, 1),
                'snap': max(1, min(100, int((3 - depth_order) * 30 + 40))),  # Snap percentage
                'injury': injury_display,
                'tier': min(5, max(1, int((100 - ensemble_pred[idx]) // 15) + 1)),
                # Enhanced stats
                'adp': adp,
                'targets': targets,
                'carries': carries,
                'redzone_touches': redzone_touches,
                'strength_of_schedule': sos,
                'bye_week': bye_week,
                'age': age,
                'experience': years_exp,
                'last_season_points': last_season,
                'consistency_rating': round(consistency, 1),
                'ceiling_projection': round(ceiling, 1),
                'floor_projection': round(floor, 1)
            }
            output_players.append(player)
    
    # Sort by prediction score descending
    output_players.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep top 300 for the app (manageable size)
    output_players = output_players[:300]
    
    # Save predictions for the web app
    with open(OUT_DIR / 'predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output_players, f, indent=2)
    
    # Also update the main data.json file for the web app
    with open(ROOT / 'data.json', 'w', encoding='utf-8') as f:
        json.dump(output_players, f, indent=2)
    
    print(f"✅ Training complete!")
    print(f"📈 Model RMSEs: {rmses}")
    print(f"🎯 Generated predictions for top {len(output_players)} players")
    print(f"💾 Updated data.json for web app")
    print(f"\n🏆 Top 10 Players:")
    for i, player in enumerate(output_players[:10]):
        print(f"  {i+1:2d}. {player['name']:<20} {player['pos']:<3} {player['team']:<3} {player['score']:.1f}")
