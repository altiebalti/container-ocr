from __future__ import annotations

import copy
import threading
from collections import OrderedDict


class MemoryStore:
    name = "memory"
    stores_images = True

    def __init__(self, limit: int = 200):
        self._items: OrderedDict[str, tuple[dict, bytes, bytes]] = OrderedDict()
        self._lock = threading.Lock()
        self._limit = limit

    def save(self, record: dict, image: bytes, thumb: bytes) -> None:
        with self._lock:

            self._items[record["id"]] = (copy.deepcopy(record), image, thumb)
            while len(self._items) > self._limit:
                self._items.popitem(last=False)

    def list(self, limit: int = 20) -> list[dict]:
        with self._lock:
            return [r for r, _, _ in reversed(self._items.values())][:limit]

    def get(self, scan_id: str) -> dict | None:
        item = self._items.get(scan_id)
        return item[0] if item else None

    def image(self, scan_id: str, thumb: bool = False) -> bytes | None:
        item = self._items.get(scan_id)
        if not item:
            return None
        return item[2] if thumb else item[1]


class GcpStore:
    name = "gcp"

    def __init__(self, collection: str = "scans", bucket: str | None = None,
                 database: str | None = None):
        from google.cloud import firestore

        self._firestore = firestore
        self.db = firestore.Client(database=database) if database else firestore.Client()
        self.collection = self.db.collection(collection)
        self.bucket = None
        if bucket:
            from google.cloud import storage
            self.bucket = storage.Client().bucket(bucket)

    @property
    def stores_images(self) -> bool:
        return self.bucket is not None

    @staticmethod
    def _blob_name(scan_id: str, thumb: bool) -> str:
        return "scans/%s%s.jpg" % (scan_id, "_thumb" if thumb else "")

    def save(self, record: dict, image: bytes, thumb: bytes) -> None:
        if self.bucket is not None:
            for data, is_thumb in ((image, False), (thumb, True)):
                blob = self.bucket.blob(self._blob_name(record["id"], is_thumb))
                blob.upload_from_string(data, content_type="image/jpeg")
            record = dict(record, image_uri="gs://%s/%s" % (self.bucket.name,
                                                           self._blob_name(record["id"], False)))
        self.collection.document(record["id"]).set(record)

    def list(self, limit: int = 20) -> list[dict]:
        query = (self.collection
                 .order_by("created_at", direction=self._firestore.Query.DESCENDING)
                 .limit(limit))
        return [doc.to_dict() for doc in query.stream()]

    def get(self, scan_id: str) -> dict | None:
        doc = self.collection.document(scan_id).get()
        return doc.to_dict() if doc.exists else None

    def image(self, scan_id: str, thumb: bool = False) -> bytes | None:
        if self.bucket is None:
            return None
        blob = self.bucket.blob(self._blob_name(scan_id, thumb))
        if not blob.exists():
            return None
        return blob.download_as_bytes()
