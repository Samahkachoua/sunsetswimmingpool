-- Run this in the Supabase SQL editor (or via the Supabase CLI) against the project's Postgres database.
-- Removes 'completed' from enrollment_status, keeping only 'pending' and 'confirmed'.
-- Postgres can't drop a single enum value directly, so this rebuilds the type.

-- Safety check: this will fail loudly if any row still uses 'completed'.
-- If it does, decide what those rows should become (e.g. 'confirmed') and update them first:
--   UPDATE public.enrollments SET status = 'confirmed' WHERE status = 'completed';

ALTER TABLE public.enrollments ALTER COLUMN status DROP DEFAULT;

CREATE TYPE enrollment_status_new AS ENUM ('pending', 'confirmed');

ALTER TABLE public.enrollments
  ALTER COLUMN status TYPE enrollment_status_new
  USING status::text::enrollment_status_new;

DROP TYPE enrollment_status;
ALTER TYPE enrollment_status_new RENAME TO enrollment_status;

ALTER TABLE public.enrollments ALTER COLUMN status SET DEFAULT 'confirmed'::enrollment_status;
