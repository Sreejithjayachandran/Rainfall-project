"""
Decision Tree Classifier - Kerala Rainfall Mini Project

Purpose:
    Train and evaluate ONLY the Decision Tree classification model.

Target:
    rainfall_category

Important:
    rainfall_mm is deliberately excluded from X because rainfall_category
    is derived from rainfall amount. Including rainfall_mm would cause
    target leakage and give misleading evaluation results.

Run:
    pip install pandas numpy scikit-learn matplotlib seaborn joblib
    python decision_tree_classifier.py

Dataset:
    Place analysis_ready_rainfall.csv in the project root, or in a
    folder named data/ under the project root.
"""

from pathlib import Path
import json
import warnings

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------
# 1. PATHS AND SETTINGS
# ---------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
TARGET = "rainfall_category"
RANDOM_STATE = 42
TEST_SIZE = 0.20

# Search common locations so the script can run from the Decision Tree
# folder without requiring a hard-coded computer-specific path.
possible_paths = [
    SCRIPT_DIR / "analysis_ready_rainfall.csv",
    SCRIPT_DIR.parent / "analysis_ready_rainfall.csv",
    SCRIPT_DIR.parent / "data" / "analysis_ready_rainfall.csv",
    SCRIPT_DIR.parent.parent / "analysis_ready_rainfall.csv",
    SCRIPT_DIR.parent.parent / "data" / "analysis_ready_rainfall.csv",
]

DATA_PATH = next((path for path in possible_paths if path.exists()), None)

if DATA_PATH is None:
    raise FileNotFoundError(
        "Dataset not found. Place 'analysis_ready_rainfall.csv' in the "
        "project root or its data/ folder. You can also update DATA_PATH "
        "in this script."
    )

RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("DECISION TREE CLASSIFIER - KERALA RAINFALL PROJECT")
print("=" * 65)

# ---------------------------------------------------------------------
# 2. LOAD DATASET
# ---------------------------------------------------------------------

df = pd.read_csv(DATA_PATH)

print(f"\nDataset loaded: {DATA_PATH}")
print(f"Dataset shape: {df.shape}")
print("\nFirst five rows:")
print(df.head())

if TARGET not in df.columns:
    raise ValueError(f"Target column '{TARGET}' is not present in the dataset.")

# Remove rows where the target is missing.
df = df.dropna(subset=[TARGET]).copy()

# ---------------------------------------------------------------------
# 3. SELECT FEATURES AND TARGET
# ---------------------------------------------------------------------

# Exclude direct rainfall measurements and aggregate columns that could
# reveal information about the target or use information unavailable
# at the time of a genuine prediction.
columns_to_drop = [
    TARGET,
    "rainfall_mm",
    "station_total_rainfall_mm",
    "station_rank",
    "date_time",
    "date",
    "month_name",  # month is already available as a numerical feature
]

X = df.drop(columns=columns_to_drop, errors="ignore")
y = df[TARGET].astype(str)

# Treat administrative codes as categorical identifiers, not continuous
# numerical measurements.
categorical_columns = X.select_dtypes(include=["object", "category"]).columns.tolist()

for column in ["state_lgd_code", "district_lgd_code"]:
    if column in X.columns:
        X[column] = X[column].astype("string")
        if column not in categorical_columns:
            categorical_columns.append(column)

numerical_columns = [
    column for column in X.columns if column not in categorical_columns
]

print("\nTarget distribution:")
print(y.value_counts())

print("\nNumber of input features:", X.shape[1])
print("Categorical features:", categorical_columns)
print("Numerical features:", numerical_columns)

if y.nunique() < 2:
    raise ValueError("The target must contain at least two classes.")

# ---------------------------------------------------------------------
# 4. TRAIN-TEST SPLIT
# ---------------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y,
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# ---------------------------------------------------------------------
# 5. PREPROCESSING
# ---------------------------------------------------------------------

# Numerical columns: replace missing values with the median.
# Categorical columns: replace missing values with the most frequent value,
# then convert categories into numerical columns using one-hot encoding.

numerical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

transformers = []

if numerical_columns:
    transformers.append(("numerical", numerical_pipeline, numerical_columns))

if categorical_columns:
    transformers.append(("categorical", categorical_pipeline, categorical_columns))

preprocessor = ColumnTransformer(transformers=transformers)

