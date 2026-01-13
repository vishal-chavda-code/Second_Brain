"""
Slack Bot Listener - Automatically captures messages to Notion Second Brain
Run this script to start listening to Slack messages 24/7
"""
import os
import re
import time
import threading
from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from notion_client_wrapper import NotionBrain
from chatgpt_processor import ChatGPTProcessor
from slack_client_wrapper import SlackBrain

load_dotenv()

# Create Flask app for health checks (required for Cloud Run)
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return {'status': 'healthy', 'service': 'second-brain-bot'}, 200

@flask_app.route('/health')
def health():
    return 'OK', 200

# Initialize components
notion = NotionBrain()
ai = ChatGPTProcessor()
slack_helper = SlackBrain()

# Initialize Slack Bolt App
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Store for tracking processed messages
processed_messages = set()


@app.event("message")
def handle_message(event, say, client):
    """Handle all incoming Slack messages with comprehensive error handling"""
    try:
        _handle_message_internal(event, say, client)
    except Exception as e:
        print(f"❌ Critical message handler error: {e}")
        import traceback
        traceback.print_exc()
        try:
            say(f"❌ An unexpected error occurred: {str(e)}")
        except:
            pass

def _handle_message_internal(event, say, client):
    """Handle all incoming messages"""
    print(f"📨 Received message: {event}")
    
    # Ignore bot messages and already processed messages
    if event.get("bot_id") or event.get("subtype"):
        print("   ↳ Skipping (bot message or subtype)")
        return
    
    message_ts = event.get("ts")
    if message_ts in processed_messages:
        return
    processed_messages.add(message_ts)
    
    text = event.get("text", "").strip()
    user_id = event.get("user")
    channel = event.get("channel")
    
    if not text:
        return
    
    # Get user info for context
    try:
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"]
    except:
        user_name = "Unknown"
    
    text_lower = text.lower()
    
    # Command: capture / note / save
    if text_lower.startswith(("capture:", "note:", "save:", "capture ", "note ", "save ")):
        handle_capture(text, user_name, say)
    
    # Command: ask / question / ?
    elif text_lower.startswith(("ask:", "ask ", "question:", "question ", "?")):
        handle_question(text, say)
    
    # Command: digest / summary
    elif "digest" in text_lower or "summary" in text_lower:
        handle_digest(say)
    
    # Command: help
    elif text_lower in ["help", "commands", "?"]:
        handle_help(say)
    
    # Default: Auto-capture everything else to Notion
    else:
        handle_auto_capture(text, user_name, say)


