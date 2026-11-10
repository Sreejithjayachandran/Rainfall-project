# Linear Regression on cleaned rainfall data
# -------------------------------------------------
# This script loads the analysis‑ready rainfall CSV produced by the ETL
# pipeline (located in ``EDA/output/analysis_ready_rainfall.csv``), performs a
# lightweight feature engineering step and fits a scikit‑learn ``LinearRegression``
# model to predict ``rainfall_mm``.
#
# The goal is to illustrate a simple supervised‑learning workflow – it is **not**
# intended to be the final production model.  Feel free to extend the feature set
# or swap the estimator.
# -------------------------------------------------

import pandas as pd
import numpy as np  # added for RMSE calculation
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
DATA_PATH = "../EDA/output/analysis_ready_rainfall.csv"  # corrected relative path
df = pd.read_csv(DATA_PATH)

# ------------------------------------------------------------------
# Basic feature engineering
# ------------------------------------------------------------------
# Convert the ``date_time`` column to a proper datetime object
df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
# Extract simple numeric time features that can be used by a linear model
df["day_of_year"] = df["date_time"].dt.dayofyear
df["year"] = df["date_time"].dt.year
# Use latitude, longitude and the two time features as predictors
features = ["latitude", "longitude", "day_of_year", "year"]
X = df[features]
# Target – daily rainfall amount (in mm)
y = df["rainfall_mm"]

# ------------------------------------------------------------------
# Train‑test split (80 % train / 20 % test)
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ------------------------------------------------------------------
# Fit the model
# ------------------------------------------------------------------
model = LinearRegression()
model.fit(X_train, y_train)

# ------------------------------------------------------------------
# Evaluation on the test set
# ------------------------------------------------------------------
y_pred = model.predict(X_test)
print("--- Linear Regression on Rainfall Data ---")
print(f"R² score   : {r2_score(y_test, y_pred):.4f}")
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"RMSE (mm)  : {rmse:.2f}")
print("\nCoefficients (feature -> weight):")
for feat, coef in zip(features, model.coef_):
    print(f"  {feat:12s}: {coef:.6f}")
print(f"Intercept   : {model.intercept_:.6f}")

# Optional – save the trained model for later reuse
# ---------------------------------------------------
# Uncomment the following lines if you want a pickle file:
# import joblib
# joblib.dump(model, "linear_regression_model.pkl")

