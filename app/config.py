from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = ""
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    supabase_service_role_key: str = ""
 


    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "pharmalens-data"
    r2_public_url: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_app_url: str = "https://pharmalens.ai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    ai_timeout_seconds: float = 10.0

    # Newsletter delivery. Empty API key keeps delivery disabled while preview remains available.
    resend_api_key: str = ""
    newsletter_from_email: str = ""
    newsletter_from_name: str = "PharmaLens AI"
    newsletter_public_url: str = "http://localhost:3000"
    newsletter_token_secret: str = ""

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    env: str = "development"
    upload_requests_per_hour: int = 30
    copilot_requests_per_hour: int = 60
    max_server_upload_mb: int = 100

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def r2_endpoint_url(self) -> str:
        return f"https://{self.r2_account_id}.r2.cloudflarestorage.com"

    def validate_production(self) -> None:
        """Fail fast on launch-critical production configuration only."""
        if self.env.lower() not in {"production", "prod"}:
            return
        missing = []
        for field in ("database_url", "supabase_url", "supabase_service_role_key"):
            if not getattr(self, field):
                missing.append(field.upper())
        if not self.cors_origin_list:
            missing.append("CORS_ORIGINS")
        if not any((self.openai_api_key, self.gemini_api_key, self.groq_api_key, self.openrouter_api_key)):
            missing.append("LLM_PROVIDER_API_KEY")
        if self.resend_api_key and not (self.newsletter_from_email and self.newsletter_token_secret):
            missing.append("NEWSLETTER_FROM_EMAIL/NEWSLETTER_TOKEN_SECRET")
        if missing:
            raise RuntimeError("Missing production configuration: " + ", ".join(missing))


settings = Settings()
