-- Additive Newsletter MVP schema. Run once against the existing PharmaLens Postgres database.
create table if not exists newsletter_preferences (
 id bigserial primary key, workspace_id bigint not null references workspaces(id) on delete cascade, user_id bigint not null references users(id) on delete cascade,
 markets_json text not null default '[]', companies_json text not null default '[]', therapeutic_areas_json text not null default '[]', topics_json text not null default '[]',
 sections_json text not null default '["daily_signals","company_performance","financial_intelligence"]', frequency varchar(20) not null default 'daily', timezone varchar(80) not null default 'UTC',
 created_at timestamptz not null default now(), updated_at timestamptz not null default now(), unique(workspace_id,user_id));
create index if not exists ix_newsletter_preferences_workspace on newsletter_preferences(workspace_id);
create table if not exists newsletter_source_items (
 id bigserial primary key, workspace_id bigint not null references workspaces(id) on delete cascade, created_by_id bigint not null references users(id) on delete cascade,
 title varchar(500) not null, summary text, source_name varchar(255) not null, source_url varchar(1200), market varchar(120), company varchar(255), therapeutic_area varchar(255), topic varchar(255),
 published_at timestamptz, retrieved_at timestamptz not null default now());
create index if not exists ix_newsletter_source_items_workspace_published on newsletter_source_items(workspace_id,published_at desc);

-- Newsletter intelligence feeding / verification extension.
create table if not exists newsletter_sources (
 id bigserial primary key,
 workspace_id bigint not null references workspaces(id) on delete cascade,
 name varchar(255) not null,
 base_url varchar(1200), source_type varchar(40) not null default 'news', region varchar(120), language varchar(40),
 role varchar(30) not null default 'discovery', verification_priority varchar(20) not null default 'medium', active boolean not null default true,
 created_at timestamptz not null default now(), unique(workspace_id,name));
create index if not exists ix_newsletter_sources_workspace on newsletter_sources(workspace_id);
alter table newsletter_source_items add column if not exists canonical_url varchar(1200);
alter table newsletter_source_items add column if not exists content_hash varchar(64);
alter table newsletter_source_items add column if not exists verification_status varchar(30) not null default 'unverified';
alter table newsletter_source_items add column if not exists evidence_level varchar(10) not null default 'E0';
alter table newsletter_source_items add column if not exists verified_at timestamptz;
alter table newsletter_source_items add column if not exists verified_by_id bigint references users(id) on delete set null;
create index if not exists ix_newsletter_source_items_hash on newsletter_source_items(workspace_id,content_hash);


-- Newsletter delivery operations / suppression.
alter table newsletter_preferences add column if not exists email_enabled boolean not null default false;
alter table newsletter_preferences add column if not exists delivery_hour integer not null default 8;
alter table newsletter_preferences add column if not exists suppressed_at timestamptz;
create unique index if not exists uq_newsletter_preference_workspace_user on newsletter_preferences(workspace_id,user_id);
create table if not exists newsletter_deliveries (
 id bigserial primary key, workspace_id bigint not null references workspaces(id) on delete cascade, user_id bigint not null references users(id) on delete cascade,
 recipient_email varchar(320) not null, subject varchar(500) not null, provider varchar(40) not null default 'resend', provider_message_id varchar(255),
 status varchar(30) not null default 'queued', error text, scheduled_for timestamptz, sent_at timestamptz, created_at timestamptz not null default now());
create index if not exists ix_newsletter_deliveries_user_workspace on newsletter_deliveries(user_id,workspace_id,created_at desc);
