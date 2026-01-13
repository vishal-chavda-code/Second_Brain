from notion_client_wrapper import NotionBrain

brain = NotionBrain()
print(f"Database ID: {brain.database_id}")
print("\nTesting direct search...")
results = brain.client.search(
    query="",
    filter={"property": "object", "value": "page"}
)
print(f"Total results: {len(results.get('results', []))}")
for page in results.get("results", [])[:5]:
    print(f"  - Parent DB: {page.get('parent', {}).get('database_id')}")
    print(f"    Expected: {brain.database_id}")
    
print("\nTesting get_recent_notes...")
notes = brain.get_recent_notes(limit=5)
print(f"Found {len(notes)} notes")
for note in notes:
    title = note.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
    print(f"  - {title}")
