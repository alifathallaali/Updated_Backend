"""Small launch-security primitives shared by API routes.

This module intentionally stays framework-light: workspace authorization remains in
``crud`` and this file only adds storage-key validation, filename normalization, and
an MVP fixed-window abuse guard for costly endpoints.
"""
from __future__ import annotations

import re
import threading
import time
from collections import defaultdict, deque
from pathlib import PurePath

from fastapi import HTTPException, status

from .config import settings

_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._() -]+")
_lock = threading.Lock()
_events: dict[tuple[str, int], deque[float]] = defaultdict(deque)


def safe_storage_filename(file_name: str) -> str:
    """Return a basename safe for use as an object-storage key segment."""
    name = PurePath((file_name or "").replace("\\", "/")).name.strip()
    name = _SAFE_FILENAME.sub("_", name).strip(". ")
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A valid file name is required")
    return name[:255]


def workspace_storage_prefix(workspace_id: int) -> str:
    if workspace_id <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid workspace identifier")
    return f"workspaces/{workspace_id}/"


def require_workspace_storage_key(workspace_id: int, storage_key: str) -> None:
    """Reject metadata registration for objects outside the caller's workspace."""
    key = (storage_key or "").lstrip("/")
    if not key.startswith(workspace_storage_prefix(workspace_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Storage object is not in this workspace")


def enforce_rate_limit(scope: str, user_id: int, limit: int, window_seconds: int = 3600) -> None:
    """Per-process fixed-window guard for beta abuse protection.

    This is deliberately minimal. Multi-instance deployments should replace it with a
    shared Redis/database limiter without changing route authorization semantics.
    """
    if limit <= 0:
        return
    now = time.monotonic()
    cutoff = now - window_seconds
    key = (scope, user_id)
    with _lock:
        bucket = _events[key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Request limit reached; try again later")
        bucket.append(now)


def enforce_upload_limit(user_id: int) -> None:
    enforce_rate_limit("upload", user_id, settings.upload_requests_per_hour)


def enforce_copilot_limit(user_id: int) -> None:
    enforce_rate_limit("copilot", user_id, settings.copilot_requests_per_hour)


def _reset_rate_limits_for_tests() -> None:
    with _lock:
        _events.clear()
