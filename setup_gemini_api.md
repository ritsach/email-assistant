# Gemini API Setup Guide

## Getting a Gemini API Key

### Step 1: Go to Google AI Studio
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar

### Step 2: Create API Key
1. Click "Create API Key"
2. Choose "Create API key in new project" or select existing project
3. Copy the generated API key (starts with `AIza...`)

### Step 3: Set Environment Variable
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

Or add to your shell profile:
```bash
echo 'export GEMINI_API_KEY="your-gemini-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 4: Set Environment Variable
The API key is now read from environment variables (no hardcoding):

**Option A: Temporary (current session only)**
```bash
export GEMINI_API_KEY="AIzaSyC..."
```

**Option B: Permanent (add to shell profile)**
```bash
echo 'export GEMINI_API_KEY="AIzaSyC..."' >> ~/.zshrc
source ~/.zshrc
```

**Option C: Use setup script**
```bash
./setup_env.sh
```

## Available Gemini Models

- **gemini-1.5-pro** - Most capable model (recommended)
- **gemini-1.5-flash** - Faster, lighter model
- **gemini-1.0-pro** - Previous generation

## Testing Gemini Integration

Run the test script:
```bash
python test_gemini_connection.py
```

## Benefits of Gemini

✅ **Free tier available** - Generous free usage limits
✅ **Fast responses** - Quick email processing
✅ **Good quality** - High-quality email analysis
✅ **Easy setup** - Simple API key authentication
✅ **No AWS required** - Direct Google integration

## Usage Limits

- **Free tier**: 15 requests per minute, 1M tokens per day
- **Paid tier**: Higher limits available
- **Rate limiting**: Automatic handling by the library

## Troubleshooting

### Common Issues

1. **Invalid API Key**
   - Verify the key is correct
   - Check if the key is active
   - Ensure no extra spaces or characters

2. **Rate Limiting**
   - Wait a few minutes before retrying
   - Consider upgrading to paid tier

3. **Model Not Available**
   - Check if the model name is correct
   - Verify your account has access to the model

### Debug Mode

Enable debug output by modifying the AI assistant:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Get your Gemini API key
2. Update the email assistant configuration
3. Test the integration
4. Start using intelligent email processing

---

**Note**: Gemini provides excellent performance for email analysis and is much easier to set up than AWS Bedrock. The free tier should be sufficient for most email processing needs.
