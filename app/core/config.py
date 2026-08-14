from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # Database Config
    LOCAL_MONGODB_URL: str = "mongodb://localhost:27017"
    LOCAL_DB_NAME: str = "local-vertical_search_engine_cw"
    
    CLOUD_MONGODB_URL: str = "" 
    CLOUD_DB_NAME: str = "cloud-vertical_search_engine_cw"
    
    # Crawler Config
    SEED_URL: str = "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/"
    ALLOWED_DOMAIN: str = "pureportal.coventry.ac.uk"
    USER_AGENT: str = "CoventryVerticalSearchBot/1.0 (+educational IR project)"
    CHROME_VERSION: int = 146
    
    # Limits & Delays
    CRAWL_DELAY_SECONDS: int = 10
    MAX_PAGES: int = 100

    # Pydantic v2 standard for loading .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()