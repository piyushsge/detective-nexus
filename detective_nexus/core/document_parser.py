import os
from pathlib import Path
from typing import Tuple, Dict, Any, List

class DocumentParser:
    """
    Parses PDF, DOCX, TXT, and Markdown files for Detective Nexus.
    Extracts raw text, identifies source metadata, and validates file structure.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".json"}

    @classmethod
    def parse_file(cls, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Reads document and extracts clean text content.
        Returns: (success, extracted_text_or_error, metadata)
        """
        if not file_path:
            return False, "No file provided.", {}

        path = Path(file_path)
        if not path.exists():
            return False, f"File does not exist: {file_path}", {}

        ext = path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type '{ext}'. Supported formats: PDF, DOCX, TXT, MD, JSON.", {}

        metadata = {
            "filename": path.name,
            "extension": ext,
            "size_bytes": path.stat().st_size
        }

        try:
            if ext == ".pdf":
                return cls._parse_pdf(path, metadata)
            elif ext == ".docx":
                return cls._parse_docx(path, metadata)
            elif ext in {".txt", ".md", ".json"}:
                return cls._parse_text(path, metadata)
            else:
                return False, f"Unhandled extension: {ext}", metadata
        except Exception as e:
            return False, f"Error parsing document: {type(e).__name__}: {str(e)}", metadata

    @classmethod
    def _parse_pdf(cls, path: Path, metadata: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"--- PAGE {i+1} ---\n{text.strip()}")
            full_text = "\n\n".join(pages_text)
            metadata["page_count"] = len(reader.pages)
            metadata["char_count"] = len(full_text)
            if not full_text.strip():
                return False, "PDF appears to be empty or contains scanned images without extractable text.", metadata
            return True, full_text, metadata
        except Exception as e:
            return False, f"Failed to extract PDF: {str(e)}", metadata

    @classmethod
    def _parse_docx(cls, path: Path, metadata: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        try:
            import docx
            doc = docx.Document(str(path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            metadata["paragraph_count"] = len(paragraphs)
            metadata["char_count"] = len(full_text)
            if not full_text.strip():
                return False, "DOCX file contains no text paragraphs.", metadata
            return True, full_text, metadata
        except Exception as e:
            return False, f"Failed to extract DOCX: {str(e)}", metadata

    @classmethod
    def _parse_text(cls, path: Path, metadata: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            metadata["char_count"] = len(content)
            return True, content, metadata
        except Exception as e:
            return False, f"Failed to read text file: {str(e)}", metadata
