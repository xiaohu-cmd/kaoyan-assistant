"""
AI writing feedback service using OpenAI-compatible API.
Evaluates English essays for the postgraduate entrance exam (考研英语二).
"""

import json
import os
import httpx
from typing import Optional

DEFAULT_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT = """You are an expert English writing evaluator for the Chinese postgraduate entrance exam (考研英语二). Your task is to evaluate an essay and provide structured feedback in JSON format.

Evaluation criteria (考研英语二 scoring: 0-15 total):
- Grammar & Spelling (0-5 points): Check for grammatical errors, spelling mistakes, and punctuation issues
- Vocabulary Range (0-5 points): Assess lexical diversity, word choice appropriateness, and collocation accuracy
- Sentence Complexity (0-5 points): Evaluate sentence variety, clause usage, and syntactic sophistication
- Content & Structure (0-5 points): Judge task completion, logical flow, and coherence. Then scale to 0-15 total.

Output MUST be valid JSON with this exact structure:
{
  "grammar_errors": [
    {"position": "original text fragment", "error_type": "grammar/spelling/punctuation", "correction": "corrected version", "explanation": "brief Chinese explanation"}
  ],
  "vocabulary_score": 4.0,
  "vocabulary_comment": "Chinese comment on vocabulary",
  "sentence_score": 3.5,
  "sentence_comment": "Chinese comment on sentence structure",
  "content_score": 4.0,
  "content_comment": "Chinese comment on content",
  "overall_score": 11.5,
  "overall_comment": "Chinese overall assessment",
  "optimized_version": "A polished version of the entire essay with improvements applied"
}

Note: overall_score = (vocabulary_score + sentence_score + content_score). Clamp to 0-15 range.
"""


async def get_ai_feedback(
    essay_content: str,
    essay_type: str,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None
) -> dict:
    """
    Send an essay to an OpenAI-compatible API for AI feedback.

    Args:
        essay_content: The full text of the essay
        essay_type: "small" (小作文, ~100 words) or "large" (大作文, ~150-200 words)
        api_key: API key; if None, reads from settings.json
        api_base: API base URL; defaults to OpenAI
        model: Model name; defaults to gpt-3.5-turbo

    Returns:
        dict with grammar_errors, vocabulary_score, sentence_score,
        content_score, overall_score, optimized_version, raw_feedback
    """
    if api_key is None:
        api_key = _load_api_key_from_settings()

    if not api_key:
        word_count = len(essay_content.split())
        return {
            "grammar_errors": json.dumps([], ensure_ascii=False),
            "vocabulary_score": 0.0,
            "sentence_score": 0.0,
            "content_score": 0.0,
            "overall_score": 0.0,
            "ai_feedback": json.dumps({"error": "No API key configured. Set it in Settings page."}, ensure_ascii=False),
            "optimized_version": "",
            "raw_feedback": f"AI feedback unavailable: No API key configured. Word count: {word_count}",
        }

    base = api_base or DEFAULT_API_BASE
    model_name = model or DEFAULT_MODEL
    url = f"{base.rstrip('/')}/chat/completions"

    type_label = "小作文 ~100 words" if essay_type == "small" else "大作文 ~150-200 words"
    user_prompt = f"Essay type: {essay_type} ({type_label})\n\nEssay content:\n{essay_content}\n\nPlease evaluate this essay according to the criteria. Return ONLY valid JSON, no extra text."

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]

            # Try to parse JSON from the response
            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError:
                # Try to extract JSON block from markdown code fence
                if "```json" in raw_content:
                    json_str = raw_content.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                elif "```" in raw_content:
                    json_str = raw_content.split("```")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                else:
                    result = {}

            grammar_errors = result.get("grammar_errors", [])
            if isinstance(grammar_errors, str):
                grammar_errors = []

            overall = float(result.get("overall_score", 0))
            overall = max(0.0, min(15.0, overall))
            vocab = float(result.get("vocabulary_score", 0))
            sent = float(result.get("sentence_score", 0))
            cont = float(result.get("content_score", 0))

            return {
                "grammar_errors": json.dumps(grammar_errors, ensure_ascii=False),
                "vocabulary_score": max(0.0, min(5.0, vocab)),
                "sentence_score": max(0.0, min(5.0, sent)),
                "content_score": max(0.0, min(5.0, cont)),
                "overall_score": overall,
                "ai_feedback": json.dumps(result, ensure_ascii=False),
                "optimized_version": result.get("optimized_version", ""),
                "raw_feedback": raw_content,
            }

        except httpx.HTTPStatusError as e:
            return _build_error_result(essay_content, f"API error: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            return _build_error_result(essay_content, f"Connection error: {str(e)}")
        except Exception as e:
            return _build_error_result(essay_content, f"Unexpected error: {str(e)}")


def _load_api_key_from_settings() -> Optional[str]:
    """Load API key from settings.json if it exists."""
    settings_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "settings.json"
    )
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            return settings.get("ai_api_key", None)
    except Exception:
        pass
    return None


def _build_error_result(essay_content: str, message: str) -> dict:
    """Return an error result when AI API is unavailable."""
    word_count = len(essay_content.split())
    return {
        "grammar_errors": json.dumps([], ensure_ascii=False),
        "vocabulary_score": 0.0,
        "sentence_score": 0.0,
        "content_score": 0.0,
        "overall_score": 0.0,
        "ai_feedback": json.dumps({"error": message}, ensure_ascii=False),
        "optimized_version": "",
        "raw_feedback": f"AI feedback unavailable: {message}. Word count: {word_count}",
    }
