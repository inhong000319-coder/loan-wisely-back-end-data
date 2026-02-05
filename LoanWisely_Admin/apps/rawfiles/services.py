from django.conf import settings
from . import client


def _mock_raw_files():
    return [
        {"id": "RAW-001", "name": "credit_input_2026_02.csv", "status": "UPLOADED", "uploaded_at": "2026-02-05 09:00"},
        {"id": "RAW-002", "name": "financial_meta_2026_02.xlsx", "status": "VALIDATED", "uploaded_at": "2026-02-04 15:30"},
    ]


def get_raw_files(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_raw_files()
    return client.list_raw_files(request, params=params)


def upload_raw_file(request, files):
    if settings.USE_MOCK_DATA:
        return {"status": "UPLOADED", "file_count": len(files)}
    return client.upload_raw_file(request, files=files)
