from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Field(..., env="VAR_NAME") says “this is required, read from VAR_NAME”
    git_token: str = Field(..., env="GIT_TOKEN")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    github_repository: str = Field(..., env="GITHUB_REPOSITORY")

    class Config:
        # Tell Pydantic to read a .env file in this directory
        env_file = "../.env"
        env_file_encoding = "utf-8"

# Create a single, validated instance
settings = Settings()
