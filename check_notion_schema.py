"""Check what properties exist in your Notion database"""
from notion_client import Client
from config import NOTION_API_KEY, NOTION_DATABASE_ID
import json

client = Client(auth=NOTION_API_KEY)

# Retrieve database schema
database = client.databases.retrieve(database_id=NOTION_DATABASE_ID)

print("=" * 60)
print("FULL DATABASE INFO")
print("=" * 60)
print(json.dumps(database, indent=2))

print("\n" + "=" * 60)
print("PROPERTIES")
print("=" * 60)

properties = database.get("properties", {})

if not properties:
    print("❌ No properties found! Database response:")
    print(json.dumps(database, indent=2))
else:
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get("type", "unknown")
        print(f"\n✓ Property: '{prop_name}'")
        print(f"  Type: {prop_type}")
    
    print(f"\nTotal properties: {len(properties)}")
    print("\nLooking for 'Follow Up' field...")

    if "Follow Up" in properties:
        print("✅ 'Follow Up' field EXISTS")
        print(f"   Type: {properties['Follow Up'].get('type')}")
    else:
        print("❌ 'Follow Up' field NOT FOUND")
        print("\nAll property names:")
        for name in properties.keys():
            print(f"   - '{name}'")
