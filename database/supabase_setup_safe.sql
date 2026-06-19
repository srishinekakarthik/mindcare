-- Supabase Database Setup Script (Safe Version)
-- Run this in your Supabase SQL Editor

-- Create institutions table
CREATE TABLE IF NOT EXISTS public.institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    institution_id INTEGER REFERENCES public.institutions(id) ON DELETE CASCADE,
    role VARCHAR(10) CHECK (role IN ('student', 'admin')),
    supabase_user_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on custom tables
ALTER TABLE public.institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist, then recreate them
DROP POLICY IF EXISTS "Institutions are viewable by everyone" ON public.institutions;
DROP POLICY IF EXISTS "Institutions are insertable by authenticated users" ON public.institutions;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.user_profiles;

-- Create policies for institutions table
CREATE POLICY "Institutions are viewable by everyone" ON public.institutions
    FOR SELECT USING (true);

CREATE POLICY "Institutions are insertable by authenticated users" ON public.institutions
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for user_profiles table
CREATE POLICY "Users can view their own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT ON public.institutions TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.user_profiles TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
