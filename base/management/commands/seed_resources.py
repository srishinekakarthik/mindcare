from django.core.management.base import BaseCommand
from base.models import Resource


SEED_RESOURCES = [
    {
        'title': 'Understanding Anxiety: What It Is and How to Manage It',
        'category': 'article',
        'description': 'A comprehensive guide to understanding the roots of anxiety and evidence-based strategies to manage it effectively.',
        'body': (
            "Anxiety is one of the most common mental health conditions. It's characterized by persistent "
            "feelings of worry, fear, or unease that are difficult to control.\n\n"
            "Common symptoms include a racing heart, difficulty concentrating, muscle tension, sleep "
            "disturbances, and excessive worry.\n\n"
            "Practical strategies: diaphragmatic breathing (in for 4, hold for 4, out for 6), progressive "
            "muscle relaxation, and cognitive reframing to challenge anxious thoughts with evidence-based "
            "alternatives."
        ),
    },
    {
        'title': 'Time Blocking for Academic Stress Reduction',
        'category': 'article',
        'description': 'Learn how strategic time management using time-blocking can dramatically reduce academic pressure.',
        'body': (
            "Time blocking is the practice of dividing your day into blocks of time, each dedicated to a "
            "specific task or group of tasks.\n\n"
            "How to time block: list all your tasks for the week, estimate time needed for each, assign them "
            "to specific time slots in your calendar, include buffer time and breaks, and protect these "
            "blocks like appointments."
        ),
    },
    {
        'title': 'Behavioral Activation: Breaking the Cycle of Low Mood',
        'category': 'article',
        'description': 'Discover how behavioral activation, a core CBT technique, can help you gradually rebuild motivation and joy.',
        'body': (
            "Behavioral activation is based on the premise that depression leads to withdrawal, which leads "
            "to more depression - a vicious cycle.\n\n"
            "The treatment involves gradually reintroducing activities that bring pleasure or a sense of "
            "accomplishment, even when you don't feel like doing them. Start small: choose one activity per "
            "day that you used to enjoy, do it anyway, and track your mood before and after."
        ),
    },
    {
        'title': 'Sleep Hygiene for College Students: A Practical Guide',
        'category': 'worksheet',
        'description': 'Evidence-based techniques to improve your sleep quality and duration, tailored for the college lifestyle.',
        'body': (
            "Poor sleep significantly impacts academic performance, mood, and physical health.\n\n"
            "Keep a consistent wake time every day, even weekends. Avoid screens for 30-60 minutes before "
            "bed. Keep your room cool (65-68F / 18-20C). Limit caffeine after 2pm. Build a wind-down routine "
            "with light reading, stretching, or journaling."
        ),
    },
    {
        'title': 'Setting Healthy Boundaries in Friendships and Relationships',
        'category': 'article',
        'description': "A guide to understanding what healthy boundaries look like and how to communicate them effectively.",
        'body': (
            "Boundaries are the limits we set on how we allow others to treat us and what we're willing to "
            "do. They are essential for healthy relationships.\n\n"
            "Types of boundaries: physical (personal space and touch preferences), emotional (how much you "
            "share and what emotional labor you take on), and time (how you protect your time and energy).\n\n"
            "Use 'I' statements to set them: 'I feel overwhelmed when...' and be specific about what you need."
        ),
    },
    {
        'title': 'Progressive Muscle Relaxation: A Step-by-Step Guide',
        'category': 'exercise',
        'description': 'A proven relaxation technique that reduces physical tension and calms the nervous system.',
        'body': (
            "Progressive muscle relaxation (PMR) involves tensing and then releasing muscle groups in "
            "sequence. It helps you recognize and reduce physical tension.\n\n"
            "Find a comfortable, quiet position. Starting with your feet, tense the muscles tightly for 5 "
            "seconds, then release and notice the relaxation for 15-20 seconds. Move up through your body: "
            "feet, calves, thighs, abdomen, hands, arms, shoulders, face. Complete the cycle once daily."
        ),
    },
    {
        'title': 'The STOP Technique for Mindful Stress Management',
        'category': 'exercise',
        'description': 'A quick, four-step mindfulness technique you can use anywhere to interrupt the stress response.',
        'body': (
            "S - Stop what you're doing.\n"
            "T - Take a breath (one long, slow, deep breath).\n"
            "O - Observe your thoughts, feelings, and sensations without judgment.\n"
            "P - Proceed with awareness.\n\n"
            "This can be done in under a minute and is especially effective during high-stress moments like "
            "before an exam or a difficult conversation."
        ),
    },
    {
        'title': 'When to Seek Professional Help: A Practical Guide',
        'category': 'article',
        'description': "Understanding the signs that indicate it's time to reach out to a mental health professional.",
        'body': (
            "Seeking help is a sign of strength, not weakness. Consider reaching out to a mental health "
            "professional if symptoms persist for more than 2 weeks, your functioning is significantly "
            "impaired, you're having thoughts of self-harm, your quality of life is significantly reduced, "
            "or self-help strategies aren't working.\n\n"
            "MindCare's Book Session feature can connect you with an approved counselor."
        ),
    },
    {
        'title': 'Navigating Loneliness in University Life',
        'category': 'article',
        'description': 'Practical strategies for building meaningful connections on campus even when you feel isolated.',
        'body': (
            "Feeling lonely at university is extremely common. You are not alone in feeling alone.\n\n"
            "Practical steps: join one club or society related to a genuine interest, use MindCare's Peer "
            "Support community, talk to classmates (even small talk builds familiarity over time), and "
            "consider volunteering, which builds purpose and connection simultaneously."
        ),
    },
    {
        'title': 'National Suicide & Crisis Lifeline',
        'category': 'hotline',
        'description': 'Free, confidential support available 24/7 for people in distress.',
        'body': 'Call or text 988 (US) any time, day or night, for free and confidential crisis support.',
    },
]


class Command(BaseCommand):
    help = 'Seed initial published resources for the Resources page.'

    def handle(self, *args, **options):
        created = 0
        for item in SEED_RESOURCES:
            _, was_created = Resource.objects.get_or_create(
                title=item['title'],
                defaults={
                    'category': item['category'],
                    'description': item['description'],
                    'body': item['body'],
                    'is_published': True,
                }
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} new resource(s).'))
