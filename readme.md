# SIC6-Project UNI437-Liburan Gabut

Project ini dibuat oleh kelompok UNI437-Liburan Gabut. Project ini bertujuan untuk membantu orang yang ingin memulai latihan olahraga. 

- [Deskripsi](#deskripsi)
- [Fitur](#fitur)

## Deskripsi

Dengan menggunakan *Computer Vision*, kami berhasil nge-*tracking* bagian tubuh untuk keperluan koreksi *form* dari suatu olahraga rumahan. Program ini menggunkan model *YOLO* untuk *tracing*/*tracking* gerakan tubuh. 

## Fitur
- **Push-up**
Kami menghitung sudut dari siku saat posisi push-up. Lalu hasil sudut akan masuk ke suatu klasifikasi berdasarkan apakah sedut tersebut posisi Push-Up bawah atau atas.
Sebagai contoh, kami menentukan 150° sebagai batas atas dan memberikan variasi batas bawah berdasarkan *range* pengguna terhadap kamera.