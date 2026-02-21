import os
from dotenv import load_dotenv
from vision_client import analyze_image

def print_summary(result: dict) -> None:
    print("\n=== DESCRIPTION ===")
    captions = result.get("description", {}).get("captions", [])
    if captions:
        for cap in captions:
            print(f"- {cap['text']} (confidence: {cap['confidence']:.2f})")
    else:
        print("- brak")

    print("\n=== TAGS ===")
    for tag in result.get("tags", []):
        print(f"- {tag['name']} (confidence: {tag['confidence']:.2f})")

    print("\n=== OBJECTS ===")
    for obj in result.get("objects", []):
        rect = obj.get("rectangle", {})
        print(
            f"- {obj['object']} (confidence: {obj['confidence']:.2f}), "
            f"bbox: x={rect.get('x')} y={rect.get('y')} w={rect.get('w')} h={rect.get('h')}"
        )

    print(result)

def main():
    load_dotenv()
    endpoint = os.getenv("VISION_ENDPOINT")
    key = os.getenv("VISION_KEY")

    if not endpoint or not key:
        raise ValueError("Brakuje VISION_ENDPOINT lub VISION_KEY w pliku .env")

    image_url = "https://learn.microsoft.com/azure/ai-services/computer-vision/media/quickstarts/presentation.png"
    result = analyze_image(endpoint, key, image_url)
    print_summary(result)

if __name__ == "__main__":
    main()