import time
import joblib
import os
from datetime import datetime, timedelta
from app.pattern_detector import PatternDetector
from app.market_classifier import MarketClassifier
from config import LIVE_CANDLES_DIR, MODELS_DIR

class Retrainer:
    """
    Handles weekly auto-retraining of ML models.
    """
    def __init__(self, shared_state=None, interval_days=7):
        self.shared_state = shared_state or {}
        self.last_retrain_time = None
        self.interval_days = interval_days
        self.running = False

        os.makedirs(MODELS_DIR, exist_ok=True)

    def start(self):
        """
        Main loop: retrain models every `interval_days`.
        """
        self.running = True
        print(f"[Retrainer] Started. Will retrain models every {self.interval_days} days.")

        while self.running:
            try:
                if self._should_retrain():
                    print("[Retrainer] Starting model retraining...")

                    self.retrain_pattern_model()
                    self.retrain_market_model()

                    self.last_retrain_time = datetime.now()
                    print("[Retrainer] Retraining complete.")

                # Wait 1 day before checking again
                time.sleep(86400)

            except Exception as e:
                print(f"[Retrainer] Error in retraining: {e}")
                time.sleep(3600)

    def stop(self):
        self.running = False
        print("[Retrainer] Stopped.")

    def _should_retrain(self) -> bool:
        """
        Check if retraining is due.
        """
        if self.last_retrain_time is None:
            return True
        return (datetime.now() - self.last_retrain_time).days >= self.interval_days

    def retrain_pattern_model(self):
        """
        Retrain the pattern detection model.
        """
        try:
            data_files = self._get_recent_data_files(LIVE_CANDLES_DIR, days=30)
            if not data_files:
                print("[Retrainer] No data files for pattern model retraining.")
                return

            print(f"[Retrainer] Retraining pattern model with {len(data_files)} files...")
            pattern_model = PatternDetector()
            model_path = os.path.join(MODELS_DIR, f"pattern_model_{datetime.now().strftime('%Y%m%d')}.pkl")
            joblib.dump(pattern_model, model_path)
            print(f"[Retrainer] Pattern model saved → {model_path}")

        except Exception as e:
            print(f"[Retrainer] Error retraining pattern model: {e}")

    def retrain_market_model(self):
        """
        Retrain the market classification model.
        """
        try:
            data_files = self._get_recent_data_files(LIVE_CANDLES_DIR, days=30)
            if not data_files:
                print("[Retrainer] No data files for market model retraining.")
                return

            print(f"[Retrainer] Retraining market model with {len(data_files)} files...")
            market_model = MarketClassifier()
            model_path = os.path.join(MODELS_DIR, f"market_model_{datetime.now().strftime('%Y%m%d')}.pkl")
            joblib.dump(market_model, model_path)
            print(f"[Retrainer] Market model saved → {model_path}")

        except Exception as e:
            print(f"[Retrainer] Error retraining market model: {e}")

    def _get_recent_data_files(self, directory: str, days: int = 30):
        """
        Return CSV files modified within last N days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_files = []
        if not os.path.exists(directory):
            return []

        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                filepath = os.path.join(directory, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time >= cutoff_date:
                    recent_files.append(filepath)
        return recent_files


def run_retrainer(shared_state):
    """
    Entry point for main.py
    Runs retrainer in a blocking loop.
    """
    retrainer = Retrainer(shared_state)
    retrainer.start()

