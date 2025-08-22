import logging
from typing import Dict, Any, Optional

from app.services.unified_service import UnifiedService

try:
    from striprtf.striprtf import rtf_to_text

    RTF_SUPPORT = True
except ImportError:
    RTF_SUPPORT = False

logger = logging.getLogger(__name__)


class UploadService:
    """Service for handling file uploads and document processing"""

    def __init__(self):
        self.unified_service = UnifiedService()

    def process_document_upload(
        self, file_content: bytes, filename: str, user_context: str
    ) -> Dict[str, Any]:
        """Process uploaded document and generate PRD"""
        logger.info(f"Processing document upload: {filename}")

        file_extension = filename.lower().split(".")[-1] if "." in filename else ""

        if file_extension == "pdf":
            raise ValueError(
                "PDF files are not supported yet. Please use .txt, .md, or .rtf files."
            )
        elif file_extension in ["doc", "docx"]:
            raise ValueError(
                "Word documents (.doc, .docx) are not supported yet. Please use .txt, .md, or .rtf files."
            )
        elif file_extension == "rtf":
            text_content = self._extract_rtf_text(file_content)
        elif file_extension in ["txt", "md"]:
            text_content = self._extract_text_content(file_content)
        else:
            raise ValueError(
                f"Unsupported file type: {file_extension}. Please use .txt, .md, or .rtf files."
            )

        enhanced_prompt = f"{user_context}\n\nDocument Content:\n{text_content}"
        return self.unified_service._handle_prd_request(enhanced_prompt)

    def _extract_rtf_text(self, content: bytes) -> str:
        """Extract text from RTF content"""
        if not RTF_SUPPORT:
            raise ValueError(
                "RTF support is not available. Please use .txt or .md files."
            )

        try:
            rtf_content = content.decode("utf-8")
            return rtf_to_text(rtf_content)
        except UnicodeDecodeError:
            try:
                rtf_content = content.decode("latin-1")
                return rtf_to_text(rtf_content)
            except UnicodeDecodeError:
                rtf_content = content.decode("cp1252", errors="ignore")
                return rtf_to_text(rtf_content)

    def _extract_text_content(self, content: bytes) -> str:
        """Extract text from plain text content with encoding fallback"""
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except UnicodeDecodeError:
                return content.decode("cp1252", errors="ignore")
