-- Run this in the Supabase SQL editor (or via the Supabase CLI) against the project's Postgres database.

-- 1. Add a price field to each cycle. Cycles are paid programs, so price must be > 0.
ALTER TABLE public.cycles
  ADD COLUMN cycle_price numeric CHECK (cycle_price > 0::numeric);
UPDATE public.cycles SET cycle_price = 1 WHERE cycle_price IS NULL; -- placeholder, update via the admin UI
ALTER TABLE public.cycles ALTER COLUMN cycle_price SET NOT NULL;

-- 2. Enforce at the database level that only one cycle can be open for registration at a time.
--    (The app already closes other open cycles automatically; this is a safety net against races.)
CREATE UNIQUE INDEX cycles_single_open_for_registration
  ON public.cycles ((is_open_for_registration))
  WHERE is_open_for_registration;
