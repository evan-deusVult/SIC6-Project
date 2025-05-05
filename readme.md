# SIC6-Project UNI437-Liburan Gabut

Project ini dibuat oleh kelompok UNI437-Liburan Gabut. Project ini bertujuan untuk membantu orang yang ingin memulai latihan olahraga. 

- [Deskripsi](#deskripsi)
- [Fitur](#fitur)
- [Cara Kerja](#cara-kerja)
- [Instalasi](#instalasi)

## Deskripsi

SMART-FIT: Smart Motion Analysis and Recognition Tracker For Intelligent Training adalah solusi IoT & Computer Vision untuk Olahraga Efisien dan Akurat dengan menggunakan *Computer Vision*, kami berhasil nge-*tracking* bagian tubuh untuk keperluan koreksi *form* dari suatu olahraga rumahan. Program ini menggunakan model *YOLOv8 Pose* untuk *tracking* gerakan tubuh secara akurat dan mengirim data penghitungan ke platform *Ubidots* untuk *monitoring real-time*.

## Fitur
- **Push-up**
    * Menghitung sudut siku saat posisi push-up menggunakan *pose estimation*.
    * Klasifikasi posisi push-up (bawah/atas) berdasarkan sudut yang terdeteksi.
    * Batas sudut bawah (75°-105°) dan atas (>150°) disesuaikan secara dinamis dengan jarak bahu pengguna terhadap kamera.
    * Penghitungan otomatis dan pengiriman data ke *Ubidots* untuk penyimpanan dan analisis.
- **Visualisasi Real-Time**
    * Menampilkan garis dan titik pada sendi (bahu, siku, pergelangan tangan).
    * Menampilkan sudut siku secara live di layar.
    * *Counter push-up* yang terus diperbarui.
## Cara Kerja
1. **Tracking Pose**
    * Model YOLOv8 Pose mendeteksi keypoint tubuh (bahu, siku, pergelangan tangan).
    * Sudut siku dihitung menggunakan rumus dot product untuk menentukan posisi push-up.
2. **Klasifikasi Gerakan**
    * Jika sudut siku berada dalam rentang tertentu (75°-105°), sistem menganggap posisi push-up bawah.
    * Jika sudut melebihi 150°, sistem menganggap posisi push-up atas dan menambah counter.
3. **Integrasi Ubidots**
    * Data counter push-up dikirim ke Ubidots via API untuk monitoring real-time.
## Instalasi
1. Buka terminal (Linux/macOS) atau Command Prompt/PowerShell (Windows).
2. Aktifkan *virtual environment* (**disarankan**).
3. Jalankan perintah berikut untuk instalasi dependensi:
   ```bash
   pip install opencv-python numpy ultralytics ubidots
   ```
4. Untuk menjalankan program:
   ```bash
   python scriptESP32_YOLO_main.py
   ```
5. Arahkan kamera (ESP32 atau webcam) ke pengguna dan mulai push-up