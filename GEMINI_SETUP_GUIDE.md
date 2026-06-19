# Gemini API Integration Setup Guide

## Prerequisites
1. Google AI Studio account (free)
2. Gemini API key

## Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the API key (starts with "AIza...")

## Step 2: Configure Environment Variables

Add the following to your `.env` file:

```env
# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key-here
```

Replace `your-gemini-api-key-here` with your actual API key from Google AI Studio.

## Step 3: Test the Integration

1. Start your Django server: `python manage.py runserver`
2. Navigate to the AI Support page
3. Send a mental health related message
4. You should receive intelligent responses from Gemini

## Features

### Mental Health Focus
- The AI is specifically trained to handle mental health topics
- Provides empathetic and supportive responses
- Offers practical coping strategies
- Encourages professional help when appropriate

### Safety Features
- Crisis detection for self-harm or suicide mentions
- Automatic provision of crisis resources
- Content filtering for inappropriate topics
- Fallback responses when API is unavailable

### Supported Topics
- Stress and anxiety management
- Depression and mood support
- Academic pressure and exam stress
- Relationship and social challenges
- Sleep and wellness habits
- Career and future planning stress
- Coping with life transitions

### Off-Topic Handling
- Redirects non-mental health topics back to mental health support
- Maintains focus on emotional well-being
- Provides gentle guidance to relevant topics

## API Endpoints

### POST /api/gemini-chat/
Sends a message to the Gemini AI for mental health support.

**Request Body:**
```json
{
    "message": "I'm feeling really anxious about my exams",
    "conversation_history": [
        {
            "sender": "user",
            "content": "Hello",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "sender": "ai", 
            "content": "Hello! I'm here to support you...",
            "timestamp": "2024-01-01T10:00:01Z"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "response": "I understand that exam anxiety can be really overwhelming...",
    "safety_flags": [],
    "model": "gemini-1.5-flash",
    "timestamp": "2024-01-01T10:00:02Z",
    "crisis_detected": false
}
```

## Troubleshooting

### Common Issues

1. **"Gemini API not available"**
   - Check that GEMINI_API_KEY is set in your .env file
   - Verify the API key is correct and active
   - Ensure you have internet connectivity

2. **"Invalid API key"**
   - Double-check your API key from Google AI Studio
   - Make sure there are no extra spaces or characters
   - Verify the key is active in your Google AI Studio dashboard

3. **"Content blocked"**
   - The AI has safety filters that may block certain content
   - Try rephrasing your message
   - Focus on mental health topics

4. **Fallback responses**
   - If the API is down, the system uses local responses
   - Check your internet connection
   - Verify the API key is still valid

### Testing

You can test the integration by sending these sample messages:

**Mental Health Topics (Supported):**
- "I'm feeling anxious about my upcoming exams"
- "I've been feeling really down lately"
- "I'm having trouble sleeping"
- "I'm stressed about my relationships"

**Non-Mental Health Topics (Redirected):**
- "What's the weather like?"
- "How do I cook pasta?"
- "Tell me about history"

## Security Notes

- API keys are stored securely in environment variables
- All conversations are processed through Google's secure infrastructure
- No conversation data is permanently stored
- Crisis detection triggers immediate resource provision

## Cost Information

- Google AI Studio provides free tier usage
- Check your usage limits in the Google AI Studio dashboard
- Monitor your API usage to avoid unexpected charges
