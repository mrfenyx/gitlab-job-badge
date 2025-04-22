import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITLAB_API_URL = os.getenv("GITLAB_API_URL")
    GITLAB_WEB_URL = os.environ.get("GITLAB_WEB_URL")
    GITLAB_ACCESS_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN")