def handle_capture(text: str, user_name: str, say):
    """Capture a note explicitly"""
    print(f"🔍 handle_capture called with text: {text}")
    
    # Remove command prefix
    content = re.sub(r'^(capture|note|save)[:\s]+', '', text, flags=re.IGNORECASE).strip()
    
    if not content:
        say("❌ Please provide content to capture. Example: `capture: my brilliant idea`")
        return
    
    print(f"   Content to save: {content}")
    
    try:
        # Save to Notion first (doesn't need AI)
        title = content[:50] + "..." if len(content) > 50 else content
        tags = []
        
        print(f"   Saving to Notion: {title}")
        
        # Try AI categorization, but don't fail if rate limited
        follow_up = None
        try:
            ai_analysis = ai.categorize_note(content)
            title_prompt = f"Generate a short, descriptive title (max 6 words) for this note: {content}"
            title = ai.process(title_prompt).strip('"').strip("'").strip()
            tags = ai_analysis.get("tags", [])
            follow_up = ai_analysis.get("follow_up_date")
            print(f"   AI title: {title}, tags: {tags}, follow_up: {follow_up}")
        except Exception as ai_error:
            print(f"   AI error (using fallback): {ai_error}")
        
        # Save to Notion
        result = notion.add_note(
            title=title,
            content=content,
            tags=tags,
            source="slack",
            follow_up_date=follow_up
        )
        
        print(f"   ✅ Saved to Notion! Page ID: {result.get('id')}")
        
        tags_str = ", ".join(tags) or "none"
        say(f"✅ *Captured to Second Brain!*\n📝 *Title:* {title}\n🏷️ *Tags:* {tags_str}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        say(f"❌ Error capturing note: {str(e)}")


def handle_question(text: str, say):
    """Answer a question using the Second Brain"""
    # Remove command prefix
    question = re.sub(r'^(ask|question|\?)[:\s]+', '', text, flags=re.IGNORECASE).strip()
    
    if not question:
        say("❌ Please ask a question. Example: `ask: what did I note about project X?`")
        return
    
    try:
        say("🤔 Thinking...")
        
        # Search Notion for context
        search_results = notion.search_notes(question)
        context_notes = []
        
        for result in search_results[:5]:
            try:
                title = result.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                if title:
                    context_notes.append(title)
            except:
                pass
        
        # Get AI answer with context
        response = ai.answer_question(question, context_notes)
        
        say(f"🧠 *Answer:*\n{response}")
        
    except Exception as e:
        say(f"❌ Error processing question: {str(e)}")


def handle_digest(say):
    """Generate and send daily digest"""
    try:
        print("📊 Generating digest...")
        say("📊 Generating digest...")
        
        recent_notes = notion.get_recent_notes(limit=10)
        note_titles = []
        
        for note in recent_notes:
            try:
                title = note.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                if title:
                    note_titles.append(title)
            except:
                pass
        
        if not note_titles:
            say("📭 No recent notes found in your Second Brain.")
            return
        
        # Try AI summary, but fallback to simple list
        try:
            summary = ai.generate_daily_summary(note_titles)
            say(f"📊 *Daily Digest:*\n\n{summary}")
        except Exception as ai_err:
            print(f"   AI failed, using simple list: {ai_err}")
            # Simple fallback without AI
            notes_list = "\n".join([f"• {title}" for title in note_titles])
            say(f"📊 *Recent Notes:*\n\n{notes_list}\n\n_({len(note_titles)} notes captured)_")
        
    except Exception as e:
        print(f"   ❌ Digest error: {e}")
        import traceback
        traceback.print_exc()
        say(f"❌ Error generating digest: {str(e)}")


def handle_auto_capture(text: str, user_name: str, say):
    """Auto-capture any message to Notion (default behavior)"""
    # Skip very short messages or common chat phrases
    skip_phrases = ["hi", "hello", "hey", "ok", "okay", "thanks", "thank you", "yes", "no", "lol", "haha"]
    if len(text) < 10 or text.lower() in skip_phrases:
        print(f"   ↳ Skipping (too short or common phrase)")
        return
    
    print(f"🔍 Auto-capturing: {text}")
    
    try:
        # Use simple title without AI to avoid rate limits
        title = text[:50] + "..." if len(text) > 50 else text
        tags = []
        
        print(f"   Saving to Notion...")
        
        # Try AI only if available
        follow_up = None
        try:
            ai_analysis = ai.categorize_note(text)
            title_prompt = f"Generate a short, descriptive title (max 6 words) for this note: {text}"
            title = ai.process(title_prompt).strip('"').strip("'").strip()
            tags = ai_analysis.get("tags", [])
            follow_up = ai_analysis.get("follow_up_date")
            print(f"   AI title: {title}, tags: {tags}, follow_up: {follow_up}")
        except Exception as ai_err:
            print(f"   AI skipped (using simple title): {ai_err}")
        
        # Save to Notion
        result = notion.add_note(
            title=title,
            content=text,
            tags=tags,
            source="slack-auto",
            follow_up_date=follow_up
        )
        
        print(f"   ✅ Saved to Notion! Page ID: {result.get('id')}")
        
        # Try to confirm in Slack (but don't fail if can't)
        try:
            say(f"💾 Auto-saved: *{title}*")
        except Exception as slack_err:
            print(f"   ⚠️  Slack confirmation failed (but Notion save succeeded): {slack_err}")
        
    except Exception as e:
        print(f"   ❌ Auto-capture error: {e}")
        import traceback
        traceback.print_exc()
        # Notify user of error
        try:
            say(f"❌ Error auto-capturing message: {str(e)}")
        except:
            pass  # Don't fail if Slack notification fails


def handle_help(say):
    """Show help message"""
    help_text = """
🧠 *Second Brain Commands:*

📝 *Capture Notes:*
• `capture: your thought here`
• `note: important idea`
• `save: meeting notes`

❓ *Ask Questions:*
• `ask: what did I note about X?`
• `question: summarize my project notes`

📊 *Get Summaries:*
• `digest` - Get daily summary
• `summary` - Same as digest

💡 *Tips:*
• Any message over 10 chars is auto-saved
• Short messages (hi, ok, etc.) are ignored
• All notes are AI-categorized automatically
"""
    say(help_text)


@app.event("app_mention")
def handle_mention(event, say):
    """Handle @mentions of the bot"""
    text = event.get("text", "")
    user_id = event.get("user")
    
    # Remove the mention from text
    text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
    
    print(f"📨 Mention received: {text}")
    
    if not text:
        handle_help(say)
        return
    
    # Get user name for capture attribution
    user_name = "Unknown"
    try:
        from slack_client_wrapper import SlackBrain
        slack = SlackBrain()
        user_info = slack.client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"]
    except:
        pass
    
    text_lower = text.lower()
    
    # Route to appropriate handler based on command
    if text_lower.startswith(("ask:", "ask ", "question:", "question ", "?")):
        handle_question(text, say)
    elif "digest" in text_lower or "summary" in text_lower:
        handle_digest(say)
    elif text_lower in ["help", "commands"]:
        handle_help(say)
    else:
        # Default: capture anything else (with or without "capture:" prefix)
        # Remove "capture:", "note:", "save:" if present
        content = re.sub(r'^(capture|note|save)[:\s]+', '', text, flags=re.IGNORECASE).strip()
        handle_capture(f"capture: {content}", user_name, say)


def main():
    """Start the Slack bot listener with health check server for Cloud Run"""
    print("=" * 50)
    print("🧠 SECOND BRAIN - Slack Listener")
    print("=" * 50)
    print("\n✅ Bot is starting...")
    
    # Start Flask health check server in background thread FIRST
    port = int(os.getenv("PORT", 8080))
    
    def run_flask():
        flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask time to start accepting connections
    time.sleep(2)
    print(f"✅ Health check server running on port {port}")
    
    print("📡 Listening for Slack messages...")
    print("\nCommands:")
    print("  capture: <text>  - Save a note")
    print("  ask: <question>  - Ask your brain")
    print("  digest           - Get daily summary")
    print("  help             - Show all commands")
    print("\n💡 All messages are auto-captured by default!")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    # Check if we have Socket Mode token
    app_token = os.getenv("SLACK_APP_TOKEN")
    
    if app_token:
        # Use Socket Mode (recommended, no public URL needed)
        print("✅ Starting Socket Mode handler...")
        handler = SocketModeHandler(app, app_token)
        handler.start()
    else:
        # Fallback: Start with HTTP server (needs ngrok or public URL)
        print("⚠️  No SLACK_APP_TOKEN found. Using HTTP mode.")
        print("   For Socket Mode, add SLACK_APP_TOKEN to your .env file")
        app.start(port=3000)


if __name__ == "__main__":
    main()
