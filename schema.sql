-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.pools (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  capacity integer NOT NULL CHECK (capacity > 0),
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT pools_pkey PRIMARY KEY (id)
);
CREATE TABLE public.pricing_rules (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  pool_id bigint NOT NULL,
  day_type USER-DEFINED NOT NULL,
  price numeric NOT NULL CHECK (price >= 0::numeric),
  currency text NOT NULL DEFAULT 'USD'::text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT pricing_rules_pkey PRIMARY KEY (id),
  CONSTRAINT pricing_rules_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES public.pools(id)
);
CREATE TABLE public.cycles (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  cycle_price numeric NOT NULL CHECK (cycle_price > 0::numeric),
  is_open_for_registration boolean NOT NULL DEFAULT false,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT cycles_pkey PRIMARY KEY (id)
);
-- Only one cycle may be open for registration at a time.
CREATE UNIQUE INDEX cycles_single_open_for_registration
  ON public.cycles ((is_open_for_registration))
  WHERE is_open_for_registration;
CREATE TABLE public.participants (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  full_name text NOT NULL,
  mother_name text NOT NULL,
  phone text NOT NULL,
  date_of_birth date NOT NULL,
  notes text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT participants_pkey PRIMARY KEY (id)
);
CREATE TABLE public.enrollments (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  participant_id bigint NOT NULL,
  cycle_id bigint NOT NULL,
  level USER-DEFINED NOT NULL,
  time_preferred USER-DEFINED NOT NULL,
  price numeric NOT NULL CHECK (price >= 0::numeric),
  status USER-DEFINED NOT NULL DEFAULT 'confirmed'::enrollment_status, -- enrollment_status enum: 'pending', 'confirmed'
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT enrollments_pkey PRIMARY KEY (id),
  CONSTRAINT enrollments_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.participants(id),
  CONSTRAINT enrollments_cycle_id_fkey FOREIGN KEY (cycle_id) REFERENCES public.cycles(id)
);
CREATE TABLE public.reservations (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  pool_id bigint NOT NULL,
  customer_name text NOT NULL,
  customer_phone text NOT NULL,
  starts_at timestamp with time zone NOT NULL,
  ends_at timestamp with time zone NOT NULL,
  price_snapshot numeric NOT NULL CHECK (price_snapshot >= 0::numeric),
  status USER-DEFINED NOT NULL DEFAULT 'pending'::reservation_status,
  notes text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT reservations_pkey PRIMARY KEY (id),
  CONSTRAINT reservations_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES public.pools(id)
);
CREATE TABLE public.payments (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  payable_type USER-DEFINED NOT NULL,
  payable_id bigint NOT NULL,
  amount numeric NOT NULL CHECK (amount > 0::numeric),
  currency text NOT NULL DEFAULT 'USD'::text,
  method USER-DEFINED NOT NULL,
  paid_at timestamp with time zone NOT NULL DEFAULT now(),
  recorded_by text,
  notes text,
  CONSTRAINT payments_pkey PRIMARY KEY (id)
);