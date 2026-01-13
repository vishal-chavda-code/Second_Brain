"""Check properties from an actual page in the database"""
from notion_client import Client
from config import NOTION_API_KEY, NOTION_DATABASE_ID
import json

client = Client(auth=NOTION_API_KEY)

# Query pages from the database
results = client.search(
    query="",
    filter={"property": "object", "value": "page"},
    page_size=1
)

# Filter to only pages in our database
db_id_no_dashes = NOTION_DATABASE_ID.replace("-", "")
db_pages = [
    page for page in results.get("results", [])
    if page.get("parent", {}).get("database_id", "").replace("-", "") == db_id_no_dashes
]

if db_pages:
    page = db_pages[0]
    print("PROPERTIES FROM ACTUAL PAGE:")
    print("=" * 60)
    properties = page.get("properties", {})
    for prop_name in properties.keys():
        print(f"  - '{prop_name}'")
    
    print(f"\nTotal: {len(properties)}")
    
    if "Follow Up" in properties:
        print("\nFollow Up field EXISTS!")
    else:
        print("\nFollow Up field NOT FOUND")
        print("\nCheck if any similar:")
        for name in properties.keys():
            if "follow" in name.lower():
                print(f"  Found: '{name}'")
else:
    print("No pages found in database")
