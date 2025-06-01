import json
import threading
import os

class SharedMemory:
    """
    Singleton class for lightweight shared memory using a JSON file.
    Stores metadata, past decisions, insights, and logs.
    """

    _instance = None
    _lock = threading.Lock()
    _memory_file = os.path.join(os.path.dirname(__file__), "shared_memory.json")

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SharedMemory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, "_initialized"):
            self._initialized = True
            if not os.path.exists(self._memory_file):
                with open(self._memory_file, "w") as f:
                    json.dump({"metadata": {}, "decisions": [], "insights": [], "logs": []}, f)

    def read_memory(self):
        with self._lock:
            with open(self._memory_file, "r") as f:
                return json.load(f)

    def write_memory(self, key, value):
        with self._lock:
            data = self.read_memory()
            data[key] = value
            with open(self._memory_file, "w") as f:
                json.dump(data, f, indent=2)

    def get_context(self):
        """
        Returns a summary of the current memory context.
        """
        data = self.read_memory()
        return {
            "metadata": data.get("metadata", {}),
            "last_decision": data.get("decisions", [])[-1] if data.get("decisions") else None,
            "last_insight": data.get("insights", [])[-1] if data.get("insights") else None,
            "logs": data.get("logs", [])
        }
