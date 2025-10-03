import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

__version__ = "0.2.0"


class ArtifactMetaData:
    """Class to handle metadata for artifacts."""

    def __init__(self, meta=Optional[Dict[str, str]]):
        self.meta = meta if meta else {}

    def load(self, path: Path) -> None:
        """Load metadata from a JSON file."""
        with open(path, "r") as f:
            self.meta = json.load(f)

    def save(self, path: Path) -> None:
        """Save metadata to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.meta, f, indent=2, sort_keys=True)

    def add(self, key: str, value: Union[str, int]) -> None:
        """Add a key-value pair to the metadata."""
        self.meta[key] = value

    def add_kv_string(self, kv: str) -> Tuple[Optional[str], Optional[str]]:
        """Add a key-value pair from a string in the format 'key=value'. 'key=' removes the key."""
        if '=' not in kv:
            raise ValueError(f"Invalid metadata format '{kv}', expected key=value")
        key, value = kv.split('=', 1)
        if value == '':
            if key in self.meta:
                del self.meta[key]
            else:
                raise KeyError(f"Key '{key}' not found in metadata")
            return None, None
        else:
            self.add(key, value)
        return key, value

    def dump(self, show_hidden=False) -> str:
        """Return a JSON string representation of the metadata."""
        meta = self.meta.copy()
        if not show_hidden:
            for key in list(meta.keys()):
                if key.startswith('__'):
                    del meta[key]
        return json.dumps(meta, indent=2, sort_keys=True)
