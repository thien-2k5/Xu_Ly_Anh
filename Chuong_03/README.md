# Chuong_03

Bài thực hành tập trung vào Canny edge detection và một số kỹ thuật xử lý ảnh liên quan. Nội dung chính so sánh OpenCV Canny với skimage Canny, điều chỉnh tham số, xử lý ảnh trước khi phát hiện biên và kết hợp biên với phân đoạn ảnh và phát hiện hình dạng.

## Mục tiêu chính

- Hiểu ảnh hưởng của ngưỡng Canny và sigma đến kết quả biên.
- So sánh OpenCV Canny và skimage Canny.
- Thử nghiệm ảnh nhiễu, ảnh tương phản thấp và ảnh nhiều chi tiết.
- Kết hợp biên với Watershed, Hough Lines và Hough Circles.

## Cấu trúc thư mục

- `input/` — chứa ảnh đầu vào (`images.jpg`).
- `src/` — chứa các notebook Jupyter thực hành:
  - `I.ipynb`
  - `II.ipynb`
  - `III.ipynb`
  - `IV.ipynb`

## File liên quan

- `requirements.md`
- `features.md`
- `tasks.md`

## Hướng dẫn chạy

1. Mở `Chuong_03/src/` và chạy lần lượt các notebook `I.ipynb`, `II.ipynb`, `III.ipynb`, `IV.ipynb`.
2. Đảm bảo ảnh đầu vào có tại `Chuong_03/input/images.jpg`.
3. Chạy từng cell hoặc toàn bộ notebook bằng kernel Python có `opencv-python`, `scikit-image`, `numpy`, `matplotlib`.
