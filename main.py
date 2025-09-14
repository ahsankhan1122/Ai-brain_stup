import os
import sys
import time
import threading
import traceback
import psutil

from app.collector import run_collector
from app.retrainer import run_retrainer
from app.flask_ui import run_flask_app

try:
    from app.chatbot_interface import TradingChatbot
except ImportError:
    TradingChatbot = None


def kill_port_5000():
    """Kill any process running on port 5000 (to avoid conflicts)."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr.port == 5000:
                    print(f"Force killing PID {proc.pid} using port 5000 ({proc.info['name']})")
                    proc.kill()
        except Exception:
            continue


def run_background(shared_state):
    """Start background threads for collector + retrainer."""
    threading.Thread(target=run_collector, args=(shared_state,), daemon=True).start()
    threading.Thread(target=run_retrainer, args=(shared_state,), daemon=True).start()


def run_flask(shared_state, llm_explainer=None):
    """Run Flask UI in a background thread."""
    threading.Thread(target=lambda: run_flask_app(shared_state, llm_explainer), daemon=True).start()


def run_telegram(shared_state, llm_explainer=None):
    """Run Telegram bot in a background thread."""
    try:
        from app.telegram_bot import run_telegram_bot
        threading.Thread(target=run_telegram_bot, args=(shared_state, llm_explainer), daemon=True).start()
    except Exception as e:
        print("Telegram bot failed:", e)
        traceback.print_exc()


def main():
    print("=== AI Crypto Trading System ===")

    # Parse command-line flags
    chatbot_mode = '--chatbot' in sys.argv
    server_mode = '--server' in sys.argv
    telegram_mode = '--telegram' in sys.argv
    all_mode = '--all' in sys.argv or (
        not chatbot_mode and not server_mode and not telegram_mode
    )

    kill_port_5000()

    # Shared state for modules
    shared_state = {
        'latest_data': None,
        'latest_signals': [],
        'latest_indicators': {},
        'balance': 10000,
        'positions': {},
        'trade_history': [],
        'market_condition': None,
        'strategy_performance': {}
    }

    # ✅ Chatbot only
    if chatbot_mode:
        if not TradingChatbot:
            print("❌ Chatbot module not found. Please check app/chatbot_interface.py")
            sys.exit(1)

        print("Chatbot mode active. No Flask, no Telegram, no background collectors.")
        chatbot = TradingChatbot(shared_state)
        try:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                response = chatbot.respond(user_input)
                print("Bot:", response)
        except KeyboardInterrupt:
            print("Exiting chatbot...")
        sys.exit(0)

    # ✅ Server only (collectors + retrainer + Flask, no Telegram)
    if server_mode:
        run_background(shared_state)
        print("Background collectors and retrainer started...")
        run_flask(shared_state, None)
        print("Flask UI started at http://localhost:5000")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Shutting down server...")
        sys.exit(0)

    # ✅ Telegram only
    if telegram_mode:
        print("Telegram bot mode active. No collectors, no Flask.")
        run_telegram(shared_state, None)
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Shutting down Telegram...")
        sys.exit(0)

    # ✅ Default: full system (collectors + retrainer + Flask + Telegram)
    if all_mode:
        run_background(shared_state)
        print("Background collectors and retrainer started...")
        run_flask(shared_state, None)
        run_telegram(shared_state, None)
        print("Flask UI started at http://localhost:5000")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Shutting down system...")
        sys.exit(0)


if __name__ == "__main__":
    main()

