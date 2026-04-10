import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

def train_milestone2_detector(csv_path):
    data = pd.read_csv(csv_path)
    X = data[['lost_packets', 'delay_sum_ns', 'jitter_ns']]
    y = data['label']
    
    # Stratified split to ensure both classes are in training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Milestone 2 Enhancement: Handling class imbalance
    model = LogisticRegression(class_weight='balanced')
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    print("\n" + "="*40)
    print("SAMSUNG PRISM: MILESTONE 2 PREDICTIVE REPORT")
    print("="*40)
    print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print("\nFeature Importance (Coefficients):")
    for feature, coef in zip(X.columns, model.coef_[0]):
        print(f"- {feature}: {coef:.4f}")
    
    print("\nDetailed Performance Metrics:")
    print(classification_report(y_test, y_pred, zero_division=0))

if __name__ == "__main__":
    train_milestone2_detector('results/training_data.csv')
