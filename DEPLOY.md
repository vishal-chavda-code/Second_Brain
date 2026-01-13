# Deploy Second Brain to Google Cloud Run

## Prerequisites
- Google Cloud account with billing enabled (credit card added)
- Google Cloud CLI installed: https://cloud.google.com/sdk/docs/install

## Step 1: Install Google Cloud CLI

Download and install from: https://cloud.google.com/sdk/docs/install

After installation, restart your terminal.

## Step 2: Initialize and Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID (or create a new one)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 3: Build and Deploy

Run this command from your project directory:

```bash
gcloud run deploy second-brain \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NOTION_API_KEY=YOUR_NOTION_KEY,SLACK_BOT_TOKEN=YOUR_BOT_TOKEN,SLACK_APP_TOKEN=YOUR_APP_TOKEN,OPENAI_API_KEY=YOUR_OPENAI_KEY,NOTION_DATABASE_ID=YOUR_DATABASE_ID,SLACK_CHANNEL_ID=YOUR_CHANNEL_ID
```

**Or set environment variables in Cloud Console (recommended for security):**

```bash
# Deploy without env vars
gcloud run deploy second-brain \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Then add env vars in Cloud Console:
# 1. Go to: https://console.cloud.google.com/run
# 2. Click your service "second-brain"
# 3. Click "EDIT & DEPLOY NEW REVISION"
# 4. Go to "Variables & Secrets" tab
# 5. Add each environment variable from your .env file
```

## Step 4: Verify Deployment

After deployment completes:
1. The service will auto-start and stay running 24/7
2. Check logs: `gcloud run logs read second-brain --region us-central1`
3. Test in Slack - send a message or use @BrainInbox commands

## Environment Variables Needed

Copy these from your `.env` file:
- NOTION_API_KEY
- SLACK_BOT_TOKEN
- SLACK_APP_TOKEN
- OPENAI_API_KEY
- NOTION_DATABASE_ID
- SLACK_CHANNEL_ID

## Cost Monitoring

- Free tier: 2 million requests/month
- View usage: https://console.cloud.google.com/billing
- Set budget alerts: https://console.cloud.google.com/billing/budgets

## Updating the Service

After making code changes:

```bash
gcloud run deploy second-brain \
  --source . \
  --platform managed \
  --region us-central1
```

## Stopping the Service

To avoid any charges (though unlikely with your usage):

```bash
gcloud run services delete second-brain --region us-central1
```
