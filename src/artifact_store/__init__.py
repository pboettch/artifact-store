import json


class ArtifactMetaData:
    """Class to handle metadata for artifacts."""

    def __init__(self, meta=None):
        self.meta = meta if meta else {}

    def add(self, key, value):
        """Add a key-value pair to the metadata."""
        self.meta[key] = value

    def __str__(self):
        """Return a string representation of the metadata."""
        return json.dumps(self.meta, indent=2, sort_keys=True)
