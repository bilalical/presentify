import cv2, threading, time, os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"  # stabler RTSP

class CameraReader:
    def __init__(self, camera_id, url):
        self.camera_id, self.url = camera_id, url
        self.frame, self.lock, self.running = None, threading.Lock(), True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            cap = cv2.VideoCapture(self.url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            while self.running and cap.isOpened():
                ok, f = cap.read()
                if not ok:
                    break                      # stream dropped, reconnect
                with self.lock:
                    self.frame = f             # keep only the newest frame
            cap.release()
            time.sleep(2)                      # wait, then auto-reconnect

    def read(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.running = False

cam = CameraReader("cam1", "http://192.168.18.12:8080/video")
direction = "IN"

while True:
    frame = cam.read()
    if frame is not None:
        cv2.putText(frame, f"MODE: {direction}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key != 255:
        print("key code:", key)

    if key in (ord("i"), ord("I")):
        direction = "IN"
        print("Mode changed to IN at", time.strftime("%H:%M:%S"))
    elif key in (ord("o"), ord("O")):
        direction = "OUT"
        print("Mode changed to OUT at", time.strftime("%H:%M:%S"))
    elif key in (ord("q"), ord("Q")):
        break

cam.stop()
cv2.destroyAllWindows()

