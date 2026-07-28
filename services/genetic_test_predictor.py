import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import streamlit as st

@st.cache_resource
def train_genetic_model():
    # Try local path first, then data/ path
    try:
        df = pd.read_csv("family_history_rare_disease_cleaned.csv")
    except:
        df = pd.read_csv("data/family_history_rare_disease_cleaned.csv")

    cat_cols = ['Gender','Parental History','Sibling History',
                'Known Genetic Mutation','Early Onset Cases in Family',
                'Environmental Risk Exposure','geneticTest']

    encoders = {}
    for c in cat_cols:
        le = LabelEncoder()
        # Adding a 'handle unknown' approach by string conversion
        df[c] = le.fit_transform(df[c].astype(str))
        encoders[c] = le

    X = df.drop(['Patient ID', 'geneticTest'], axis=1)
    y = df['geneticTest']

    # Balancing
    X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
    
    clf = XGBClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=5,
        random_state=42, eval_metric='logloss'
    )
    clf.fit(X_res, y_res)
    
    return clf, encoders, X.columns

def predict_genetic_test(user_input):
    clf, encoders, feature_cols = train_genetic_model()
    input_df = pd.DataFrame([user_input])
    
    # Encode user input
    for col in input_df.columns:
        if col in encoders:
            try:
                input_df[col] = encoders[col].transform(input_df[col].astype(str))
            except ValueError:
                # If "Other" or unknown value is provided, use a default class
                input_df[col] = 0
                
    input_df = input_df[feature_cols]
    prediction = clf.predict(input_df)[0]
    
    # LabelEncoder usually assigns 1 to 'P' and 0 to 'N'
    # Check encoder classes to be sure
    res_label = encoders['geneticTest'].inverse_transform([prediction])[0]
    return "Genetic Test Recommended" if res_label == 'P' else "No Genetic Test Needed"