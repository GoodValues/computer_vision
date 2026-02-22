def print_top_predictions(result: dict, top_k: int = 3, threshold: float = 0.0) -> None:
    preds = result.get("predictions", [])
    if not preds:
        print("Brak pola 'predictions' w odpowiedzi.")
        print(result)
        return

    preds_sorted = sorted(preds, key=lambda p: p.get("probability", 0), reverse=True)

    print("\n=== TOP PREDICTIONS ===")
    shown = 0
    for p in preds_sorted:
        prob = float(p.get("probability", 0))
        if prob < threshold:
            continue
        tag = p.get("tagName") or p.get("tagId") or "(unknown)"
        print(f"- {tag}: {prob:.3f}")
        shown += 1
        if shown >= top_k:
            break

    if shown == 0:
        print(f"(Nic powyżej progu threshold={threshold})")

def print_detection_boxes_if_present(result: dict, threshold: float = 0.5) -> None:
    preds = result.get("predictions", [])
    any_box = False

    for p in preds:
        bb = p.get("boundingBox")
        if not bb:
            continue
        prob = float(p.get("probability", 0))
        if prob < threshold:
            continue

        any_box = True
        tag = p.get("tagName") or "(unknown)"
        # boundingBox zwykle ma wartości względne 0..1
        left = bb.get("left")
        top = bb.get("top")
        width = bb.get("width")
        height = bb.get("height")
        print(f"- {tag}: {prob:.3f} | box: left={left} top={top} w={width} h={height}")

    if any_box:
        print("\n(Uwaga: boundingBox jest zwykle w skali względnej 0..1, a nie w pikselach.)")
