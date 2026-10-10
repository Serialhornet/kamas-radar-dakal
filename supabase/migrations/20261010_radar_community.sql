-- Radar Dakal • Base communautaire, version 1.
-- Exécuter dans Supabase SQL Editor AVANT d'activer le mode multi-profils.
create extension if not exists pgcrypto;

create table if not exists public.radar_profiles(
 id uuid primary key references auth.users(id) on delete cascade,
 pseudo text not null unique check (char_length(pseudo) between 2 and 30),
 role text not null default 'player' check (role in ('admin','player')),
 active boolean not null default true,
 created_at timestamptz not null default now()
);

create table if not exists public.radar_personal_state(
 user_id uuid not null references auth.users(id) on delete cascade,
 tool text not null check (tool in ('kamas','craft','recolte','farm','quete','brisage','elevage')),
 state jsonb not null default '{}'::jsonb,
 updated_at timestamptz not null default now(),
 primary key (user_id,tool)
);

create table if not exists public.radar_shared_prices(
 item_id bigint primary key,
 server text not null default 'Dakal' check (server='Dakal'),
 unit_price bigint not null check (unit_price >= 0),
 updated_by uuid references auth.users(id) on delete set null,
 updated_at timestamptz not null default now()
);

create table if not exists public.radar_votes(
 trick_id text not null check (char_length(trick_id) between 1 and 250),
 user_id uuid not null references auth.users(id) on delete cascade,
 value smallint not null check (value in (-1,1)),
 updated_at timestamptz not null default now(),
 primary key (trick_id,user_id)
);

create table if not exists public.radar_comments(
 id uuid primary key default gen_random_uuid(),
 trick_id text not null check (char_length(trick_id) between 1 and 250),
 user_id uuid not null references auth.users(id) on delete cascade,
 body text not null check (char_length(btrim(body)) between 1 and 1200),
 created_at timestamptz not null default now()
);
create index if not exists radar_comments_trick_idx on public.radar_comments(trick_id,created_at);
create index if not exists radar_votes_trick_idx on public.radar_votes(trick_id);

-- SECURITY DEFINER reads only a tiny subset and never uses client-supplied user ids.
create or replace function public.radar_is_active()
returns boolean language sql stable security definer set search_path='' as $$
 select exists(select 1 from public.radar_profiles where id=(select auth.uid()) and active=true)
$$;
create or replace function public.radar_is_admin()
returns boolean language sql stable security definer set search_path='' as $$
 select exists(select 1 from public.radar_profiles where id=(select auth.uid()) and active=true and role='admin')
$$;
revoke all on function public.radar_is_active() from public;
revoke all on function public.radar_is_admin() from public;
grant execute on function public.radar_is_active() to authenticated;
grant execute on function public.radar_is_admin() to authenticated;

alter table public.radar_profiles enable row level security;
alter table public.radar_personal_state enable row level security;
alter table public.radar_shared_prices enable row level security;
alter table public.radar_votes enable row level security;
alter table public.radar_comments enable row level security;

-- Pseudos publics entre membres actifs pour afficher les auteurs des commentaires.
-- Aucune adresse e-mail ni clé secrète n'est enregistrée dans radar_profiles.
create policy "profiles active members read" on public.radar_profiles for select to authenticated
 using (public.radar_is_active());
-- Profile writes are ADMIN edge function only, using server-side service role.

create policy "personal read" on public.radar_personal_state for select to authenticated
 using (public.radar_is_active() and user_id=(select auth.uid()));
create policy "personal insert" on public.radar_personal_state for insert to authenticated
 with check (public.radar_is_active() and user_id=(select auth.uid()));
create policy "personal update" on public.radar_personal_state for update to authenticated
 using (public.radar_is_active() and user_id=(select auth.uid()))
 with check (public.radar_is_active() and user_id=(select auth.uid()));
create policy "personal delete" on public.radar_personal_state for delete to authenticated
 using (public.radar_is_active() and user_id=(select auth.uid()));

create policy "shared prices read" on public.radar_shared_prices for select to authenticated
 using (public.radar_is_active());
create policy "shared prices insert" on public.radar_shared_prices for insert to authenticated
 with check (public.radar_is_active() and updated_by=(select auth.uid()));
create policy "shared prices update" on public.radar_shared_prices for update to authenticated
 using (public.radar_is_active())
 with check (public.radar_is_active() and updated_by=(select auth.uid()));

create policy "votes read" on public.radar_votes for select to authenticated using (public.radar_is_active());
create policy "votes insert" on public.radar_votes for insert to authenticated
 with check (public.radar_is_active() and user_id=(select auth.uid()));
create policy "votes update" on public.radar_votes for update to authenticated
 using (public.radar_is_active() and user_id=(select auth.uid()))
 with check (public.radar_is_active() and user_id=(select auth.uid()));
create policy "votes delete" on public.radar_votes for delete to authenticated
 using (public.radar_is_active() and user_id=(select auth.uid()));

create policy "comments read" on public.radar_comments for select to authenticated using (public.radar_is_active());
create policy "comments insert" on public.radar_comments for insert to authenticated
 with check (public.radar_is_active() and user_id=(select auth.uid()));
create policy "comments delete own/admin" on public.radar_comments for delete to authenticated
 using (public.radar_is_active() and (user_id=(select auth.uid()) or public.radar_is_admin()));

-- Empêche une modification de profil/rôle par le navigateur : aucun policy insert/update sur profiles.
-- IMPORTANT : NE PAS exposer SUPABASE_SERVICE_ROLE_KEY ou sb_secret_... sur GitHub Pages.
-- Initialisation manuelle après avoir créé l'utilisateur admin dans Authentication > Users :
-- insert into public.radar_profiles(id,pseudo,role) values ('UUID_ADMIN_SUPABASE','Serialhornet','admin');
