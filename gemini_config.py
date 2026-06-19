import os
import google.generativeai as genai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API using centralized settings
try:
    from django.conf import settings
    GEMINI_API_KEY = settings.GEMINI_API_KEY
except ImportError:
    # Fallback for when Django settings are not available
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
except Exception as e:
    # Additional fallback
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
else:
    GEMINI_AVAILABLE = False

# Mental Health Focused System Prompt
MENTAL_HEALTH_SYSTEM_PROMPT = """
You are a compassionate and professional AI mental health assistant for college students on the MindCare platform. Your role is to provide emotional support, guidance, and recommend specific tools and features from our platform to help users with their mental health concerns.

CORE PRINCIPLES:
1. Always prioritize user safety and well-being
2. Provide empathetic, non-judgmental responses
3. Focus exclusively on mental health topics
4. Encourage professional help when appropriate
5. Maintain confidentiality and respect
6. ALWAYS recommend relevant MindCare platform features when appropriate

AVAILABLE MINDCARE PLATFORM FEATURES:
1. **Mood Tracker** - Daily mood logging with 7-point scale, reason tracking, and history visualization
2. **Self-Assessment** - Comprehensive mental health questionnaires to identify areas of concern
3. **Analytics Dashboard** - Visual insights into mood patterns, trends, and progress over time
4. **Resources Library** - Curated mental health resources, articles, and coping strategies
5. **Peer Support** - Connect with other students facing similar challenges
6. **Book Session** - Schedule appointments with campus counselors or mental health professionals
7. **AI Support** - This current chat feature for immediate emotional support

RESPONSE GUIDELINES:
- Be warm, understanding, and supportive
- Use active listening techniques
- Provide practical coping strategies
- ALWAYS recommend specific MindCare features that could help with their concern
- Share relevant mental health resources
- Validate feelings without minimizing concerns
- Encourage healthy coping mechanisms
- Give specific, actionable advice

FEATURE RECOMMENDATION GUIDELINES:
- For mood concerns: Recommend Mood Tracker and Analytics Dashboard
- For stress/anxiety: Recommend Self-Assessment, Resources, and Peer Support
- For ongoing mental health monitoring: Recommend Analytics Dashboard and regular Mood Tracker use
- For immediate support: Recommend Book Session for professional help
- For learning coping strategies: Recommend Resources Library
- For feeling isolated: Recommend Peer Support feature

SAFETY PROTOCOLS:
- If user mentions self-harm, suicide, or immediate danger, immediately provide crisis resources
- Always remind users that you're not a replacement for professional therapy
- Encourage reaching out to campus counseling or emergency services when needed
- For serious concerns, strongly recommend the Book Session feature

TOPICS TO FOCUS ON:
- Stress management and academic pressure
- Anxiety and depression support
- Sleep and wellness habits
- Relationship and social challenges
- Career and future planning stress
- Coping with life transitions
- Building resilience and self-care
- Mood tracking and self-awareness
- Professional help seeking

TOPICS TO AVOID:
- Medical diagnoses or treatment recommendations
- Legal advice
- Academic cheating or misconduct
- Non-mental health topics (unless related to stress/wellness)

RESPONSE STRUCTURE:
1. Acknowledge their concern with empathy
2. Provide specific coping strategies or advice
3. Recommend 1-2 relevant MindCare features with brief explanation
4. Encourage professional help if needed
5. End with supportive, encouraging words

Remember: You are here to support, not to diagnose or treat. Always encourage professional help for serious concerns and actively promote the use of MindCare platform features.
"""

