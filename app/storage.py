import uuid

from supabase import create_client, Client

from .config import settings

BUCKET_NAME = "uploads"


def _client() -> Client:
    if not (settings.supabase_url and settings.supabase_service_role_key):
        raise RuntimeError(
            "Storage is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY "
            "in your environment."
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def _r2_client():
    if not (settings.r2_account_id and settings.r2_access_key_id and settings.r2_secret_access_key):
        return None
    import boto3
    return boto3.client(
        "s3", endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


def _normalize_key(rel_key: str) -> str:
    return rel_key.lstrip("/")


def _append_hash_suffix(rel_key: str) -> str:
    suffix = uuid.uuid4().hex[:8]
    if "." in rel_key.rsplit("/", 1)[-1]:
        base, _, ext = rel_key.rpartition(".")
        return f"{base}_{suffix}.{ext}"
    return f"{rel_key}_{suffix}"


def storage_put(rel_key: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
    """Uploads bytes to Supabase Storage and returns the stored object key."""
    key = _append_hash_suffix(_normalize_key(rel_key))
    # Supabase is the primary store; R2 remains an optional compatibility fallback.
    if settings.supabase_url and settings.supabase_service_role_key:
        res = _client().storage.from_(BUCKET_NAME).upload(key, data, {"content-type": content_type, "upsert": "false"})
        if isinstance(res, dict) and res.get("error"):
            raise RuntimeError(f"Storage upload failed: {res['error']}")
        return {"key": key}
    r2 = _r2_client()
    if r2:
        r2.put_object(Bucket=settings.r2_bucket_name, Key=key, Body=data, ContentType=content_type)
        return {"key": key}
    res = _client().storage.from_(BUCKET_NAME).upload(
        key,
        data,
        {"content-type": content_type, "upsert": "false"},
    )
    if isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Storage upload failed: {res['error']}")
    return {"key": key}


def storage_get_signed_url(rel_key: str, expires_in: int = 3600) -> str:
    key = _normalize_key(rel_key)
    if settings.supabase_url and settings.supabase_service_role_key:
        res = _client().storage.from_(BUCKET_NAME).create_signed_url(key, expires_in)
    else:
        r2 = _r2_client()
        if r2:
            return r2.generate_presigned_url("get_object", Params={"Bucket": settings.r2_bucket_name, "Key": key}, ExpiresIn=expires_in)
        raise RuntimeError("Storage is not configured")
    if isinstance(res, dict):
        return res.get("signedURL") or res.get("signedUrl") or ""
    return res


def storage_put_presigned_url(rel_key: str, expires_in: int = 7200, add_suffix: bool = True) -> dict:
    """Create a signed Supabase Storage upload session for resumable browser upload."""
    key = _append_hash_suffix(_normalize_key(rel_key)) if add_suffix else _normalize_key(rel_key)
    if settings.supabase_url and settings.supabase_service_role_key:
        response = _client().storage.from_(BUCKET_NAME).create_signed_upload_url(key)
        payload = response.get("data", response) if isinstance(response, dict) else response
        token = payload.get("token") if isinstance(payload, dict) else getattr(payload, "token", None)
        if not token:
            raise RuntimeError("Supabase did not return a signed upload token")
        project_ref = settings.supabase_url.split("//", 1)[-1].split(".", 1)[0]
        endpoint = f"https://{project_ref}.storage.supabase.co/storage/v1/upload/resumable"
        return {"key": key, "bucket": BUCKET_NAME, "token": token, "endpoint": endpoint, "expiresIn": expires_in, "method": "TUS"}
    r2 = _r2_client()
    if r2:
        url = r2.generate_presigned_url("put_object", Params={"Bucket": settings.r2_bucket_name, "Key": key}, ExpiresIn=expires_in)
        return {"key": key, "url": url, "expiresIn": expires_in, "method": "PUT"}
    raise RuntimeError("Storage is not configured")


def storage_delete(rel_key: str) -> None:
    key = _normalize_key(rel_key)
    if settings.supabase_url and settings.supabase_service_role_key:
        _client().storage.from_(BUCKET_NAME).remove([key])
        return
    r2 = _r2_client()
    if r2:
        r2.delete_object(Bucket=settings.r2_bucket_name, Key=key)
        return
    raise RuntimeError("Storage is not configured")
