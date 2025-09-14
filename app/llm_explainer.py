from typing import Dict, Any
from llama_cpp import Llama
import os

class LLMExplainer:
    """
    Uses your local TinyLLaMA GGUF model to explain trading signals
    and handle free-form chat queries.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "tinyllama-1.1b-chat-v1.0.Q4_0.gguf")

        # Same initialization as agent_chat.py
        self.llm = Llama(
            model_path=model_path,
            n_ctx=1024,      # match agent_chat
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )
        print(f"LLMExplainer ready (TinyLLaMA: {model_path})")

    # 🔹 Free-form chatbot interface
    def chat(self, message: str) -> str:
        """
        Handle general chat queries using the exact settings from agent_chat.py.
        """
        try:
            prompt = f"Q: {message}\nA:"
            output = self.llm(
                prompt,
                max_tokens=100,
                stop=["\n", "Q:", "###"],
                temperature=0.1,
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            return f"[TinyLLaMA Chat Error] {e}"

    # 🔹 Structured trading explanation
    def generate_explanation(
        self,
        signal: Dict[str, Any],
        market_condition: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for trading signals using TinyLLaMA.
        """
        prompt = self._create_prompt(signal, market_condition, indicators)

        try:
            output = self.llm(
                prompt,
                max_tokens=100,
                stop=["\n", "Q:", "###"],
                temperature=0.1,
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            print(f"[TinyLLaMA Error] {e}")
            return self._fallback_explanation(signal, market_condition, indicators)

    def _create_prompt(
        self,
        signal: Dict[str, Any],
        market_condition: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> str:
        action = signal.get('action', 'HOLD')
        reason = signal.get('reason', '')
        confidence = signal.get('confidence', 0) * 100
        condition = market_condition.get('condition', 'Unknown')

        return f"""
Q: Explain this cryptocurrency trading signal in simple terms:

Action: {action}
Market Condition: {condition}
Confidence: {confidence:.1f}%
Reason: {reason}

A:"""

    def _fallback_explanation(
        self,
        signal: Dict[str, Any],
        market_condition: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> str:
        action = signal.get('action', 'HOLD')
        reason = signal.get('reason', '')
        confidence = signal.get('confidence', 0) * 100
        condition = market_condition.get('condition', 'Unknown')

        return (
            f"The system suggests {action} with {confidence:.1f}% confidence, "
            f"due to {reason} in a {condition} market."
        )

