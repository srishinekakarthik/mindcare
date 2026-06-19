"""
Fallback Gemini implementation that doesn't require the google module
This provides intelligent responses without external API calls
"""

import os
from datetime import datetime

def is_mental_health_related(message):
    """Check if the message is related to mental health topics"""
    mental_health_keywords = [
        # Emotions and feelings
        'anxious', 'anxiety', 'worried', 'nervous', 'stressed', 'stress',
        'depressed', 'depression', 'sad', 'lonely', 'empty', 'hopeless',
        'angry', 'frustrated', 'overwhelmed', 'tired', 'exhausted',
        
        # Mental health conditions
        'panic', 'panic attack', 'phobia', 'trauma', 'ptsd', 'ocd',
        'bipolar', 'eating disorder', 'self-harm', 'suicide', 'kill myself',
        'end it all', 'hurt myself', 'not want to live', 'don\'t want to live',
        'do not want to live', 'end my life', 'hopeless', 'worthless',
        
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

def generate_mental_health_response(user_message, conversation_history=None):
    """
    Generate a mental health focused response using intelligent fallback
    """
    try:
        # Crisis detection - check this first
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'die', 'hopeless', 'worthless', 'not want to live', 'end my life', 'don\'t want to live', 'do not want to live']
        if any(keyword in user_message.lower() for keyword in crisis_keywords):
            response_text = """🚨 I'm really concerned about what you're sharing. Your safety is the most important thing right now. Please reach out to a crisis counselor immediately or call the mental health helpline at 1800-XXX-XXXX (24/7). You don't have to go through this alone - there are people who want to help you. Your life has value and meaning, even when it doesn't feel that way.

🔴 IMMEDIATE SUPPORT:
• Campus Counsellor: Mon-Fri 9AM-5PM
• Crisis Helpline: 1800-XXX-XXXX (24/7)
• Emergency: Call 911 or campus security
• National Suicide Prevention Lifeline: 988"""
            
            return {
                "text": response_text,
                "safety_flags": ["crisis_detected"],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Anxiety support
        if any(keyword in user_message.lower() for keyword in ['anxious', 'anxiety', 'worried', 'nervous', 'panic']):
            response_text = """I understand that anxiety can feel overwhelming and scary. It's completely normal to feel this way, especially during stressful times. Here are some techniques that might help:

🧘 BREATHING TECHNIQUES:
• 4-7-8 breathing: Inhale for 4 counts, hold for 7, exhale for 8
• Box breathing: Inhale 4, hold 4, exhale 4, hold 4
• Belly breathing: Focus on breathing into your diaphragm

🎯 GROUNDING TECHNIQUES:
• 5-4-3-2-1: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste
• Progressive muscle relaxation
• Mindfulness meditation

💙 RESOURCES AVAILABLE:
• Book a counseling session through our platform
• Join our anxiety support groups
• Access our wellness library for more techniques

What's making you feel anxious right now? I'm here to help you work through it."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Depression support
        if any(keyword in user_message.lower() for keyword in ['depressed', 'sad', 'down', 'hopeless', 'empty']):
            response_text = """I hear that you're going through a really difficult time. Depression can make everything feel heavy and overwhelming, like you're carrying a weight that never lifts. Please know that:

💙 YOU ARE NOT ALONE:
• Your feelings are valid and temporary
• Seeking help is a sign of strength, not weakness
• Small steps matter - even getting out of bed or having a meal is an achievement
• Depression is treatable and manageable

🛠️ COPING STRATEGIES:
• Maintain a daily routine, even if it's simple
• Stay connected with friends and family
• Get some sunlight and fresh air daily
• Practice self-compassion - be kind to yourself
• Consider our depression support groups

📞 PROFESSIONAL SUPPORT:
• Book a counseling session through our platform
• Our campus counselors specialize in depression support
• Consider reaching out to a mental health professional

What's been weighing on you lately? I'm here to help you work through this."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Relationship stress
        if any(keyword in user_message.lower() for keyword in ['relationship', 'friend', 'family', 'lonely', 'isolated']) and any(keyword in user_message.lower() for keyword in ['stressed', 'stress', 'worried', 'anxious']):
            response_text = """Relationship stress can be really challenging to navigate. It's completely normal to feel overwhelmed when dealing with interpersonal issues. Here are some strategies:

💙 RELATIONSHIP STRESS MANAGEMENT:
• Practice open and honest communication
• Set healthy boundaries to protect your well-being
• Remember that you can't control others' actions, only your responses
• Take time for yourself to process your feelings

🤝 COMMUNICATION STRATEGIES:
• Use "I" statements to express your feelings
• Listen actively and try to understand the other person's perspective
• Choose the right time and place for important conversations
• Consider our communication skills workshops

📞 RELATIONSHIP SUPPORT:
• Book a relationship counseling session through our platform
• Join our peer support groups to connect with others
• Access our relationship resources and guides
• Consider our social skills workshops

What specific relationship challenges are you facing? I'm here to help you work through them."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Sleep issues with worry
        if any(keyword in user_message.lower() for keyword in ['sleep', 'insomnia', 'tired', 'exhausted', 'nightmare']) or ('can\'t sleep' in user_message.lower() or 'cannot sleep' in user_message.lower()):
            response_text = """Sleep problems can really affect your mental health and daily functioning. Here are some tips for better sleep:

😴 SLEEP HYGIENE:
• Establish a consistent bedtime routine
• Avoid screens 1 hour before bed
• Keep your room cool, dark, and quiet
• Avoid caffeine and heavy meals before bedtime

🧘 RELAXATION TECHNIQUES:
• Deep breathing exercises before bed
• Gentle stretching or yoga
• Meditation or mindfulness practices
• Reading a book (not on a screen)

💙 SLEEP RESOURCES:
• Access our sleep wellness resources on the platform
• Book a counseling session to discuss sleep issues
• Join our sleep hygiene workshops
• Consider our relaxation and meditation groups

If sleep issues persist, it might be worth talking to a healthcare provider or booking a counseling session."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Stress support
        if any(keyword in user_message.lower() for keyword in ['stressed', 'stress', 'overwhelmed', 'pressure', 'burnout']):
            response_text = """Stress can feel like it's taking over everything in your life. It's important to remember that you don't have to handle everything at once. Here are some strategies:

📋 STRESS MANAGEMENT:
• Break tasks into smaller, manageable pieces
• Use the Pomodoro technique: 25 minutes work, 5 minutes break
• Practice time management and prioritization
• Learn to say no when you're overwhelmed

🧘 RELAXATION TECHNIQUES:
• Deep breathing exercises
• Progressive muscle relaxation
• Mindfulness meditation
• Gentle stretching or yoga

💙 SELF-CARE ESSENTIALS:
• Stay hydrated and eat regular meals
• Get adequate sleep (7-9 hours)
• Take regular breaks throughout the day
• Engage in activities you enjoy

📚 RESOURCES:
• Book a stress management counseling session
• Join our stress relief workshops
• Access our wellness library for more techniques

What's causing you the most stress right now? Let's work through it together."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Academic stress
        if any(keyword in user_message.lower() for keyword in ['exam', 'study', 'grades', 'academic', 'assignment']):
            response_text = """Academic pressure can be intense, especially when you're juggling multiple responsibilities. Remember that your worth isn't determined by your grades. Here are some strategies:

📚 STUDY TECHNIQUES:
• Use the Pomodoro technique for focused study sessions
• Create a realistic study schedule with breaks
• Practice active recall and spaced repetition
• Form study groups with classmates

🎯 ACADEMIC SUPPORT:
• Don't compare yourself to others - focus on your own progress
• Take advantage of our academic counseling services
• Use our study groups and peer support features
• Consider tutoring or academic workshops

💙 WELLNESS TIPS:
• Maintain a healthy study-life balance
• Take regular breaks and get enough sleep
• Stay organized with planners and to-do lists
• Practice stress-reduction techniques

📞 RESOURCES:
• Book an academic counseling session
• Join our study support groups
• Access our academic success resources

What specific academic challenges are you facing? I'm here to help you work through them."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Sleep issues
        if any(keyword in user_message.lower() for keyword in ['sleep', 'insomnia', 'tired', 'exhausted', 'nightmare']):
            response_text = """Sleep problems can really affect your mental health and daily functioning. Here are some tips for better sleep:

😴 SLEEP HYGIENE:
• Establish a consistent bedtime routine
• Avoid screens 1 hour before bed
• Keep your room cool, dark, and quiet
• Avoid caffeine and heavy meals before bedtime

🧘 RELAXATION TECHNIQUES:
• Deep breathing exercises before bed
• Gentle stretching or yoga
• Meditation or mindfulness practices
• Reading a book (not on a screen)

💙 SLEEP RESOURCES:
• Access our sleep wellness resources on the platform
• Book a counseling session to discuss sleep issues
• Join our sleep hygiene workshops
• Consider our relaxation and meditation groups

If sleep issues persist, it might be worth talking to a healthcare provider or booking a counseling session."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # Relationship issues
        if any(keyword in user_message.lower() for keyword in ['relationship', 'friend', 'family', 'lonely', 'isolated']):
            response_text = """Relationships can be complex and sometimes challenging. It's normal to feel lonely or have difficulties with friends and family. Remember that:

💙 HEALTHY RELATIONSHIPS:
• Involve communication, respect, and boundaries
• You deserve to be treated with kindness and understanding
• It's okay to set boundaries and prioritize your well-being
• Quality matters more than quantity in friendships

🤝 BUILDING CONNECTIONS:
• Join our peer support groups to connect with others
• Participate in campus activities and clubs
• Consider our social skills workshops
• Practice active listening and empathy

📞 RELATIONSHIP SUPPORT:
• Our relationship counselors can help you navigate challenges
• Book a counseling session to discuss relationship issues
• Join our communication skills workshops
• Access our relationship resources

What's going on in your relationships? I'm here to listen and support you."""
            
            return {
                "text": response_text,
                "safety_flags": [],
                "model": "intelligent-fallback",
                "timestamp": str(datetime.now())
            }
        
        # General support and encouragement
        response_text = """Thank you for sharing what's on your mind. It takes courage to reach out for support, and I'm proud of you for taking this step. I'm here to listen and help you work through whatever you're experiencing.

💙 REMEMBER:
• Your feelings are valid and important
• You're not alone in this journey
• It's okay to not be okay sometimes
• Small steps forward are still progress
• Our platform offers various resources to support you

🛠️ AVAILABLE RESOURCES:
• Book counseling sessions through our platform
• Join peer support groups
• Access our wellness library
• Participate in workshops and activities
• Connect with campus mental health services

What would you like to explore or discuss further? I'm here to help guide you through this."""
        
        return {
            "text": response_text,
            "safety_flags": [],
            "model": "intelligent-fallback",
            "timestamp": str(datetime.now())
        }
        
    except Exception as e:
        return {
            "text": "I'm here to listen and support you. Could you tell me more about what's on your mind?",
            "safety_flags": ["api_error"],
            "error": str(e)
        }
