from openai import OpenAI
from app.core.config import settings
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )

    def chat(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        """
        General-purpose chat using deepseek-chat.
        Supports system messages, structured JSON output, and fast responses.
        """
        try:
            kwargs = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 4096,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            return f"Error communicating with DeepSeek: {str(e)}"

    def reason(self, user_prompt: str) -> str:
        """
        Deep reasoning using deepseek-reasoner for complex analysis.
        NOTE: deepseek-reasoner only supports user/assistant roles, no system messages.
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM reason error: {e}")
            # Fallback to chat model
            return self.chat([{"role": "user", "content": user_prompt}])

    def extract_structured_data(self, text: str, schema_description: str) -> Dict[str, Any]:
        prompt = f"""Extract structured information from the following document text.

Schema (return ONLY these fields as valid JSON):
{schema_description}

RULES:
- If a field is not found in the text, set it to null.
- Do NOT hallucinate values. Only extract what is explicitly stated.
- For prices, extract numeric values only (no currency symbols in number fields).
- For dates, use YYYY-MM-DD format.

Document Text:
{text}
"""
        messages = [{"role": "user", "content": prompt}]
        response_str = self.chat(messages, json_mode=True)
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM: {response_str[:200]}")
            return {"error": "Failed to parse structured data", "raw": response_str}

llm_engine = LLMEngine()
