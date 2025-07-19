from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """Hospital Management System Configuration"""
    
    # Application settings
    app_name: str = "Hospital Management System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database settings
    # Default to SQLite for development, MySQL for production
    database_url: str = "sqlite:///./hospital.db"
    
    # Security settings
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    cors_origins: list = ["*"]
    
    @field_validator('*', mode='before')
    @classmethod
    def strip_strings(cls, v):
        """Strip whitespace and carriage returns from all string values"""
        if isinstance(v, str):
            return v.strip()
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Try to use MySQL if available, fallback to SQLite
        mysql_database = os.getenv("MYSQL_DATABASE", "").strip()
        if mysql_database:
            mysql_user = os.getenv("MYSQL_USER", "hospital_user").strip()
            mysql_password = os.getenv("MYSQL_PASSWORD", "hospital_pass123").strip()
            mysql_host = os.getenv("MYSQL_HOST", "localhost").strip()
            mysql_port = os.getenv("MYSQL_PORT", "3306").strip()
            mysql_database = mysql_database.strip()
            
            # Check if running in Docker (mysql host vs localhost)
            if os.getenv("RUNNING_IN_DOCKER"):
                mysql_host = "mysql"  # Docker service name
            
            self.database_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
            print(f"🔗 Using MySQL: {mysql_host}:{mysql_port}/{mysql_database}")
        else:
            print("📁 Using SQLite fallback: ./hospital.db")
    
    class Config:
        env_file = [".env", "../.env", "../../.env"]  # Look in multiple locations
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env file


# Load settings from environment variables or .env file
settings = Settings()