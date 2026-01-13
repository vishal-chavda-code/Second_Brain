"""
Test Slack connection - send a test message
"""
from slack_client_wrapper import SlackBrain

slack = SlackBrain()

print("🧪 Testing Slack connection...")
print(f"Channel ID: {slack.default_channel}")

try:
    result = slack.send_message("🧠 Second Brain Test: Connection successful!")
    if result:
        print("✅ Message sent successfully!")
        print(f"Message timestamp: {result.get('ts')}")
    else:
        print("❌ Failed to send message")
except Exception as e:
    print(f"❌ Error: {e}")
