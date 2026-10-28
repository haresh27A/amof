"""
Automatic Document Metadata Profiler
Component Tag: [A. Offline Metadata Generation]
"""

import os
from typing import Dict, Any
from datetime import datetime, timezone
import pypdf
import docx
import pandas as pd

class DocumentProfiler:
    """
    Extracts text statistics and metadata from PDF, DOCX, CSV, and TXT files.
    Tag: [A. Offline Metadata Generation]
    """

    @staticmethod
    def profile_file(file_path: str) -> Dict[str, Any]:
        """
        Extract title, text preview, size, modified timestamp, and key terms.
        """
        if not os.path.exists(file_path):
            return {
                "document_summary": f"Document at {file_path}",
                "capabilities": "Unstructured text document search",
                "file_type": "unknown",
                "size_bytes": 0,
                "modified_time": datetime.now(timezone.utc).isoformat()
            }

        stat = os.stat(file_path)
        size_bytes = stat.st_size
        mod_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        ext = os.path.splitext(file_path)[1].lower()

        extracted_text = ""

        try:
            if ext == ".pdf":
                reader = pypdf.PdfReader(file_path)
                text_pages = [p.extract_text() or "" for p in reader.pages[:5]]
                extracted_text = " ".join(text_pages)
            elif ext in [".docx", ".doc"]:
                doc = docx.Document(file_path)
                extracted_text = " ".join([p.text for p in doc.paragraphs[:20]])
            elif ext in [".csv", ".xlsx"]:
                df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)
                extracted_text = f"Columns: {', '.join(df.columns)}. Rows count: {len(df)}"
            elif ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read(2000)
            else:
                extracted_text = f"File type {ext}"
        except Exception as e:
            extracted_text = f"Error reading file text: {str(e)}"

        preview = extracted_text[:500].replace("\n", " ")
        doc_summary = f"[{ext.upper()}] {os.path.basename(file_path)}: {preview}"
        capabilities = f"Unstructured document search for {ext.upper()} policy and specifications"

        return {
            "document_summary": doc_summary,
            "capabilities": capabilities,
            "file_type": ext,
            "size_bytes": size_bytes,
            "modified_time": mod_time
        }
