import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters

import asyncio
from config import TELEGRAM_CONFIG

# Global references
shared_state = None
llm_explainer = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🤖 AI Crypto Trading Bot\n\n'
        'Available commands:\n'
        '/signal - Get latest trading signals\n'
        '/why [signal_index] - Explain a specific signal\n'
        '/balance - Check current balance\n'
        '/performance - View strategy performance'
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if shared_state is None:
        await update.message.reply_text("System not initialized yet.")
        return
    
    signals = shared_state.get('latest_signals', [])
    if not signals:
        await update.message.reply_text("No signals available at the moment.")
        return
    
    message = "📈 Latest Trading Signals:\n\n"
    for i, signal in enumerate(signals):
        message += f"{i+1}. {signal.get('action', 'HOLD')} - {signal.get('reason', 'No reason')}\n"
        message += f"   Confidence: {signal.get('confidence', 0)*100:.1f}%\n\n"
    
    await update.message.reply_text(message)

async def why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if llm_explainer is None or shared_state is None:
        await update.message.reply_text("System not initialized yet.")
        return
    
    try:
        args = context.args
        index = int(args[0]) - 1 if args else 0
        
        signals = shared_state.get('latest_signals', [])
        if not signals or index < 0 or index >= len(signals):
            await update.message.reply_text("Invalid signal index.")
            return
        
        signal = signals[index]
        market_condition = shared_state.get('market_condition', {})
        indicators = shared_state.get('latest_indicators', {})
        
        explanation = llm_explainer.generate_explanation(signal, market_condition, indicators)
        
        message = f"🤔 Explanation for Signal #{index+1}:\n\n"
        message += f"Action: {signal.get('action', 'HOLD')}\n"
        message += f"Confidence: {signal.get('confidence', 0)*100:.1f}%\n\n"
        message += f"Explanation:\n{explanation}"
        
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error generating explanation: {e}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if shared_state is None:
        await update.message.reply_text("System not initialized yet.")
        return
    
    balance = shared_state.get('balance', 0)
    positions = shared_state.get('positions', {})
    
    message = f"💰 Account Balance: ${balance:.2f}\n"
    message += f"📊 Open Positions: {len(positions)}\n\n"
    
    if positions:
        message += "Open Positions:\n"
        for pos_id, position in positions.items():
            message += f"• {position.get('action', '')} at ${position.get('price', 0):.2f}\n"
    
    await update.message.reply_text(message)

async def performance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if shared_state is None:
        await update.message.reply_text("System not initialized yet.")
        return
    
    performance = shared_state.get('strategy_performance', {})
    if not performance:
        await update.message.reply_text("No performance data available yet.")
        return
    
    message = "📊 Strategy Performance:\n\n"
    for strategy, stats in performance.items():
        message += f"• {strategy}:\n"
        message += f"  Avg Profit: ${stats.get('avg_profit', 0):.2f}\n"
        message += f"  Win Rate: {stats.get('win_rate', 0)*100:.1f}%\n"
        message += f"  Trades: {stats.get('total_trades', 0)}\n\n"
    
    await update.message.reply_text(message)

def run_telegram_bot(state_ref, explainer_ref):
    global shared_state, llm_explainer
    shared_state = state_ref
    llm_explainer = explainer_ref
    
    token = TELEGRAM_CONFIG.get('token')
    if not token or token == 'your_telegram_bot_token_here':
        print("Telegram bot not configured. Please set TELEGRAM_TOKEN in config.py")
        return

    async def main():
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("signal", signal))
        app.add_handler(CommandHandler("why", why))
        app.add_handler(CommandHandler("balance", balance))
        app.add_handler(CommandHandler("performance", performance))
        print("Telegram bot is running...")
        # ✅ Disable signal handlers to run safely inside threads
        await app.run_polling(stop_signals=None)

    def run_async_bot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())

    import threading
    threading.Thread(target=run_async_bot, daemon=True).start()

