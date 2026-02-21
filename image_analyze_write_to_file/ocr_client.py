import time
import requests


class OcrError(Exception):
    """Niestandardowy wyjątek dla błędów operacji OCR."""
    pass


def start_read(endpoint: str, key: str, image_url: str) -> str:
    """
    Startuje OCR (Read API). Zwraca URL do pobrania wyniku z nagłówka Operation-Location.
    """
    url = endpoint.rstrip("/") + "/vision/v3.2/read/analyze"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    payload = {"url": image_url}

    resp = requests.post(url, headers=headers, json=payload)

    # Read API zwykle zwraca 202 Accepted
    if resp.status_code != 202:
        raise OcrError(f"Start OCR failed: {resp.status_code} {resp.text}")

    op_location = resp.headers.get("Operation-Location")
    if not op_location:
        raise OcrError("Brak nagłówka Operation-Location w odpowiedzi.")

    return op_location


def poll_read_result(op_location: str, key: str, timeout_s: int = 30, interval_s: float = 1.0) -> dict:
    """
    Odpytuje Operation-Location aż OCR się zakończy lub minie timeout.
    """
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

        # Status: "notStarted" lub "running" - czekamy dalej
        time.sleep(interval_s)

    raise OcrError(f"Timeout po {timeout_s}s. Spróbuj zwiększyć timeout.")