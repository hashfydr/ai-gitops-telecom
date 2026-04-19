import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def train_network_model():
    # 1. Load the data we generated with Mininet
    data_path = 'simulation/network_data.csv'
    if not os.path.exists(data_path):
        print("Error: Dataset not found! Run simulation first.")
        return

    df = pd.read_csv(data_path)

    # 2. Features (X) and Target (y)
    # We use latency to predict the label (0 or 1)
    X = df[['latency']] 
    y = df['label']

    # 3. Train a Random Forest Model
    # Even though this is a simple gap, Random Forest is 
    # excellent for more complex telecom data later.
    print("Training AI model on Mininet data...")
    model = RandomForestClassifier(n_estimators=10)
    model.fit(X, y)

    # 4. Save the "Brain"
    # This .joblib file is what the controller will use 
    # to make real-time decisions.
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/network_model.joblib')
    
    print("SUCCESS: AI Model trained and saved to models/network_model.joblib")

if __name__ == '__main__':
    train_network_model()
