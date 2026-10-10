-- Radar Dakal : présence et bannissements temporaires.
-- Migration appliquée sur le projet Supabase de production le 10 octobre 2026.
alter table public.radar_profiles add column if not exists banned_until timestamptz;
alter table public.radar_profiles add column if not exists last_seen_at timestamptz;
alter table public.radar_profiles add column if not exists online_since timestamptz;

-- Une suspension ou un ban expirant dans le futur bloque immédiatement les opérations des membres.
create or replace function public.radar_is_active()
returns boolean language sql stable security definer set search_path='' as $$
 select exists(select 1 from public.radar_profiles
 where id=(select auth.uid()) and active=true
 and (banned_until is null or banned_until<=now()))
$$;
revoke all on function public.radar_is_active() from public;
grant execute on function public.radar_is_active() to authenticated;

-- Aucun utilisateur ne choisit son propre ID ni n'écrit directement dans ces champs.
create or replace function public.radar_heartbeat()
returns void language plpgsql security definer set search_path='' as $$
begin
 if (select auth.uid()) is null then raise exception 'Authentication required'; end if;
 update public.radar_profiles
 set online_since=case when last_seen_at is null or last_seen_at<now()-interval '2 minutes'
 then now() else coalesce(online_since,now()) end,
 last_seen_at=now()
 where id=(select auth.uid()) and active=true and (banned_until is null or banned_until<=now());
end
$$;
revoke all on function public.radar_heartbeat() from public;
grant execute on function public.radar_heartbeat() to authenticated;
