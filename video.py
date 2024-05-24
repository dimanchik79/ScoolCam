import numpy as np
import cv2


class VideoCapture:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('camera_0.avi', self.fourcc, 25.0, (640, 480))

    def video_save(self):
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            ret, frame = self.cap.read()
            self.out.write(frame)
            cv2.imshow("Camera-0", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        self.out.release()
        self.cap.release()
        cv2.destroyAllWindows()
