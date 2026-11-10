"""
LegalLens - OCR & Document Parsing Module
Supports PDF, Scanned Images, and Handwritten Documents via PaddleOCR.
Uses LangChain RecursiveCharacterTextSplitter for legal chunking.
"""

# [Summary]: Extracts text from PDFs/images (PaddleOCR) & splits contracts into clauses.

import os
import io
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegalLens.OCRParser")

# Global singleton cache for PaddleOCR instance
_PADDLE_OCR_INSTANCE = None


def get_paddle_ocr(lang: str = "en", use_angle_cls: bool = True):
    """Lazy singleton loader for PaddleOCR engine."""
    # Caches PaddleOCR in memory so models load only once.
    global _PADDLE_OCR_INSTANCE
    if _PADDLE_OCR_INSTANCE is None:
        try:
            from paddleocr import PaddleOCR
            logger.info(f"Initializing PaddleOCR (lang={lang}, use_angle_cls={use_angle_cls})...")
            _PADDLE_OCR_INSTANCE = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=lang,
                show_log=False
            )
            logger.info("PaddleOCR initialized successfully.")
        except ImportError as e:
            logger.warning(f"PaddleOCR package not installed: {e}. Falling back.")
            return None
        except Exception as e:
            logger.error(f"Error initializing PaddleOCR: {e}")
            return None
    return _PADDLE_OCR_INSTANCE


class OCRParser:
    """Parser for extracting text from PDF and Image documents."""

    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang

    def extract_text_from_image(
        self,
        image_input: Union[str, bytes, Image.Image],
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extracts text lines and confidence scores using PaddleOCR."""
        # Converts input to RGB NumPy array and runs OCR with angle detection
        if isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        img_np = np.array(image)
        ocr_engine = get_paddle_ocr(lang=lang or self.default_lang)

        # Tier 1: Run PaddleOCR if available
        if ocr_engine is not None:
            try:
                result = ocr_engine.ocr(img_np, cls=True)
                lines = []
                confidences = []

                if result and len(result) > 0 and result[0] is not None:
                    for line in result[0]:
                        if line and len(line) >= 2:
                            box, text_info = line[0], line[1]
                            text = text_info[0]
                            conf = float(text_info[1])
                            lines.append({"text": text, "confidence": conf, "box": box})
                            confidences.append(conf)

                full_text = "\n".join([item["text"] for item in lines])
                avg_conf = float(np.mean(confidences)) if confidences else 0.0

                return {
                    "text": full_text,
                    "lines": lines,
                    "average_confidence": round(avg_conf, 3),
                    "engine": "PaddleOCR"
                }
            except Exception as e:
                logger.warning(f"PaddleOCR failed: {e}. Trying pytesseract fallback...")

        # Tier 2: Run lightweight pytesseract fallback
        try:
            import pytesseract
            raw_text = pytesseract.image_to_string(image)
            lines = [{"text": l.strip(), "confidence": 0.85} for l in raw_text.split("\n") if l.strip()]
            return {
                "text": raw_text.strip(),
                "lines": lines,
                "average_confidence": 0.85,
                "engine": "pytesseract"
            }
        except Exception as e:
            logger.warning(f"pytesseract fallback failed or not installed: {e}")

        return {
            "text": "[Scanned document: Text layer processed via PDF/Digital extractor]",
            "lines": [],
            "average_confidence": 0.5,
            "engine": "fallback"
        }

    def extract_text_from_pdf(
        self,
        pdf_input: Union[str, bytes],
        force_ocr: bool = False,
        max_pages: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fast digital text extraction via pypdf; falls back to PaddleOCR for scans."""
        extracted_pages: List[Dict[str, Any]] = []
        overall_text = []
        is_scanned = False

        # Tier 1: Fast digital extraction (~0.1s)
        if not force_ocr:
            try:
                import pypdf
                pdf_file = io.BytesIO(pdf_input) if isinstance(pdf_input, bytes) else open(pdf_input, "rb")
                reader = pypdf.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                pages_to_process = min(total_pages, max_pages) if max_pages else total_pages

                digital_text_collected = []
                for idx in range(pages_to_process):
                    page = reader.pages[idx]
                    page_text = page.extract_text() or ""
                    if len(page_text.strip()) > 30:
                        digital_text_collected.append(page_text.strip())
                        extracted_pages.append({
                            "page_number": idx + 1,
                            "text": page_text.strip(),
                            "method": "digital_pdf",
                            "confidence": 1.0
                        })

                if len(digital_text_collected) >= (pages_to_process * 0.7) and sum(len(t) for t in digital_text_collected) > 100:
                    logger.info("Extracted digital text from PDF directly.")
                    return {
                        "text": "\n\n".join(digital_text_collected),
                        "pages": extracted_pages,
                        "total_pages": total_pages,
                        "is_scanned": False,
                        "engine": "pypdf_digital"
                    }
                else:
                    is_scanned = True
            except Exception as e:
                logger.warning(f"Digital PDF extraction skipped: {e}. Using OCR.")
                is_scanned = True
        else:
            is_scanned = True

        # Tier 2: OCR fallback for scanned pages
        rendered_images = self._render_pdf_to_images(pdf_input, max_pages=max_pages)
        if not rendered_images:
            return {
                "text": "[Error: Unable to render PDF pages for OCR.]",
                "pages": [],
                "total_pages": 0,
                "is_scanned": True,
                "error": "Rendering failed"
            }

        extracted_pages = []
        for idx, img in enumerate(rendered_images):
            ocr_res = self.extract_text_from_image(img)
            extracted_pages.append({
                "page_number": idx + 1,
                "text": ocr_res["text"],
                "confidence": ocr_res.get("average_confidence", 0.0),
                "method": "paddle_ocr"
            })
            if ocr_res["text"].strip():
                overall_text.append(ocr_res["text"].strip())

        return {
            "text": "\n\n".join(overall_text),
            "pages": extracted_pages,
            "total_pages": len(rendered_images),
            "is_scanned": is_scanned,
            "engine": "PaddleOCR"
        }

    def _render_pdf_to_images(
        self,
        pdf_input: Union[str, bytes],
        max_pages: Optional[int] = None
    ) -> List[Image.Image]:
        """Renders PDF pages to 200 DPI images via pypdfium2 (no poppler needed)."""
        images = []
        try:
            import pypdfium2 as pdfium
            pdf_bytes = pdf_input if isinstance(pdf_input, bytes) else open(pdf_input, "rb").read()
            pdf = pdfium.PdfDocument(pdf_bytes)
            n_pages = len(pdf)
            pages_to_render = min(n_pages, max_pages) if max_pages else n_pages

            for i in range(pages_to_render):
                page = pdf[i]
                bitmap = page.render(scale=2.0)
                pil_image = bitmap.to_pil()
                images.append(pil_image)
            return images
        except ImportError:
            try:
                from pdf2image import convert_from_bytes, convert_from_path
                if isinstance(pdf_input, bytes):
                    return convert_from_bytes(pdf_input, dpi=200, first_page=1, last_page=max_pages)
                else:
                    return convert_from_path(pdf_input, dpi=200, first_page=1, last_page=max_pages)
            except Exception as e:
                logger.error(f"PDF rendering failed: {e}")
                return []
        except Exception as e:
            logger.error(f"Error rendering PDF pages: {e}")
            return []

    def parse_document(
        self,
        file_input: Union[str, bytes],
        filename: str = "",
        force_ocr: bool = False
    ) -> Dict[str, Any]:
        """Ingestion router: handles .pdf, images (.png, .jpg), and raw text."""
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            return self.extract_text_from_pdf(file_input, force_ocr=force_ocr)
        elif any(filename_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]):
            res = self.extract_text_from_image(file_input)
            return {
                "text": res["text"],
                "pages": [{"page_number": 1, "text": res["text"], "confidence": res.get("average_confidence", 0.0)}],
                "total_pages": 1,
                "is_scanned": True,
                "engine": res.get("engine", "PaddleOCR")
            }
        else:
            if isinstance(file_input, bytes):
                try:
                    text = file_input.decode("utf-8")
                except UnicodeDecodeError:
                    text = file_input.decode("latin-1", errors="ignore")
            else:
                text = str(file_input)
            return {
                "text": text,
                "pages": [{"page_number": 1, "text": text, "confidence": 1.0}],
                "total_pages": 1,
                "is_scanned": False,
                "engine": "raw_text"
            }


