import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier

recommendation_map = ["Improve sleep", "Increase activity", "Adjust diet", "Maintain lifestyle"]

def train_and_load_model():
    np.random.seed(42)
    num_samples = 500
    data = {
        'age': np.random.randint(18, 70, num_samples),
        'gender': np.random.randint(0, 2, num_samples),
        'weight': np.random.randint(45, 100, num_samples),
        'height': np.round(np.random.uniform(1.5, 2.0, num_samples), 2),
        'activity_level': np.random.randint(1, 6, num_samples),
        'sleep_hours': np.round(np.random.uniform(4, 9, num_samples), 1),
        'diet_score': np.random.randint(1, 5, num_samples)
    }
    df = pd.DataFrame(data)
    
    y = np.stack([
        (df['sleep_hours'] < 6).astype(int),
        (df['activity_level'] < 3).astype(int),
        (df['diet_score'] < 3).astype(int),
        ((df['sleep_hours'] >= 6) & (df['activity_level'] >= 3) & (df['diet_score'] >= 3)).astype(int)
    ], axis=1)

    X = df[['age', 'gender', 'weight', 'height', 'activity_level', 'sleep_hours', 'diet_score']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
    model.fit(X_scaled, y)
    
    return model, scaler

def predict_lifestyle(age, gender, weight, height, activity, sleep, diet, model, scaler):
    gender_val = 0 if gender.upper() == "M" else 1
    user_input = np.array([[age, gender_val, weight, height, activity, sleep, diet]])
    user_input_scaled = scaler.transform(user_input)
    
    pred_probs = model.predict_proba(user_input_scaled)
    probs = [p[0][1] for p in pred_probs] 
    
    recommendations = [recommendation_map[i] for i, p in enumerate(probs) if p > 0.5]
    
    return {"probabilities": probs, "recommendations": recommendations}