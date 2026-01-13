import os
from dotenv import load_dotenv

load_dotenv()

# Notion Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
