-- Run this migration once on the existing Supabase/Postgres database.
create table if not exists upload_jobs (
  id bigserial primary key,
  workspace_id bigint not null references workspaces(id) on delete cascade,
  user_id bigint not null references users(id) on delete cascade,
  dataset_version_id bigint references dataset_versions(id) on delete set null,
  file_name varchar(255) not null,
  storage_key varchar(512) not null,
  idempotency_key varchar(160) not null unique,
  status varchar(32) not null default 'created',
  stage varchar(64) not null default 'created',
  progress integer not null default 0,
  size_bytes bigint,
  error_message text,
  cancel_requested boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists ix_upload_jobs_queue on upload_jobs(status, created_at);
create index if not exists ix_upload_jobs_user on upload_jobs(user_id, created_at);
