# app/train_market_model.py
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
from config import MARKET_MODEL_PATH

class MarketModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def load_training_data(self, data_dir="data/training/market_data"):
        """
        Load labeled market condition data.
        You need to create this data first!
        """
        # Dummy data for example
        X = np.random.rand(800, 8)  # 800 samples, 8 features
        y = np.random.randint(0, 8, 800)  # 8 market condition classes
        
        return X, y
    
    def train(self):
        """Train the market classification model."""
        print("Loading training data...")
        X, y = self.load_training_data()
        
        print("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("Training model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.2f}")
        
        # Save model
        joblib.dump(self.model, MARKET_MODEL_PATH)
        print(f"Model saved to {MARKET_MODEL_PATH}")
        
        return accuracy

def main():
    trainer = MarketModelTrainer()
    accuracy = trainer.train()
    print(f"Market model training complete! Accuracy: {accuracy:.2f}")

if __name__ == "__main__":
    main()
