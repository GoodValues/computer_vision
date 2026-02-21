import time
import requests

class OcrError(Exception):
    pass

def start_read_url(endpoint: str, key: str, image_url: str) -> str:
    """Start OCR dla publicznego URL (JSON body)."""
    url = endpoint.rstrip("/") + "/vision/v3.2/read/analyze"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    payload = {"url": image_url}
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 202:
        raise OcrError(f"Start OCR (url) failed: {resp.status_code} {resp.text}")
    op_location = resp.headers.get("Operation-Location")
    if not op_location:
        raise OcrError("Brak nagłówka Operation-Location.")
    return op_location

def start_read_stream(endpoint: str, key: str, file_path: str, content_type: str) -> str:
    """
    Start OCR dla pliku lokalnego (binary/stream).
    W REST referencji to wariant 'Read In Stream' (overload=stream).
    """
    url = endpoint.rstrip("/") + "/vision/v3.2/read/analyze?overload=stream"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": content_type
    }
    with open(file_path, "rb") as f:
        data = f.read()
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 202:
        raise OcrError(f"Start OCR (stream) failed: {resp.status_code} {resp.text}")
    op_location = resp.headers.get("Operation-Location")
    if not op_location:
        raise OcrError("Brak nagłówka Operation-Location.")
    return op_location

def poll_read_result(op_location: str, key: str, timeout_s: int = 45, interval_s: float = 1.0) -> dict:
    """Polling wyniku OCR (Get Read Result)."""
    headers = {"Ocp-Apim-Subscription-Key": key}
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = requests.get(op_location, headers=headers)
        if resp.status_code != 200:
            raise OcrError(f"Polling failed: {resp.status_code} {resp.text}")
        data = resp.json()
        status = data.get("status")
        if status == "succeeded":
            return data
        if status == "failed":
            raise OcrError(f"OCR failed: {data}")
        time.sleep(interval_s)
    raise OcrError(f"Timeout po {timeout_s}s.")