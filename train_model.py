import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc, classification_report

# Create models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

print("--- Loading dataset ---")
df = pd.read_csv('data/train.csv')

# Preprocessing
X = df.drop('label', axis=1)
y = df['label']

# Standardizing features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("--- Saving scaler ---")
joblib.dump(scaler, 'models/scaler.pkl')

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

print("--- Initializing Base Learners ---")
# Define base learners
base_learners = [
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
    ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ('svm', SVC(probability=True, random_state=42)),
    ('mlp', MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42))
]

# Define stacking ensemble
print("--- Building Stacking Ensemble ---")
stack_model = StackingClassifier(
    estimators=base_learners,
    final_estimator=LogisticRegression(),
    cv=5
)

# Training
print("--- Training Ensemble Model (this may take a minute) ---")
stack_model.fit(X_train, y_train)

# Saving the model
print("--- Saving Ensemble Model ---")
joblib.dump(stack_model, 'models/ensemble_model.pkl')

# --- Evaluation & Visualizations ---
print("--- Generating Visualizations ---")

# 1. Algorithm Comparison (Simplified for this script)
accuracies = {}
for name, model in base_learners:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracies[name.upper()] = accuracy_score(y_test, y_pred)

y_pred_stack = stack_model.predict(X_test)
accuracies['ENSEMBLE'] = accuracy_score(y_test, y_pred_stack)

plt.figure(figsize=(10, 6))
sns.barplot(x=list(accuracies.keys()), y=list(accuracies.values()), palette='viridis')
plt.title('Algorithm Performance Comparison')
plt.ylabel('Accuracy')
plt.ylim(0.8, 1.0)
plt.savefig('models/comparison.png')
plt.close()

# 2. Confusion Matrix
cm = confusion_matrix(y_test, y_pred_stack)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix - Stacking Ensemble')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.savefig('models/confusion_matrix.png')
plt.close()

# 3. ROC Curve
y_prob_stack = stack_model.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_prob_stack)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC)')
plt.legend(loc="lower right")
plt.savefig('models/roc_curve.png')
plt.close()

print("\nAll done! Model building complete.")
print(f"Final Ensemble Accuracy: {accuracies['ENSEMBLE']:.4f}")
print("Check the 'models/' folder for all outputs.")
