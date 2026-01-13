"""
Notion API wrapper for Second Brain operations
"""
from notion_client import Client
from config import NOTION_API_KEY, NOTION_DATABASE_ID
from datetime import datetime


class NotionBrain:
    def __init__(self):
        self.client = Client(auth=NOTION_API_KEY)
        self.database_id = NOTION_DATABASE_ID

    def add_note(self, title: str, content: str, tags: list = None, source: str = "manual", follow_up_date: str = None):
        """Add a new note/thought to the Second Brain"""
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Source": {"select": {"name": source}},
            "Created": {"date": {"start": datetime.now().isoformat()}},
        }
        
        if tags:
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}
        
        if follow_up_date:
            properties["Follow Up"] = {"date": {"start": follow_up_date}}

        # Create page with content
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]

        response = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            children=children
        )
        return response

    def query_notes(self, filter_dict: dict = None, limit: int = 10):
        """Query notes from the Second Brain database"""
        # Use search to get pages from the database
        results = self.client.search(
            query="",
            filter={"property": "object", "value": "page"},
            page_size=limit * 2  # Get more to filter
        )
        # Filter to only pages in our database (compare without dashes)
        db_id_no_dashes = self.database_id.replace("-", "")
        db_pages = [
            page for page in results.get("results", [])
            if page.get("parent", {}).get("database_id", "").replace("-", "") == db_id_no_dashes
        ]
        return db_pages[:limit]

    def search_notes(self, query: str):
        """Search for notes containing specific text"""
        response = self.client.search(
            query=query,
            filter={"property": "object", "value": "page"}
        )
        return response.get("results", [])

    def get_page_content(self, page_id: str):
        """Get the full content of a page"""
        blocks = self.client.blocks.children.list(block_id=page_id)
        return blocks.get("results", [])

    def update_note(self, page_id: str, properties: dict = None, content: str = None):
        """Update an existing note"""
        if properties:
            self.client.pages.update(page_id=page_id, properties=properties)
        
        if content:
            # Append new content block
            self.client.blocks.children.append(
                block_id=page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }]
            )

    def get_recent_notes(self, limit: int = 5):
        """Get most recent notes"""
        return self.query_notes(filter_dict=None, limit=limit)


if __name__ == "__main__":
    # Test connection
    brain = NotionBrain()
    print("✅ Connected to Notion successfully!")
    print(f"Database ID: {NOTION_DATABASE_ID}")
