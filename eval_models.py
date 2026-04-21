import pandas as pd
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

def main():
    print("Loading data...")
    df = pd.read_csv('data/train.csv')
    X = df.drop('label', axis=1)
    y = df['label']

    print("Loading scaler and model...")
    scaler = joblib.load('models/scaler.pkl')
    X_scaled = scaler.transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    stack_model = joblib.load('models/ensemble_model.pkl')
    
    metrics = []
    
    print("Evaluating base learners...")
    for name, estimator in stack_model.named_estimators_.items():
        y_pred = estimator.predict(X_test)
        metrics.append({
            "name": name.upper(),
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted')),
            "recall": float(recall_score(y_test, y_pred, average='weighted')),
            "f1": float(f1_score(y_test, y_pred, average='weighted'))
        })
        
    print("Evaluating Ensemble...")
    y_pred_stack = stack_model.predict(X_test)
    metrics.append({
        "name": "ENSEMBLE",
        "accuracy": float(accuracy_score(y_test, y_pred_stack)),
        "precision": float(precision_score(y_test, y_pred_stack, average='weighted')),
        "recall": float(recall_score(y_test, y_pred_stack, average='weighted')),
        "f1": float(f1_score(y_test, y_pred_stack, average='weighted'))
    })
    
    with open('models/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("Saved to models/metrics.json")

if __name__ == "__main__":
    main()
