import os
from abc import ABC, abstractmethod
from flask import current_app
from azure.storage.blob import BlobServiceClient

class StorageBackend(ABC):
    @abstractmethod
    def save(self, rel_path: str, binary_data: bytes):
        pass

    @abstractmethod
    def load(self, rel_path: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, rel_path: str):
        pass


class LocalFilesystemStorage(StorageBackend):
    def __init__(self, root_folder):
        self.root = root_folder
        print(f"[LocalFilesystemStorage] Initialized with root folder: {self.root}")

    def save(self, rel_path: str, binary_data: bytes):
        abs_path = os.path.join(self.root, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'wb') as f:
            f.write(binary_data)
        print(f"[LocalFilesystemStorage] Saved file: {abs_path}")

    def load(self, rel_path: str) -> bytes:
        abs_path = os.path.join(self.root, rel_path)
        print(f"[LocalFilesystemStorage] Loading file: {abs_path}")
        with open(abs_path, 'rb') as f:
            return f.read()

    def delete(self, rel_path: str):
        abs_path = os.path.join(self.root, rel_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)
            print(f"[LocalFilesystemStorage] Deleted file: {abs_path}")
        else:
            print(f"[LocalFilesystemStorage] File not found for delete: {abs_path}")


class BlobStorage(StorageBackend):
    def __init__(self, settings: dict):
        connection_string = settings['connection_string']
        container_name = settings['container']
        self.container_name = container_name
        self.client = BlobServiceClient.from_connection_string(connection_string).get_container_client(container_name)
        print(f"[BlobStorage] Initialized for container: {self.container_name}")

    def save(self, rel_path: str, binary_data: bytes):
        print(f"[BlobStorage] Saving blob: {rel_path}")
        self.client.upload_blob(name=rel_path, data=binary_data, overwrite=True)

    def load(self, rel_path: str) -> bytes:
        print(f"[BlobStorage] Loading blob: {rel_path}")
        downloader = self.client.download_blob(rel_path)
        return downloader.readall()

    def delete(self, rel_path: str):
        print(f"[BlobStorage] Deleting blob: {rel_path}")
        self.client.delete_blob(rel_path)


_storage = None

def get_storage() -> StorageBackend:
    """
    Decide at runtime whether to use local or blob storage.
    Looks at current_app.config['STORAGE_BACKEND'].
    """
    global _storage
    if _storage is None:
        backend = current_app.config.get('STORAGE_BACKEND', 'local')
        print(f"[get_storage] Configured backend: {backend}")
        if backend == 'blob':
            blob_config = current_app.config.get('BLOB_SETTINGS', {})
            print(f"[get_storage] Blob settings: {blob_config}")
            _storage = BlobStorage(blob_config)
        else:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            print(f"[get_storage] Local upload folder: {upload_folder}")
            _storage = LocalFilesystemStorage(upload_folder)
    return _storage
