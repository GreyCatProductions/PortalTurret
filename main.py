import cv2
from picamera2 import Picamera2

cascade_path = "haarcascade_frontalface_default.xml"
classifier = cv2.CascadeClassifier(cascade_path)

if classifier.empty():
    raise RuntimeError("Cascade not loaded. Path: " + cascade_path)

picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (320, 240), "format": "RGB888"}
        )
)
picam2.start()

frame_id = 0
last_bboxes = []

DETECT_EVERY = 3         
DOWNSCALE = 1.0       

try:
    while True:
        rgb = picam2.capture_array()    
        frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        frame_id += 1
        if frame_id % DETECT_EVERY == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if DOWNSCALE != 1.0:
                small = cv2.resize(gray, (0, 0), fx=DOWNSCALE, fy=DOWNSCALE)
                b = classifier.detectMultiScale(
                    small,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(30, 30),
                )
                print("faces:", len(b))

                last_bboxes = [(int(x / DOWNSCALE), int(y / DOWNSCALE),
                                int(w / DOWNSCALE), int(h / DOWNSCALE)) for (x, y, w, h) in b]
            else:
                last_bboxes = classifier.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=(50, 50),
                )

        for (x, y, w, h) in last_bboxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imshow("Face detection (PiCam)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

finally:
    cv2.destroyAllWindows()
    picam2.stop()