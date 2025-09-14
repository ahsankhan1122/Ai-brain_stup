from flask import Flask, render_template, jsonify
import threading
import os
from typing import Dict, Any
from datetime import datetime

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR,
            static_url_path='/static')

# Add configuration for URL generation outside request context
app.config['SERVER_NAME'] = 'localhost:5000'  # Change if different port
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Global reference to shared state and LLM explainer
shared_state = None
llm_explainer = None


def run_flask_app(state_ref, explainer_ref):
    """
    Start the Flask web UI.
    """
    global shared_state, llm_explainer
    shared_state = state_ref
    llm_explainer = explainer_ref

    # Run Flask in a separate thread
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000),
        daemon=True
    )
    flask_thread.start()

    print("Flask UI started at http://localhost:5000")


@app.route('/')
def dashboard():
    """Main dashboard page."""
    if shared_state is None:
        return render_template('dashboard.html', error="System not initialized")

    # Prepare data for the template
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'balance': shared_state.get('balance', 0),
        'market_condition': shared_state.get('market_condition', {}),
        'signals': shared_state.get('latest_signals', []),
        'positions': list(shared_state.get('positions', {}).values()),
        'performance': shared_state.get('strategy_performance', {})
    }

    return render_template('dashboard.html', **data)


@app.route('/signals')
def signals():
    """Signals page with detailed explanations."""
    if shared_state is None or llm_explainer is None:
        return render_template('signals.html', error="System not initialized")

    signals_with_explanations = []
    signals = shared_state.get('latest_signals', [])
    market_condition = shared_state.get('market_condition', {})
    indicators = shared_state.get('latest_indicators', {})

    for signal in signals:
        explanation = llm_explainer.generate_explanation(signal, market_condition, indicators)
        signal_with_expl = signal.copy()
        signal_with_expl['explanation'] = explanation
        signals_with_explanations.append(signal_with_expl)

    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signals': signals_with_explanations
    }

    return render_template('signals.html', **data)


@app.route('/api/data')
def api_data():
    """JSON API endpoint for system data."""
    if shared_state is None:
        return jsonify({'error': 'System not initialized'})

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'balance': shared_state.get('balance', 0),
        'market_condition': shared_state.get('market_condition', {}),
        'signals': shared_state.get('latest_signals', []),
        'positions': list(shared_state.get('positions', {}).values()),
        'performance': shared_state.get('strategy_performance', {})
    })


# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error=error), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=error), 500


# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    # This allows running the Flask app directly for testing
    app.run(debug=True, host='0.0.0.0', port=5000)

