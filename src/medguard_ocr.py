try:
    from .ocr_engine import LocalOCRError, perform_ocr
except ImportError:
    from ocr_engine import LocalOCRError, perform_ocr


class OCRServiceError(Exception):
    def __init__(self, message, status_code=502, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def perform_health_ocr(image_path, image_bytes, filename, mimetype, group_id=None):
    return run_local_health_ocr(image_bytes, group_id), "local_src"


def run_local_health_ocr(image_bytes, group_id=None):
    try:
        return perform_ocr(image_bytes, group_id)
    except LocalOCRError as error:
        raise OCRServiceError(str(error)) from error
