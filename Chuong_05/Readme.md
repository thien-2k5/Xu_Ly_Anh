# Giải thích bài tập: Nhận diện khuôn mặt thời gian thực với MTCNN & FaceNet

## 1. Tổng quan pipeline

```
Webcam (OpenCV)
     │  đọc từng khung hình (frame)
     ▼
MTCNN  ──► phát hiện khuôn mặt, trả về toạ độ (box) + ảnh mặt đã cắt & căn chỉnh (160x160)
     │
     ▼
FaceNet (InceptionResnetV1) ──► trích xuất vector đặc trưng (embedding) 512 chiều
     │
     ▼
So sánh cosine similarity với các embedding đã lưu (known_faces)
     │
     ├─ similarity > 0.7  →  hiển thị "Matched"
     └─ similarity ≤ 0.7  →  hiển thị "Unknown"
```

## 2. Vì sao dùng MTCNN + FaceNet?

- **MTCNN (Multi-task Cascaded Convolutional Networks)**: một mạng 3 tầng (P-Net, R-Net, O-Net)
  chuyên phát hiện khuôn mặt và các điểm mốc (mắt, mũi, miệng...). Nhờ các điểm mốc này,
  khuôn mặt được "căn chỉnh" (align) về đúng góc trước khi đưa vào bước trích xuất đặc trưng,
  giúp tăng độ chính xác nhận diện.
- **FaceNet**: một mạng CNN được huấn luyện để ánh xạ mỗi khuôn mặt thành một vector số
  (embedding) sao cho hai ảnh của cùng một người sẽ có vector gần nhau, còn hai người khác nhau
  sẽ có vector cách xa nhau. Ở đây dùng kiến trúc **InceptionResnetV1** được huấn luyện sẵn trên
  bộ dữ liệu **VGGFace2** (tham số `pretrained='vggface2'`).

Thư viện `facenet-pytorch` cung cấp sẵn cả hai mô hình này nên không cần tự huấn luyện lại.

## 3. Giải thích từng phần code (`realtime_face_recognition.py`)

### 3.1. Khởi tạo mô hình
```python
mtcnn = MTCNN(keep_all=True, device=DEVICE)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)
```
- `keep_all=True`: cho phép MTCNN phát hiện **nhiều khuôn mặt** trong cùng một khung hình,
  thay vì chỉ lấy 1 mặt có độ tin cậy cao nhất.
- `.eval()`: chuyển FaceNet sang chế độ suy luận (không cập nhật gradient), giúp chạy nhanh
  và ổn định hơn.

### 3.2. Nạp danh sách khuôn mặt đã biết — `load_known_faces()`
- Đọc từng ảnh trong thư mục `known_faces/`.
- Dùng `mtcnn(img)` để vừa phát hiện vừa cắt/căn chỉnh khuôn mặt về kích thước chuẩn 160x160.
- Đưa ảnh mặt đã cắt qua FaceNet để lấy **embedding** đại diện cho người đó.
- Lưu vào dict: `{"an": embedding_an, "binh": embedding_binh, ...}`.
- Tên file ảnh (bỏ phần đuôi) được dùng làm **tên hiển thị** khi nhận diện đúng người.

### 3.3. Hàm tính độ tương đồng — `cosine_similarity()`
```python
def cosine_similarity(a, b):
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_norm, b_norm))
```
- Cosine similarity đo góc giữa 2 vector, giá trị nằm trong khoảng **[-1, 1]**.
- Giá trị càng gần **1** nghĩa là hai khuôn mặt càng giống nhau.
- Cộng thêm `1e-10` để tránh chia cho 0 khi vector có độ dài bằng 0.

### 3.4. Vòng lặp webcam chính — `main()`
1. `cap.read()`: đọc từng khung hình từ webcam.
2. Đổi màu **BGR → RGB** vì OpenCV mặc định đọc ảnh theo BGR còn MTCNN/FaceNet cần RGB.
3. `mtcnn.detect(pil_img)`: trả về toạ độ các khung khuôn mặt (`boxes`) và độ tin cậy (`probs`)
   — dùng để **vẽ khung** lên khung hình.
4. `mtcnn(pil_img)`: trả về các ảnh khuôn mặt đã cắt & chuẩn hoá sẵn — dùng để **trích xuất
   embedding**.
5. Với mỗi khuôn mặt phát hiện được:
   - Bỏ qua nếu độ tin cậy phát hiện (`probs[i]`) thấp hơn `0.90` (tránh nhận nhầm vật thể
     không phải khuôn mặt).
   - Tính embedding của khuôn mặt hiện tại.
   - So sánh với **từng** embedding trong `known_faces`, giữ lại điểm số cao nhất
     (`best_score`, `best_name`).
   - **Áp dụng điều kiện của đề bài**:
     ```python
     if best_score > SIMILARITY_THRESHOLD:   # > 0.7
         label = f"Matched: {best_name}"
     else:
         label = "Unknown"
     ```
6. Vẽ khung chữ nhật (xanh lá nếu Matched, đỏ nếu Unknown) và nhãn lên khung hình, rồi
   hiển thị bằng `cv2.imshow`.
7. Nhấn phím **`q`** để thoát vòng lặp và đóng webcam.

## 4. Cách cài đặt và chạy

```bash
# 1. Cài thư viện cần thiết
pip install -r requirements.txt

# 2. Tạo thư mục known_faces/ và bỏ vào đó ảnh chân dung
#    Ví dụ: known_faces/an.jpg, known_faces/binh.png
#    Lưu ý: mỗi ảnh nên rõ mặt, chính diện, chỉ 1 người trong ảnh mẫu.

# 3. Chạy chương trình
python realtime_face_recognition.py

# 4. Đưa mặt vào trước webcam để xem kết quả nhận diện
#    Nhấn "q" để thoát.
```

## 5. Về ngưỡng (threshold) 0.7

- Ngưỡng `0.7` là một lựa chọn phổ biến khi dùng **cosine similarity** với embedding của
  FaceNet, nhưng **không phải là con số cố định tuyệt đối** — nó phụ thuộc vào chất lượng
  ảnh mẫu, điều kiện ánh sáng, góc chụp...
- Nếu hệ thống báo "Unknown" quá nhiều dù đúng là người quen → có thể **giảm** ngưỡng
  (ví dụ 0.6).
- Nếu hệ thống hay nhận nhầm người lạ thành người quen → có thể **tăng** ngưỡng
  (ví dụ 0.8).
- Có thể chỉnh trực tiếp trong code: biến `SIMILARITY_THRESHOLD` ở đầu file.

## 6. Một số lưu ý mở rộng (nếu muốn nâng cấp bài tập)

- **Nhiều ảnh mẫu / người**: có thể lưu nhiều ảnh cho cùng 1 người và lấy **trung bình
  embedding** để tăng độ ổn định.
- **Tăng tốc độ xử lý**: nếu máy có GPU (CUDA), code sẽ tự động dùng GPU nhờ dòng
  `torch.device('cuda' if torch.cuda.is_available() else 'cpu')`.
- **Ghi log nhận diện**: có thể lưu lại thời gian + tên người được nhận diện vào file
  CSV để làm chức năng điểm danh (attendance system).
- **Giao diện đẹp hơn**: có thể thay `cv2.imshow` bằng giao diện Streamlit/Flask để hiển
  thị qua trình duyệt.

## 7. Cấu trúc thư mục đề xuất

```
project/
├── realtime_face_recognition.py
├── requirements.txt
├── GIAI_THICH.md
└── known_faces/
    ├── Nhat.jpg
    ├── Thien.png
    └── ...
```
