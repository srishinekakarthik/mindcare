# Supabase Integration Setup Guide

This guide will help you connect your Django application with Supabase for authentication and data management.

## Prerequisites

1. A Supabase account (sign up at [supabase.com](https://supabase.com))
2. Python 3.8+ installed
3. Django project set up

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `your-project-name`
   - Database Password: (choose a strong password)
   - Region: (choose closest to your users)
5. Click "Create new project"

## Step 2: Get Your Supabase Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://your-project-id.supabase.co`)
   - **anon public** key
   - **service_role** key (keep this secret!)

## Step 3: Configure Environment Variables

Create a `.env` file in your project root with the following content:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Django Configuration
SECRET_KEY=your_django_secret_key
DEBUG=True
```

**Important:** Replace the placeholder values with your actual Supabase credentials.

## Step 4: Update Frontend Configuration

In your HTML templates (`templates/login.html` and `templates/signup.html`), update the Supabase configuration:

```javascript
// Replace these with your actual values
const SUPABASE_URL = 'https://your-project-id.supabase.co';
const SUPABASE_ANON_KEY = 'your_anon_key_here';
```

## Step 5: Set Up Supabase Database Tables

You can either use the Django models (recommended) or create tables directly in Supabase:

### Option A: Using Django Models (Recommended)
The Django models will automatically create the necessary tables when you run migrations.

### Option B: Manual Table Creation in Supabase
If you prefer to create tables manually in Supabase:

1. Go to **Table Editor** in your Supabase dashboard
2. Create the following tables:

```sql
-- Institutions table
CREATE TABLE base_institution (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles table
CREATE TABLE base_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_users(id) ON DELETE CASCADE,
    institution_id INTEGER REFERENCES base_institution(id) ON DELETE CASCADE,
    role VARCHAR(10) CHECK (role IN ('student', 'admin')),
    supabase_user_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Step 6: Configure Supabase Authentication

1. In your Supabase dashboard, go to **Authentication** → **Settings**
2. Configure the following:
   - **Site URL**: `http://localhost:8000` (for development)
   - **Redirect URLs**: Add your application URLs
   - **Email Templates**: Customize as needed

## Step 7: Run the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. Visit `http://localhost:8000/admin-student-portal/` to test the application

## Step 8: Test the Integration

1. **Test Signup Flow:**
   - Go to the admin-student portal
   - Enter an institution name
   - Select a role (Student/Admin)
   - Fill out the signup form
   - Check your email for verification

2. **Test Login Flow:**
   - Use the credentials from signup
   - Verify successful login and dashboard redirect

3. **Test Logout:**
   - Click logout button
   - Verify session is cleared

## API Endpoints

The following API endpoints are available:

- `POST /api/signup/` - User registration
- `POST /api/login/` - User authentication
- `POST /api/logout/` - User logout

### Signup API Example:
```javascript
fetch('/api/signup/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        username: 'john_doe',
        email: 'john@example.com',
        password: 'secure_password',
        institution: 'University of Example',
        role: 'student'
    })
});
```

### Login API Example:
```javascript
fetch('/api/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        email: 'john@example.com',
        password: 'secure_password'
    })
});
```

## Troubleshooting

### Common Issues:

1. **"Invalid API key" error:**
   - Verify your Supabase URL and keys are correct
   - Check that the keys are properly set in environment variables

2. **CORS errors:**
   - Add your domain to Supabase CORS settings
   - Check that your site URL is configured correctly

3. **Database connection issues:**
   - Verify your Supabase project is active
   - Check that the database tables exist

4. **Authentication not working:**
   - Ensure email verification is configured properly
   - Check Supabase authentication settings

### Debug Mode:
Set `DEBUG=True` in your `.env` file to see detailed error messages.

## Security Considerations

1. **Never commit your `.env` file** to version control
2. **Use environment variables** for all sensitive data
3. **Enable Row Level Security (RLS)** in Supabase for production
4. **Use HTTPS** in production
5. **Regularly rotate your API keys**

## Next Steps

1. **Add more features:**
   - Password reset functionality
   - Email verification
   - User profile management
   - Role-based permissions

2. **Enhance security:**
   - Implement rate limiting
   - Add input validation
   - Set up monitoring

3. **Deploy to production:**
   - Configure production environment variables
   - Set up proper CORS settings
   - Enable SSL/TLS

## Support

For additional help:
- [Supabase Documentation](https://supabase.com/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [Supabase Community](https://github.com/supabase/supabase/discussions)
