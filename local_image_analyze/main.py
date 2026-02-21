import os
from dotenv import load_dotenv
from ocr_client import start_read_stream, start_read_url, poll_read_result
from text_writer import save_text


def extract_text_from_read_result(result: dict) -> str:
    analyze = result.get("analyzeResult", {})
    read_results = analyze.get("readResults", [])
    lines_out = []
    for page in read_results:
        for line in page.get("lines", []):
            lines_out.append(line.get("text", ""))
    return "\n".join(lines_out).strip()


def guess_content_type(path: str) -> str:
    ext = os.path.splitext(path.lower())[1]
    if ext == ".pdf":
        return "application/pdf"
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".bmp":
        return "image/bmp"
    if ext in [".tif", ".tiff"]:
        return "image/tiff"
    # fallback (często działa dla obrazów, ale lepiej dać właściwy typ)
    return "application/octet-stream"


def main():
    load_dotenv()
    endpoint = os.getenv("VISION_ENDPOINT")
    key = os.getenv("VISION_KEY")

    if not endpoint or not key:
        raise ValueError("Brakuje VISION_ENDPOINT lub VISION_KEY w pliku .env")

    # Ustaw jedno z nich w pliku .env:
    file_path = os.getenv("FILE_PATH")  # np. samples/receipt.jpg
    image_url = os.getenv("IMAGE_URL")  # np. publiczny link

    if file_path:
        ct = guess_content_type(file_path)
        op_location = start_read_stream(endpoint, key, file_path, ct)
    elif image_url:
        op_location = start_read_url(endpoint, key, image_url)
    else:
        raise ValueError("Ustaw FILE_PATH albo IMAGE_URL (np. w .env).")

    result = poll_read_result(op_location, key, timeout_s=60, interval_s=1.0)
    text = extract_text_from_read_result(result) or "(Brak rozpoznanego tekstu.)"

    save_text(text, "output.txt")

    print("✓ Zapisano tekst do output.txt")
    print("\n--- PODGLĄD ---\n")
    print(text[:600])


if __name__ == "__main__":
    main()