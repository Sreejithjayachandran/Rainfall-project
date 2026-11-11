import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

# ------------------------------------------------------------------------------
# 1. LOAD DATASET
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CANDIDATE_PATHS = [
    os.path.join(BASE_DIR, "output", "analysis_ready_rainfall.csv"),
    os.path.join(BASE_DIR, "..", "Member_5_Load_Pipeline_and_README", "output", "analysis_ready_rainfall.csv"),
    os.path.join(r"d:\Mini\Team_Folders\Member_5_Load_Pipeline_and_README\output", "analysis_ready_rainfall.csv"),
    os.path.join(r"c:\Users\SREEJITH\Downloads", "analysis_ready_rainfall.csv"),
    os.path.join(BASE_DIR, "analysis_ready_rainfall.csv"),
]

DATA_PATH = None
for p in CANDIDATE_PATHS:
    if os.path.exists(p):
        DATA_PATH = os.path.abspath(p)
        break

if not DATA_PATH:
    raise FileNotFoundError("Could not find analysis_ready_rainfall.csv.")

df = pd.read_csv(DATA_PATH)

# ------------------------------------------------------------------------------
# 2. FEATURE ENGINEERING & PREPROCESSING
# ------------------------------------------------------------------------------
season_mapping = {
    "Winter": 1,
    "Pre-Monsoon": 2,
    "Southwest Monsoon": 3,
    "Post-Monsoon": 4
}
df["season_num"] = df["season"].map(season_mapping).fillna(0).astype(int)

day_mapping = {
    "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
    "Friday": 5, "Saturday": 6, "Sunday": 7
}
df["day_num"] = df["day_of_week"].map(day_mapping).fillna(0).astype(int)

FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "month",
    "season_num",
    "day_num",
    "district_lgd_code",
    "station_total_rainfall_mm",
    "station_rank"
]

X = df[FEATURE_COLUMNS]
y = df["rainfall_category"]

# Stratified 80/20 train-test split (42,017 train, 10,505 test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ------------------------------------------------------------------------------
# 3. TRAIN KNN MODEL & EVALUATE
# ------------------------------------------------------------------------------
knn = KNeighborsClassifier(n_neighbors=25, weights="uniform")
knn.fit(X_train_scaled, y_train)

y_pred = knn.predict(X_test_scaled)

acc = accuracy_score(y_test, y_pred)
macro_prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
macro_rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

# ------------------------------------------------------------------------------
# 4. PRINT RESULTS IN EXACT TEMPLATE FORMAT
# ------------------------------------------------------------------------------
print("=" * 80)
print("KNN CLASSIFICATION RESULTS")
print("=" * 80)
print(f"Accuracy        : {acc:.4f}")
print(f"Macro Precision : {macro_prec:.4f}")
print(f"Macro Recall    : {macro_rec:.4f}")
print(f"Macro F1-score  : {macro_f1:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))
