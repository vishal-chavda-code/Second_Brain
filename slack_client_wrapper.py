"""
Slack API wrapper for Second Brain notifications and input
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID


class SlackBrain:
    def __init__(self):
        self.client = WebClient(token=SLACK_BOT_TOKEN)
        self.default_channel = SLACK_CHANNEL_ID

    def send_message(self, message: str, channel: str = None):
        """Send a message to Slack"""
        try:
            response = self.client.chat_postMessage(
                channel=channel or self.default_channel,
                text=message
            )
            return response
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
            return None

    def send_formatted_note(self, title: str, content: str, source: str = None, channel: str = None):
        """Send a formatted note notification to Slack"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📝 {title}", "emoji": True}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": content[:2000]}  # Slack limit
            }
        ]
        
        if source:
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Source: *{source}*"}]
            })

        try:
            response = self.client.chat_postMessage(
                channel=channel or self.default_channel,
                blocks=blocks,
                text=title  # Fallback text
            )
            return response
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
            return None

    def get_channel_history(self, channel: str = None, limit: int = 10):
        """Get recent messages from a channel"""
        try:
            response = self.client.conversations_history(
                channel=channel or self.default_channel,
                limit=limit
            )
            return response.get("messages", [])
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
            return []

    def send_ai_summary(self, summary: str, original_query: str = None, channel: str = None):
        """Send an AI-generated summary to Slack"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 AI Summary", "emoji": True}
            }
        ]
        
        if original_query:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Query:* {original_query}"}
            })
        
        blocks.append({
            "type": "divider"
        })
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": summary[:2000]}
        })

        try:
            response = self.client.chat_postMessage(
                channel=channel or self.default_channel,
                blocks=blocks,
                text="AI Summary"
            )
            return response
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
            return None


if __name__ == "__main__":
    # Test connection
    slack = SlackBrain()
    print("✅ Slack client initialized!")
    print(f"Default channel: {SLACK_CHANNEL_ID}")
