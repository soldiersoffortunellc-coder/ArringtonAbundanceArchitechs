"""
StorageAdapter — stores/references scripts, videos, captions, thumbnails,
disclosures, approval records, and campaign assets. Dry-run/local mode by
default: writes go to a local `.local_storage/` directory (git-ignored)
rather than any live bucket, unless constructed live+authorized against a
real backend (S3, GCS, etc. — not wired in; see docs/16 next-steps).
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from csuite.providers.base import ProviderAdapterBase, ProviderAction

LOCAL_STORAGE_ROOT = Path(__file__).resolve().parents[3] / ".local_storage"


class StorageAdapter(ProviderAdapterBase):
    provider_name = "storage"

    def __init__(self, dry_run: bool = True, live_authorized: bool = False, root: Path | None = None):
        super().__init__(dry_run=dry_run, live_authorized=live_authorized)
        self.root = root or LOCAL_STORAGE_ROOT

    def store_asset(self, *, campaign_id: str, kind: str, content: bytes | str) -> ProviderAction:
        asset_id = f"asset_{uuid.uuid4().hex[:12]}"
        storage_ref = f"local://{campaign_id}/{kind}/{asset_id}"
        if self.dry_run:
            result = {"status": "SIMULATED", "storage_ref": storage_ref, "asset_id": asset_id}
        else:
            path = self.root / campaign_id / kind
            path.mkdir(parents=True, exist_ok=True)
            mode = "wb" if isinstance(content, bytes) else "w"
            with open(path / asset_id, mode) as fh:
                fh.write(content)
            result = {"status": "STORED", "storage_ref": str(path / asset_id), "asset_id": asset_id}
        return self._record("store_asset", {"campaign_id": campaign_id, "kind": kind}, result)

    def retrieve_asset_ref(self, storage_ref: str) -> ProviderAction:
        if self.dry_run:
            result = {"status": "SIMULATED", "exists": True}
        else:
            result = {"status": "CHECKED", "exists": os.path.exists(storage_ref)}
        return self._record("retrieve_asset_ref", {"storage_ref": storage_ref}, result)
