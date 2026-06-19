# 🎯 How to View Mood Table in Supabase

## **Current Situation:**
Your mood data is currently stored in a **local SQLite database** (`db.sqlite3`), not in Supabase. That's why you don't see the `base_moodentry` table in Supabase.

## **🔧 Step-by-Step Setup:**

### **Step 1: Get Your Supabase Credentials**

1. **Go to [supabase.com](https://supabase.com)** and sign in
2. **Create a new project** (if you don't have one):
   - Click "New Project"
   - Choose your organization
   - Enter project name: `mindcare-platform`
   - Choose a strong database password
   - Select region closest to you
   - Click "Create new project"

3. **Get your credentials**:
   - Go to **Settings** → **API**
   - Copy these values:
     - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
     - **anon public** key
     - **service_role** key

### **Step 2: Configure Your .env File**

1. **Edit the `.env` file** that was just created:
   ```env
   # Replace with your actual Supabase credentials
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
   
   # Add your Supabase database URL
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

2. **Get your database URL**:
   - In Supabase dashboard, go to **Settings** → **Database**
   - Copy the **Connection string** under "Connection parameters"
   - Replace `[YOUR-PASSWORD]` with your database password

### **Step 3: Install Required Packages**

```bash
pip install dj-database-url psycopg2-binary
```

### **Step 4: Run Migrations to Supabase**

```bash
python manage.py migrate
```

This will create all your tables in Supabase, including:
- `base_moodentry` (your mood tracking table)
- `base_userprofile`
- `base_institution`
- Django's built-in tables

### **Step 5: Transfer Existing Data (Optional)**

If you want to keep your existing mood data:

```bash
# Export from SQLite
python manage.py dumpdata base.MoodEntry > mood_data.json

# After switching to Supabase, import the data
python manage.py loaddata mood_data.json
```

## **🎉 After Setup - Viewing Your Mood Table:**

### **Method 1: Supabase Dashboard**
1. Go to your Supabase project dashboard
2. Click **"Table Editor"** in the sidebar
3. You'll see `base_moodentry` table
4. Click on it to view all mood entries

### **Method 2: SQL Editor**
1. Go to **"SQL Editor"** in Supabase
2. Run this query:
   ```sql
   SELECT * FROM base_moodentry ORDER BY created_at DESC;
   ```

### **Method 3: Your Website's Database Viewer**
1. Login with `admin@test.com` / `admin123`
2. Go to **Analytics** → **Database Viewer**
3. Scroll to **"😊 Mood Entries"** section

## **🔍 What You'll See in Supabase:**

The `base_moodentry` table will have these columns:
- `id` - Primary key
- `user_id` - Foreign key to auth.users
- `mood_value` - 1-7 scale
- `mood_label` - Text description
- `reason` - Why they feel this way
- `notes` - Additional notes
- `created_at` - Timestamp
- `updated_at` - Last modified

## **🚀 Quick Test:**

After setup, create a test mood entry:
1. Go to your website
2. Login and go to Mood Tracker
3. Log a mood
4. Check Supabase Table Editor - you should see the new entry!

## **📊 Benefits of Using Supabase:**

- **Real-time data** - See mood entries instantly
- **Scalable** - Handles thousands of users
- **Backup** - Automatic backups
- **Analytics** - Built-in charts and insights
- **API** - Direct database access
- **Security** - Row-level security

## **🆘 Troubleshooting:**

**If you don't see the table:**
1. Check your `.env` file has correct credentials
2. Run `python manage.py migrate` again
3. Check Supabase project is active
4. Verify database URL is correct

**If migrations fail:**
1. Check your database password
2. Ensure Supabase project is not paused
3. Try creating a new Supabase project

---

**Once set up, your mood data will be permanently stored in Supabase and you'll be able to see the `base_moodentry` table in the Table Editor!** 🎉
