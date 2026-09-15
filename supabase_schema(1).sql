-- PharmaLens AI — Supabase Postgres schema
-- Run this once in Supabase Dashboard > SQL Editor (or `psql "$DATABASE_URL" -f supabase_schema.sql`)
-- Alternative: the FastAPI backend can also create these tables automatically on
-- startup via SQLAlchemy metadata.create_all() — see app/database.py.

create type user_role as enum ('user', 'admin');
create type member_role as enum ('owner', 'editor', 'viewer', 'admin', 'manager', 'analyst', 'sales_user');
create type file_status as enum ('uploaded', 'processing', 'ready', 'failed');
create type report_status as enum ('queued', 'processing', 'ready', 'failed');
create type run_status as enum ('success', 'partial', 'error');
create type message_role as enum ('user', 'assistant');
create type notification_type as enum ('report_ready', 'workspace_invite', 'access_alert');
-- member_role also gained admin/manager/analyst/sales_user in Phase 1.5 — see the
-- create type member_role statement below (owner/editor/viewer kept for compatibility).
create type dataset_status as enum ('uploaded', 'validating', 'mapping', 'processing', 'ready', 'failed', 'archived');

-- Local profile row synced 1:1 with the Supabase Auth user (auth.users.id).
create table users (
  id serial primary key,
  supabase_uid varchar(64) unique not null,
  name text,
  email varchar(320),
  login_method varchar(64),
  role user_role not null default 'user',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_signed_in timestamptz not null default now()
);

-- "Organizations" in the architecture doc.
create table workspaces (
  id serial primary key,
  owner_id integer not null references users(id) on delete cascade,
  name varchar(160) not null,
  organization varchar(200),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table workspace_members (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  user_id integer not null references users(id) on delete cascade,
  role member_role not null default 'viewer',
  created_at timestamptz not null default now()
);

create table uploaded_files (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  uploaded_by_id integer not null references users(id) on delete cascade,
  file_name varchar(255) not null,
  storage_key varchar(512) not null,
  mime_type varchar(120),
  status file_status not null default 'uploaded',
  created_at timestamptz not null default now()
);

create table saved_filters (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  user_id integer not null references users(id) on delete cascade,
  name varchar(160) not null,
  definition text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table copilot_messages (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  user_id integer not null references users(id) on delete cascade,
  role message_role not null,
  content text not null,
  created_at timestamptz not null default now()
);

create table generated_reports (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  created_by_id integer not null references users(id) on delete cascade,
  report_type varchar(80) not null,
  title varchar(255) not null,
  storage_key varchar(512),
  status report_status not null default 'queued',
  created_at timestamptz not null default now()
);

create table product_runs (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  user_id integer not null references users(id) on delete cascade,
  product_id varchar(40) not null,
  status run_status not null default 'success',
  input_definition text not null,
  output_definition text not null,
  created_at timestamptz not null default now()
);

create table user_notifications (
  id serial primary key,
  user_id integer not null references users(id) on delete cascade,
  type notification_type not null,
  title varchar(255) not null,
  content text not null,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

-- ==== Dataset Registry (Phase 1.5) ====

create table datasets (
  id serial primary key,
  workspace_id integer not null references workspaces(id) on delete cascade,
  owner_id integer not null references users(id) on delete cascade,
  name varchar(200) not null,
  source_type varchar(60) not null default 'user_upload',
  dataset_type varchar(60),
  status dataset_status not null default 'uploaded',
  latest_version_id integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table dataset_versions (
  id serial primary key,
  dataset_id integer not null references datasets(id) on delete cascade,
  version_number integer not null,
  raw_storage_key varchar(512) not null,
  curated_storage_key varchar(512),
  file_name varchar(255) not null,
  row_count integer,
  status dataset_status not null default 'uploaded',
  created_by_id integer not null references users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table dataset_mappings (
  id serial primary key,
  dataset_version_id integer not null references dataset_versions(id) on delete cascade,
  mapping_json text not null,
  confidence_json text not null,
  confirmed_by_id integer references users(id) on delete set null,
  confirmed_at timestamptz,
  created_at timestamptz not null default now()
);

create table data_quality_reports (
  id serial primary key,
  dataset_version_id integer not null references dataset_versions(id) on delete cascade,
  quality_score integer not null,
  critical_errors_json text not null default '[]',
  warnings_json text not null default '[]',
  recommendations_json text not null default '[]',
  created_at timestamptz not null default now()
);

create index idx_datasets_workspace on datasets(workspace_id);
create index idx_dataset_versions_dataset on dataset_versions(dataset_id);
create index idx_workspace_members_user on workspace_members(user_id);
create index idx_workspace_members_workspace on workspace_members(workspace_id);
create index idx_uploaded_files_workspace on uploaded_files(workspace_id);
create index idx_product_runs_workspace on product_runs(workspace_id);
create index idx_generated_reports_workspace on generated_reports(workspace_id);

-- NOTE on Row Level Security:
-- The FastAPI backend connects with the Supabase service-role/DB-owner connection
-- string and enforces workspace membership itself (see app/crud.py), so RLS is not
-- required for this backend to function. If you also want Postgres-level RLS as a
-- defense-in-depth layer, enable it per table and add policies keyed off
-- auth.uid() = supabase_uid (via a join through users), e.g.:
--
-- alter table workspaces enable row level security;
-- create policy "workspace members can read" on workspaces for select
--   using (id in (
--     select workspace_id from workspace_members wm
--     join users u on u.id = wm.user_id
--     where u.supabase_uid = auth.uid()::text
--   ));
