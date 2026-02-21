import os
from dotenv import load_dotenv
from ocr_client import start_read, poll_read_result
from text_writer import save_text

def extract_text_from_read_result(result: dict) -> str:
    """
    Składa tekst z odpowiedzi Read API.
    Zwykle: analyzeResult -> readResults -> lines -> text
    """
    analyze = result.get("analyzeResult", {})
    read_results = analyze.get("readResults", [])
    lines_out = []
    for page in read_results:


        for line in page.get("lines", []):
            lines_out.append(line.get("text", ""))
    return "\n".join(lines_out).strip()

def main():
    load_dotenv()
    endpoint = os.getenv("VISION_ENDPOINT")
    key = os.getenv("VISION_KEY")
    if not endpoint or not key:
        raise ValueError("Brakuje VISION_ENDPOINT lub VISION_KEY w pliku .env")
    # Obraz musi być dostępny publicznie, jeśli używasz URL.
    # Na zajęciach możesz podać 2-3 linki testowe (paragon, etykieta, dokument).
    image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/printed_text.jpg"
    op_location = start_read(endpoint, key, image_url)
    print("op location: ", op_location)
    result = poll_read_result(op_location, key, timeout_s=45, interval_s=1.0)
    text = extract_text_from_read_result(result)
    if not text:
        text = "(Brak rozpoznanego tekstu.)"
    save_text(text, "output.txt")
    print(" Zapisano tekst do output.txt")
    print("\n--- PODGLĄD ---\n")
    print(text[:500]) # pierwsze 500 znaków

if __name__ == "__main__":
    main()