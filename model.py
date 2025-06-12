# model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load data
df = pd.read_csv("insurance_dataset.csv")

X = df.drop("EstimatedCoverage_Lakhs", axis=1)
y = df["EstimatedCoverage_Lakhs"]

# Categorical columns
cat_cols = X.select_dtypes(include="object").columns.tolist()

# Preprocessing and pipeline
preprocessor = ColumnTransformer([
    ("onehot", OneHotEncoder(handle_unknown='ignore'), cat_cols)
], remainder='passthrough')

model = Pipeline([
    ("preprocess", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "insurance_model.pkl")