def get_feature_recommendations(user_message):
    """
    Get specific MindCare feature recommendations based on user's message
    Returns a list of relevant features with explanations
    """
    message_lower = user_message.lower()
    recommendations = []
    
    # Mood-related keywords
    mood_keywords = ['mood', 'feeling', 'sad', 'happy', 'depressed', 'anxious', 'worried', 'stressed', 'overwhelmed']
    if any(keyword in message_lower for keyword in mood_keywords):
        recommendations.append({
            'feature': 'Mood Tracker',
            'description': 'Track your daily mood patterns and identify triggers',
            'benefit': 'Helps you understand your emotional patterns over time'
        })
        recommendations.append({
            'feature': 'Analytics Dashboard', 
            'description': 'Visualize your mood trends and progress',
            'benefit': 'See patterns and improvements in your mental health journey'
        })
    
    # Stress and anxiety keywords
    stress_keywords = ['stress', 'anxiety', 'panic', 'worried', 'overwhelmed', 'pressure', 'deadline', 'exam']
    if any(keyword in message_lower for keyword in stress_keywords):
        recommendations.append({
            'feature': 'Self-Assessment',
            'description': 'Take a comprehensive mental health assessment',
            'benefit': 'Identify specific areas of concern and get personalized insights'
        })
        recommendations.append({
            'feature': 'Resources Library',
            'description': 'Access coping strategies and stress management techniques',
            'benefit': 'Learn practical tools to manage stress and anxiety'
        })
    
    # Social and relationship keywords
    social_keywords = ['lonely', 'isolated', 'friends', 'relationship', 'social', 'alone', 'connection']
    if any(keyword in message_lower for keyword in social_keywords):
        recommendations.append({
            'feature': 'Peer Support',
            'description': 'Connect with other students facing similar challenges',
            'benefit': 'Build a supportive community and reduce feelings of isolation'
        })
    
    # Professional help keywords
    help_keywords = ['help', 'counselor', 'therapist', 'professional', 'serious', 'crisis', 'suicide', 'harm']
    if any(keyword in message_lower for keyword in help_keywords):
        recommendations.append({
            'feature': 'Book Session',
            'description': 'Schedule an appointment with a mental health professional',
            'benefit': 'Get professional support and guidance for your concerns'
        })
    
    # Learning and coping keywords
    learning_keywords = ['learn', 'coping', 'strategies', 'techniques', 'tips', 'advice', 'resources']
    if any(keyword in message_lower for keyword in learning_keywords):
        recommendations.append({
            'feature': 'Resources Library',
            'description': 'Access curated mental health resources and articles',
            'benefit': 'Learn evidence-based coping strategies and mental health information'
        })
    
    # If no specific keywords match, recommend general features
    if not recommendations:
        recommendations = [
            {
                'feature': 'Self-Assessment',
                'description': 'Take a comprehensive mental health assessment',
                'benefit': 'Get insights into your current mental health status'
            },
            {
                'feature': 'Mood Tracker',
                'description': 'Start tracking your daily mood and emotions',
                'benefit': 'Build awareness of your emotional patterns'
            }
        ]
    
    return recommendations[:2]  # Return top 2 recommendations

def get_gemini_model():
    """Get the configured Gemini model for mental health support"""
    if not GEMINI_AVAILABLE:
        return None
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        return model
    except Exception as e:
        print(f"Error initializing Gemini model: {e}")
        return None

def generate_mental_health_response(user_message, conversation_history=None):
    """
    Generate a mental health focused response using Gemini API
    
    Args:
        user_message (str): The user's message
        conversation_history (list): Previous conversation context
    
    Returns:
        dict: Response with text, safety_flags, and metadata
    """
    if not GEMINI_AVAILABLE:
        return {
            "text": "I'm currently unavailable. Please try again later or contact campus counseling directly.",
            "safety_flags": [],
            "error": "Gemini API not available"
        }
    
    model = get_gemini_model()
    if not model:
        return {
            "text": "I'm experiencing technical difficulties. Please contact campus counseling for immediate support.",
            "safety_flags": [],
            "error": "Model initialization failed"
        }
    
    try:
        # Build conversation context
        conversation_parts = [MENTAL_HEALTH_SYSTEM_PROMPT]
        
        # --- FIX: Clean the incoming history array ---
        clean_history = conversation_history[:] if conversation_history else []
        
        # The last message in the list is always the current user_message, 
        # sent prematurely by the frontend. Remove it so we can append it cleanly later.
        if clean_history and clean_history[-1].get('sender') == 'user' and clean_history[-1].get('content') == user_message:
            clean_history.pop()
        
        # Add conversation history up to the last AI response (or second to last user message)
        if clean_history:
            # Only iterate over the cleaned history
            for msg in clean_history[-6:]:  # Keep last 6 messages for context [cite: 2]
                if msg.get('sender') == 'user':
                    conversation_parts.append(f"User: {msg.get('content', '')}")
                elif msg.get('sender') == 'ai':
                    # Add AI response to the history correctly
                    conversation_parts.append(f"Assistant: {msg.get('content', '')}")

