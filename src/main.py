import cv2
import time
from pycoral.adapters import common, detect
from pycoral.utils.edgetpu import make_interpreter

# zmienne wejściowe
MODEL     = "model/mobilenet_v2_1.0_224_quant_edgetpu.tflite"
LABELS    = "model/coco_labels.txt"
CAMERA    = 0
THRESHOLD = 0.4

# wgranie labeli
labels = {}
with open(LABELS) as f:
    for line in f:
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            labels[int(parts[0])] = parts[1]

# tworzenie sieci na corala 
interpreter = make_interpreter(MODEL)
interpreter.allocate_tensors()
iw, ih = common.input_size(interpreter)

# konfiguracja kamery
cap = cv2.VideoCapture(CAMERA)
fps, t0 = 0.0, time.perf_counter()

while True:
    # pobranie klatki i tego czy została dana poprawnie
    ret, frame = cap.read()
    if not ret:
        continue

    resized_frame = cv2.resize(frame, (iw, ih)); 
    # zamiana z BGR na RGB
    rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    common.set_input(interpreter, rgb) # wrzucenie do corala

    t1 = time.perf_counter()
    interpreter.invoke()
    ms = (time.perf_counter() - t1) * 1000
    # ile zajęło wykonanie modelu

    # liczy współczynniki skalowania pomiędzy wielkością obrazu w modelu, a tymi jakie są irl
    sx, sy = frame.shape[1] / iw, frame.shape[0] / ih
    objs = detect.get_objects(interpreter, score_threshold=THRESHOLD,
                              image_scale=(sx, sy))

    # rysowanie bounding boxów
    for o in objs:
        b = o.bbox
        cv2.rectangle(frame, (b.xmin, b.ymin), (b.xmax, b.ymax), (0, 200, 255), 2)
        cv2.putText(frame, f"{labels.get(o.id, o.id)}  {o.score:.0%}", (b.xmin, b.ymin - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1, cv2.LINE_AA)

    # ile fpsów jest kamera
    fps = 0.9 * fps + 0.1 * (1 / max(time.perf_counter() - t0, 1e-9))
    t0 = time.perf_counter()
    cv2.putText(frame, f"FPS: {fps:.1f}  inf: {ms:.1f}ms",
                (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 180), 1)

    # otwarcie okna
    cv2.imshow("Coral Detector", frame)
    if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
        break

cap.release()
cv2.destroyAllWindows()