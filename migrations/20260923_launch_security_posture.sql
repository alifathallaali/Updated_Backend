-- Launch Closure Wave 2: backend-mediated data access posture.
--
-- The MVP intentionally keeps application-table RLS disabled because the FastAPI
-- backend uses a service-role/owner connection and performs workspace authorization.
-- To prevent the browser's Supabase anon/authenticated roles from bypassing that
-- backend authorization, remove direct table privileges from those roles.
-- Supabase Auth remains available to the frontend; this affects application tables only.

revoke all on table users from anon, authenticated;
revoke all on table workspaces from anon, authenticated;
revoke all on table workspace_members from anon, authenticated;
revoke all on table uploaded_files from anon, authenticated;
revoke all on table saved_filters from anon, authenticated;
revoke all on table copilot_messages from anon, authenticated;
revoke all on table generated_reports from anon, authenticated;
revoke all on table product_runs from anon, authenticated;
revoke all on table user_notifications from anon, authenticated;
revoke all on table datasets from anon, authenticated;
revoke all on table dataset_versions from anon, authenticated;
revoke all on table dataset_mappings from anon, authenticated;
revoke all on table data_quality_reports from anon, authenticated;

-- Storage remains private and is accessed through service-role operations or narrowly
-- scoped signed upload/download URLs issued only after backend workspace authorization.
