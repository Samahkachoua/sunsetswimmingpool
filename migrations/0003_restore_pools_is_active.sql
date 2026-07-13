-- Run this in the Supabase SQL editor (or via the Supabase CLI) against the project's Postgres database.
-- The live `pools` table is missing `is_active`, which the app (Settings page, pool
-- activate/deactivate toggle) and schema.sql both expect. Restores it with existing
-- rows defaulting to active.

ALTER TABLE public.pools
  ADD COLUMN is_active boolean NOT NULL DEFAULT true;
