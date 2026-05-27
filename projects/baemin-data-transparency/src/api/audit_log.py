from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..models.types import AuditAction, AuditLogEntry

_log_store: list[AuditLogEntry] = []


def log_action(
    actor_id: UUID,
    actor_type: str,
    action: AuditAction,
    store_id: UUID | None = None,
    data_scope: str | None = None,
    detail: dict | None = None,
    ip_address: str | None = None,
) -> AuditLogEntry:
    entry = AuditLogEntry(
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        store_id=store_id,
        data_scope=data_scope,
        detail=detail,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    _log_store.append(entry)
    return entry


def get_logs(
    store_id: UUID | None = None,
    action: AuditAction | None = None,
    actor_id: UUID | None = None,
    limit: int = 100,
) -> list[AuditLogEntry]:
    results = _log_store
    if store_id:
        results = [e for e in results if e.store_id == store_id]
    if action:
        results = [e for e in results if e.action == action]
    if actor_id:
        results = [e for e in results if e.actor_id == actor_id]
    return sorted(results, key=lambda e: e.created_at, reverse=True)[:limit]


def clear_store() -> None:
    _log_store.clear()
