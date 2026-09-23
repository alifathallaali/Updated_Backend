from pathlib import Path
from .tender_schemas import Tender

SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".doc", ".json"}

def parse_tender(source):
    if isinstance(source, Tender):
        return source
    if isinstance(source, dict):
        return Tender(**{
            key: source[key]
            for key in Tender.__dataclass_fields__
            if key in source
        })
    if isinstance(source, str):
        suffix = Path(source).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported tender file type: {suffix}")
        raise NotImplementedError(
            "File extraction/OCR is not wired yet. Provide an extracted tender payload."
        )
    raise TypeError("Tender source must be a Tender object, dict, or supported file path.")
