"""
NLP-Medora — Genetic Risk Prediction Model Trainer
XGBoost + SMOTE on family_history_rare_disease_cleaned.csv
Run once: python model/train_genetic_model.py
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve, precision_recall_curve, average_precision_score
)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE, "data",  "family_history_rare_disease_cleaned.csv")
MODEL_DIR  = os.path.join(BASE, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── 1. Load & inspect ──────────────────────────────────────────────────────────
print("=" * 60)
print("NLP-Medora | Genetic Risk Model Trainer")
print("=" * 60)
df = pd.read_csv(DATA_PATH)
print(f"Dataset shape : {df.shape}")
print(f"Target balance: {df['geneticTest'].value_counts().to_dict()}")

# ── 2. Encode categorical columns ──────────────────────────────────────────────
CAT_COLS = [
    "Gender",
    "Parental History",
    "Sibling History",
    "Known Genetic Mutation",
    "Early Onset Cases in Family",
    "Environmental Risk Exposure",
]

encoders = {}
for col in CAT_COLS:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Encode target  N→0, P→1
target_le = LabelEncoder()
df["geneticTest"] = target_le.fit_transform(df["geneticTest"])   # N=0, P=1
encoders["geneticTest"] = target_le

# ── 3. Features / target ───────────────────────────────────────────────────────
FEATURE_COLS = [
    "Age",
    "Gender",
    "Parental History",
    "Sibling History",
    "Number of Relatives with Disease",
    "Known Genetic Mutation",
    "Early Onset Cases in Family",
    "Environmental Risk Exposure",
]

X = df[FEATURE_COLS]
y = df["geneticTest"]

print(f"\nFeatures : {FEATURE_COLS}")
print(f"Class dist before SMOTE: {dict(zip(*np.unique(y, return_counts=True)))}")

# ── 4. SMOTE to handle 80/20 imbalance ────────────────────────────────────────
smote = SMOTE(random_state=42, k_neighbors=5)
X_res, y_res = smote.fit_resample(X, y)
print(f"Class dist after  SMOTE: {dict(zip(*np.unique(y_res, return_counts=True)))}")

# ── 5. Train / test split ──────────────────────────────────────────────────────
X_tr, X_te, y_tr, y_te = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
)
print(f"\nTrain: {X_tr.shape[0]} | Test: {X_te.shape[0]}")

# ── 6. XGBoost ────────────────────────────────────────────────────────────────
pos_ratio = y_tr.sum() / len(y_tr)
clf = XGBClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0,
    scale_pos_weight=(1 - pos_ratio) / pos_ratio,
    random_state=42,
    n_jobs=-1,
    eval_metric="logloss",
    verbosity=0,
)
print("\nTraining XGBoost...")
clf.fit(X_tr, y_tr)

# ── 7. Evaluation ─────────────────────────────────────────────────────────────
y_pred      = clf.predict(X_te)
y_pred_prob = clf.predict_proba(X_te)[:, 1]

acc      = accuracy_score(y_te, y_pred)
auc      = roc_auc_score(y_te, y_pred_prob)
avg_prec = average_precision_score(y_te, y_pred_prob)
cm       = confusion_matrix(y_te, y_pred).tolist()
report   = classification_report(y_te, y_pred, output_dict=True)

print(f"\nTest Accuracy  : {acc:.4f}  ({acc*100:.2f}%)")
print(f"ROC-AUC        : {auc:.4f}")
print(f"Avg Precision  : {avg_prec:.4f}")
print(f"\nClassification Report:\n{classification_report(y_te, y_pred, target_names=['No Test','Recommended'])}")

# ── 8. Cross-validation ───────────────────────────────────────────────────────
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_acc = cross_val_score(clf, X_res, y_res, cv=cv, scoring="accuracy")
cv_auc = cross_val_score(clf, X_res, y_res, cv=cv, scoring="roc_auc")
print(f"5-Fold CV Accuracy : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
print(f"5-Fold CV AUC      : {cv_auc.mean():.4f} ± {cv_auc.std():.4f}")

# ── 9. Feature importance ─────────────────────────────────────────────────────
importance_dict = dict(zip(FEATURE_COLS, clf.feature_importances_.tolist()))
print("\nFeature Importances:")
for f, v in sorted(importance_dict.items(), key=lambda x: -x[1]):
    bar = "█" * int(v * 40)
    print(f"  {f:<40} {v:.4f}  {bar}")

# ── 10. ROC curve data for UI ─────────────────────────────────────────────────
fpr, tpr, roc_thresholds = roc_curve(y_te, y_pred_prob)
prec, rec, pr_thresholds  = precision_recall_curve(y_te, y_pred_prob)

# ── 11. Save everything ───────────────────────────────────────────────────────
joblib.dump(clf,      os.path.join(MODEL_DIR, "genetic_xgb_model.pkl"))
joblib.dump(encoders, os.path.join(MODEL_DIR, "genetic_encoders.pkl"))

metadata = {
    "feature_cols":   FEATURE_COLS,
    "cat_cols":       CAT_COLS,
    "target_classes": target_le.classes_.tolist(),  # ['N','P']
    "model_type":     "XGBClassifier",
    "n_estimators":   400,
    "accuracy":       round(acc * 100, 2),
    "roc_auc":        round(auc * 100, 2),
    "avg_precision":  round(avg_prec * 100, 2),
    "cv_accuracy":    round(cv_acc.mean() * 100, 2),
    "cv_auc":         round(cv_auc.mean() * 100, 2),
    "confusion_matrix": cm,
    "classification_report": report,
    "feature_importances":   importance_dict,
    "roc_curve": {
        "fpr": fpr.tolist()[::5],
        "tpr": tpr.tolist()[::5],
    },
    "pr_curve": {
        "precision": prec.tolist()[::5],
        "recall":    rec.tolist()[::5],
    },
    "encoder_classes": {
        col: le.classes_.tolist()
        for col, le in encoders.items()
        if hasattr(le, "classes_")
    },
    "age_range":      [int(df["Age"].min()), int(df["Age"].max())],
    "relatives_range":[int(df["Number of Relatives with Disease"].min()),
                       int(df["Number of Relatives with Disease"].max())],
}

with open(os.path.join(MODEL_DIR, "genetic_metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Model   : model/genetic_xgb_model.pkl")
print(f"✅ Encoders: model/genetic_encoders.pkl")
print(f"✅ Metadata: model/genetic_metadata.json")
print(f"\n{'='*60}")
print(f"FINAL  Accuracy : {acc*100:.2f}%")
print(f"FINAL  ROC-AUC  : {auc*100:.2f}%")
print(f"FINAL  CV-AUC   : {cv_auc.mean()*100:.2f}%")
print(f"{'='*60}")
