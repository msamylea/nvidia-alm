import os
import shutil
import hashlib
import pickle

class ClearableCache:
    def __init__(self, cache_dir='cache-directory'):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def set(self, key, value, timeout=None):
        file_path = os.path.join(self.cache_dir, key)
        with open(file_path, 'wb') as f:
            pickle.dump(value, f)

    def get(self, key):
        file_path = os.path.join(self.cache_dir, key)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        return None

    def clear(self):
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

cache = ClearableCache()

def cache_key(*args, **kwargs):
    """Generate a cache key from the given arguments."""
    key = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key.encode()).hexdigest()