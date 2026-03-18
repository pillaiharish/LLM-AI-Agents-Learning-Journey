import os
import re
import uuid


class FileRenamer:
    # Patterns commonly found in downloaded files
    METADATA_PATTERNS = [
        r'\s*\(\d+\)',                # (1), (2), etc.
        r'\s*-\s*Copy',              # - Copy
        r'\s*copy\s*\d*',            # copy, copy 2
        r'\s*\[\d+\]',              # [1], [2]
        r'[_\-]\d{10,}',            # Unix timestamps
        r'[_\-]\d{4}-\d{2}-\d{2}',  # date stamps (2024-01-15)
        r'[_\-]\d{8}(?!\d)',         # compact dates (20240115)
    ]

    @staticmethod
    def random_name(original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        return str(uuid.uuid4()) + ext

    @staticmethod
    def strip_metadata(original_filename: str) -> str:
        name, ext = os.path.splitext(original_filename)
        for pattern in FileRenamer.METADATA_PATTERNS:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        name = name.strip(' -_')
        if not name:
            name = 'file'
        return name + ext

    @staticmethod
    def custom_name(new_name: str, original_filename: str) -> str:
        orig_ext = os.path.splitext(original_filename)[1]
        if '.' in new_name:
            return new_name
        return new_name + orig_ext
