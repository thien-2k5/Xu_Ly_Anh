# Features

- Đọc ảnh từ `input/images.jpg` và resize về kích thước chuẩn.
- Chuyển ảnh sang grayscale.
- Áp dụng OpenCV Canny edge detection với các ngưỡng khác nhau.
- Áp dụng skimage Canny với các giá trị sigma khác nhau.
- So sánh số điểm biên và thời gian thực hiện giữa các cấu hình.
- Vary tham số Canny để quan sát ảnh hưởng của ngưỡng thấp, ngưỡng cao và sigma.
- Sinh ảnh nhiễu Gaussian và so sánh Canny trực tiếp với Canny sau blur.
- Tạo ảnh tương phản thấp và áp dụng cân bằng histogram trước khi Canny.
- Tăng cường chi tiết bằng sharpening và so sánh kết quả Canny.
- Sử dụng Watershed dựa trên biên Canny để phân đoạn ảnh.
- Phát hiện đường thẳng và đường tròn bằng Hough transform từ biên.
