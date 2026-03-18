"""
train_random_forest.py — GSS ML Model Training
===============================================
Trains a Random Forest classifier on labelled sensor data.

Classes:
  0 → Normal     (safe atmospheric conditions)
  1 → Dangerous  (hazardous gas levels detected)
  2 → Recovery   (transitional / alert phase)

Usage:
  python train_random_forest.py --data sensor_data.csv
  python train_random_forest.py --data sensor_data.csv --n-estimators 200

Output:
  model/rf_model.pkl   — trained model
  model/scaler.pkl     — fitted MinMaxScaler (required for inference)
  model/encoder.pkl    — fitted LabelEncoder
"""

import argparse
import os
import pickle

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from preprocess import full_pipeline, LABEL_CLASSES

MODEL_DIR = "model"


def parse_args():
    p = argparse.ArgumentParser(description="Train Random Forest for GSS")
    p.add_argument("--data",          required=True, help="Path to labelled CSV")
    p.add_argument("--n-estimators",  type=int, default=100)
    p.add_argument("--max-depth",     type=int, default=None)
    p.add_argument("--test-size",     type=float, default=0.2)
    p.add_argument("--random-state",  type=int, default=42)
    p.add_argument("--grid-search",   action="store_true",
                   help="Run GridSearchCV for hyperparameter tuning")
    return p.parse_args()


def save_artifact(obj, filename: str):
    os.makedirs(MODEL_DIR, exist_ok=True)
    path = os.path.join(MODEL_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"  Saved → {path}")


def main():
    args = parse_args()

    print("[1/4] Loading & preprocessing data...")
    X, y, scaler, encoder = full_pipeline(args.data)
    print(f"      Samples: {len(X)} | Features: {X.shape[1]} | Classes: {LABEL_CLASSES}")

    print("[2/4] Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    print(f"      Train: {len(X_train)} | Test: {len(X_test)}")

    print("[3/4] Training Random Forest...")
    if args.grid_search:
        param_grid = {
            "n_estimators": [50, 100, 200],
            "max_depth":    [None, 10, 20],
            "min_samples_split": [2, 5],
        }
        rf = GridSearchCV(
            RandomForestClassifier(random_state=args.random_state),
            param_grid, cv=5, n_jobs=-1, verbose=1
        )
        rf.fit(X_train, y_train)
        print(f"      Best params: {rf.best_params_}")
        best_model = rf.best_estimator_
    else:
        best_model = RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.random_state,
            n_jobs=-1,
        )
        best_model.fit(X_train, y_train)

    print("[4/4] Evaluating model...")
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(y_test, y_pred, target_names=LABEL_CLASSES))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importance
    importances = best_model.feature_importances_
    from preprocess import SENSOR_COLS
    print("\nFeature Importances:")
    for col, imp in sorted(zip(SENSOR_COLS, importances), key=lambda x: -x[1]):
        print(f"  {col:<12} {imp:.4f}")

    # Save artifacts
    print("\nSaving model artifacts...")
    save_artifact(best_model, "rf_model.pkl")
    save_artifact(scaler, "scaler.pkl")
    save_artifact(encoder, "encoder.pkl")
    print("\nDone! Use predict.py for live inference.")


if __name__ == "__main__":
    main()
