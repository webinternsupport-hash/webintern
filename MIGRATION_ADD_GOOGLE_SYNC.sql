ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS google_account_id text;

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS auth_provider text DEFAULT 'email';

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS sync_enabled boolean DEFAULT true;

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_sync_time timestamp with time zone;

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS department text;

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS degree text;

ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS college_name text;

CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_google_account_id ON public.profiles(google_account_id) WHERE google_account_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_auth_provider ON public.profiles(auth_provider);

UPDATE public.profiles SET auth_provider = 'email' WHERE auth_provider IS NULL;
