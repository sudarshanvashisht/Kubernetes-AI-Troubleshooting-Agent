import secrets
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(_api_key_header)):
    if not settings.api_key:
        if settings.is_dev:
            import logging
            logging.warning("API_KEY not set; allowing request in dev mode")
            return
        raise HTTPException(status_code=503, detail="API key not configured")
    if api_key is None or not secrets.compare_digest(api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
