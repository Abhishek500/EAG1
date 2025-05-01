from typing import Any, Dict, Optional

class MemoryManager:
    def __init__(self):
        # simple dict storage
        self.store: Dict[str, Any] = {}

    def store_item(self, key: str, value: Any) -> None:
        """Store a value under a key."""
        self.store[key] = value

    def recall_item(self, key: str) -> Optional[Any]:
        """Recall a stored value or None if missing."""
        return self.store.get(key)