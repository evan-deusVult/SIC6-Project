import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from ubidots import ApiClient

# Fungsi bantu
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def load_movenet_model():
    model = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
    return model.signatures['serving_default']

def preprocess_frame(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = tf.image.resize_with_pad(tf.expand_dims(img, axis=0), 192, 192)
    return tf.cast(img, dtype=tf.int32)

def draw_keypoints(frame, keypoints, threshold=0.3):
    h, w, _ = frame.shape
    for kp in keypoints:
        y, x, c = kp
        if c > threshold:
            cx, cy = int(x * w), int(y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

# Main code
def main():
    # Ubidots setup
    UBIDOTS_TOKEN = "BBUS-DHs4IfDYDWUWHfHRTnZNSL9wuXiOR9"
    VARIABLE_ID = "67fa31aaa395d7300baf1cd8"
    api = ApiClient(token=UBIDOTS_TOKEN)
    pushup_var = api.get_variable(VARIABLE_ID)

    # Model & Kamera
    movenet = load_movenet_model()
    cap = cv2.VideoCapture(0)

    pushup_count = 0
    is_down = False

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            input_tensor = preprocess_frame(frame)
            outputs = movenet(input_tensor)
            keypoints = outputs['output_0'].numpy()[0, 0, :, :]  # (17, 3)

            h, w, _ = frame.shape
            # Ambil keypoints penting
            l_shoulder = (keypoints[5][1] * w, keypoints[5][0] * h)
            r_shoulder = (keypoints[6][1] * w, keypoints[6][0] * h)
            l_elbow = (keypoints[7][1] * w, keypoints[7][0] * h)
            r_elbow = (keypoints[8][1] * w, keypoints[8][0] * h)
            l_wrist = (keypoints[9][1] * w, keypoints[9][0] * h)
            r_wrist = (keypoints[10][1] * w, keypoints[10][0] * h)

            # Hitung sudut
            angle_left = calculate_angle(l_shoulder, l_elbow, l_wrist)
            angle_right = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # Jarak antar bahu
            shoulder_distance = np.linalg.norm(np.array(l_shoulder) - np.array(r_shoulder))
            scale = np.clip((shoulder_distance - 120) / 80, 0, 1)
            down_min = int(75 + (10 * scale))
            down_max = int(105 - (10 * scale))

            # Deteksi posisi push-up
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

            # Gambar keypoints
            draw_keypoints(frame, keypoints)

            # Overlay info
            cv2.putText(frame, f"Push-ups: {pushup_count}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(frame, f"Range: {down_min}-{down_max}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            cv2.imshow("Push-Up Counter", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Dihentikan manual.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Total push-up kamu: {pushup_count}")

if __name__ == "__main__":
    main()