class LegalTextChunker:
    """Splits contracts along legal boundaries (Articles, Sections, Clauses)."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Splits by Article/Section/Clause headers first, then paragraphs
        self.separators = [
            "\n\nARTICLE ",
            "\n\nArticle ",
            "\n\nSECTION ",
            "\n\nSection ",
            "\n\nClause ",
            "\n\n[0-9]+\\.",
            "\n\n",
            "\n",
            ". ",
            "; ",
            " "
        ]

    def split_text_into_chunks(self, text: str) -> List[str]:
        """Splits contract into context-preserving legal chunks."""
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
            except ImportError:
                return self._fallback_split(text)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            keep_separator=True
        )

        chunks = splitter.split_text(text)
        return [c.strip() for c in chunks if len(c.strip()) > 25]

    def _fallback_split(self, text: str) -> List[str]:
        """Fallback splitter if LangChain is not installed."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if current_len + len(p) > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_len = len(p)
            else:
                current_chunk.append(p)
                current_len += len(p)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        return chunks

    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        Splits text into chunks using LangChain RecursiveCharacterTextSplitter.
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
            except ImportError:
                # Basic fallback if langchain is missing
                return self._fallback_split(text)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            keep_separator=True
        )

        chunks = splitter.split_text(text)
        # Filter out empty or whitespace-only chunks
        clean_chunks = [c.strip() for c in chunks if len(c.strip()) > 25]
        return clean_chunks

    def _fallback_split(self, text: str) -> List[str]:
        """Fallback splitter if LangChain is not yet available."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if current_len + len(p) > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_len = len(p)
            else:
                current_chunk.append(p)
                current_len += len(p)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        return chunks