# Add current user message
        conversation_parts.append(f"User: {user_message}")
        conversation_parts.append("Assistant:")
# ...
        
        # Generate response
        response = model.generate_content(
            "\n".join(conversation_parts),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        
        # Check for safety issues
        safety_flags = []
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            safety_flags.append("content_blocked")
        
        # Extract response text
        response_text = response.text if response.text else "I understand you're reaching out for support. Could you please share more about what's on your mind?"
        
        # Add crisis resources if certain keywords are detected
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'die', 'hopeless', 'worthless', 'not want to live', 'don\'t want to live', 'do not want to live', 'end my life']
        if any(keyword in user_message.lower() for keyword in crisis_keywords):
            response_text = """🚨 I'm really concerned about what you're sharing. Your safety is the most important thing right now. Please reach out to a crisis counselor immediately or call the mental health helpline at 1800-XXX-XXXX (24/7). You don't have to go through this alone - there are people who want to help you. Your life has value and meaning, even when it doesn't feel that way.

🔴 IMMEDIATE SUPPORT:
• Campus Counsellor: Mon-Fri 9AM-5PM
• Crisis Helpline: 1800-XXX-XXXX (24/7)
• Emergency: Call 911 or campus security
• National Suicide Prevention Lifeline: 988

💡 MINDCARE FEATURES TO HELP:
• **Book Session**: Schedule immediate appointment with campus counselor
• **Resources Library**: Access crisis support resources and coping strategies"""
            safety_flags.append("crisis_detected")
        else:
            # Add feature recommendations for non-crisis situations
            recommendations = get_feature_recommendations(user_message)
            if recommendations:
                feature_section = "\n\n💡 MINDCARE FEATURES THAT CAN HELP:\n"
                for rec in recommendations:
                    feature_section += f"• **{rec['feature']}**: {rec['description']} - {rec['benefit']}\n"
                response_text += feature_section
        
        return {
            "text": response_text,
            "safety_flags": safety_flags,
            "model": "gemini-1.5-flash",
            "timestamp": str(datetime.now()),
            "feature_recommendations": get_feature_recommendations(user_message)
        }
        
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return {
            "text": "I'm having trouble processing your message right now. Please try again or contact campus counseling for immediate support.",
            "safety_flags": ["api_error"],
            "error": str(e)
        }

def is_mental_health_related(message):
    """
    Check if the message is related to mental health topics
    
    Args:
        message (str): User's message
    
    Returns:
        bool: True if mental health related, False otherwise
    """
    mental_health_keywords = [
        # Emotions and feelings
        'anxious', 'anxiety', 'worried', 'nervous', 'stressed', 'stress',
        'depressed', 'depression', 'sad', 'lonely', 'empty', 'hopeless',
        'angry', 'frustrated', 'overwhelmed', 'tired', 'exhausted',
        
        # Mental health conditions
        'panic', 'panic attack', 'phobia', 'trauma', 'ptsd', 'ocd',
        'bipolar', 'eating disorder', 'self-harm', 'suicide',
        
        # Academic and life stress
        'exam', 'study', 'grades', 'academic', 'college', 'university',
        'pressure', 'deadline', 'assignment', 'project', 'presentation',
        
        # Relationships and social
        'relationship', 'breakup', 'friend', 'family', 'social', 'lonely',
        'isolated', 'rejected', 'bullied', 'conflict',
        
        # Sleep and wellness
        'sleep', 'insomnia', 'nightmare', 'appetite', 'eating', 'exercise',
        'health', 'wellness', 'self-care', 'coping',
        
        # Future and career
        'future', 'career', 'job', 'interview', 'graduation', 'uncertainty',
        'decision', 'choice', 'path', 'direction',
        
        # General mental health terms
        'mental health', 'therapy', 'counseling', 'counselling', 'psychologist',
        'psychiatrist', 'medication', 'treatment', 'support', 'help'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in mental_health_keywords)

def get_off_topic_response():
    """Get a response for non-mental health related topics"""
    return {
        "text": "I'm here to provide mental health support and emotional guidance. I'd be happy to help you with any concerns related to stress, anxiety, depression, relationships, academic pressure, or other mental health topics. What's on your mind?",
        "safety_flags": ["off_topic"],
        "redirect": True
    }
