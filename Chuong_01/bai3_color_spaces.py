"""
Bài 3: Chuyển đổi không gian màu
- Chuyển đổi RGB sang Grayscale
- Chuyển đổi RGB sang HSV
- Chuyển đổi RGB sang LAB
- Hiển thị và lưu kết quả
"""

import cv2
import numpy as np
from PIL import Image
import os

# =====================================================
# Đường dẫn file
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "images", "sample_image.png")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("BÀI 3: CHUYỂN ĐỔI KHÔNG GIAN MÀU")
print("=" * 60)

# Đọc ảnh
img_bgr = cv2.imread(INPUT_PATH)
if img_bgr is None:
    print(f"❌ Không thể đọc file: {INPUT_PATH}")
    exit(1)

img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
print(f"\n📖 Đã đọc ảnh: {img_bgr.shape[1]}x{img_bgr.shape[0]} pixels")

# =====================================================
# PHẦN 1: Chuyển đổi sang Grayscale (Ảnh xám)
# =====================================================
print("\n🔲 Chuyển đổi sang Grayscale...")

# OpenCV: BGR -> Gray
img_gray_cv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
print(f"  [OpenCV] Kích thước: {img_gray_cv.shape}")
print(f"  [OpenCV] Giá trị pixel min: {img_gray_cv.min()}, max: {img_gray_cv.max()}")

# Pillow: RGB -> Gray
img_pil = Image.open(INPUT_PATH)
img_gray_pil = img_pil.convert("L")
print(f"  [Pillow] Kích thước: {img_gray_pil.size}")
print(f"  [Pillow] Chế độ: {img_gray_pil.mode}")

# Lưu kết quả
cv2.imwrite(os.path.join(OUTPUT_DIR, "gray_opencv.jpg"), img_gray_cv)
img_gray_pil.save(os.path.join(OUTPUT_DIR, "gray_pillow.jpg"))
print("  ✅ Đã lưu ảnh grayscale.")

# =====================================================
# PHẦN 2: Chuyển đổi sang HSV
# =====================================================
print("\n🌈 Chuyển đổi sang HSV (Hue-Saturation-Value)...")

# OpenCV: BGR -> HSV
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
print(f"  Kích thước: {img_hsv.shape}")

# Tách các kênh H, S, V
h_channel, s_channel, v_channel = cv2.split(img_hsv)
print(f"  Kênh H (Hue - Sắc độ):        min={h_channel.min()}, max={h_channel.max()}")
print(f"  Kênh S (Saturation - Bão hòa): min={s_channel.min()}, max={s_channel.max()}")
print(f"  Kênh V (Value - Giá trị):      min={v_channel.min()}, max={v_channel.max()}")

# Lưu từng kênh
cv2.imwrite(os.path.join(OUTPUT_DIR, "hsv_full.jpg"), img_hsv)
cv2.imwrite(os.path.join(OUTPUT_DIR, "hsv_h_channel.jpg"), h_channel)
cv2.imwrite(os.path.join(OUTPUT_DIR, "hsv_s_channel.jpg"), s_channel)
cv2.imwrite(os.path.join(OUTPUT_DIR, "hsv_v_channel.jpg"), v_channel)
print("  ✅ Đã lưu ảnh HSV và các kênh riêng.")

# Pillow: RGB -> HSV
img_hsv_pil = img_pil.convert("HSV")
print(f"  [Pillow] Chế độ: {img_hsv_pil.mode}")

# =====================================================
# PHẦN 3: Chuyển đổi sang LAB
# =====================================================
print("\n🎨 Chuyển đổi sang LAB (CIE L*a*b*)...")

# OpenCV: BGR -> LAB
img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
print(f"  Kích thước: {img_lab.shape}")

# Tách các kênh L, A, B
l_channel, a_channel, b_channel = cv2.split(img_lab)
print(f"  Kênh L (Lightness - Độ sáng): min={l_channel.min()}, max={l_channel.max()}")
print(f"  Kênh A (Green-Red):           min={a_channel.min()}, max={a_channel.max()}")
print(f"  Kênh B (Blue-Yellow):         min={b_channel.min()}, max={b_channel.max()}")

