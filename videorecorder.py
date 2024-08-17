import cv2


class VideoRecorder:

    def __init__(self, cameras: dict, date: str):

        self.window = None
        self.cameras = {}
        self.files = []
        self.out = []
        self.fps = None
        self.height = None
        self.width = None

        self.cameras = cameras
        self.date = date

    def videorecord_init(self):
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        for key in self.cameras.keys():
            self.files.append(f"camera-{key}-{self.date}.avi")
        for count in range(len(self.files)):
            self.out.append(cv2.VideoWriter(self.files[count], fourcc, 25, (1024, 768)))

    def video_record(self, frames):
        count = 0
        for out in self.out:
            frame = cv2.resize(frames[count], (1024, 768), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            out.write(frame)
            count += 1

    def stop_record(self):
        for out in self.out:
            out.release()