# ---------------------------------------------------------------------
# 6. BUILD THE DECISION TREE PIPELINE
# ---------------------------------------------------------------------

decision_tree_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            DecisionTreeClassifier(random_state=RANDOM_STATE),
        ),
    ]
)

# ---------------------------------------------------------------------
# 7. HYPERPARAMETER TUNING
# ---------------------------------------------------------------------

# Macro F1 gives equal importance to each rainfall category. This is useful
# because the dataset has considerably fewer Extremely Heavy observations.
parameter_grid = {
    "classifier__criterion": ["gini", "entropy"],
    "classifier__max_depth": [10, 20, 30, None],
    "classifier__min_samples_split": [2, 10],
    "classifier__min_samples_leaf": [1, 5],
    "classifier__class_weight": [None, "balanced"],
}

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=RANDOM_STATE,
)

grid_search = GridSearchCV(
    estimator=decision_tree_pipeline,
    param_grid=parameter_grid,
    scoring="f1_macro",
    cv=cv,
    n_jobs=-1,
    verbose=1,
)

print("\nStarting Decision Tree hyperparameter tuning...")
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_

print("\nBest parameters:")
print(grid_search.best_params_)
print(f"Best cross-validation macro F1-score: {grid_search.best_score_:.4f}")

# ---------------------------------------------------------------------
# 8. PREDICTION
# ---------------------------------------------------------------------

y_pred = best_model.predict(X_test)

# ---------------------------------------------------------------------
# 9. MODEL EVALUATION
# ---------------------------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

print("\n" + "=" * 65)
print("DECISION TREE CLASSIFICATION RESULTS")
print("=" * 65)
print(f"Accuracy          : {accuracy:.4f}")
print(f"Macro Precision   : {precision:.4f}")
print(f"Macro Recall      : {recall:.4f}")
print(f"Macro F1-score    : {f1:.4f}")

report = classification_report(y_test, y_pred, zero_division=0)
print("\nClassification Report:")
print(report)

# Save evaluation metrics.
metrics = {
    "model": "Decision Tree Classifier",
    "accuracy": float(accuracy),
    "macro_precision": float(precision),
    "macro_recall": float(recall),
    "macro_f1_score": float(f1),
    "best_cross_validation_macro_f1": float(grid_search.best_score_),
    "best_parameters": grid_search.best_params_,
    "training_records": int(len(X_train)),
    "testing_records": int(len(X_test)),
}

with open(RESULTS_DIR / "evaluation_metrics.json", "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=4)

with open(RESULTS_DIR / "classification_report.txt", "w", encoding="utf-8") as file:
    file.write(report)

# Save actual and predicted values for later analysis.
predictions = pd.DataFrame(
    {
        "Actual_Rainfall_Category": y_test.to_numpy(),
        "Predicted_Rainfall_Category": y_pred,
    }
)
predictions.to_csv(RESULTS_DIR / "predictions.csv", index=False)

# ---------------------------------------------------------------------
# 10. CONFUSION MATRIX
# ---------------------------------------------------------------------

class_labels = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred, labels=class_labels)

plt.figure(figsize=(10, 7))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_labels,
    yticklabels=class_labels,
)
plt.title("Decision Tree - Confusion Matrix")
plt.xlabel("Predicted Category")
plt.ylabel("Actual Category")
plt.xticks(rotation=35, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=300)
plt.show()

# ---------------------------------------------------------------------
# 11. SAVE TRAINED MODEL
# ---------------------------------------------------------------------

model_path = RESULTS_DIR / "decision_tree_model.joblib"
joblib.dump(best_model, model_path)

# ---------------------------------------------------------------------
# 12. SAVE A SIMPLE TREE VISUALIZATION
# ---------------------------------------------------------------------

# One-hot encoding can create many features. Display a limited number of
# tree levels so the plot remains readable.
fitted_tree = best_model.named_steps["classifier"]
feature_names = best_model.named_steps["preprocessor"].get_feature_names_out()



# ---------------------------------------------------------------------
# 13. COMPLETION
# ---------------------------------------------------------------------

print("\n" + "=" * 65)
print("DECISION TREE MODEL COMPLETED SUCCESSFULLY")
print("=" * 65)
print(f"Saved model       : {model_path}")
print(f"Saved results in : {RESULTS_DIR}")
print("\nGenerated files:")
for result_file in sorted(RESULTS_DIR.iterdir()):
    print("-", result_file.name)
