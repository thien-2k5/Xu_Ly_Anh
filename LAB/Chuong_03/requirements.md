# Requirements

## Mục tiêu bài thực hành

- So sánh và đánh giá Canny edge detection trong OpenCV và skimage.
- Quan sát ảnh hưởng của tham số ngưỡng thấp, ngưỡng cao và sigma.
- Kiểm tra hiệu quả Canny trên ảnh bị nhiễu, ảnh tương phản thấp và ảnh được tăng cường chi tiết.
- Kết hợp kết quả biên với phân đoạn Watershed và phát hiện hình dạng bằng Hough.

## Input

- Ảnh màu nguồn tại `../input/images.jpg`.
- Notebook sử dụng cùng một ảnh để thực hiện các bước tiền xử lý và hiển thị kết quả.

## Output

- Hình ảnh biên Canny với các tham số khác nhau.
- So sánh số điểm biên và thời gian thực thi.
- Kết quả Canny trên ảnh nhiễu, ảnh tương phản thấp và ảnh tăng chi tiết.
- Hình ảnh phân đoạn Watershed và kết quả Hough Lines / Circles.

## Yêu cầu chương trình

- Đọc và resize ảnh đầu vào.
- Chuyển đổi ảnh sang grayscale.
- Áp dụng OpenCV Canny và skimage Canny.
- So sánh các bộ tham số khác nhau.
- Tiền xử lý ảnh bằng Gaussian blur, cân bằng histogram, và sharpen.
- Sử dụng biên để hỗ trợ Watershed, Hough Lines, Hough Circles.
