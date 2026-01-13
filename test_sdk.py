from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))

print("Available methods on databases:")
print([m for m in dir(client.databases) if not m.startswith('_')])
