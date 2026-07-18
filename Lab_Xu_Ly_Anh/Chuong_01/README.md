# 🖼️ Xử Lý Ảnh Cơ Bản với OpenCV và Pillow

> **Môn học:** Xử lý ảnh  
> **Sinh viên:** Trần Quốc Thiện  
> **MSSV:** 051205012409

---

## 📋 Mục Lục

- [Giới thiệu](#giới-thiệu)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Các bài tập](#các-bài-tập)
  - [Bài 1: Kiểm tra cài đặt](#bài-1-kiểm-tra-cài-đặt)
  - [Bài 2: Đọc, hiển thị và lưu ảnh](#bài-2-đọc-hiển-thị-và-lưu-ảnh)
  - [Bài 3: Chuyển đổi không gian màu](#bài-3-chuyển-đổi-không-gian-màu)
  - [Bài 4: Cắt xén và thay đổi kích thước](#bài-4-cắt-xén-và-thay-đổi-kích-thước)
  - [Bài 5: Vẽ hình và thêm văn bản](#bài-5-vẽ-hình-và-thêm-văn-bản)
- [Tham khảo](#tham-khảo)

---

## Giới Thiệu

Project này thực hành các kỹ thuật **xử lý ảnh cơ bản** sử dụng hai thư viện phổ biến nhất trong Python:

| Thư viện | Mô tả | Ưu điểm |
|----------|--------|---------|
| **OpenCV** | Thư viện Computer Vision mạnh mẽ nhất | Tốc độ cao, hỗ trợ video, nhiều thuật toán |
| **Pillow** | Thư viện xử lý ảnh Python thuần | Dễ sử dụng, hỗ trợ nhiều định dạng ảnh |
| **NumPy** | Thư viện tính toán mảng | Nền tảng cho xử lý pixel dạng mảng |

---

## Yêu Cầu Hệ Thống

- **Python:** >= 3.8
- **Hệ điều hành:** Windows / macOS / Linux
- **RAM:** >= 4 GB (khuyến nghị)

---

## Cài Đặt

### 1. Clone hoặc tải project

```bash
cd /path/to/project
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Hoặc cài đặt từng thư viện:

```bash
pip install opencv-python Pillow numpy
```

### 3. Kiểm tra cài đặt

```bash
python bai1_install_check.py
```

Kết quả mong đợi:
```
==================================================
KIỂM TRA CÀI ĐẶT THƯ VIỆN XỬ LÝ ẢNH
==================================================

✅ OpenCV version: 4.13.0
✅ NumPy version: 2.x.x
✅ Pillow version: 12.x.x

🎉 Tất cả thư viện đã được cài đặt thành công!
```

---

## Cấu Trúc Thư Mục

```
OpenCV-Pillow-Demo/
│
├── README.md                    # File hướng dẫn (file này)
├── requirements.txt             # Danh sách thư viện cần cài
│
├── images/                      # Thư mục chứa ảnh đầu vào
│   └── sample_image.png         # Ảnh mẫu
│
├── output/                      # Thư mục chứa ảnh kết quả (tự tạo)
│   ├── output_opencv.jpg
│   ├── gray_opencv.jpg
│   ├── hsv_h_channel.jpg
│   ├── crop_center_opencv.jpg
│   ├── drawing_opencv_canvas.jpg
│   └── ...
│
├── bai1_install_check.py        # Bài 1: Kiểm tra cài đặt
├── bai2_read_display_save.py    # Bài 2: Đọc, hiển thị, lưu ảnh
├── bai3_color_spaces.py         # Bài 3: Chuyển đổi không gian màu
├── bai4_crop_resize.py          # Bài 4: Cắt xén và thay đổi kích thước
└── bai5_drawing_text.py         # Bài 5: Vẽ hình và thêm văn bản
```

---

## Các Bài Tập

### Bài 1: Kiểm Tra Cài Đặt

**File:** `bai1_install_check.py`

```bash
python bai1_install_check.py
```

**Nội dung:**
- Kiểm tra phiên bản OpenCV, Pillow, NumPy
- Xác nhận tất cả thư viện hoạt động bình thường

---

### Bài 2: Đọc, Hiển Thị và Lưu Ảnh

**File:** `bai2_read_display_save.py`

```bash
python bai2_read_display_save.py
```

**Nội dung:**

| Chức năng | OpenCV | Pillow |
|-----------|--------|--------|
| Đọc ảnh | `cv2.imread()` | `Image.open()` |
| Hiển thị ảnh | `cv2.imshow()` | `img.show()` |
| Lưu ảnh | `cv2.imwrite()` | `img.save()` |

**Các định dạng đầu ra:**
- `output_opencv.jpg` — PNG → JPG (OpenCV)
- `output_opencv.bmp` — PNG → BMP (OpenCV)
- `output_pillow.jpg` — PNG → JPG (Pillow)
- `output_pillow.bmp` — PNG → BMP (Pillow)
- `output_pillow.tiff` — PNG → TIFF (Pillow)

**Lưu ý:**
- OpenCV đọc ảnh ở định dạng **BGR** (Blue-Green-Red), không phải RGB
- Pillow đọc ảnh ở định dạng **RGB** (Red-Green-Blue)
- Khi chuyển đổi giữa hai thư viện, cần đổi thứ tự kênh màu

---

### Bài 3: Chuyển Đổi Không Gian Màu

**File:** `bai3_color_spaces.py`

```bash
python bai3_color_spaces.py
```

**Nội dung:**

#### 🔲 RGB → Grayscale (Ảnh xám)
```python
# OpenCV
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

# Pillow
img_gray = img.convert("L")
```
- Chuyển ảnh 3 kênh thành 1 kênh
- Công thức: `Gray = 0.299×R + 0.587×G + 0.114×B`

#### 🌈 RGB → HSV
```python
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
```
- **H (Hue):** Sắc độ màu (0–180 trong OpenCV)
- **S (Saturation):** Độ bão hòa (0–255)
- **V (Value):** Độ sáng (0–255)
- Ứng dụng: Phát hiện màu sắc, theo dõi đối tượng theo màu

#### 🎨 RGB → LAB (CIE L\*a\*b\*)
```python
img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
```
- **L:** Lightness — Độ sáng (0–100)
- **a:** Trục Green(−) → Red(+)
- **b:** Trục Blue(−) → Yellow(+)
- Ứng dụng: Cân bằng màu, phân đoạn ảnh, so sánh màu theo cảm nhận mắt người

**Ảnh đầu ra:**
- `gray_opencv.jpg`, `gray_pillow.jpg` — Ảnh xám
- `hsv_h_channel.jpg`, `hsv_s_channel.jpg`, `hsv_v_channel.jpg` — Các kênh HSV
- `lab_l_channel.jpg`, `lab_a_channel.jpg`, `lab_b_channel.jpg` — Các kênh LAB
- `color_spaces_comparison.jpg` — Ảnh so sánh tổng hợp

---

### Bài 4: Cắt Xén và Thay Đổi Kích Thước

**File:** `bai4_crop_resize.py`

```bash
python bai4_crop_resize.py
```

**Nội dung:**

#### ✂️ Cắt xén (Crop)
```python
# OpenCV — sử dụng numpy slicing [y1:y2, x1:x2]
img_crop = img[y1:y2, x1:x2]

# Pillow — sử dụng crop((left, top, right, bottom))
img_crop = img.crop((x1, y1, x2, y2))
```

#### 📏 Thay đổi kích thước theo tỷ lệ (Scale)
```python
# OpenCV
new_w, new_h = int(w * 0.5), int(h * 0.5)
img_scaled = cv2.resize(img, (new_w, new_h))

# Pillow
img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
```

#### 📐 Thay đổi kích thước cố định
```python
# OpenCV
img_fixed = cv2.resize(img, (640, 480))

# Pillow
img_fixed = img.resize((640, 480), Image.Resampling.LANCZOS)
```

#### 🔍 So sánh phương pháp nội suy (Interpolation)

| Phương pháp | Hàm OpenCV | Đặc điểm |
|-------------|------------|-----------|
| Nearest | `cv2.INTER_NEAREST` | Nhanh nhất, chất lượng thấp |
| Linear | `cv2.INTER_LINEAR` | Cân bằng (mặc định) |
| Area | `cv2.INTER_AREA` | Tốt nhất khi thu nhỏ |
| Cubic | `cv2.INTER_CUBIC` | Chất lượng cao (4×4 pixels) |
| Lanczos4 | `cv2.INTER_LANCZOS4` | Chất lượng cao nhất (8×8 pixels) |

---

### Bài 5: Vẽ Hình và Thêm Văn Bản

**File:** `bai5_drawing_text.py`

```bash
python bai5_drawing_text.py
```

**Nội dung:**

#### Các hàm vẽ trong OpenCV

```python
# Đường thẳng
cv2.line(img, pt1, pt2, color, thickness)

# Mũi tên
cv2.arrowedLine(img, pt1, pt2, color, thickness)

# Hình chữ nhật
cv2.rectangle(img, pt1, pt2, color, thickness)
# thickness=-1 để tô đặc

# Hình tròn
cv2.circle(img, center, radius, color, thickness)

# Ellipse
cv2.ellipse(img, center, axes, angle, startAngle, endAngle, color, thickness)

# Đa giác
cv2.polylines(img, [pts], isClosed, color, thickness)

# Văn bản
cv2.putText(img, text, org, fontFace, fontScale, color, thickness)
```

#### Các hàm vẽ trong Pillow

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(img)

# Đường thẳng
draw.line([(x1,y1), (x2,y2)], fill=color, width=w)

# Hình chữ nhật
draw.rectangle([(x1,y1), (x2,y2)], outline=color, fill=color)

# Hình tròn / Ellipse
draw.ellipse([(x1,y1), (x2,y2)], outline=color, fill=color)

# Đa giác
draw.polygon([(x1,y1), (x2,y2), ...], outline=color)

# Văn bản
draw.text((x, y), "text", fill=color, font=font)
```

**Ảnh đầu ra:**
- `drawing_opencv_canvas.jpg` — Canvas trắng với các hình vẽ (OpenCV)
- `drawing_pillow_canvas.jpg` — Canvas trắng với các hình vẽ (Pillow)
- `drawing_on_image_opencv.jpg` — Vẽ hình trên ảnh thật (OpenCV)
- `drawing_on_image_pillow.jpg` — Vẽ hình trên ảnh thật (Pillow)

---

## 📝 Ghi Chú Quan Trọng

### Sự khác biệt giữa OpenCV và Pillow

| Đặc điểm | OpenCV | Pillow |
|-----------|--------|--------|
| Thứ tự kênh màu | BGR | RGB |
| Kiểu dữ liệu | NumPy ndarray | PIL Image object |
| Tọa độ crop | `[y1:y2, x1:x2]` | `(x1, y1, x2, y2)` |
| Hiển thị | Cửa sổ riêng | Trình xem mặc định |
| Tốc độ xử lý | Nhanh hơn | Chậm hơn |
| Hỗ trợ video | ✅ Có | ❌ Không |
| Dễ sử dụng | Trung bình | Dễ |

### Chuyển đổi giữa OpenCV và Pillow

```python
# OpenCV → Pillow
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
img_pil = Image.fromarray(img_rgb)

# Pillow → OpenCV
img_np = np.array(img_pil)
img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
```

---

## Tham Khảo

- [OpenCV Documentation](https://docs.opencv.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [OpenCV Python Tutorial](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

---

> 📌 **Lưu ý:** Tất cả ảnh kết quả sẽ được lưu trong thư mục `output/`. Thư mục này sẽ được tự động tạo khi chạy script.
