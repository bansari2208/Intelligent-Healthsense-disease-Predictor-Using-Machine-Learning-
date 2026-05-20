from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder


diseaselist = [
    'Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
    'Peptic ulcer diseae', 'AIDS', 'Diabetes ', 'Gastroenteritis', 'Bronchial Asthma',
    'Hypertension ', 'Migraine', 'Cervical spondylosis', 'Paralysis (brain hemorrhage)',
    'Jaundice', 'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
    'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis',
    'Tuberculosis', 'Common Cold', 'Pneumonia', 'Dimorphic hemmorhoids(piles)',
    'Heart attack', 'Varicose veins', 'Hypothyroidism', 'Hyperthyroidism',
    'Hypoglycemia', 'Osteoarthristis', 'Arthritis',
    '(vertigo) Paroymsal  Positional Vertigo', 'Acne',
    'Urinary tract infection', 'Psoriasis', 'Impetigo'
]

label_encoder = LabelEncoder()
label_encoder.fit(diseaselist)

workspace_dataset_path = Path(__file__).resolve().parent / 'dataset.csv'
desktop_dataset_path = Path(__file__).resolve().parent.parent / 'dataset.csv'
dataset_path = workspace_dataset_path if workspace_dataset_path.exists() else desktop_dataset_path
df = pd.read_csv(dataset_path)

# Build symptom space exactly from dataset contents.
symptoms = set()
for col in df.columns[1:]:
    for val in df[col].dropna():
        if isinstance(val, str):
            symptoms.add(val.strip())
symptomslist = sorted(symptoms)
symptom_index = {symptom: idx for idx, symptom in enumerate(symptomslist)}

# One-hot encode symptoms
X = np.zeros((len(df), len(symptomslist)), dtype=np.int8)
for i, row in df.iterrows():
    for col in df.columns[1:]:
        val = row[col]
        if isinstance(val, str):
            cleaned = val.strip()
            idx = symptom_index.get(cleaned)
            if idx is not None:
                X[i, idx] = 1

# Normalize disease labels to match application's class names
normalized_targets = []
for disease in df['Disease'].values:
    d_clean = str(disease).strip()
    match = None
    for app_disease in diseaselist:
        if d_clean.lower() == app_disease.strip().lower():
            match = app_disease
            break
    normalized_targets.append(match if match else d_clean)
y = label_encoder.transform(normalized_targets)

# Data augmentation for real-world use:
# users often provide only a subset of symptoms, so we train with partial vectors too.
rng = np.random.default_rng(42)
augmented_X = [row.copy() for row in X]
augmented_y = list(y)
for i in range(len(X)):
    positive_idx = np.where(X[i] == 1)[0]
    if len(positive_idx) <= 1:
        continue
    for _ in range(2):
        keep_ratio = float(rng.uniform(0.55, 0.85))
        keep_count = max(1, int(round(len(positive_idx) * keep_ratio)))
        chosen_idx = rng.choice(positive_idx, size=keep_count, replace=False)
        row = np.zeros_like(X[i])
        row[chosen_idx] = 1
        augmented_X.append(row)
        augmented_y.append(y[i])

X = np.asarray(augmented_X, dtype=np.int8)
y = np.asarray(augmented_y)

# Compare multiple models and keep the best CV performer.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
candidate_models = {
    'multinomial_nb': MultinomialNB(),
    'random_forest': RandomForestClassifier(
        n_estimators=500, random_state=42, n_jobs=-1
    ),
    'extra_trees': ExtraTreesClassifier(
        n_estimators=700, random_state=42, n_jobs=-1
    ),
}

best_name = None
best_score = -1.0
best_model = None

for name, candidate in candidate_models.items():
    scores = cross_val_score(candidate, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    score_mean = float(scores.mean())
    print(f"{name} CV accuracy: {score_mean:.4f} (+/- {scores.std():.4f})")
    if score_mean > best_score:
        best_score = score_mean
        best_name = name
        best_model = candidate

best_model.fit(X, y)

output_model_path = Path(__file__).resolve().parent / 'model.pkl'
joblib.dump(best_model, output_model_path)

print(f"Selected model: {best_name}")
print(f"Best CV accuracy: {best_score:.4f}")
print(f"Model saved at: {output_model_path}")