import os
from dotenv import load_dotenv
from cv_predict_client import predict_from_url, predict_from_file
from formatters import print_top_predictions, print_detection_boxes_if_present

def main():
    load_dotenv()

    prediction_url = os.getenv("PREDICTION_URL")
    prediction_key = os.getenv("PREDICTION_KEY")

    if not prediction_url or not prediction_key:
        raise ValueError("Brakuje PREDICTION_URL lub PREDICTION_KEY w pliku .env")

    file_path = os.getenv("PREDICTION_FILE_PATH")
    image_url = os.getenv("PREDICTION_IMAGE_URL")

    if file_path:
        result = predict_from_file(prediction_url, prediction_key, file_path)
    elif image_url:
        result = predict_from_url(prediction_url, prediction_key, image_url)
    else:
        raise ValueError("Ustaw FILE_PATH albo IMAGE_URL w .env")

    print("result: {}".format(result))
    # 1) klasyfikacja: top 3
    print_top_predictions(result, top_k=3, threshold=0.05)

    # 2) jeśli to detekcja: pokaż boxy (jeśli istnieją)
    print("\n=== DETECTION BOXES (if any) ===")
    print_detection_boxes_if_present(result, threshold=0.5)

if __name__ == "__main__":
    main()
