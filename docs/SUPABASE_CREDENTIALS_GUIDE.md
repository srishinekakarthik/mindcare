# 🔑 How to Find Your Supabase Credentials

## **Step-by-Step Visual Guide:**

### **1. Go to Supabase Dashboard**
- Visit: https://supabase.com
- Sign in to your account
- Select your project (or create new one)

### **2. Navigate to Settings**
```
Supabase Dashboard
├── Table Editor
├── SQL Editor
├── Authentication
├── Storage
├── Edge Functions
├── Settings ⚙️  ← Click here
    ├── General
    ├── API 🔑  ← Click here
    ├── Database
    ├── Auth
    └── Storage
```

### **3. API Settings Page**
You'll see a page like this:

```
┌─────────────────────────────────────────────────────────┐
│ API Settings                                            │
├─────────────────────────────────────────────────────────┤
│ Project URL:                                            │
│ https://abcdefghijklmnop.supabase.co                    │
│                                                         │
│ API Keys:                                               │
│                                                         │
│ anon public:                                            │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY5ODc2ODAwMCwiZXhwIjoyMDE0MzQ0MDAwfQ.example_signature_here │
│                                                         │
│ service_role:                                           │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjk4NzY4MDAwLCJleHAiOjIwMTQzNDQwMDB9.example_signature_here │
└─────────────────────────────────────────────────────────┘
```

### **4. Database Settings Page**
Go to Settings → Database:

```
┌─────────────────────────────────────────────────────────┐
│ Database Settings                                       │
├─────────────────────────────────────────────────────────┤
│ Connection parameters:                                  │
│                                                         │
│ Host: db.abcdefghijklmnop.supabase.co                  │
│ Database name: postgres                                 │
│ Port: 5432                                              │
│ User: postgres                                          │
│ Password: [YOUR-PASSWORD]                               │
│                                                         │
│ Connection string:                                      │
│ postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres │
└─────────────────────────────────────────────────────────┘
```

## **📝 What to Copy:**

### **From API Settings:**
1. **Project URL**: `https://abcdefghijklmnop.supabase.co`
2. **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### **From Database Settings:**
4. **Connection string**: `postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres`

## **🔧 Update Your .env File:**

```env
# Supabase Configuration
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Configuration
DATABASE_URL=postgresql://postgres:your_actual_password@db.abcdefghijklmnop.supabase.co:5432/postgres

# Django Configuration
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
```

## **🚨 Important Notes:**

1. **Keep your service_role key secret** - don't share it publicly
2. **Replace [YOUR-PASSWORD]** with your actual database password
3. **The anon key is safe** to use in frontend code
4. **Test your connection** after updating the .env file

## **✅ After Updating .env:**

1. **Install packages**:
   ```bash
   pip install dj-database-url psycopg2-binary
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Test mood tracking** - create a mood entry and check Supabase!

## **🆘 If You Can't Find These:**

- **Make sure you're in the right project**
- **Check you have admin access** to the project
- **Try refreshing the page**
- **Contact Supabase support** if still having issues

---

**Once you have these credentials, your mood data will be stored in Supabase and you'll see the `base_moodentry` table!** 🎉
