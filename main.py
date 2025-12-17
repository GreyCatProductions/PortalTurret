import cv2

cascade_path = "haarcascade_frontalface_default.xml"
classifier = cv2.CascadeClassifier(cascade_path)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 5)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

frame_id = 0
last_bboxes = []

while True:
    for _ in range(2):
        cap.grab()
    ret, frame = cap.retrieve()
    if not ret:
        break

    frame_id += 1

    if frame_id % 4 == 0:  
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray) 
        last_bboxes = classifier.detectMultiScale(
            gray,
            scaleFactor=1.2,      
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

    for (x, y, w, h) in last_bboxes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    cv2.imshow("Face detection", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
