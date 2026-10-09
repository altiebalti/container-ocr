"""GcpStore з підміненими Firestore і Cloud Storage: перевіряє імена об'єктів і записи."""
from app.store import GcpStore


class FakeBlob:
    def __init__(self, bucket, name):
        self.bucket, self.name = bucket, name

    def upload_from_string(self, data, content_type=None):
        self.bucket.objects[self.name] = (data, content_type)

    def exists(self):
        return self.name in self.bucket.objects

    def download_as_bytes(self):
        return self.bucket.objects[self.name][0]


class FakeBucket:
    name = "demo-bucket"

    def __init__(self):
        self.objects = {}

    def blob(self, name):
        return FakeBlob(self, name)


class FakeDoc:
    def __init__(self, col, doc_id):
        self.col, self.id = col, doc_id

    def set(self, data):
        self.col.docs[self.id] = data

    def get(self):
        return self

    @property
    def exists(self):
        return self.id in self.col.docs

    def to_dict(self):
        return self.col.docs[self.id]


class FakeCollection:
    def __init__(self):
        self.docs = {}

    def document(self, doc_id):
        return FakeDoc(self, doc_id)


def make_store(bucket=True):
    store = GcpStore.__new__(GcpStore)
    store.collection = FakeCollection()
    store.bucket = FakeBucket() if bucket else None
    return store


def test_save_uploads_image_and_thumb_and_writes_record():
    store = make_store()
    assert store.stores_images
    store.save({"id": "abc", "status": "valid"}, b"IMG", b"THUMB")
    assert store.bucket.objects["scans/abc.jpg"] == (b"IMG", "image/jpeg")
    assert store.bucket.objects["scans/abc_thumb.jpg"] == (b"THUMB", "image/jpeg")
    doc = store.get("abc")
    assert doc["status"] == "valid" and doc["image_uri"] == "gs://demo-bucket/scans/abc.jpg"
    assert store.image("abc") == b"IMG" and store.image("abc", thumb=True) == b"THUMB"
    assert store.image("missing") is None and store.get("missing") is None


def test_without_bucket_only_record_is_saved():
    store = make_store(bucket=False)
    assert not store.stores_images
    store.save({"id": "abc"}, b"IMG", b"THUMB")
    assert store.get("abc") == {"id": "abc"}
    assert store.image("abc") is None
