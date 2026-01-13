# Second Brain - Automated Notion Knowledge Capture

An intelligent Slack bot that automatically captures messages to your Notion database using AI-powered categorization.

## Features

- **Auto-capture**: Automatically saves Slack messages to Notion
- **AI Processing**: Uses GPT-4 to generate titles, tags, and categorization
- **Smart Commands**: 
  - `@BrainInbox capture: <text>` - Save a note
  - `@BrainInbox ask: <question>` - Query your knowledge base
  - `@BrainInbox digest` - Get AI-generated summary of recent notes
  - `@BrainInbox help` - Show all commands
- **24/7 Operation**: Runs on Google Cloud Run for continuous availability

## Setup

### 1. Prerequisites

- Python 3.13+
- Notion account with API access
- Slack workspace with bot permissions
- OpenAI API key
- Google Cloud account (for deployment)

### 2. Local Development

1. Clone the repository:
```bash
git clone https://github.com/vishal-chavda-code/Second_Brain.git
cd Second_Brain
```

2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run locally:
```bash
python slack_listener.py
```

### 3. Cloud Deployment

See [DEPLOY.md](DEPLOY.md) for complete Google Cloud Run deployment instructions.

## Configuration

### Notion Setup
1. Create a Notion integration at https://www.notion.so/my-integrations
2. Create a database with these columns: Name, Tags, Source, Created, Status, Follow Up
3. Share the database with your integration
4. Copy the database ID from the URL

### Slack Setup
1. Create a Slack app at https://api.slack.com/apps
2. Enable Socket Mode and generate app-level token
3. Add bot scopes: `chat:write`, `channels:history`, `app_mentions:read`
4. Install app to workspace and invite bot to channel
5. Copy bot token and app token

### OpenAI Setup
1. Get API key from https://platform.openai.com/api-keys
2. Ensure billing is enabled for API access

## Architecture

```
Slack Message → Socket Mode Listener → AI Processing (GPT-4) → Notion Database
                     ↓
              Flask Health Check (for Cloud Run)
```

## Files

- `slack_listener.py` - Main bot application
- `notion_client_wrapper.py` - Notion API interface
- `chatgpt_processor.py` - OpenAI integration
- `slack_client_wrapper.py` - Slack messaging helper
- `config.py` - Environment configuration
- `second_brain.py` - Interactive CLI (local use)

## Security

- All API keys stored in `.env` (gitignored)
- Environment variables configured in Cloud Run
- No secrets in source code

## License

MIT

## Author

Vishal Chavda
