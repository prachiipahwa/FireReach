from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application Settings for FireReach Backend.
    Uses pydantic_settings to load from environment variables / .env file.
    """
    PROJECT_NAME: str = "FireReach AI Outreach Engine"
    API_V1_STR: str = "/api/v1"
    
    # API Keys for tools and LLMs
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    SENDGRID_API_KEY: str = ""
    HUNTER_API_KEY: str = ""
    
    # Optional API keys for additional signal harvesting
    SERPAPI_API_KEY: str = ""
    NEWSAPI_KEY: str = ""
    
    # Email Configuration
    SENDER_EMAIL: str = "noreply@firereach.ai"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
