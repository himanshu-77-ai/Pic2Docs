"""
batch_ocr.py — Multi-Image Batch OCR
──────────────────────────────────────
Processes multiple uploaded images in sequence.
- Returns combined text with per-file headers
- Tracks per-file success/failure
- Exports combined TXT, PDF, Word
- Progress bar support
"""
from __future__ import annotations
import io
import logging
from dataclasses import dataclass
from typing import Callable

from ocr_engine import run_ocr, OCRResult

logger = logging.getLogger("pic2docs.batch")


@dataclass
class BatchItem:
    filename:   str
    result:     OCRResult
    success:    bool
    error:      str | None = None


def run_batch_ocr(
    files: list[tuple[str, bytes]],      # list of (filename, bytes)
    lang_code: str = "en",
    on_progress: Callable[[int, int, str], None] | None = None,
) -> list[BatchItem]:
    """
    Process multiple images with OCR.
    
    Args:
        files:       List of (filename, file_bytes)
        lang_code:   OCR language code
        on_progress: Optional callback(current, total, filename)
    
    Returns:
        List of BatchItem results
    """
    results: list[BatchItem] = []
    total = len(files)

    for i, (filename, file_bytes) in enumerate(files):
        if on_progress:
            on_progress(i + 1, total, filename)

        logger.info("Batch OCR [%d/%d]: %s", i + 1, total, filename)
        try:
            result = run_ocr(file_bytes, filename, lang_code)
            if result.error:
                results.append(BatchItem(
                    filename=filename, result=result,
                    success=False, error=result.error))
            else:
                results.append(BatchItem(
                    filename=filename, result=result, success=True))
        except Exception as exc:
            logger.exception("Batch item failed: %s — %s", filename, exc)
            empty = OCRResult("", 0.0, 0, lang_code, str(exc))
            results.append(BatchItem(
                filename=filename, result=empty,
                success=False, error=str(exc)))

    return results


def combine_results_txt(items: list[BatchItem]) -> bytes:
    """Merge all batch results into one TXT with headers."""
    parts = []
    for i, item in enumerate(items, 1):
        header = (
            f"{'='*60}\n"
            f"File {i}/{len(items)}: {item.filename}\n"
        )
        if item.success:
            conf = int(item.result.confidence * 100)
            header += f"Confidence: {conf}% | Blocks: {item.result.block_count}\n"
            header += f"{'─'*60}\n"
            header += item.result.text
        else:
            header += f"ERROR: {item.error}\n"
        parts.append(header)
    return "\n\n".join(parts).encode("utf-8")


def batch_stats(items: list[BatchItem]) -> dict:
    """Return summary statistics for a batch run."""
    success = [i for i in items if i.success]
    failed  = [i for i in items if not i.success]
    avg_conf = (
        sum(i.result.confidence for i in success) / len(success)
        if success else 0.0
    )
    total_words = sum(
        len(i.result.text.split()) for i in success
    )
    return {
        "total":       len(items),
        "success":     len(success),
        "failed":      len(failed),
        "avg_conf":    round(avg_conf * 100, 1),
        "total_words": total_words,
    }
