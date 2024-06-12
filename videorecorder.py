import subprocess
import cv2


class VideoRecorder:

    def __init__(self, ):
        self.captures = []
        self.frame = None
        self.window = None
        self.cameras = {}
        self.out = []
        self.fps = None
        self.height = None
        self.width = None

        self.fourcc = cv2.VideoWriter_fourcc(*'MPEG')

    def videorecord_init(self, parrent: object, current_frame: object, cameras: dict, captures: list):
        self.cameras = cameras
        self.window = parrent
        self.frame = current_frame
        self.captures = captures

        for key, word in self.cameras.items():
            pass
        self.out.append(cv2.VideoWriter_fourcc(f'{self.file}', self.fourcc, 25, (768, 1024)))


    def video_save(self):
        for file in self.out:
            file.write(self.frame)

    def stop_record(self):
        self.out[0].release()
        subprocess.run(f"ffmpeg -i {self.video_file[0]} -i temp.wav -c copy {self.video_file[0]}")
