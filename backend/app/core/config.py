from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_env: str = "dev"
    api_key: str = ""
    allowed_origins: str = "http://localhost:3000"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.0-flash-001"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Kubernetes
    kubeconfig_path: str = "~/.kube/config"
    kubeconfig_allowlist_dir: str = ""
    kubectl_alternate_server: str = ""

    # InsForge realtime
    insforge_url: str = ""
    insforge_anon_key: str = ""

    # Limits
    max_request_body_bytes: int = 1024 * 1024
    rate_limit_per_minute: int = 30
    kubectl_semaphore_size: int = 5

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"


settings = Settings()
