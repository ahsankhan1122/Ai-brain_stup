# app/train_pattern_model.py
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
from config import PATTERN_MODEL_PATH

class PatternModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def load_training_data(self, data_dir="data/training/pattern_data"):
        """
        Load labeled pattern data for training.
        You need to create this data first!
        """
        # This is where you'd load your labeled training data
        # For now, we'll create dummy data
        X = np.random.rand(1000, 10)  # 1000 samples, 10 features
        y = np.random.randint(0, 5, 1000)  # 5 pattern classes
        
        return X, y
    
    def extract_features(self, df):
        """
        Extract features from OHLCV data for pattern recognition.
        Same as in PatternDetector.
        """
        features = df.copy()
        features['body_size'] = abs(features['close'] - features['open'])
        features['upper_wick'] = features['high'] - features[['open', 'close']].max(axis=1)
        features['lower_wick'] = features[['open', 'close']].min(axis=1) - features['low']
        features['price_change'] = features['close'].pct_change()
        features['volume_change'] = features['volume'].pct_change()
        return features.dropna()
    
    def train(self):
        """Train the pattern recognition model."""
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
        joblib.dump(self.model, PATTERN_MODEL_PATH)
        print(f"Model saved to {PATTERN_MODEL_PATH}")
        
        return accuracy

def main():
    trainer = PatternModelTrainer()
    accuracy = trainer.train()
    print(f"Pattern model training complete! Accuracy: {accuracy:.2f}")

if __name__ == "__main__":
    main()
