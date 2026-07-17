# 🧠 Xử Lý Ảnh Số - Chuong 02

> **Môn học:** Xử lý ảnh
> **Chủ đề:** Toán tử điểm ảnh, lọc tuyến tính, lọc phi tuyến tính và đánh giá bộ lọc

---

## Mục tiêu bài tập

Trong `Chuong_02`, chúng ta thực hiện các phép biến đổi ảnh cơ bản dựa trên điểm ảnh và các bộ lọc ảnh, bao gồm:

1. Toán tử điểm ảnh
   - Thay đổi độ sáng
   - Thay đổi độ tương phản
   - Biến đổi âm bản
   - Cắt ngưỡng ảnh
2. Lọc tuyến tính
   - Lọc trung bình (average filter)
   - Lọc Gaussian
   - Làm sắc nét (sharpen)
3. Bài tập nâng cao
   - Phát hiện cạnh với Sobel và Prewitt
   - Thiết kế kernel tùy chỉnh
   - So sánh các loại lọc
   - Áp dụng lọc phi tuyến tính: median filter, bilateral filter

---

## Yêu cầu cài đặt

Sử dụng Python 3.8+ và cài đặt các thư viện sau:

```bash
pip install -r requirements.txt
```

---

## Hướng dẫn nội dung

### I. Toán tử điểm ảnh

- `Bai_01/Bai_01_01.py` — thay đổi độ sáng.
  - Kết quả lưu trong `Bai_01/output/`
- `Bai_01/Bai_01_02.py` — thay đổi độ tương phản.
  - Kết quả lưu trong `Bai_01/output/`
- `Bai_01/Bai_01_03.py` — biến đổi ảnh âm bản.
  - Kết quả lưu trong `Bai_01/output/`
- `Bai_01/Bai_01_04.py` — cắt ngưỡng ảnh.
  - Kết quả lưu trong `Bai_01/output/`

### II. Lọc tuyến tính

- `Bai_02/Bai_02_01.py` — lọc trung bình, Gaussian và làm sắc nét.
  - Kết quả lưu trong `Bai_02/output/`
- `Bai_02/Bai_02_02.py` — thiết kế và áp dụng kernel tùy chỉnh.
  - Kết quả lưu trong `Bai_02/output/`
- `Bai_02/Bai_02_03.py` — so sánh các bộ lọc khác nhau.
  - Kết quả lưu trong `Bai_02/output/`

### III. Bài tập nâng cao

- `Bai_03/Bai_03_01.py` — phát hiện cạnh Sobel.
  - Kết quả lưu trong `Bai_03/output/`
- `Bai_03/Bai_03_02.py` — phát hiện cạnh Prewitt.
  - Kết quả lưu trong `Bai_03/output/`
- `Bai_03/Bai_03_03.py` — lọc median.
  - Kết quả lưu trong `Bai_03/output/`
- `Bai_03/Bai_03_04.py` — lọc bilateral.
  - Kết quả lưu trong `Bai_03/output/`

---

## Cấu trúc thư mục

```
Chuong_02/
├── README.md
├── requirements.txt
├── images/
├── Bai_01/
│   ├── Bai_01_01.py
│   ├── Bai_01_02.py
│   ├── Bai_01_03.py
│   ├── Bai_01_04.py
│   └── output/
├── Bai_02/
│   ├── Bai_02_01.py
│   ├── Bai_02_02.py
│   ├── Bai_02_03.py
│   └── output/
├── Bai_03/
│   ├── Bai_03_01.py
│   ├── Bai_03_02.py
│   ├── Bai_03_03.py
│   ├── Bai_03_04.py
│   └── output/
```

> Gợi ý: mỗi bài trong `Bai_01`, `Bai_02`, `Bai_03` đều dùng thư mục `output/` riêng để lưu ảnh đã xử lý.

---

## Chạy bài tập

Ví dụ chạy từ thư mục `Chuong_02`:

```bash
python Bai_01/Bai_01_01.py
python Bai_02/Bai_02_01.py
python Bai_03/Bai_03_01.py
```

---

## Tham khảo

- OpenCV Python: https://docs.opencv.org/
- NumPy: https://numpy.org/doc/
- Tài liệu mô-đun `argparse` và `pathlib` trong Python
