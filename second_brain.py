"""
Second Brain - Main orchestrator connecting Notion, Slack, and ChatGPT
"""
from notion_client_wrapper import NotionBrain
from slack_client_wrapper import SlackBrain
from chatgpt_processor import ChatGPTProcessor


class SecondBrain:
    def __init__(self):
        print("🧠 Initializing Second Brain...")
        self.notion = NotionBrain()
        self.slack = SlackBrain()
        self.ai = ChatGPTProcessor()
        print("✅ Second Brain ready!")

    def capture_thought(self, title: str, content: str, tags: list = None, notify_slack: bool = True):
        """Capture a new thought/note and optionally notify via Slack"""
        # Get AI suggestions for categorization
        ai_suggestions = self.ai.categorize_note(content)
        
        # Merge suggested tags with provided tags
        all_tags = list(set((tags or []) + ai_suggestions.get("tags", [])))
        
        # Save to Notion
        result = self.notion.add_note(
            title=title,
            content=content,
            tags=all_tags,
            source="second_brain"
        )
        
        # Notify via Slack
        if notify_slack:
            self.slack.send_formatted_note(
                title=title,
                content=f"{content}\n\n*Tags:* {', '.join(all_tags)}",
                source="Notion Second Brain"
            )
        
        return result

    def ask(self, question: str, search_notes: bool = True):
        """Ask a question to your Second Brain"""
        context_notes = []
        
        if search_notes:
            # Search Notion for relevant notes
            search_results = self.notion.search_notes(question)
            for result in search_results[:5]:  # Top 5 results
                try:
                    title = result.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
                    context_notes.append(title)
                except:
                    pass
        
        # Get AI response with context
        response = self.ai.answer_question(question, context_notes)
        
        return response

    def daily_digest(self, send_to_slack: bool = True):
        """Generate and optionally send daily digest"""
        # Get recent notes
        recent_notes = self.notion.get_recent_notes(limit=10)
        
        note_titles = []
        for note in recent_notes:
            try:
                title = note.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
                note_titles.append(title)
            except:
                pass
        
        # Generate summary
        summary = self.ai.generate_daily_summary(note_titles)
        
        if send_to_slack:
            self.slack.send_ai_summary(summary, "Daily Digest")
        
        return summary

    def process_slack_input(self, message: str):
        """Process a message from Slack and take appropriate action"""
        # Determine intent
        message_lower = message.lower()
        
        if message_lower.startswith("note:") or message_lower.startswith("capture:"):
            # Extract and save note
            content = message.split(":", 1)[1].strip()
            title = content[:50] + "..." if len(content) > 50 else content
            return self.capture_thought(title, content, notify_slack=False)
        
        elif message_lower.startswith("ask:") or message_lower.startswith("question:"):
            # Answer question
            question = message.split(":", 1)[1].strip()
            return self.ask(question)
        
        elif "digest" in message_lower or "summary" in message_lower:
            return self.daily_digest(send_to_slack=False)
        
        else:
            # Default: treat as question
            return self.ask(message)

    def quick_capture(self, text: str):
        """Quick capture - AI determines title and tags automatically"""
        # Use AI to generate title
        title_prompt = f"Generate a short, descriptive title (max 6 words) for this note: {text}"
        title = self.ai.process(title_prompt).strip('"').strip("'")
        
        return self.capture_thought(title, text)


def main():
    """Interactive CLI for Second Brain"""
    brain = SecondBrain()
    
    print("\n" + "="*50)
    print("🧠 SECOND BRAIN - Interactive Mode")
    print("="*50)
    print("\nCommands:")
    print("  capture <text>  - Capture a new thought")
    print("  ask <question>  - Ask your second brain")
    print("  digest          - Get daily digest")
    print("  quit            - Exit")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("🧠 > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            if user_input.lower().startswith("capture "):
                text = user_input[8:]
                result = brain.quick_capture(text)
                print("✅ Captured!")
            
            elif user_input.lower().startswith("ask "):
                question = user_input[4:]
                response = brain.ask(question)
                print(f"\n📖 {response}\n")
            
            elif user_input.lower() == "digest":
                summary = brain.daily_digest()
                print(f"\n📊 Daily Digest:\n{summary}\n")
            
            else:
                # Treat as question by default
                response = brain.ask(user_input)
                print(f"\n📖 {response}\n")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
