# Strands Token Cost Optimization Demo

This web application demonstrates token cost optimization strategies using Strands agents:

1. **ConversationManager Comparison**: Compare different conversation manager types
2. **Prompt Cache Analysis**: Compare performance with/without prompt caching

## Features

- Interactive web interface for testing different configurations
- Real-time token usage tracking
- Cost comparison visualization
- Side-by-side results display

## Setup

```bash
pip install -r requirements.txt
```

## Configuration

Configure AWS credentials for Bedrock:

**Option 1: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1  # or your preferred region
```

**Option 2: AWS Profile**
```bash
export AWS_PROFILE=your_profile_name
export AWS_REGION=us-east-1
```

**Option 3: AWS CLI Configuration**
```bash
aws configure
```

## Run

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## ConversationManager Types

- **BufferedConversationManager**: Keeps full conversation history
- **SlidingWindowConversationManager**: Maintains a sliding window of recent messages
- **SummarizingConversationManager**: Summarizes older messages to reduce tokens

## Prompt Caching

Prompt caching can significantly reduce costs by reusing previously processed context.
