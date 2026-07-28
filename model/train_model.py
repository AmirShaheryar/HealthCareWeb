"""
NLP-Medora — Disease Prediction Model Trainer
Trains a Random Forest on the Disease-Symptom dataset (Kaggle equivalent).
Run once: python model/train_model.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import json
import os

# ── Full 132-symptom × 41-disease dataset ─────────────────────────────────────
DISEASE_DATA = {
    "Fungal infection":         ["itching","skin_rash","nodal_skin_eruptions","dischromic_patches"],
    "Allergy":                  ["continuous_sneezing","shivering","chills","watering_from_eyes"],
    "GERD":                     ["stomach_pain","acidity","ulcers_on_tongue","vomiting","cough","chest_pain"],
    "Chronic cholestasis":      ["itching","vomiting","yellowish_skin","nausea","loss_of_appetite","abdominal_pain","yellowing_of_eyes"],
    "Drug Reaction":            ["itching","skin_rash","stomach_pain","burning_micturition","spotting_urination"],
    "Peptic ulcer disease":     ["vomiting","indigestion","loss_of_appetite","abdominal_pain","passage_of_gases","internal_itching"],
    "AIDS":                     ["muscle_wasting","patches_in_throat","high_fever","extra_marital_contacts"],
    "Diabetes":                 ["fatigue","weight_loss","restlessness","lethargy","irregular_sugar_level","blurred_and_distorted_vision","obesity","excessive_hunger","increased_appetite","polyuria"],
    "Gastroenteritis":          ["vomiting","sunken_eyes","dehydration","diarrhoea"],
    "Bronchial Asthma":         ["fatigue","cough","high_fever","breathlessness","family_history","mucoid_sputum"],
    "Hypertension":             ["headache","chest_pain","dizziness","loss_of_balance","lack_of_concentration"],
    "Migraine":                 ["acidity","indigestion","headache","blurred_and_distorted_vision","excessive_hunger","stiff_neck","depression","irritability","visual_disturbances"],
    "Cervical spondylosis":     ["back_pain","weakness_in_limbs","neck_pain","dizziness","loss_of_balance"],
    "Paralysis (brain hemorrhage)": ["vomiting","headache","weakness_of_one_body_side","altered_sensorium"],
    "Jaundice":                 ["itching","vomiting","fatigue","weight_loss","high_fever","yellowish_skin","dark_urine","abdominal_pain"],
    "Malaria":                  ["chills","vomiting","high_fever","sweating","headache","nausea","diarrhoea","muscle_pain"],
    "Chicken pox":              ["itching","skin_rash","fatigue","lethargy","high_fever","headache","loss_of_appetite","mild_fever","swelled_lymph_nodes","malaise","red_spots_over_body"],
    "Dengue":                   ["skin_rash","chills","joint_pain","vomiting","fatigue","high_fever","headache","nausea","loss_of_appetite","pain_behind_the_eyes","back_pain","muscle_pain","red_spots_over_body"],
    "Typhoid":                  ["chills","vomiting","fatigue","high_fever","headache","nausea","constipation","abdominal_pain","diarrhoea","toxic_look_(typhos)","belly_pain"],
    "Hepatitis A":              ["joint_pain","vomiting","yellowish_skin","dark_urine","nausea","loss_of_appetite","abdominal_pain","diarrhoea","mild_fever","yellowing_of_eyes","muscle_pain"],
    "Hepatitis B":              ["itching","fatigue","lethargy","yellowish_skin","dark_urine","loss_of_appetite","abdominal_pain","mild_fever","yellowing_of_eyes","malaise","receiving_blood_transfusion","receiving_unsterile_injections"],
    "Hepatitis C":              ["fatigue","yellowish_skin","nausea","loss_of_appetite","family_history","yellowing_of_eyes"],
    "Hepatitis D":              ["joint_pain","vomiting","fatigue","yellowish_skin","dark_urine","nausea","loss_of_appetite","abdominal_pain","yellowing_of_eyes"],
    "Hepatitis E":              ["joint_pain","vomiting","fatigue","high_fever","yellowish_skin","dark_urine","nausea","loss_of_appetite","abdominal_pain","acute_liver_failure","coma","stomach_bleeding"],
    "Alcoholic hepatitis":      ["vomiting","yellowish_skin","abdominal_pain","swelling_of_stomach","distention_of_abdomen","history_of_alcohol_consumption","fluid_overload"],
    "Tuberculosis":             ["chills","vomiting","fatigue","weight_loss","cough","high_fever","breathlessness","sweating","loss_of_appetite","mild_fever","swelled_lymph_nodes","malaise","phlegm","blood_in_sputum","chest_pain"],
    "Common Cold":              ["continuous_sneezing","chills","fatigue","cough","high_fever","headache","swelled_lymph_nodes","malaise","phlegm","throat_irritation","redness_of_eyes","sinus_pressure","runny_nose","congestion","chest_pain","loss_of_smell","muscle_pain"],
    "Pneumonia":                ["chills","fatigue","cough","high_fever","breathlessness","sweating","malaise","phlegm","chest_pain","fast_heart_rate","rusty_sputum"],
    "Dimorphic hemorrhoids(piles)": ["constipation","pain_during_bowel_movements","pain_in_anal_region","bloody_stool","irritation_in_anus"],
    "Heart attack":             ["vomiting","breathlessness","sweating","chest_pain","chest_tightness","pain_in_left_arm","fast_heart_rate"],
    "Varicose veins":           ["fatigue","cramps","bruising","obesity","swollen_legs","swollen_blood_vessels","prominent_veins_on_calf"],
    "Hypothyroidism":           ["fatigue","weight_gain","cold_hands_and_feets","mood_swings","lethargy","dizziness","puffy_face_and_eyes","enlarged_thyroid","brittle_nails","swollen_extremeties","depression","irritability","abnormal_menstruation"],
    "Hyperthyroidism":          ["fatigue","mood_swings","weight_loss","restlessness","sweating","diarrhoea","fast_heart_rate","excessive_hunger","muscle_weakness","irritability","abnormal_menstruation"],
    "Hypoglycemia":             ["vomiting","fatigue","anxiety","sweating","headache","nausea","blurred_and_distorted_vision","excessive_hunger","drying_and_tingling_lips","slurred_speech","irritability","palpitations"],
    "Osteoarthritis":           ["joint_pain","neck_pain","knee_pain","hip_joint_pain","swelling_joints","painful_walking"],
    "Arthritis":                ["muscle_weakness","stiff_neck","swelling_joints","movement_stiffness","painful_walking"],
    "Vertigo":                  ["vomiting","headache","nausea","spinning_movements","loss_of_balance","unsteadiness"],
    "Acne":                     ["skin_rash","pus_filled_pimples","blackheads","scurring"],
    "Urinary tract infection":  ["burning_micturition","bladder_discomfort","foul_smell_of_urine","continuous_feel_of_urine"],
    "Psoriasis":                ["skin_rash","joint_pain","skin_peeling","silver_like_dusting","small_dents_in_nails","inflammatory_nails"],
    "Impetigo":                 ["skin_rash","high_fever","blister","red_sore_around_nose","yellow_crust_ooze"],
}

# ── Build full symptom list ────────────────────────────────────────────────────
ALL_SYMPTOMS = sorted(set(s for symptoms in DISEASE_DATA.values() for s in symptoms))
print(f"Total unique symptoms: {len(ALL_SYMPTOMS)}")
print(f"Total diseases: {len(DISEASE_DATA)}")

# ── Generate dataset with augmentation ────────────────────────────────────────
rows = []
np.random.seed(42)

for disease, symptoms in DISEASE_DATA.items():
    # Generate 120 samples per disease with slight variation
    for _ in range(120):
        row = {s: 0 for s in ALL_SYMPTOMS}
        # Always include core symptoms
        n_core = max(2, len(symptoms) - 2)
        chosen = np.random.choice(symptoms, size=min(n_core, len(symptoms)), replace=False)
        for s in chosen:
            row[s] = 1
        # Add 0-2 random noise symptoms occasionally
        if np.random.random() < 0.3:
            noise_sym = np.random.choice(ALL_SYMPTOMS, size=np.random.randint(1, 3), replace=False)
            for s in noise_sym:
                row[s] = 1
        row["disease"] = disease
        rows.append(row)

df = pd.DataFrame(rows)
print(f"Dataset shape: {df.shape}")

X = df[ALL_SYMPTOMS].values
y = df["disease"].values

# ── Label encode ───────────────────────────────────────────────────────────────
le = LabelEncoder()
y_enc = le.fit_transform(y)

# ── Train / test split ─────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# ── Train Random Forest ────────────────────────────────────────────────────────
print("\nTraining Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=3,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)
rf.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────────
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {acc:.4f} ({acc*100:.2f}%)")

cv_scores = cross_val_score(rf, X, y_enc, cv=5, scoring="accuracy")
print(f"5-Fold CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ── Save model & metadata ──────────────────────────────────────────────────────
os.makedirs("model", exist_ok=True)

joblib.dump(rf, "model/disease_rf_model.pkl")
joblib.dump(le, "model/label_encoder.pkl")

metadata = {
    "symptoms": ALL_SYMPTOMS,
    "diseases": list(le.classes_),
    "accuracy": round(acc * 100, 2),
    "cv_accuracy": round(cv_scores.mean() * 100, 2),
    "n_estimators": 200,
    "model_type": "RandomForestClassifier",
    "n_symptoms": len(ALL_SYMPTOMS),
    "n_diseases": len(DISEASE_DATA),
}

with open("model/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

# ── Disease descriptions for UI ────────────────────────────────────────────────
DISEASE_INFO = {
    "Fungal infection":    {"urgency": "Low",    "advice": "Antifungal cream or oral medication. Keep affected area dry.", "icon": "🍄"},
    "Allergy":             {"urgency": "Low",    "advice": "Antihistamines. Identify and avoid triggers.", "icon": "🤧"},
    "GERD":                {"urgency": "Medium", "advice": "Avoid spicy/fatty food. Antacids. Elevate head while sleeping.", "icon": "🔥"},
    "Chronic cholestasis": {"urgency": "High",   "advice": "Consult gastroenterologist. Liver function tests required.", "icon": "🫀"},
    "Drug Reaction":       {"urgency": "High",   "advice": "Stop suspected medication immediately. Seek medical attention.", "icon": "💊"},
    "Peptic ulcer disease":{"urgency": "Medium", "advice": "Avoid NSAIDs. PPI medication. Test for H. pylori.", "icon": "🩺"},
    "AIDS":                {"urgency": "High",   "advice": "Immediate referral to infectious disease specialist. ART therapy.", "icon": "🔴"},
    "Diabetes":            {"urgency": "Medium", "advice": "Monitor blood sugar. Low GI diet. Metformin if prescribed.", "icon": "🩸"},
    "Gastroenteritis":     {"urgency": "Medium", "advice": "ORS rehydration. Bland diet. Antibiotics if bacterial.", "icon": "🤢"},
    "Bronchial Asthma":    {"urgency": "High",   "advice": "Use inhaler as prescribed. Avoid triggers. Nebulization if severe.", "icon": "🫁"},
    "Hypertension":        {"urgency": "High",   "advice": "Low sodium diet. Regular BP monitoring. Antihypertensives.", "icon": "❤️"},
    "Migraine":            {"urgency": "Medium", "advice": "Rest in dark room. Triptans or OTC pain relief. Track triggers.", "icon": "🧠"},
    "Cervical spondylosis":{"urgency": "Medium", "advice": "Physiotherapy. Neck exercises. NSAIDs for pain.", "icon": "🦴"},
    "Paralysis (brain hemorrhage)": {"urgency": "Critical", "advice": "EMERGENCY — Call ambulance immediately. Time-critical treatment.", "icon": "🚨"},
    "Jaundice":            {"urgency": "High",   "advice": "Liver function tests. Rest. High carb low fat diet.", "icon": "💛"},
    "Malaria":             {"urgency": "High",   "advice": "Antimalarial drugs (Chloroquine/Artemisinin). Blood smear test.", "icon": "🦟"},
    "Chicken pox":         {"urgency": "Medium", "advice": "Rest, calamine lotion, antiviral if severe. Avoid scratching.", "icon": "🔴"},
    "Dengue":              {"urgency": "High",   "advice": "No aspirin/ibuprofen. Monitor platelet count. IV fluids if severe.", "icon": "🦟"},
    "Typhoid":             {"urgency": "High",   "advice": "Antibiotics (Ciprofloxacin). Boiled water. Rest.", "icon": "🌡️"},
    "Hepatitis A":         {"urgency": "High",   "advice": "Rest. Avoid alcohol. High calorie diet. Usually self-limiting.", "icon": "🫀"},
    "Hepatitis B":         {"urgency": "High",   "advice": "Antiviral therapy. Avoid alcohol. Regular liver monitoring.", "icon": "🫀"},
    "Hepatitis C":         {"urgency": "High",   "advice": "Antiviral therapy (DAAs). Specialist referral. No alcohol.", "icon": "🫀"},
    "Hepatitis D":         {"urgency": "High",   "advice": "Pegylated interferon. Specialist referral required.", "icon": "🫀"},
    "Hepatitis E":         {"urgency": "High",   "advice": "Rest. Supportive care. Avoid alcohol. Usually self-limiting.", "icon": "🫀"},
    "Alcoholic hepatitis": {"urgency": "High",   "advice": "Stop alcohol immediately. Corticosteroids. Nutritional support.", "icon": "🍺"},
    "Tuberculosis":        {"urgency": "High",   "advice": "6-month DOTS therapy. Isolation initially. Chest X-ray.", "icon": "🫁"},
    "Common Cold":         {"urgency": "Low",    "advice": "Rest, fluids, vitamin C. OTC decongestants. Usually 7-10 days.", "icon": "🤧"},
    "Pneumonia":           {"urgency": "High",   "advice": "Antibiotics. Chest X-ray. Hospitalization if SpO2 < 94%.", "icon": "🫁"},
    "Dimorphic hemorrhoids(piles)": {"urgency": "Medium", "advice": "High fibre diet. Sitz baths. Surgical if severe.", "icon": "🩺"},
    "Heart attack":        {"urgency": "Critical","advice": "EMERGENCY — Call ambulance. Aspirin 325mg. Do not drive yourself.", "icon": "🚨"},
    "Varicose veins":      {"urgency": "Low",    "advice": "Compression stockings. Elevate legs. Surgery if severe.", "icon": "🦵"},
    "Hypothyroidism":      {"urgency": "Medium", "advice": "Levothyroxine replacement. Regular TSH monitoring.", "icon": "🦋"},
    "Hyperthyroidism":     {"urgency": "Medium", "advice": "Antithyroid drugs. Beta-blockers for symptoms. Specialist referral.", "icon": "🦋"},
    "Hypoglycemia":        {"urgency": "High",   "advice": "Eat 15g fast sugar immediately. Recheck blood glucose after 15 min.", "icon": "🍬"},
    "Osteoarthritis":      {"urgency": "Medium", "advice": "Physiotherapy. Weight loss. NSAIDs. Joint replacement if severe.", "icon": "🦴"},
    "Arthritis":           {"urgency": "Medium", "advice": "Anti-inflammatories. Physiotherapy. DMARDs if rheumatoid.", "icon": "🦴"},
    "Vertigo":             {"urgency": "Medium", "advice": "Epley maneuver. Vestibular rehab. Antivertigo medication.", "icon": "🌀"},
    "Acne":                {"urgency": "Low",    "advice": "Benzoyl peroxide. Retinoids. Avoid touching face. Dermatologist.", "icon": "😶"},
    "Urinary tract infection": {"urgency": "Medium", "advice": "Antibiotics. Drink plenty of water. Cranberry juice.", "icon": "🚽"},
    "Psoriasis":           {"urgency": "Low",    "advice": "Topical corticosteroids. Moisturizers. Phototherapy. Biologics.", "icon": "🩹"},
    "Impetigo":            {"urgency": "Medium", "advice": "Topical or oral antibiotics. Keep area clean. Avoid contact.", "icon": "🩹"},
}

with open("model/disease_info.json", "w") as f:
    json.dump(DISEASE_INFO, f, indent=2)

print(f"\n✅ Model saved: model/disease_rf_model.pkl")
print(f"✅ Encoder saved: model/label_encoder.pkl")
print(f"✅ Metadata saved: model/model_metadata.json")
print(f"✅ Disease info saved: model/disease_info.json")
print(f"\n📊 Final Stats:")
print(f"   Symptoms : {len(ALL_SYMPTOMS)}")
print(f"   Diseases : {len(DISEASE_DATA)}")
print(f"   Accuracy : {acc*100:.2f}%")
print(f"   CV Score : {cv_scores.mean()*100:.2f}%")
