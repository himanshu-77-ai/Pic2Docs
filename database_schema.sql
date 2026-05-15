-- ─────────────────────────────────────────────
-- Pic2Docs — Supabase Database Schema
-- Run this in Supabase SQL Editor
-- ─────────────────────────────────────────────

-- 1. Users profile table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id              UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT,
    avatar_url      TEXT,
    plan            TEXT DEFAULT 'free' CHECK (plan IN ('free', 'basic', 'pro')),
    images_used     INTEGER DEFAULT 0,
    images_limit    INTEGER DEFAULT 10,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. OCR Usage history
CREATE TABLE IF NOT EXISTS public.ocr_history (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    filename        TEXT,
    language        TEXT,
    word_count      INTEGER DEFAULT 0,
    confidence      FLOAT DEFAULT 0.0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    plan                TEXT CHECK (plan IN ('basic', 'pro')),
    status              TEXT CHECK (status IN ('active', 'cancelled', 'expired')),
    payment_gateway     TEXT CHECK (payment_gateway IN ('stripe', 'razorpay')),
    gateway_sub_id      TEXT UNIQUE,
    amount              DECIMAL(10,2),
    currency            TEXT DEFAULT 'USD',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end   TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Payments table
CREATE TABLE IF NOT EXISTS public.payments (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.subscriptions(id),
    amount          DECIMAL(10,2),
    currency        TEXT DEFAULT 'USD',
    status          TEXT CHECK (status IN ('success', 'failed', 'pending', 'refunded')),
    gateway         TEXT CHECK (gateway IN ('stripe', 'razorpay')),
    gateway_pay_id  TEXT UNIQUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- Row Level Security (RLS) — Users only see their own data
-- ─────────────────────────────────────────────

ALTER TABLE public.profiles      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ocr_history   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments      ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- OCR History policies
CREATE POLICY "Users can view own history"
    ON public.ocr_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own history"
    ON public.ocr_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Subscriptions policies
CREATE POLICY "Users can view own subscriptions"
    ON public.subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Payments policies
CREATE POLICY "Users can view own payments"
    ON public.payments FOR SELECT
    USING (auth.uid() = user_id);

-- ─────────────────────────────────────────────
-- Auto-create profile when user signs up
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ─────────────────────────────────────────────
-- Auto-reset usage every month
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION public.reset_monthly_usage()
RETURNS VOID AS $$
BEGIN
    UPDATE public.profiles
    SET images_used = 0,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ─────────────────────────────────────────────
-- Update plan limits when subscription changes
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION public.update_plan_limits()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.plan = 'basic' AND NEW.status = 'active' THEN
        UPDATE public.profiles
        SET plan = 'basic', images_limit = 100
        WHERE id = NEW.user_id;
    ELSIF NEW.plan = 'pro' AND NEW.status = 'active' THEN
        UPDATE public.profiles
        SET plan = 'pro', images_limit = 999999
        WHERE id = NEW.user_id;
    ELSIF NEW.status IN ('cancelled', 'expired') THEN
        UPDATE public.profiles
        SET plan = 'free', images_limit = 10
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_subscription_change
    AFTER INSERT OR UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_plan_limits();
