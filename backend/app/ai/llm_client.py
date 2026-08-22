"""LLM client for communicating with OpenRouter.

Provides async chat completions with timeout, error handling,
and retry capabilities.
"""

import asyncio
import httpx
from loguru import logger

from app.core.config import settings

class LLMClient:
    """Async client for OpenRouter completions."""

    async def chat(self, system_prompt: str, user_prompt: str, retries: int = 2, timeout: int = 60) -> str:
        """Send chat messages to OpenRouter and return the completion text.

        Args:
            system_prompt: System context instructions for SRE behavior.
            user_prompt: Collected investigation data to analyze.
            retries: Number of retry attempts on network or rate limit failure.
            timeout: HTTP timeout in seconds.

        Returns:
            The raw text response from the model.
        """
        api_key = settings.openrouter_api_key
        if not api_key:
            logger.error("OPENROUTER_API_KEY environment variable is not set")
            raise ValueError("OpenRouter API key is missing")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/insforge/ai-kubernetes-agent",
            "X-Title": "AI Kubernetes Troubleshooting Agent"
        }

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1  # Low temperature for structured/deterministic results
        }

        url = f"{settings.openrouter_base_url}/chat/completions"
        backoff = 2.0

        for attempt in range(retries + 1):
            try:
                logger.info(f"Sending request to OpenRouter (model: {settings.openrouter_model}), attempt {attempt + 1}")
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise ValueError("OpenRouter returned empty choices")
                        
                    content = choices[0].get("message", {}).get("content", "").strip()
                    logger.info("Successfully received response from OpenRouter")
                    return content

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error from OpenRouter (status {e.response.status_code}): {e.response.text}")
                # Retry on rate limits (429) or server errors (5xx)
                if attempt < retries and (e.response.status_code == 429 or e.response.status_code >= 500):
                    logger.info(f"Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    raise
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                logger.warning(f"Connection or timeout error from OpenRouter: {e}")
                if attempt < retries:
                    logger.info(f"Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    raise

        raise RuntimeError("Failed to get response from OpenRouter after retries")

llm_client = LLMClient()
