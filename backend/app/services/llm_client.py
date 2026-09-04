"""FreeLLMAPI client for OpenAI-compatible API calls"""
import json
import httpx
from typing import Dict, Any, Optional
from ..config import FREELLMAPI_API_KEY, FREELLMAPI_BASE_URL, FREELLMAPI_MODEL


class LLMClientError(Exception):
    """Exception raised for LLM API errors"""
    pass


def call_llm(context: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    """
    Call FreeLLMAPI with structured context to get plain English explanation.

    Args:
        context: Factual investigation results from the investigator
        timeout: Request timeout in seconds

    Returns:
        Dictionary with structured response: status, plain_english, exceptions, confidence

    Raises:
        LLMClientError: On API failure, malformed response, or invalid output
    """
    if not FREELLMAPI_API_KEY:
        raise LLMClientError("FREELLMAPI_API_KEY is not configured")

    system_prompt = """You are a settlement investigation assistant for a fintech platform.
You will receive factual investigation data about a transaction from three sources:
- Gateway (the payment processor)
- Bank (the settlement bank)
- Ledger (internal accounting)

Your job is to EXPLAIN the findings in plain English. You must NEVER invent transaction facts.
If data is missing or conflicting, you MUST mention it in the exceptions list and reduce confidence.

You MUST respond with ONLY valid JSON in this exact format (no markdown, no commentary):
{
    "status": "SETTLED" | "PENDING" | "FAILED" | "PARTIAL" | "UNKNOWN",
    "plain_english": "A clear, non-technical explanation of what happened with this transaction",
    "exceptions": ["Specific data gaps or uncertainties, e.g. 'Bank settlement record not found'"],
    "confidence": 0.0-1.0
}

Rules:
- status must match the overall_status from the factual data unless evidence suggests otherwise
- plain_english must reference actual data provided (amounts, dates, merchant_id, processor_ref)
- exceptions must list every missing source or inconsistency from the factual data
- confidence: 1.0 if all sources match perfectly, 0.0 if no data, reduce by 0.2 per anomaly
- Do not invent transactions, amounts, or merchants
- Keep plain_english to 2-4 sentences
- Output ONLY the JSON object"""

    user_prompt = f"""Investigate this transaction and explain the findings:

```json
{json.dumps(context, indent=2, default=str)}
```

Provide your response as valid JSON only."""

    url = f"{FREELLMAPI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {FREELLMAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": FREELLMAPI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as e:
        raise LLMClientError(f"HTTP error calling FreeLLMAPI: {str(e)}")
    except json.JSONDecodeError as e:
        raise LLMClientError(f"Failed to parse LLM API response as JSON: {str(e)}")

    # Extract the assistant message content
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMClientError(f"Unexpected LLM response structure: {str(e)}")

    # Parse the JSON content from the LLM
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMClientError(f"LLM response is not valid JSON: {str(e)}")

    return result


def validate_llm_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that the LLM response has the required fields and types.
    Returns a sanitized dictionary.
    """
    valid_statuses = {"SETTLED", "PENDING", "FAILED", "PARTIAL", "UNKNOWN"}

    status = result.get("status", "UNKNOWN")
    if status not in valid_statuses:
        status = "UNKNOWN"

    plain_english = result.get("plain_english", "")
    if not isinstance(plain_english, str):
        plain_english = str(plain_english) if plain_english is not None else ""

    exceptions = result.get("exceptions", [])
    if not isinstance(exceptions, list):
        exceptions = [str(exceptions)]
    exceptions = [str(e) for e in exceptions if e]

    confidence = result.get("confidence", 0.5)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    return {
        "status": status,
        "plain_english": plain_english,
        "exceptions": exceptions,
        "confidence": confidence,
    }