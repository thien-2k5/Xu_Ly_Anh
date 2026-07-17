# Yêu cầu gửi AI

**Đề tài:**
Nhận diện khuôn mặt thời gian thực với FaceNet & MTCNN trên Webcam.

**Kết quả cần:**
- Một chương trình Python chạy được, mở webcam và nhận diện khuôn mặt theo thời gian
  thực, kèm file giải thích rõ ràng cách hoạt động của code.

**Quá trình muốn AI thực hiện:**
1. Dùng thư viện **OpenCV** để truy cập và thu thập hình ảnh từ webcam.
2. Tích hợp **MTCNN** để phát hiện khuôn mặt trong từng khung hình.
3. Dùng **FaceNet** để trích xuất đặc trưng (embedding) và so sánh khuôn mặt theo thời
   gian thực.
4. Áp dụng điều kiện so sánh:
   - `similarity > 0.7` → hiển thị **"Matched"**
   - `similarity < 0.7` → hiển thị **"Unknown"**
5. Viết code hoàn chỉnh kèm file giải thích để nộp bài, và hỗ trợ xử lý các lỗi phát
   sinh khi chạy thử trên máy thật (lỗi webcam không hiện cửa sổ, lỗi luôn báo
   "Unknown", lỗi tên hiển thị/khung nhận diện).
