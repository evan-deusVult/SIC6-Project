print("Loading Library...")
import cv2
import numpy as np
from ultralytics import YOLO
from ubidots import ApiClient
import threading

print("Script dimulai...")

class CameraStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret, self.frame = ret, frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def stop(self):
        self.stopped = True
        self.cap.release()

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def smooth_keypoints(kp, window_size=5):
    # Use the last 'window_size' frames for averaging the keypoints
    if len(kp) > window_size:
        kp = np.mean(kp[-window_size:], axis=0)
    return kp

def main():
    # Inisialisasi Ubidots
    UBIDOTS_TOKEN = "BBUS-DHs4IfDYDWUWHfHRTnZNSL9wuXiOR9"
    VARIABLE_ID = "67fa31aaa395d7300baf1cd8"
    api = ApiClient(token=UBIDOTS_TOKEN)
    pushup_var = api.get_variable(VARIABLE_ID)

    # Inisialisasi YOLOv8 dan kamera
    model = YOLO("yolov8n-pose.pt")
    esp32_link = "http://192.168.0.216:81/stream"

    print("Menghubungkan ke kamera...")
    cap = CameraStream(esp32_link).start()  # Ganti dengan URL ESP32 stream jika perlu

    if not cap.ret:
        print("Error: Kamera tidak bisa diakses!")
        exit()
    else:
        print("Kamera berhasil dibuka.")

    if not cap.isOpened():
        print("Error: Kamera tidak bisa diakses!")
        exit()
    else:
        print("Kamera berhasil dibuka.")

    pushup_count = 0
    is_down = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame for better processing (optional, for performance)
            frame_resized = cv2.resize(frame, (640, 480))

            results = model.predict(frame, conf=0.7, verbose=False)
            keypoints = results[0].keypoints

            if keypoints is not None and len(keypoints.xy) > 0:
                kp = keypoints.xy[0]

                try:
                    # Ensure that enough keypoints are detected (at least 6 keypoints)
                    if len(kp) >= 10:  # Shoulder, elbows, wrists are at least 10 keypoints
                        ids = [5, 6, 7, 8, 9, 10]  # Shoulder, elbow, wrist keypoints
                        points = [tuple(kp[i].tolist()) for i in ids]

                        # Check if all points are valid (positive coordinates)
                        if all(p[0] > 0 and p[1] > 0 for p in points):
                            l_shoulder, r_shoulder, l_elbow, r_elbow, l_wrist, r_wrist = points

                            angle_left = calculate_angle(l_shoulder, l_elbow, l_wrist)
                            angle_right = calculate_angle(r_shoulder, r_elbow, r_wrist)

                            shoulder_distance = np.linalg.norm(np.array(l_shoulder) - np.array(r_shoulder))
                            scale = np.clip((shoulder_distance - 120) / 80, 0, 1)
                            down_min = int(75 + (10 * scale))
                            down_max = int(105 - (10 * scale))

                            cv2.putText(frame, f"Range: {down_min}-{down_max}", (20, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

                            for (a, b, c) in [(l_shoulder, l_elbow, l_wrist), (r_shoulder, r_elbow, r_wrist)]:
                                cv2.line(frame, tuple(map(int, a)), tuple(map(int, b)), (255, 255, 0), 2)
                                cv2.line(frame, tuple(map(int, c)), tuple(map(int, b)), (255, 255, 0), 2)
                                for pt in [a, b, c]:
                                    cv2.circle(frame, tuple(map(int, pt)), 6, (0, 255, 0), -1)

                            cv2.putText(frame, f"L: {int(angle_left)}", tuple(map(int, l_elbow)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                            cv2.putText(frame, f"R: {int(angle_right)}", tuple(map(int, r_elbow)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                            if down_min <= angle_left <= down_max and down_min <= angle_right <= down_max:
                                if not is_down:
                                    is_down = True
                            elif angle_left > 150 and angle_right > 150:
                                if is_down:
                                    pushup_count += 1
                                    is_down = False

                                    try:
                                        pushup_var.save_value({'value': pushup_count})
                                        print(f"Data terkirim ke Ubidots: {pushup_count}")
                                    except Exception as e:
                                        print("Gagal mengirim ke Ubidots:", e)

                except Exception as e:
                    print("Tracking gagal:", e)

            cv2.putText(frame, f"Push-ups: {pushup_count}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.imshow("Push-Up Counter", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Tracking dihentikan manual.")

    finally:
        cap.stop()
        cv2.destroyAllWindows()
        print(f"Total push-up kamu: {pushup_count}")

if __name__ == "__main__":
    main()
