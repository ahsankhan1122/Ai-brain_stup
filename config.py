import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
LIVE_CANDLES_DIR = os.path.join(DATA_DIR, 'live_candles')
TRADE_LOGS_DIR = os.path.join(DATA_DIR, 'trade_logs')
INDICATOR_HISTORY_DIR = os.path.join(DATA_DIR, 'indicator_history')

# Model paths
MODELS_DIR = os.path.join(BASE_DIR, 'models')
PATTERN_MODEL_PATH = os.path.join(MODELS_DIR, 'pattern_model.pkl')
MARKET_MODEL_PATH = os.path.join(MODELS_DIR, 'market_model.pkl')
STRATEGY_MODEL_PATH = os.path.join(MODELS_DIR, 'strategy_model.pkl')

# Bybit API configuration
BYBIT_CONFIG = {
    'testnet': True,
    'api_key': 'api_key',
    'api_secret': 'api_sectret',
}

# Trading parameters
SYMBOLS = ['BTCUSDT', 'ETHUSDT']
INTERVALS = ['15', '60']
INITIAL_BALANCE = 10000  # USD

# Telegram bot configuration
TELEGRAM_CONFIG = {
    'token': 'bot_toke',
    'chat_id': 'chat_id'
}

# Create directories if they don't exist
for directory in [LIVE_CANDLES_DIR, TRADE_LOGS_DIR, INDICATOR_HISTORY_DIR, MODELS_DIR]:
    os.makedirs(directory, exist_ok=True)
