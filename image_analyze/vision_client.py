import requests


def analyze_image(endpoint: str, key: str, image_url: str) -> dict:
    url = endpoint + "vision/v3.2/analyze?visualFeatures=Description,Objects,Tags"


    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    data = {"url": image_url}
    response = requests.post(url, headers=headers, json=data)
    # podstawa dobrych praktyk: fail fast
    response.raise_for_status()
    return response.json()
