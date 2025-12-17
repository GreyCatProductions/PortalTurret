import cv2
import numpy as np

cap = cv2.VideoCapture(0) 
print("opened:", cap.isOpened())

for i in range(30):  
    ret, frame = cap.read()
    print(i, "ret:", ret, "type:", type(frame), "shape:", None if frame is None else frame.shape,
          "mean:", None if frame is None else frame.mean())

    if ret and frame is not None:
        cv2.imshow("test", frame)
        cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
