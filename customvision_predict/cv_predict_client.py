# cv_predict_client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import os
import requests


@dataclass
class PredictionError(Exception):
    message: str
    status_code: Optional[int] = None
    response_text: Optional[str] = None

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"(HTTP {self.status_code})")
        if self.response_text:
            parts.append(f"Response: {self.response_text}")
        return " ".join(parts)


def _require(value: Optional[str], name: str) -> str:
    if value is None or str(value).strip() == "":
        raise PredictionError(f"Missing required value: {name}")
    return value.strip()


def _post(prediction_url: str, headers: Dict[str, str], *, data=None, json=None, timeout: int = 30) -> Dict[str, Any]:
    try:
        resp = requests.post(prediction_url, headers=headers, data=data, json=json, timeout=timeout)
    except requests.RequestException as e:
        raise PredictionError(f"Request failed: {e}") from e

    # Custom Vision returns JSON on success; on errors often JSON too, but not always.
    if not (200 <= resp.status_code < 300):
        raise PredictionError(
            "Prediction request failed",
            status_code=resp.status_code,
            response_text=resp.text,
        )

    try:
        return resp.json()
    except ValueError as e:
        raise PredictionError(
            "Prediction succeeded but response is not valid JSON",
            status_code=resp.status_code,
            response_text=resp.text,
        ) from e


def predict_from_file(prediction_url: str, prediction_key: str, file_path: str, *, timeout: int = 30) -> Dict[str, Any]:
    """
    Use Custom Vision Prediction endpoint that ends with: .../image
    Sends raw bytes with Content-Type: application/octet-stream
    """
    prediction_url = _require(prediction_url, "prediction_url")
    prediction_key = _require(prediction_key, "prediction_key")
    file_path = _require(file_path, "file_path")

    # Helpful guard: endpoint mismatch is a very common source of HTTP 415.
    if prediction_url.rstrip("/").endswith("/url"):
        raise PredictionError(
            "PREDICTION_URL ends with '/url' but you're calling predict_from_file(). "
            "Use the '/image' endpoint or call predict_from_url()."
        )

    if not os.path.isfile(file_path):
        raise PredictionError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        data = f.read()

    headers = {
        "Prediction-Key": prediction_key,
        "Content-Type": "application/octet-stream",
    }

    return _post(prediction_url, headers, data=data, timeout=timeout)


def predict_from_url(prediction_url: str, prediction_key: str, image_url: str, *, timeout: int = 30) -> Dict[str, Any]:
    """
    Use Custom Vision Prediction endpoint that ends with: .../url
    Sends JSON body: {"Url": "<image_url>"} with Content-Type: application/json
    """
    prediction_url = _require(prediction_url, "prediction_url")
    prediction_key = _require(prediction_key, "prediction_key")
    image_url = _require(image_url, "image_url")

    # Helpful guard: endpoint mismatch is a very common source of HTTP 415.
    if prediction_url.rstrip("/").endswith("/image"):
        raise PredictionError(
            "PREDICTION_URL ends with '/image' but you're calling predict_from_url(). "
            "Use the '/url' endpoint or call predict_from_file()."
        )

    headers = {
        "Prediction-Key": prediction_key,
        "Content-Type": "application/json",
    }
    payload = {"Url": image_url}

    return _post(prediction_url, headers, json=payload, timeout=timeout)
