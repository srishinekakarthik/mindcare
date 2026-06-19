# MindCare Mental Health Platform

A comprehensive Django-based web application designed to provide mental health support, resources, and community features for students and institutions.

## 🌟 Features

### Core Features
- **AI-Powered Chatbot**: Integrated with Google Gemini AI for empathetic mental health support
- **Mood Tracking**: Interactive mood tracking with reason analysis and history
- **Peer Support**: Community-driven support groups and live chat
- **Resource Library**: Curated mental health resources, articles, and tools
- **Self-Assessment**: Comprehensive mental health assessment tools
- **Session Booking**: Professional counselor appointment scheduling

### Admin Features
- **Analytics Dashboard**: Comprehensive analytics with interactive charts
- **User Management**: Role-based access control (Student/Admin)
- **Crisis Management**: Real-time crisis detection and response
- **Platform Usage Analytics**: Detailed usage statistics and trends

## 🎨 Design

- **Modern UI**: Clean, responsive design with warm yellow/gold theme
- **Glassmorphism Effects**: Beautiful translucent UI elements
- **Mobile-First**: Fully responsive across all devices
- **Accessibility**: WCAG compliant with proper ARIA labels

## 🛠️ Tech Stack

### Backend
- **Django 4.2+**: Python web framework
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)
- **Google Gemini AI**: AI chatbot integration
- **Supabase**: Optional cloud database and authentication

### Frontend
- **HTML5/CSS3**: Semantic markup with modern CSS
- **JavaScript (ES6+)**: Interactive features and API integration
- **Chart.js**: Data visualization for analytics
- **Responsive Design**: Mobile-first approach

### Development Tools
- **Git**: Version control
- **Python Virtual Environment**: Isolated dependencies
- **Django Management Commands**: Custom admin tools

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mindcare-platform.git
   cd mindcare-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser to `http://localhost:8000`
   - Login with demo credentials:
     - **Student**: `demo@test.com` / `demo123`
     - **Admin**: `admin@test.com` / `admin123`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini AI (Optional)
GEMINI_API_KEY=your-gemini-api-key

# Supabase (Optional)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### AI Integration Setup
1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file
3. Run the setup script: `python setup_gemini.py`

### Supabase Integration (Optional)
1. Create a Supabase project
2. Add credentials to `.env` file
3. Run database setup: `python supabase_setup.sql`

## 📱 Usage

### For Students
1. **Login** with student credentials
2. **Access Features**:
   - Chat with AI for mental health support
   - Track daily mood and emotions
   - Join peer support communities
   - Access mental health resources
   - Take self-assessment quizzes
   - Book counseling sessions

### For Administrators
1. **Login** with admin credentials
2. **Access Admin Features**:
   - View comprehensive analytics dashboard
   - Monitor platform usage
   - Manage user accounts
   - Generate reports
   - Crisis management tools

## 🧪 Testing

### Manual Testing
Follow the comprehensive testing guide in `MANUAL_TESTING_CHECKLIST.md`

### Automated Testing
```bash
# Run Django tests
python manage.py test

# Test AI integration
python test_gemini_integration.py

# Test API endpoints
python test_api_endpoint.py
```

## 📊 Analytics Dashboard

The admin analytics dashboard provides:
- **User Engagement**: Active users, session duration, feature usage
- **Mental Health Trends**: Mood patterns, assessment results
- **Crisis Management**: Crisis detection, response times
- **Platform Performance**: Load times, error rates, user satisfaction

## 🔒 Security Features

- **Role-based Access Control**: Student and Admin roles
- **CSRF Protection**: Django's built-in CSRF protection
- **Input Validation**: Comprehensive form validation
- **Crisis Detection**: AI-powered crisis keyword detection
- **Secure Authentication**: Django's authentication system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- `GEMINI_SETUP_GUIDE.md` - AI integration setup
- `SUPABASE_SETUP_GUIDE.md` - Database setup
- `TESTING_GUIDE.md` - Testing procedures
- `MANUAL_TESTING_CHECKLIST.md` - Manual testing checklist

### Troubleshooting
1. Check the Django logs for errors
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check database migrations are up to date

### Contact
For support or questions, please open an issue on GitHub.

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced AI features
- [ ] Multi-language support
- [ ] Integration with more counseling platforms
- [ ] Advanced analytics and reporting
- [ ] Real-time notifications
- [ ] Video counseling integration

## 🙏 Acknowledgments

- Google Gemini AI for mental health support
- Django community for the excellent framework
- Chart.js for beautiful data visualizations
- All contributors and testers

---

**Made with ❤️ for mental health awareness and support**
