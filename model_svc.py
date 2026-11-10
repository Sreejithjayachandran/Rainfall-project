import time, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)

# Steps 1-2: load data and create the rainfall category
df = (pd.read_csv("analysis_ready_rainfall.csv", parse_dates=["date"])
      .sort_values(["date", "station"]).reset_index(drop=True))
labels = ["Very Light", "Light", "Moderate", "Heavy", "Very Heavy", "Extremely Heavy"]
df["target"] = pd.cut(df["rainfall_mm"], [0, 2.5, 15.6, 64.5, 115.6, 204.5, np.inf],
                      labels=labels, right=False)

# Use only rainfall readings observed earlier for the same station.
previous_rainfall = df.groupby("station", sort=False)["rainfall_mm"].shift(1)
df["previous_rainfall_mm"] = previous_rainfall
df["previous_3_reading_mean"] = previous_rainfall.groupby(
    df["station"], sort=False
).transform(lambda values: values.rolling(3, min_periods=1).mean())
df["has_previous_reading"] = previous_rainfall.notna().astype(float)

# Do not include current rainfall, rainfall_category, station totals, or ranks.
feature_columns = [
    "year", "month", "season", "district", "station", "day_of_week",
    "latitude", "longitude", "previous_rainfall_mm",
    "previous_3_reading_mean", "has_previous_reading"
]
X = pd.get_dummies(
    df[feature_columns],
    columns=["season", "district", "station", "day_of_week"],
    dtype=float
).fillna(0)
y = df["target"].astype(str)

# Step 5: time-ordered 80/20 split
cut = int(len(df) * 0.8)
X_tr, X_te, y_tr, y_te = X.iloc[:cut], X.iloc[cut:], y.iloc[:cut], y.iloc[cut:]

# SVC is slow, so train on a reproducible sample of the training set.
sample_size = min(12000, len(X_tr))
idx = np.sort(np.random.RandomState(42).choice(len(X_tr), sample_size, replace=False))
X_s, y_s = X_tr.iloc[idx], y_tr.iloc[idx]

# Steps 6-8: scaler + VarianceThreshold + SelectKBest + SVC, tuned C and gamma
pipe = Pipeline([("scale", StandardScaler()),
                 ("var", VarianceThreshold(0.0)),
                 ("kbest", SelectKBest(f_classif, k=25)),
                 ("svc", SVC(kernel="rbf"))])
grid = {
    "svc__C": [0.1, 1, 10],
    "svc__gamma": ["scale", 0.01, 0.1],
    "svc__class_weight": [None, "balanced"]
}
search = GridSearchCV(pipe, grid, scoring="f1_macro", cv=TimeSeriesSplit(3), n_jobs=-1)

t0 = time.time()
search.fit(X_s, y_s)
train_time = time.time() - t0
print("Best params:", search.best_params_)

# Steps 9-10: predict on test set and evaluate
pred = search.predict(X_te)
acc = accuracy_score(y_te, pred)
macro_precision = precision_score(y_te, pred, average="macro", zero_division=0)
macro_recall = recall_score(y_te, pred, average="macro", zero_division=0)
mf1 = f1_score(y_te, pred, average="macro", zero_division=0)
weighted_f1 = f1_score(y_te, pred, average="weighted", zero_division=0)
baseline = y_te.value_counts(normalize=True).max()
print(f"Accuracy                : {acc:.4f}")
print(f"Majority-class baseline : {baseline:.4f}")
print(f"Macro precision         : {macro_precision:.4f}")
print(f"Macro recall            : {macro_recall:.4f}")
print(f"Macro F1                : {mf1:.4f}")
print(f"Weighted F1             : {weighted_f1:.4f}")
print(f"Training time           : {train_time:.2f} seconds")

print("\nPer-class classification report:")
print(classification_report(y_te, pred, labels=labels, zero_division=0, digits=4))

print("Confusion matrix (rows=actual, cols=predicted):")
print(pd.DataFrame(confusion_matrix(y_te, pred, labels=labels), index=labels, columns=labels))

# Step 11: save one row in the shared format
pd.DataFrame([{
    "Model": "SVC",
    "Accuracy": acc,
    "Majority-class baseline": baseline,
    "Macro-precision": macro_precision,
    "Macro-recall": macro_recall,
    "Macro-F1": mf1,
    "Weighted-F1": weighted_f1,
    "Training time": train_time
}]).to_csv("results_svc.csv", index=False)
