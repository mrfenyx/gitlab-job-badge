import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITLAB_API_URL = os.getenv("GITLAB_API_URL")
    GITLAB_WEB_URL = os.getenv("GITLAB_WEB_URL")
    GITLAB_ACCESS_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN")
    AZURE_SSO = os.getenv("AZURE_SSO", "false").lower() == "true"
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "default-client-id")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "default-client-secret")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "default-tenant-id")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-insecure-key")
