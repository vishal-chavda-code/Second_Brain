# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY notion_client_wrapper.py .
COPY slack_client_wrapper.py .
COPY chatgpt_processor.py .
COPY slack_listener.py .

# Run the Slack listener
CMD ["python", "slack_listener.py"]