# Lưu từng kênh
cv2.imwrite(os.path.join(OUTPUT_DIR, "lab_full.jpg"), img_lab)
cv2.imwrite(os.path.join(OUTPUT_DIR, "lab_l_channel.jpg"), l_channel)
cv2.imwrite(os.path.join(OUTPUT_DIR, "lab_a_channel.jpg"), a_channel)
cv2.imwrite(os.path.join(OUTPUT_DIR, "lab_b_channel.jpg"), b_channel)
print("  ✅ Đã lưu ảnh LAB và các kênh riêng.")

# =====================================================
# PHẦN 4: Hiển thị tất cả các không gian màu
# =====================================================
print("\n🖼️  Hiển thị so sánh các không gian màu...")

# Tạo ảnh tổng hợp để so sánh
# Resize ảnh nhỏ lại để dễ hiển thị
scale = 0.4
h, w = img_bgr.shape[:2]
new_w, new_h = int(w * scale), int(h * scale)

img_small = cv2.resize(img_bgr, (new_w, new_h))
gray_small = cv2.resize(img_gray_cv, (new_w, new_h))
gray_bgr = cv2.cvtColor(gray_small, cv2.COLOR_GRAY2BGR)

h_small = cv2.resize(h_channel, (new_w, new_h))
h_bgr = cv2.cvtColor(h_small, cv2.COLOR_GRAY2BGR)

l_small = cv2.resize(l_channel, (new_w, new_h))
l_bgr = cv2.cvtColor(l_small, cv2.COLOR_GRAY2BGR)

# Ghép ảnh thành lưới 2x2
row1 = np.hstack([img_small, gray_bgr])
row2 = np.hstack([h_bgr, l_bgr])
grid = np.vstack([row1, row2])

# Thêm nhãn
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(grid, "Original (BGR)", (10, 30), font, 0.8, (0, 255, 0), 2)
cv2.putText(grid, "Grayscale", (new_w + 10, 30), font, 0.8, (0, 255, 0), 2)
cv2.putText(grid, "HSV - H Channel", (10, new_h + 30), font, 0.8, (0, 255, 0), 2)
cv2.putText(grid, "LAB - L Channel", (new_w + 10, new_h + 30), font, 0.8, (0, 255, 0), 2)

cv2.imwrite(os.path.join(OUTPUT_DIR, "color_spaces_comparison.jpg"), grid)

cv2.namedWindow("So sanh khong gian mau", cv2.WINDOW_NORMAL)
cv2.imshow("So sanh khong gian mau", grid)

print("  ➡️  Đóng cửa sổ ảnh để thoát.")

while True:
    # Nếu cửa sổ bị đóng thì thoát
    if cv2.getWindowProperty(
        "So sanh khong gian mau",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break

    cv2.waitKey(100)

cv2.destroyAllWindows()

# =====================================================
# Giải thích các không gian màu
# =====================================================
print("\n📚 GIẢI THÍCH CÁC KHÔNG GIAN MÀU:")
print("-" * 50)
print("""
  🔵 RGB/BGR (Red-Green-Blue):
     - Không gian màu cơ bản, mỗi pixel có 3 kênh.
     - OpenCV sử dụng BGR (Blue-Green-Red) thay vì RGB.
     - Giá trị mỗi kênh: 0-255.

  ⬛ Grayscale (Ảnh xám):
     - Chỉ có 1 kênh, biểu diễn cường độ sáng.
     - 0 = đen, 255 = trắng.
     - Công thức: Gray = 0.299*R + 0.587*G + 0.114*B

  🌈 HSV (Hue-Saturation-Value):
     - H (Hue): Sắc độ màu (0-180 trong OpenCV).
     - S (Saturation): Độ bão hòa (0-255).
     - V (Value): Độ sáng (0-255).
     - Hữu ích cho phát hiện màu sắc.

  🎨 LAB (CIE L*a*b*):
     - L: Lightness - Độ sáng (0-255, ánh xạ từ 0-100).
     - a: Trục Green(-) đến Red(+).
     - b: Trục Blue(-) đến Yellow(+).
     - Gần với cảm nhận màu của mắt người.
""")

print("🎉 Hoàn thành Bài 3!")
print("=" * 60)
